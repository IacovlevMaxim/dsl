import tempfile
import os
from functools import wraps


def with_tempfile(extension):
    def decorator(test_func):
        @wraps(test_func)
        def wrapper(self, *args, **kwargs):
            with tempfile.NamedTemporaryFile(suffix=f".{extension}", delete=False) as tmp:
                temp_path = tmp.name
                try:
                    if extension in ('png', 'jpg', 'jpeg', 'gif', 'mp3', 'mp4', 'pdf'):
                        tmp.flush()
                        os.system(f"cp ../temp/test.{extension} {temp_path}")
                    return test_func(self, temp_path, *args, **kwargs)
                finally:
                    try:
                        os.unlink(temp_path)
                    except OSError:
                        pass
        return wrapper
    return decorator
