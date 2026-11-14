from game.scoring import ScoringEngine

class GameState:

    def __init__(self):

        #
        # Submitted formulas
        #

        self.human_candidates = []

        self.miner_candidates = []

        #
        # Verified formulas
        #

        self.human_verified = []

        self.miner_verified = []

        #
        # Scores
        #

        self.human_score = 0

        self.miner_score = 0

        self.scorer = ScoringEngine()

    #
    # Candidate collection
    #

    def add_human_candidate(self, formula):

        if formula not in self.human_candidates:

            self.human_candidates.append(
                formula
            )

    def add_miner_candidate(self, formula):

        if formula not in self.miner_candidates:

            self.miner_candidates.append(
                formula
            )

    #
    # End-game processing
    #

    def process_results(
            self,
            results,
            actor
    ):

        for result in results:

            if not result["verified"]:
                continue

            formula = result["formula"]

            #
            # simple temporary scoring
            #

            points = self.scorer.score_formula(
                formula
            )

            if actor == "human":

                if (
                        formula
                        not in self.human_verified
                ):

                    self.human_verified.append(
                        formula
                    )

                    self.human_score += points

            else:

                if (
                        formula
                        not in self.miner_verified
                ):

                    self.miner_verified.append(
                        formula
                    )

                    self.miner_score += points

    #
    # Statistics
    #

    def total_human_candidates(self):

        return len(
            self.human_candidates
        )

    def total_miner_candidates(self):

        return len(
            self.miner_candidates
        )

    def total_human_verified(self):

        return len(
            self.human_verified
        )

    def total_miner_verified(self):

        return len(
            self.miner_verified
        )

    def winner(self):

        if self.human_score > self.miner_score:
            return "Human"

        if self.miner_score > self.human_score:
            return "Miner"

        return "Tie"