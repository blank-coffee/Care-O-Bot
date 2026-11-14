import subprocess


class TraceRunner:

    def __init__(self):

        self.model_path = (
            "promela/CareBot.pml"
        )

    def generate_trace(self):

        try:

            result = subprocess.run(
                [
                    "wsl",
                    "spin",
                    "-u500",
                    "-p",
                    "/mnt/c/Users/josep/Care-O-Bot/promela/CareBot.pml"
                ],
                capture_output=True,
                text=True
            )

            return result.stdout

        except Exception as error:

            return (
                f"ERROR: {error}"
            )