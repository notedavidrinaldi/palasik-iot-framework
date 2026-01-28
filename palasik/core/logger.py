# palasik/core/logger.py

class Logger:
    """
    Logger default PALASIK.
    Bisa digantikan plugin logger.
    """

    def info(self, message: str):
        print(f"[INFO] {message}")

    def warning(self, message: str):
        print(f"[WARN] {message}")

    def error(self, message: str):
        print(f"[ERROR] {message}")
