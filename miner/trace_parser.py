import re

from game.propositions import VALID_PROPOSITIONS


class TraceParser:

    def __init__(self):

        self.states = []

        self.seen_true = set()

        self.seen_false = set()

    def parse_file(self, filepath):

        with open(
            filepath,
            "r",
            encoding="utf-8"
        ) as file:

            trace_text = file.read()

        return self.parse_text(
            trace_text
        )

    def parse_text(self, trace_text):

        self.states = []

        self.seen_true = set()

        self.seen_false = set()

        current_state = {}

        for line in trace_text.splitlines():

            match = re.search(
                r"([A-Za-z_][A-Za-z0-9_]*)\s*=\s*([01])",
                line
            )

            if not match:
                continue

            variable = match.group(1)

            value = (
                match.group(2) == "1"
            )

            if variable not in VALID_PROPOSITIONS:
                continue

            current_state[
                variable
            ] = value

            if value:

                self.seen_true.add(
                    variable
                )

            else:

                self.seen_false.add(
                    variable
                )

        if current_state:

            self.states.append(
                current_state
            )

        return self.states

    def propositions_seen(self):

        return sorted(
            self.seen_true |
            self.seen_false
        )

    def eventuality_candidates(self):

        candidates = []

        for proposition in self.propositions_seen():

            candidates.append(
                f"<> {proposition}"
            )

        return candidates

    def fairness_candidates(self):

        candidates = []

        for proposition in self.propositions_seen():
            candidates.append(
                f"[] <> {proposition}"
            )

        return candidates

    def conjunction_candidates(self):

        propositions = (
            self.propositions_seen()
        )

        candidates = []

        for left in propositions:

            for right in propositions:

                if left == right:
                    continue

                candidates.append(
                    f"<> ({left} && {right})"
                )

                candidates.append(
                    f"[] ({left} && {right})"
                )

        return candidates

    def persistence_candidates(self):

        candidates = []

        for proposition in self.propositions_seen():
            candidates.append(
                f"[] ({proposition} -> [] {proposition})"
            )

        return candidates


    def invariance_candidates(self):

        candidates = []

        for p in self.propositions_seen():
            candidates.append(
                f"[] ({p} -> [] {p})"
            )

        return candidates


    def strong_response_candidates(self):

        props = self.propositions_seen()

        candidates = []

        for left in props:

            for right in props:

                if left == right:
                    continue

                candidates.append(
                    f"[] ({left} -> [] <> {right})"
                )

        return candidates

    def chained_response_candidates(self):

        props = self.propositions_seen()

        candidates = []

        for a in props:

            for b in props:

                for c in props:

                    if len(
                            {a, b, c}
                    ) < 3:
                        continue

                    candidates.append(

                        f"[] ({a} -> <> ({b} && <> {c}))"

                    )

        return candidates

    def nested_response_candidates(self):

        propositions = (
            self.propositions_seen()
        )

        candidates = []

        for left in propositions:

            for right in propositions:

                if left == right:
                    continue

                candidates.append(

                    f"[] ({left} -> <> ({right} && <> {left}))"

                )

        return candidates

    def safety_candidates(self):

        candidates = []

        for proposition in self.propositions_seen():

            candidates.append(
                f"[] {proposition}"
            )

        return candidates

    def implication_candidates(self):

        relationships = [

            ("task_active", "task_completed"),

            ("object_carried", "delivered"),

            ("low_battery", "charging"),

            ("in_error", "recovery_active"),

            ("navigation_active", "object_carried"),

            ("waiting_for_human", "task_active"),

            ("recovery_active", "task_active")
        ]

        discovered = set(
            self.propositions_seen()
        )

        candidates = []

        for left, right in relationships:

            if (
                    left in discovered and
                    right in discovered
            ):
                candidates.append(
                    f"[] ({left} -> <> {right})"
                )

        return candidates