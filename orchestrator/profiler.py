import time


class Profiler:

    def __init__(self):
        self.timings = {}

    def start(self, name):
        self.timings[name] = {
            "start": time.perf_counter()
        }

    def stop(self, name):
        if name not in self.timings:
            return

        self.timings[name]["elapsed"] = (
            time.perf_counter()
            - self.timings[name]["start"]
        )

    def get(self, name):
        if name not in self.timings:
            return 0.0

        return self.timings[name].get("elapsed", 0.0)

    def report(self):

        print("\n========== PERFORMANCE ==========")

        total = 0

        for name, value in self.timings.items():

            elapsed = value.get("elapsed", 0)

            total += elapsed

            print(f"{name:<20} {elapsed:.3f} sec")

        print("---------------------------------")
        print(f"{'TOTAL':<20} {total:.3f} sec")
        print("=================================\n")

    def reset(self):
        self.timings.clear()