import os
import sys
import logging
import threading
import time
from queue import Queue, Empty
import re
from datetime import datetime
from types import SimpleNamespace
from typing import Optional, List
import flet as ft

from auto_reference_generator.reference_generator import ReferenceGenerator
from auto_reference_generator.common import running_time
from auto_reference_generator.cli import fixity_helper, suffix_helper

logger = logging.getLogger(__name__)


def _configure_logging(log_level: Optional[str], log_file: Optional[str]) -> None:
    try:
        level = getattr(logging, (log_level or "INFO").upper())
    except Exception:
        level = logging.INFO
    log_format = "%(asctime)s %(levelname)-8s [%(name)s] %(message)s"
    if log_file:
        logging.basicConfig(level=level, filename=log_file, filemode="a", format=log_format)
    else:
        logging.basicConfig(level=level, format=log_format)


def _parse_keywords(raw: Optional[str], mode: Optional[str]) -> Optional[List[str]]:
    if not raw:
        return None
    raw = raw.strip()
    if not raw:
        return None
    if mode == "from_json":
        return [raw]
    if "," in raw:
        return [k.strip() for k in raw.split(",") if k.strip()]
    return [k.strip() for k in raw.split() if k.strip()]


def _build_sort_key(sort_by: str | None):
    if sort_by == "alphabetical":
        return str.casefold
    return lambda x: (os.path.isfile(x), str.casefold(x))


def main(page: ft.Page):
    page.title = "Auto Reference Generator"
    page.window_width = 1400
    page.window_height = 900
    page.scroll = ft.ScrollMode.AUTO

    status_text = ft.Text("Idle", color=ft.Colors.GREY_600)
    progress_label = ft.Text("", color=ft.Colors.GREY_500)
    progress_bar = ft.ProgressBar(value=0.0)

    output_queue: Queue[str] = Queue()
    output_lines: list[str] = []
    output_lock = threading.Lock()
    output_max_lines = 500

    tqdm_pattern = re.compile(r"(?P<label>.+?):\s*(?P<pct>\d+)%\|.*?\|\s*(?P<cur>\d+)/(?:\s*)?(?P<total>\d+)")

    def update_progress_from_line(line: str) -> bool:
        match = tqdm_pattern.search(line)
        if not match:
            return False
        pct = int(match.group("pct"))
        cur = match.group("cur")
        total = match.group("total")
        label = match.group("label").strip()

        def _apply():
            progress_bar.value = max(0.0, min(1.0, pct / 100.0))
            progress_label.value = f"{label}: {pct}% ({cur}/{total})"
            page.update()
        run_in_ui(_apply)
        return True

    def enqueue_output(text: str):
        if not text:
            return
        cleaned = text.replace("\r", "\n")
        lines = cleaned.splitlines(True)
        filtered = []
        for line in lines:
            if update_progress_from_line(line):
                continue
            filtered.append(line)
        if filtered:
            output_queue.put("".join(filtered))

    class QueueLogHandler(logging.Handler):
        def emit(self, record: logging.LogRecord) -> None:
            try:
                msg = self.format(record)
            except Exception:
                msg = record.getMessage()
            enqueue_output(msg + "\n")

    class StreamRedirector:
        def __init__(self, write_fn):
            self._write_fn = write_fn

        def write(self, s: str):
            self._write_fn(s)

        def flush(self):
            return None

    def run_in_ui(fn):
        if threading.current_thread() is threading.main_thread():
            fn()
            return
        if hasattr(page, "call_from_thread"):
            try:
                page.call_from_thread(fn)
                return
            except Exception:
                pass
        if hasattr(page, "run_task"):
            async def runner():
                fn()
            try:
                page.run_task(runner)
                return
            except Exception:
                pass
        # No supported cross-thread UI update method available
        return

    def show_message(message: str, error: bool = False):
        def _apply():
            page.snack_bar = ft.SnackBar(
                ft.Text(message), bgcolor=ft.Colors.RED_400 if error else ft.Colors.GREEN_400
            )
            page.snack_bar.open = True
            page.update()
        run_in_ui(_apply)

    root_path = ft.TextField(label="Root directory", value=os.getcwd(), expand=True)
    output_path = ft.TextField(label="Output directory (optional)", expand=True)
    options_file = ft.TextField(
        label="Options file",
        value=os.path.join(os.path.dirname(__file__), "options", "options.properties"),
        expand=True,
    )
    log_level = ft.Dropdown(
        label="Log level",
        options=[
            ft.dropdown.Option(""),
            ft.dropdown.Option("DEBUG"),
            ft.dropdown.Option("INFO"),
            ft.dropdown.Option("WARNING"),
            ft.dropdown.Option("ERROR"),
        ],
        value="",
        width=200,
    )
    log_file = ft.TextField(label="Log file (optional)", expand=True)

    prefix = ft.TextField(label="Prefix", width=240)
    suffix = ft.TextField(label="Suffix", width=240)
    suffix_option = ft.Dropdown(
        label="Suffix option",
        options=[ft.dropdown.Option("file"), ft.dropdown.Option("dir"), ft.dropdown.Option("both")],
        value="file",
        width=200,
    )
    accession = ft.Dropdown(
        label="Accession mode",
        options=[ft.dropdown.Option(""), ft.dropdown.Option("file"), ft.dropdown.Option("dir"), ft.dropdown.Option("both")],
        value="",
        width=200,
    )
    acc_prefix = ft.TextField(label="Accession prefix", width=240)

    level_limit = ft.TextField(label="Level limit", width=160, hint_text="Integer")
    start_ref = ft.TextField(label="Start ref", value="1", width=120)
    delimiter = ft.TextField(label="Delimiter", value="/", width=120)

    remove_empty = ft.Checkbox(label="Remove empty directories", value=False)
    empty_export = ft.Checkbox(label="Export empty directories log", value=True)
    include_hidden = ft.Checkbox(label="Include hidden files/folders", value=False)
    create_meta_dir = ft.Checkbox(label="Create meta dir", value=True)
    skip_refs = ft.Checkbox(label="Skip reference generation", value=False)

    fixity = ft.Dropdown(
        label="Fixity",
        options=[
            ft.dropdown.Option(""),
            ft.dropdown.Option("MD5"),
            ft.dropdown.Option("SHA-1"),
            ft.dropdown.Option("SHA-256"),
            ft.dropdown.Option("SHA-512"),
        ],
        value="",
        width=200,
    )
    sort_by = ft.Dropdown(
        label="Sort by",
        options=[ft.dropdown.Option("folders_first"), ft.dropdown.Option("alphabetical")],
        value="folders_first",
        width=200,
    )
    output_format = ft.Dropdown(
        label="Output format",
        options=[
            ft.dropdown.Option("xlsx"),
            ft.dropdown.Option("csv"),
            ft.dropdown.Option("json"),
            ft.dropdown.Option("ods"),
            ft.dropdown.Option("xml"),
            ft.dropdown.Option("dict"),
        ],
        value="xlsx",
        width=160,
    )

    keywords = ft.TextField(
        label="Keywords (comma or space separated, or JSON path)",
        hint_text="Example: Project Alpha, Project Beta",
        expand=True,
    )
    keywords_mode = ft.Dropdown(
        label="Keywords mode",
        options=[
            ft.dropdown.Option("initialise"),
            ft.dropdown.Option("firstletters"),
            ft.dropdown.Option("from_json"),
        ],
        value="initialise",
        width=200,
    )
    keywords_retain_order = ft.Checkbox(label="Retain keyword order", value=False)
    keywords_case_sensitive = ft.Checkbox(label="Case sensitive", value=True)
    keywords_abbrev = ft.TextField(label="Abbreviation length", value="3", width=180)

    run_button = ft.Button(content=ft.Text("Generate References"))
    show_output_button = ft.TextButton("Show output")
    progress = ft.ProgressRing(visible=False)

    output_view = ft.TextField(
        value="",
        multiline=True,
        read_only=True,
        expand=True,
        min_lines=12,
        max_lines=16,
    )
    output_progress = ft.ProgressRing(visible=False)
    output_close = None
    output_panel = ft.Container(
        content=ft.Column(
            [
                ft.Row([output_progress, ft.Text("Running...")]),
                progress_bar,
                progress_label,
                output_view,
            ],
            spacing=8,
        ),
        visible=False,
    )

    def safe_show_picker_error():
        show_message(
            "File picker is not supported by this Flet runtime or platform. "
            "On Linux desktop, install Zenity. Otherwise, enter paths manually.",
            error=True,
        )

    async def pick_root(e):
        try:
            path = await ft.FilePicker().get_directory_path()
        except Exception:
            safe_show_picker_error()
            return
        if path:
            root_path.value = path
            page.update()

    async def pick_output(e):
        try:
            path = await ft.FilePicker().get_directory_path()
        except Exception:
            safe_show_picker_error()
            return
        if path:
            output_path.value = path
            page.update()

    async def pick_options(e):
        try:
            files = await ft.FilePicker().pick_files(allow_multiple=False)
        except Exception:
            safe_show_picker_error()
            return
        if files:
            options_file.value = files[0].path
            page.update()

    async def pick_log(e):
        try:
            files = await ft.FilePicker().pick_files(allow_multiple=False)
        except Exception:
            safe_show_picker_error()
            return
        if files:
            log_file.value = files[0].path
            page.update()

    root_pick = ft.IconButton(icon=ft.Icons.FOLDER_OPEN, on_click=pick_root)
    output_pick = ft.IconButton(icon=ft.Icons.FOLDER_OPEN, on_click=pick_output)
    options_pick = ft.IconButton(icon=ft.Icons.FILE_OPEN, on_click=pick_options)
    log_pick = ft.IconButton(icon=ft.Icons.FILE_OPEN, on_click=pick_log)

    def do_run():
        root = (root_path.value or "").strip()
        if not root or not os.path.isdir(root):
            show_message("Please select a valid root directory.", error=True)
            return

        output = (output_path.value or "").strip() or os.path.abspath(root)
        keywords_value = _parse_keywords(keywords.value, keywords_mode.value)
        if keywords_mode.value == "from_json" and (not keywords_value or len(keywords_value) != 1):
            show_message("Keywords mode 'from_json' requires a single JSON file path.", error=True)
            return

        try:
            level_limit_value = int(level_limit.value) if level_limit.value else None
        except ValueError:
            show_message("Level limit must be an integer.", error=True)
            return

        try:
            start_ref_value = int(start_ref.value) if start_ref.value else 1
        except ValueError:
            show_message("Start ref must be an integer.", error=True)
            return

        try:
            keywords_abbrev_value = int(keywords_abbrev.value) if keywords_abbrev.value else 3
        except ValueError:
            show_message("Abbreviation length must be an integer.", error=True)
            return

        _configure_logging(log_level.value or None, log_file.value or None)

        args = SimpleNamespace(
            root=root,
            output=output,
            prefix=prefix.value or None,
            suffix=suffix.value or None,
            suffix_option=suffix_helper(suffix_option.value) if suffix_option.value else None,
            accession=accession.value or None,
            acc_prefix=acc_prefix.value or None,
            level_limit=level_limit_value,
            start_ref=start_ref_value,
            delimiter=delimiter.value or None,
            remove_empty=remove_empty.value,
            disable_empty_export=empty_export.value,
            hidden=include_hidden.value,
            fixity=fixity_helper(fixity.value) if fixity.value else None,
            sort_by=sort_by.value or None,
            output_format=(output_format.value or "xlsx"),
            options_file=options_file.value or None,
            skip=skip_refs.value,
            disable_meta_dir=create_meta_dir.value,
            keywords=keywords_value,
            keywords_mode=keywords_mode.value,
            keywords_retain_order=keywords_retain_order.value,
            keywords_case_sensitivity=keywords_case_sensitive.value,
            keywords_abbreviation_number=keywords_abbrev_value,
        )

        sort_key = _build_sort_key(args.sort_by)

        start_time = datetime.now()
        ReferenceGenerator(
            args.root,
            output_path=args.output,
            prefix=args.prefix,
            accprefix=args.acc_prefix,
            suffix=args.suffix,
            suffix_options=args.suffix_option,
            level_limit=args.level_limit,
            fixity=args.fixity,
            empty_flag=args.remove_empty,
            empty_export_flag=args.disable_empty_export,
            accession_flag=args.accession,
            hidden_flag=args.hidden,
            start_ref=args.start_ref,
            meta_dir_flag=args.disable_meta_dir,
            skip_flag=args.skip,
            output_format=args.output_format,
            keywords=args.keywords,
            keywords_mode=args.keywords_mode,
            keywords_retain_order=args.keywords_retain_order,
            keywords_case_sensitivity=args.keywords_case_sensitivity,
            sort_key=sort_key,
            delimiter=args.delimiter,
            keywords_abbreviation_number=args.keywords_abbreviation_number,
            options_file=args.options_file,
        ).main()

        show_message(f"Run complete in {running_time(start_time)}")

    def on_run_clicked(e: ft.ControlEvent):
        ui_thread_safe = hasattr(page, "call_from_thread") or hasattr(page, "run_task")
        def set_running_state(running: bool, message: str):
            def _apply():
                run_button.disabled = running
                progress.visible = running
                status_text.value = message
                output_progress.visible = running
                page.update()
            run_in_ui(_apply)

        def toggle_output_panel(e: ft.ControlEvent):
            output_panel.visible = not output_panel.visible
            show_output_button.text = "Hide output" if output_panel.visible else "Show output"
            page.update()

        show_output_button.on_click = toggle_output_panel

        def append_output_text(text: str):
            with output_lock:
                output_lines.extend(text.splitlines(True))
                if len(output_lines) > output_max_lines:
                    del output_lines[: len(output_lines) - output_max_lines]
                output_view.value = "".join(output_lines)
            page.update()

        def pump_output(stop_event: threading.Event):
            while not stop_event.is_set():
                drained = []
                try:
                    while True:
                        drained.append(output_queue.get_nowait())
                except Empty:
                    pass
                if drained:
                    run_in_ui(lambda: append_output_text("".join(drained)))
                time.sleep(0.2)

        def run_background():
            stop_event = threading.Event()
            log_handler = QueueLogHandler()
            log_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
            root_logger = logging.getLogger()
            root_logger.addHandler(log_handler)
            stdout_prev = sys.stdout
            stderr_prev = sys.stderr
            sys.stdout = StreamRedirector(enqueue_output)
            sys.stderr = StreamRedirector(enqueue_output)
            pump_thread = threading.Thread(target=pump_output, args=(stop_event,), daemon=True)

            set_running_state(True, "Running...")
            if ui_thread_safe:
                pump_thread.start()
            try:
                do_run()
            except Exception as ex:
                logger.exception("Error running generator")
                show_message(str(ex), error=True)
                set_running_state(False, "Error")
                stop_event.set()
                return
            finally:
                stop_event.set()
                sys.stdout = stdout_prev
                sys.stderr = stderr_prev
                root_logger.removeHandler(log_handler)
            set_running_state(False, "Completed")

        def start_run():
            def _apply():
                output_lines.clear()
                output_view.value = ""
                page.update()
            run_in_ui(_apply)
            if ui_thread_safe:
                threading.Thread(target=run_background, daemon=True).start()
            else:
                run_background()

        if remove_empty.value:
            def confirm(result: bool):
                if result:
                    start_run()
                else:
                    show_message("Operation cancelled.")

            dialog = ft.AlertDialog(
                modal=True,
                title=ft.Text("Remove empty directories?"),
                content=ft.Text("This will permanently delete empty folders."),
                actions=[
                    ft.TextButton(
                        "Cancel",
                        on_click=lambda e: (
                            setattr(dialog, "open", False),
                            page.update(),
                            confirm(False),
                        ),
                    ),
                    ft.Button(
                        content=ft.Text("Proceed"),
                        on_click=lambda e: (
                            setattr(dialog, "open", False),
                            page.update(),
                            confirm(True),
                        ),
                    ),
                ],
            )
            page.dialog = dialog
            dialog.open = True
            page.update()
            return

        start_run()

    run_button.on_click = on_run_clicked

    page.add(
        ft.Column(
            [
                ft.Text("Auto Reference Generator", size=24, weight=ft.FontWeight.BOLD),
                ft.Text("Run the generator with a graphical interface.", color=ft.Colors.GREY_600),
                ft.Divider(),
                ft.Text("Paths", size=18, weight=ft.FontWeight.W_600),
                ft.Row([root_path, root_pick, output_path, output_pick]),
                ft.Row([options_file, options_pick, log_file, log_pick, log_level]),
                ft.Divider(),
                ft.Text("Reference options", size=18, weight=ft.FontWeight.W_600),
                ft.Row([prefix, suffix, suffix_option, accession, acc_prefix]),
                ft.Row([level_limit, start_ref, delimiter, fixity, sort_by, output_format]),
                ft.Row([remove_empty, empty_export, include_hidden, create_meta_dir, skip_refs]),
                ft.Divider(),
                ft.Text("Keywords", size=18, weight=ft.FontWeight.W_600),
                ft.Row([keywords, keywords_mode, keywords_abbrev]),
                ft.Row([keywords_retain_order, keywords_case_sensitive]),
                ft.Divider(),
                ft.Row([run_button, show_output_button, progress, status_text]),
                output_panel,
            ],
            spacing=6,
        )
    )


if __name__ == "__main__":
    try:
        ft.run(main)
    except TypeError:
        ft.run(target=main)
