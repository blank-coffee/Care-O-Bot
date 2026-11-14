class PlayerSession:

    def __init__(self):

        self.formulas = []

        self.score = 0

    def add_formula(self, formula):

        entry = {
            "formula": formula,
            "verified": False,
            "score": 0
        }

        self.formulas.append(entry)

        return entry