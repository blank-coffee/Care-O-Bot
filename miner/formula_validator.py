from game.propositions import VALID_PROPOSITIONS


class FormulaValidator:

    def is_valid(self, formula):

        if not formula.strip():
            return False

        for proposition in VALID_PROPOSITIONS:

            if proposition in formula:
                return True

        return False