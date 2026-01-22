"""
Hash Generator class for generating Fixities for files.

author: Christopher Prince
license: Apache License 2.0"
"""

import hashlib, logging
from auto_reference_generator.common import win_256_check

logger = logging.getLogger(__name__)

class HashGenerator():
    def __init__(self, algorithm: str = "SHA-1"):
        self.algorithm = algorithm
        self.buffer = 4096

    def hash_generator(self, file_path: str):
        file_path = win_256_check(file_path)
        if "SHA-1" in self.algorithm:
            hash = hashlib.sha1()
        elif "MD5" in self.algorithm:
            hash = hashlib.md5()
        elif "SHA-256" in self.algorithm:
            hash = hashlib.sha256()
        elif "SHA-512" in self.algorithm:
            hash = hashlib.sha512()
        else:
            hash = hashlib.sha1()
        logger.info(f'Generating Fixity using {self.algorithm} for: {file_path}')
        try:
            with open(file_path, 'rb', buffering = 0) as f:
                while True:
                    buff = f.read(self.buffer)
                    if not buff:
                        break
                    hash.update(buff)
                f.close()
            logger.debug(f'Generated Hash: {hash.hexdigest().upper()}')
            return hash.hexdigest().upper()
        except FileNotFoundError as e:
            logger.exception(f'File Not Found generating Hash: {e}')
            raise
        except IOError as e:
            logger.exception(f'I/O Error generating Hash: {e}')
            raise
        except Exception as e:
            logger.exception(f'Error Generating Hash: {e}')
            raise
