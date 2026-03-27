import time


class ProgressLogger:

    def __init__(self, total):
        self.total = total
        self.start_time = time.time()
        self.last_print_time = 0

    def log(self, bucket, current, source):

        now = time.time()

        # 🔥 avoid spamming (print every 1 sec)
        if now - self.last_print_time < 1:
            return

        self.last_print_time = now

        elapsed = now - self.start_time

        if current == 0:
            eta = "N/A"
        else:
            rate = elapsed / current
            remaining = self.total - current
            eta_seconds = int(rate * remaining)

            mins = eta_seconds // 60
            secs = eta_seconds % 60
            eta = f"{mins}m {secs}s"

        percent = (current / self.total) * 100

        print(
            f"[{bucket}] {current}/{self.total} "
            f"({percent:.1f}%) | Source: {source} | ETA: {eta}"
        )