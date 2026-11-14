import json
import os
import matplotlib.pyplot as plt
from datetime import datetime


class StatisticsManager:

    def __init__(self):

        self.stats_dir = (
            "results/stats"
        )

        os.makedirs(
            self.stats_dir,
            exist_ok=True
        )

    def save_match(
            self,
            match_data
    ):

        timestamp = (
            datetime.now()
            .strftime(
                "%Y%m%d_%H%M%S"
            )
        )

        filename = os.path.join(
            self.stats_dir,
            f"match_{timestamp}.json"
        )

        with open(
                filename,
                "w",
                encoding="utf-8"
        ) as file:

            json.dump(
                match_data,
                file,
                indent=4
            )

        return filename

    def load_matches(self):

        matches = []

        if not os.path.exists(
                self.stats_dir
        ):
            return matches

        for filename in os.listdir(
                self.stats_dir
        ):

            if not filename.endswith(
                    ".json"
            ):
                continue

            path = os.path.join(
                self.stats_dir,
                filename
            )

            try:

                with open(
                        path,
                        "r",
                        encoding="utf-8"
                ) as file:

                    matches.append(
                        json.load(file)
                    )

            except Exception:

                pass

        return matches

    def graph_scores(self):

        matches = self.load_matches()

        if not matches:
            return

        human_scores = [
            match["human_score"]
            for match in matches
        ]

        miner_scores = [
            match["miner_score"]
            for match in matches
        ]

        match_numbers = list(
            range(
                1,
                len(matches) + 1
            )
        )

        plt.figure(
            figsize=(8, 5)
        )

        plt.plot(
            match_numbers,
            human_scores,
            marker="o",
            label="Human"
        )

        plt.plot(
            match_numbers,
            miner_scores,
            marker="s",
            label="Miner"
        )

        plt.title(
            "Scores by Match"
        )

        plt.xlabel(
            "Match Number"
        )

        plt.ylabel(
            "Score"
        )

        plt.legend()

        plt.grid(True)

        plt.show()

    def graph_property_types(self):

        matches = self.load_matches()

        if not matches:
            return

        human_safety = sum(
            m.get(
                "human_safety",
                0
            )
            for m in matches
        )

        human_liveness = sum(
            m.get(
                "human_liveness",
                0
            )
            for m in matches
        )

        human_response = sum(
            m.get(
                "human_response",
                0
            )
            for m in matches
        )

        human_fairness = sum(
            m.get(
                "human_fairness",
                0
            )
            for m in matches
        )

        miner_safety = sum(
            m.get(
                "miner_safety",
                0
            )
            for m in matches
        )

        miner_liveness = sum(
            m.get(
                "miner_liveness",
                0
            )
            for m in matches
        )

        miner_response = sum(
            m.get(
                "miner_response",
                0
            )
            for m in matches
        )

        miner_fairness = sum(
            m.get(
                "miner_fairness",
                0
            )
            for m in matches
        )

        import numpy as np

        labels = [
            "Safety",
            "Liveness",
            "Response",
            "Fairness"
        ]

        human_values = [
            human_safety,
            human_liveness,
            human_response,
            human_fairness
        ]

        miner_values = [
            miner_safety,
            miner_liveness,
            miner_response,
            miner_fairness
        ]

        x = np.arange(
            len(labels)
        )

        width = 0.35

        plt.figure(
            figsize=(8, 5)
        )

        plt.bar(
            x - width / 2,
            human_values,
            width,
            label="Human"
        )

        plt.bar(
            x + width / 2,
            miner_values,
            width,
            label="Miner"
        )

        plt.xticks(
            x,
            labels
        )

        plt.ylabel(
            "Verified Properties"
        )

        plt.title(
            "Property Types Discovered"
        )

        plt.legend()

        plt.tight_layout()

        plt.show()

    def summary(self):

        matches = (
            self.load_matches()
        )

        games = len(matches)

        human_wins = sum(
            1
            for match in matches
            if match.get("winner")
            == "Human"
        )

        miner_wins = sum(
            1
            for match in matches
            if match.get("winner")
            == "Miner"
        )

        ties = sum(
            1
            for match in matches
            if match.get("winner")
            == "Tie"
        )

        avg_human = 0
        avg_miner = 0

        best_human = 0
        best_miner = 0

        if games:

            avg_human = round(
                sum(
                    match.get(
                        "human_score",
                        0
                    )
                    for match in matches
                ) / games,
                2
            )

            avg_miner = round(
                sum(
                    match.get(
                        "miner_score",
                        0
                    )
                    for match in matches
                ) / games,
                2
            )

            best_human = max(
                match.get(
                    "human_score",
                    0
                )
                for match in matches
            )

            best_miner = max(
                match.get(
                    "miner_score",
                    0
                )
                for match in matches
            )

        return {

            "games":
                games,

            "human_wins":
                human_wins,

            "miner_wins":
                miner_wins,

            "ties":
                ties,

            "avg_human":
                avg_human,

            "avg_miner":
                avg_miner,

            "best_human":
                best_human,

            "best_miner":
                best_miner
        }