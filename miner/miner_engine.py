import random
import threading
import time

from miner.formula_generator import FormulaGenerator


class MinerEngine:

    def __init__(
            self,
            callback,
            limit_miner=True
    ):

        self.callback = callback

        self.limit_miner = limit_miner

        self.running = False

        self.thread = None

        self.discovered = set()

        self.generator = FormulaGenerator()

    def start(self):

        self.running = True

        self.thread = threading.Thread(
            target=self.mine_loop,
            daemon=True
        )

        self.thread.start()

    def stop(self):

        self.running = False

    def mine_loop(self):

        while self.running:

            #
            # Difficulty / limiter
            #

            if self.limit_miner:

                time.sleep(
                    random.randint(3, 8)
                )

            else:

                #
                # unrestricted
                #

                time.sleep(
                    0
                )

            candidates = (
                self.generator.generate_candidates()
            )

            if not candidates:
                continue

            formula = random.choice(
                candidates
            )

            if formula in self.discovered:
                continue

            self.discovered.add(
                formula
            )

            self.callback(
                formula
            )