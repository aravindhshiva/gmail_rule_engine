import logging
import sys

class CustomLogger(logging.Logger):
    def success(self, msg, *args, **kwargs):
        self.log(logging.INFO, f"✅ {msg}", *args, **kwargs)

    def failure(self, msg, *args, **kwargs):
        self.log(logging.ERROR, f"❌ {msg}", *args, **kwargs)

def get_logger():
    log = CustomLogger("GmailRELogger")
    handler = logging.StreamHandler(sys.stdout)
    log.addHandler(handler)
    return log