from miner.trace_runner import TraceRunner
from miner.trace_parser import TraceParser


class FormulaGenerator:

    def __init__(self):

        self.runner = TraceRunner()

        self.parser = TraceParser()

    def generate_candidates(self):

        trace_text = self.runner.generate_trace()

        if (
            not trace_text
            or trace_text.startswith("ERROR:")
        ):
            return []

        self.parser.parse_text(
            trace_text
        )

        candidates = []

        candidates.extend(
            self.parser.eventuality_candidates()
        )

        candidates.extend(
            self.parser.safety_candidates()
        )

        candidates.extend(
            self.parser.implication_candidates()
        )

        candidates.extend(
            self.parser.conjunction_candidates()
        )

        candidates.extend(
            self.parser.fairness_candidates()
        )

        candidates.extend(
            self.parser.strong_response_candidates()
        )

        candidates.extend(
            self.parser.chained_response_candidates()
        )

        candidates.extend(
            self.parser.persistence_candidates()
        )

        candidates.extend(
            self.parser.nested_response_candidates()
        )

        #
        # Remove duplicates while
        # preserving order
        #

        return list(
            dict.fromkeys(candidates)
        )