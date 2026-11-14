import json
import os
import time
from datetime import datetime


class ReplayLog:

    def __init__(self):

        self.start_time = time.time()

        self.events = []

    def record(self, actor, formula):

        event = {
            "timestamp": round(
                time.time() - self.start_time,
                2
            ),
            "actor": actor,
            "formula": formula
        }

        self.events.append(event)

    def save(self):

        os.makedirs(
            "results/logs",
            exist_ok=True
        )

        timestamp = datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        )

        filename = (
            f"results/logs/game_{timestamp}.json"
        )

        game_data = {
            "created": timestamp,
            "events": self.events
        }

        with open(
            filename,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                game_data,
                file,
                indent=4
            )

        return filename

    def print_log(self):

        print("\n=== GAME LOG ===")

        for event in self.events:

            print(
                f"[{event['timestamp']}s] "
                f"{event['actor']} -> "
                f"{event['formula']}"
            )