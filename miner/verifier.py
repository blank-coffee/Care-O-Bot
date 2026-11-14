import json
import os
import re
import shutil
import subprocess
import tempfile

from game.propositions import (
    VALID_PROPOSITIONS,
    LTL_OPERATORS
)


class Verifier:

    def __init__(self):

        self.valid_props = set(
            VALID_PROPOSITIONS
        )

        self.operators = set(
            LTL_OPERATORS
        )

        self.model_path = (
            "promela/CareBot.pml"
        )

        self.cache_file = (
            "results/cache/verifier_cache.json"
        )

        with open(
            self.model_path,
            "r",
            encoding="utf-8"
        ) as file:

            self.base_model = file.read()

        self.cache = {}

        self.load_cache()

    def syntax_check(self, formula):

        if not formula:

            return (
                False,
                "Empty formula"
            )

        formula = formula.strip()

        if formula.count("(") != formula.count(")"):

            return (
                False,
                "Mismatched parentheses"
            )

        found_prop = False

        for proposition in self.valid_props:

            if proposition in formula:

                found_prop = True
                break

        if not found_prop:

            return (
                False,
                "No known propositions"
            )

        found_operator = False

        for operator in self.operators:

            if operator in formula:

                found_operator = True
                break

        if not found_operator:

            return (
                False,
                "No LTL operator found"
            )

        return (
            True,
            "Syntax valid"
        )

    def build_temp_model(
            self,
            formula
    ):

        model = self.base_model

        #
        # Remove any existing LTL property
        #

        model = re.sub(
            r"ltl\s+\w+\s*\{.*?\}",
            "",
            model,
            flags=re.DOTALL
        )

        model += (
            "\n\n"
            "ltl game_property {\n"
            f"    {formula}\n"
            "}\n"
        )

        temp_dir = tempfile.mkdtemp()

        temp_model = os.path.join(
            temp_dir,
            "verify_model.pml"
        )

        with open(
            temp_model,
            "w",
            encoding="utf-8"
        ) as file:

            file.write(model)

        return (
            temp_dir,
            temp_model
        )

    def spin_check(
            self,
            formula
    ):

        temp_dir = None

        try:

            temp_dir, temp_model = (
                self.build_temp_model(
                    formula
                )
            )

            wsl_model = (
                temp_model
                .replace("\\", "/")
                .replace(
                    "C:",
                    "/mnt/c"
                )
                .replace(
                    "c:",
                    "/mnt/c"
                )
            )

            #
            # Generate pan
            #

            result = subprocess.run(
                [
                    "wsl",
                    "spin",
                    "-a",
                    wsl_model
                ],
                cwd=temp_dir,
                capture_output=True,
                text=True
            )

            if result.returncode != 0:

                return (
                    False,
                    "SPIN generation failed"
                )

            #
            # Compile pan
            #

            result = subprocess.run(
                [
                    "wsl",
                    "gcc",
                    "pan.c",
                    "-o",
                    "pan"
                ],
                cwd=temp_dir,
                capture_output=True,
                text=True
            )

            if result.returncode != 0:

                return (
                    False,
                    "PAN compilation failed"
                )

            #
            # Execute verifier
            #

            result = subprocess.run(
                [
                    "wsl",
                    "./pan"
                ],
                cwd=temp_dir,
                capture_output=True,
                text=True
            )

            output = (
                result.stdout +
                result.stderr
            )

            if "errors: 0" in output:

                return (
                    True,
                    "Property holds"
                )

            return (
                False,
                "Counterexample found"
            )

        except Exception as error:

            return (
                False,
                str(error)
            )

        finally:

            if (
                temp_dir and
                os.path.exists(temp_dir)
            ):

                shutil.rmtree(
                    temp_dir,
                    ignore_errors=True
                )

    def verify(
            self,
            formula
    ):

        if formula in self.cache:

            return self.cache[
                formula
            ]

        valid, message = (
            self.syntax_check(
                formula
            )
        )

        if not valid:

            result = (
                False,
                message
            )

            self.cache[
                formula
            ] = result

            return result

        result = self.spin_check(
            formula
        )

        self.cache[
            formula
        ] = result

        return result

    def verify_batch(
            self,
            formulas
    ):

        results = []

        seen = set()

        for formula in formulas:

            verified, message = (
                self.verify(
                    formula
                )
            )

            duplicate = (
                formula in seen
            )

            seen.add(
                formula
            )

            results.append(
                {
                    "formula": formula,
                    "verified": verified,
                    "duplicate": duplicate,
                    "message": message
                }
            )

        self.save_cache()

        return results

    def load_cache(self):

        os.makedirs(
            "results/cache",
            exist_ok=True
        )

        if not os.path.exists(
                self.cache_file
        ):
            return

        try:

            with open(
                self.cache_file,
                "r",
                encoding="utf-8"
            ) as file:

                contents = json.load(
                    file
                )

            self.cache = {

                formula: (
                    data["verified"],
                    data["message"]
                )

                for formula, data
                in contents.items()
            }

        except Exception:

            self.cache = {}

    def save_cache(self):

        os.makedirs(
            "results/cache",
            exist_ok=True
        )

        contents = {}

        for formula, result in self.cache.items():

            contents[
                formula
            ] = {

                "verified": result[0],
                "message": result[1]
            }

        with open(
            self.cache_file,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                contents,
                file,
                indent=4
            )