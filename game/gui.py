import tkinter as tk
from tkinter import ttk

from game.player_session import PlayerSession
from game.replay import ReplayLog
from game.game_state import GameState
from miner.verifier import Verifier
from miner.miner_engine import MinerEngine
from miner.formula_validator import FormulaValidator
from game.statistics import (StatisticsManager)


class GameScreen:

    def __init__(self, root, minutes, show_miner, save_stats, limit_miner):

        self.root = root
        self.minutes = minutes
        self.show_miner = show_miner
        self.game_over = False
        self.save_stats = save_stats

        self.statistics = (
            StatisticsManager()
        )

        self.player = PlayerSession()

        self.replay_log = ReplayLog()

        self.game_state = GameState()

        self.validator = FormulaValidator()
        self.verifier = Verifier()

        self.remaining_seconds = int(minutes) * 60
        self.limit_miner = limit_miner

        self.miner = MinerEngine(
            self.on_miner_discovery,
            self.limit_miner
        )


        self.build_ui()

        self.update_timer()

        self.miner.start()

    def load_promela_model(self):

        try:

            with open(
                "promela/CareBot.pml",
                "r",
                encoding="utf-8"
            ) as file:

                return file.read()

        except Exception as error:

            return f"Unable to load model:\n\n{error}"

    def highlight_promela(self):

        keywords = [
            "proctype",
            "do",
            "od",
            "if",
            "fi",
            "bool",
            "chan",
            "mtype",
            "init",
            "run"
        ]

        states = [
            "idle",
            "navigate",
            "fetch",
            "deliver",
            "wait_human",
            "error",
            "recover",
            "charge"
        ]

        self.model_text.tag_config(
            "keyword",
            foreground="blue"
        )

        self.model_text.tag_config(
            "state",
            foreground="dark green"
        )

        for keyword in keywords:

            start = "1.0"

            while True:

                pos = self.model_text.search(
                    keyword,
                    start,
                    stopindex=tk.END
                )

                if not pos:
                    break

                end = f"{pos}+{len(keyword)}c"

                self.model_text.tag_add(
                    "keyword",
                    pos,
                    end
                )

                start = end

        for state in states:

            start = "1.0"

            while True:

                pos = self.model_text.search(
                    state,
                    start,
                    stopindex=tk.END
                )

                if not pos:
                    break

                end = f"{pos}+{len(state)}c"

                self.model_text.tag_add(
                    "state",
                    pos,
                    end
                )

                start = end

    def classify_property(self, formula):

        formula = formula.strip()

        if formula.startswith("[] <>"):
            return "Fairness"

        if (
                formula.startswith("[]")
                and "-> <>" in formula
        ):
            return "Response"

        if formula.startswith("<>"):
            return "Liveness"

        if formula.startswith("[]"):
            return "Safety"

        return "Unknown"

    def format_result(self, result):

        status = (
            "✓"
            if result["verified"]
            else "✗"
        )

        property_type = (
            self.classify_property(
                result["formula"]
            )
        )

        return (
            f"{status} "
            f"{result['formula']} "
            f"[{property_type}]"
        )

    def show_results_window(self):

        window = tk.Toplevel(
            self.root
        )

        window.title(
            "Match Results"
        )

        window.geometry(
            "500x350"
        )

        summary = (

            f"Winner: "
            f"{self.game_state.winner()}\n\n"

            f"Human Score: "
            f"{self.game_state.human_score}\n"

            f"Miner Score: "
            f"{self.game_state.miner_score}\n\n"

            f"Human Verified: "
            f"{self.game_state.total_human_verified()}\n"

            f"Miner Verified: "
            f"{self.game_state.total_miner_verified()}\n\n"

            f"Human Candidates: "
            f"{self.game_state.total_human_candidates()}\n"

            f"Miner Candidates: "
            f"{self.game_state.total_miner_candidates()}"
        )

        tk.Label(
            window,
            text=summary,
            font=("Arial", 12)
        ).pack(
            pady=20
        )

        tk.Button(
            window,
            text="Play Again",
            command=self.play_again
        ).pack(
            pady=5
        )

        tk.Button(
            window,
            text="Main Menu",
            command=self.return_to_menu
        ).pack(
            pady=5
        )

    def play_again(self):

        self.miner.stop()

        for widget in self.root.winfo_children():
            widget.destroy()

        self.root.geometry(
            "1200x700"
        )

        GameScreen(
            self.root,
            self.minutes,
            self.show_miner,
            self.save_stats,
            self.limit_miner
        )

    def return_to_menu(self):

        self.miner.stop()

        for widget in self.root.winfo_children():
            widget.destroy()

        self.root.geometry(
            "600x300"
        )

        StartScreen(
            self.root
        )

    def build_ui(self):

        self.timer_label = tk.Label(
            self.root,
            text="00:00",
            font=("Arial", 20, "bold")
        )

        self.timer_label.pack(
            pady=(10, 5)
        )

        self.score_label = tk.Label(
            self.root,
            text="Human: 0    Miner: 0",
            font=("Arial", 14, "bold")
        )

        self.score_label.pack(
            pady=(0, 10)
        )

        main_frame = tk.Frame(
            self.root
        )

        main_frame.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10
        )

        #
        # PROMELA MODEL
        #

        model_frame = tk.LabelFrame(
            main_frame,
            text="PROMELA Model"
        )

        model_frame.pack(
            side="left",
            fill="both",
            expand=True,
            padx=5
        )

        model_scroll = tk.Scrollbar(
            model_frame
        )

        model_scroll.pack(
            side="right",
            fill="y"
        )

        self.model_text = tk.Text(
            model_frame,
            font=("Consolas", 10),
            wrap="none",
            yscrollcommand=model_scroll.set
        )

        self.model_text.pack(
            side="left",
            fill="both",
            expand=True
        )

        model_scroll.config(
            command=self.model_text.yview
        )

        self.model_text.insert(
            "1.0",
            self.load_promela_model()
        )

        self.highlight_promela()

        self.model_text.config(
            state="disabled"
        )

        #
        # RIGHT PANEL
        #

        right_panel = tk.Frame(
            main_frame
        )

        right_panel.pack(
            side="left",
            fill="both",
            expand=True,
            padx=5
        )

        formula_frame = tk.Frame(
            right_panel
        )

        formula_frame.pack(
            fill="x",
            pady=5
        )

        self.formula_entry = tk.Entry(
            formula_frame,
            font=("Consolas", 12)
        )

        self.formula_entry.pack(
            side="left",
            fill="x",
            expand=True
        )

        self.formula_entry.bind(
            "<Return>",
            lambda event: self.submit_formula()
        )

        self.formula_entry.focus_set()

        submit_button = tk.Button(
            formula_frame,
            text="Submit",
            command=self.submit_formula
        )

        submit_button.pack(
            side="left",
            padx=5
        )

        #
        # HUMAN
        #

        human_frame = tk.LabelFrame(
            right_panel,
            text="Human Discoveries"
        )

        human_frame.pack(
            fill="both",
            expand=True,
            pady=5
        )

        self.human_list = tk.Listbox(
            human_frame,
            font=("Consolas", 10)
        )

        self.human_list.pack(
            fill="both",
            expand=True
        )

        #
        # MINER
        #

        miner_frame = tk.LabelFrame(
            right_panel,
            text="Miner Discoveries"
        )

        miner_frame.pack(
            fill="both",
            expand=True,
            pady=5
        )

        self.miner_list = tk.Listbox(
            miner_frame,
            font=("Consolas", 10)
        )

        self.miner_list.pack(
            fill="both",
            expand=True
        )

        if not self.show_miner:

            self.miner_list.insert(
                tk.END,
                "Hidden until game ends"
            )

    def update_score_display(self):

        self.score_label.config(
            text=
            f"Human: {self.game_state.human_score}    "
            f"Miner: {self.game_state.miner_score}"
        )

    def submit_formula(self):

        formula = self.formula_entry.get().strip()

        if not formula:
            return

        if not self.validator.is_valid(formula):

            self.human_list.insert(
                tk.END,
                f"INVALID: {formula}"
            )

            self.formula_entry.delete(
                0,
                tk.END
            )

            return

        self.player.add_formula(
            formula
        )

        self.game_state.add_human_candidate(
            formula
        )

        self.replay_log.record(
            "Human",
            formula
        )

        self.human_list.insert(
            tk.END,
            f"{formula:<70} [candidate]"
        )

        self.formula_entry.delete(
            0,
            tk.END
        )

    def update_timer(self):

        minutes = self.remaining_seconds // 60
        seconds = self.remaining_seconds % 60

        self.timer_label.config(
            text=f"{minutes:02}:{seconds:02}"
        )

        if self.remaining_seconds > 0:

            self.remaining_seconds -= 1

            self.root.after(
                1000,
                self.update_timer
            )

        else:

            self.end_game()

    def end_game(self):

        if self.game_over:
            return

        self.game_over = True

        self.miner.stop()

        self.timer_label.config(
            text="MATCH OVER"
        )

        self.formula_entry.config(
            state="disabled"
        )

        #
        # Verify human candidates
        #

        human_results = self.verifier.verify_batch(
            self.game_state.human_candidates
        )

        #
        # Verify miner candidates
        #

        miner_results = self.verifier.verify_batch(
            self.game_state.miner_candidates
        )

        #
        # Count verified property types
        #
        property_counts = {

            "human_safety": 0,
            "human_liveness": 0,
            "human_response": 0,
            "human_fairness": 0,

            "miner_safety": 0,
            "miner_liveness": 0,
            "miner_response": 0,
            "miner_fairness": 0

        }

        for result in human_results:

            if not result["verified"]:
                continue

            property_type = (
                self.classify_property(
                    result["formula"]
                ).lower()
            )

            property_counts[
                f"human_{property_type}"
            ] += 1

        for result in miner_results:

            if not result["verified"]:
                continue

            property_type = (
                self.classify_property(
                    result["formula"]
                ).lower()
            )

            property_counts[
                f"miner_{property_type}"
            ] += 1

        self.human_list.delete(
            0,
            tk.END
        )

        for result in human_results:
            self.human_list.insert(
                tk.END,
                self.format_result(
                    result
                )
            )

        self.miner_list.delete(
            0,
            tk.END
        )

        for result in miner_results:
            self.miner_list.insert(
                tk.END,
                self.format_result(
                    result
                )
            )

        print()
        print("=" * 50)
        print("VERIFICATION RESULTS")
        print("=" * 50)

        print()
        print("Human Formulas")
        print("-" * 50)

        for result in human_results:
            print(
                f"{result['formula']}"
                f" -> "
                f"{result['message']}"
            )

        print()
        print("Miner Formulas")
        print("-" * 50)

        for result in miner_results:
            print(
                f"{result['formula']}"
                f" -> "
                f"{result['message']}"
            )

        print()
        print("=" * 50)

        self.game_state.process_results(
            human_results,
            "human"
        )

        self.game_state.process_results(
            miner_results,
            "miner"
        )

        self.update_score_display()

        if self.save_stats:
            self.statistics.save_match(

                {

                    "winner":
                        self.game_state.winner(),

                    "human_score":
                        self.game_state.human_score,

                    "miner_score":
                        self.game_state.miner_score,

                    "human_verified":
                        self.game_state.total_human_verified(),

                    "miner_verified":
                        self.game_state.total_miner_verified(),

                    "human_candidates":
                        self.game_state.total_human_candidates(),

                    "miner_candidates":
                        self.game_state.total_miner_candidates(),

                    "duration_seconds":
                        int(self.minutes) * 60,

                    #
                    # Property statistics
                    #

                    "human_safety":
                        property_counts["human_safety"],

                    "human_liveness":
                        property_counts["human_liveness"],

                    "human_response":
                        property_counts["human_response"],

                    "human_fairness":
                        property_counts["human_fairness"],

                    "miner_safety":
                        property_counts["miner_safety"],

                    "miner_liveness":
                        property_counts["miner_liveness"],

                    "miner_response":
                        property_counts["miner_response"],

                    "miner_fairness":
                        property_counts["miner_fairness"]

                }

            )

        log_file = self.replay_log.save()

        print()
        print(
            f"Replay saved to: {log_file}"
        )

        print()

        print(
            "Verified Human:",
            self.game_state.total_human_verified()
        )

        print(
            "Verified Miner:",
            self.game_state.total_miner_verified()
        )

        print()

        print(
            "Winner:",
            self.game_state.winner()
        )

        print()

        print("=" * 50)
        print("FINAL RESULT")
        print("=" * 50)

        print(
            f"Human Candidates: "
            f"{self.game_state.total_human_candidates()}"
        )

        print(
            f"Miner Candidates: "
            f"{self.game_state.total_miner_candidates()}"
        )

        print()

        print(
            f"Human Verified: "
            f"{self.game_state.total_human_verified()}"
        )

        print(
            f"Miner Verified: "
            f"{self.game_state.total_miner_verified()}"
        )

        print()

        print(
            f"Human Score: "
            f"{self.game_state.human_score}"
        )

        print(
            f"Miner Score: "
            f"{self.game_state.miner_score}"
        )

        print()

        print(
            "Winner:",
            self.game_state.winner()
        )

        self.replay_log.print_log()

        self.show_results_window()

    def on_miner_discovery(self, formula):

        self.root.after(
            0,
            lambda: self.add_miner_formula(formula)
        )

    def add_miner_formula(self, formula):

        self.game_state.add_miner_candidate(
            formula
        )

        self.replay_log.record(
            "Miner",
            formula
        )

        if self.show_miner:

            self.miner_list.insert(
                tk.END,
                f"{formula:<70} [candidate]"
            )


class StartScreen:

    def __init__(self, root):

        self.root = root

        self.limit_miner = tk.BooleanVar(
            value=True
        )

        self.root.title(
            "Care-O-Bot Property Challenge"
        )

        self.root.geometry(
            "600x350"
        )

        self.time_limit = tk.StringVar(
            value="5"
        )

        self.show_miner = tk.BooleanVar(
            value=True
        )

        self.save_stats = tk.BooleanVar(
            value=False
        )

        self.build_ui()

    def build_ui(self):

        title = tk.Label(
            self.root,
            text="Care-O-Bot Property Challenge",
            font=("Arial", 18, "bold")
        )

        title.pack(
            pady=20
        )

        frame = tk.Frame(
            self.root
        )

        frame.pack(
            pady=20
        )

        tk.Label(
            frame,
            text="Time Limit (minutes)"
        ).grid(
            row=0,
            column=0,
            padx=10
        )

        box = ttk.Combobox(
            frame,
            textvariable=self.time_limit,
            values=[
                "1",
                "5",
                "10",
                "15",
                "30"
            ],
            state="readonly"
        )

        box.grid(
            row=0,
            column=1
        )

        tk.Checkbutton(
            self.root,
            text="Show Miner Progress",
            variable=self.show_miner
        ).pack()

        tk.Checkbutton(
            self.root,
            text="Limit Miner Speed",
            variable=self.limit_miner
        ).pack()

        tk.Checkbutton(
            self.root,
            text="Save Match Statistics",
            variable=self.save_stats
        ).pack()

        tk.Button(
            self.root,
            text="Match Statistics",
            command=self.show_statistics
        ).pack(
            pady=5
        )

        tk.Button(
            self.root,
            text="Start Match",
            command=self.start_match
        ).pack(
            pady=20
        )

    def show_statistics(self):

        stats = (
            StatisticsManager()
            .summary()
        )

        window = tk.Toplevel(
            self.root
        )

        window.title(
            "Match Statistics"
        )

        window.geometry(
            "450x300"
        )

        text = (

            f"Games Recorded: "
            f"{stats['games']}\n\n"

            f"Human Wins: "
            f"{stats['human_wins']}\n"

            f"Miner Wins: "
            f"{stats['miner_wins']}\n"

            f"Ties: "
            f"{stats['ties']}\n\n"

            f"Average Human Score: "
            f"{stats['avg_human']}\n"

            f"Average Miner Score: "
            f"{stats['avg_miner']}\n\n"

            f"Best Human Score: "
            f"{stats['best_human']}\n"

            f"Best Miner Score: "
            f"{stats['best_miner']}"
        )

        tk.Label(
            window,
            text=text,
            justify="left",
            font=("Arial", 11)
        ).pack(
            padx=20,
            pady=20
        )
        tk.Button(
            window,
            text="Score Graph",
            command=lambda:
            StatisticsManager()
            .graph_scores()
        ).pack(
            pady=5
        )

        tk.Button(
            window,
            text="Property Types Graph",
            command=lambda:
            StatisticsManager()
            .graph_property_types()
        ).pack(
            pady=5
        )

    def start_match(self):

        self.root.geometry(
            "1200x700"
        )

        for widget in self.root.winfo_children():

            widget.destroy()

        GameScreen(
            self.root,
            self.time_limit.get(),
            self.show_miner.get(),
            self.save_stats.get(),
            self.limit_miner.get()
        )


def launch_gui():

    root = tk.Tk()

    StartScreen(root)

    root.mainloop()