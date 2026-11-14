# game/scoring.py

class ScoringEngine:

    def __init__(self):

        self.discovered = set()

    def score_formula(self, formula):

        if formula in self.discovered:
            return 0

        self.discovered.add(formula)

        complexity = self._complexity(formula)

        if complexity <= 1:
            return 1

        if complexity <= 3:
            return 3

        return 5

    def _complexity(self, formula):

        operators = [
            "[]",
            "<>",
            "U",
            "->",
            "&",
            "|"
        ]

        count = 0

        for op in operators:
            count += formula.count(op)

        return count