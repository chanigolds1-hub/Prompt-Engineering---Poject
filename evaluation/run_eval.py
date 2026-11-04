"""Run all test scenarios against one prompt version and save the results.

Usage: uv run python evaluation/run_eval.py v1
Commands are only generated and checked. They are never executed.

Only real model answers are saved. If the API fails, the run stops, and the
next run continues from the first scenario that has no saved answer.
"""

import csv
import os
import sys
import time
from pathlib import Path

from prompt_engineering_poject import agent
from prompt_engineering_poject.safety import check_command

EVAL_DIR = Path(__file__).resolve().parent
MAX_ATTEMPTS = 3
RETRY_DELAY_SECONDS = 10
REQUEST_DELAY_SECONDS = 5


def generate_with_retries(user_request: str) -> str:
    """Retry temporary failures, but not an exhausted quota."""

    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            return agent.generate_command(user_request)
        except Exception as error:
            if "429" in str(error) or attempt == MAX_ATTEMPTS:
                raise
            time.sleep(RETRY_DELAY_SECONDS)


def load_saved_results(path: Path) -> dict[str, dict]:
    """Load answers saved by an earlier run of the same prompt version."""

    if not path.exists():
        return {}

    with open(path, encoding="utf-8-sig", newline="") as file:
        return {
            row["id"]: row
            for row in csv.DictReader(file)
            if not row["output"].startswith("API_ERROR")
        }


def save_results(path: Path, results: dict[str, dict]) -> None:
    # utf-8-sig keeps the Hebrew readable when imported into a spreadsheet
    rows = sorted(results.values(), key=lambda row: int(row["id"]))
    with open(path, "w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    version = sys.argv[1] if len(sys.argv) > 1 else "v1"
    agent.PROMPT_PATH = agent.PROJECT_ROOT / "prompts" / f"prompt_{version}.txt"
    result_path = EVAL_DIR / f"results_{version}.csv"

    with open(EVAL_DIR / "scenarios.csv", encoding="utf-8", newline="") as file:
        scenarios = list(csv.DictReader(file))

    results = load_saved_results(result_path)

    for scenario in scenarios:
        if scenario["id"] in results:
            continue

        try:
            output = generate_with_retries(scenario["input"])
        except Exception as error:
            print(f"Stopped at scenario {scenario['id']}: {str(error)[:150]}")
            break

        _, filter_message = check_command(output)
        results[scenario["id"]] = {
            **scenario,
            "output": output,
            "filter_status": filter_message,
            "model": os.environ["GEMINI_MODEL"],
        }
        print(f"{scenario['id']}: {output!r}", flush=True)
        time.sleep(REQUEST_DELAY_SECONDS)

    if results:
        save_results(result_path, results)

    print(f"Saved {len(results)} of {len(scenarios)} answers to {result_path}")
    return 0 if len(results) == len(scenarios) else 1


if __name__ == "__main__":
    sys.exit(main())
