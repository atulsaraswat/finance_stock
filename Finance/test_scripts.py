import subprocess
import sys
import unittest
from pathlib import Path


class FinanceCliTests(unittest.TestCase):
    def test_sentiment_script_runs_from_finance_dir(self) -> None:
        finance_dir = Path(__file__).resolve().parent
        output_path = finance_dir / 'sentiment_output.json'
        if output_path.exists():
            output_path.unlink()
        self.addCleanup(lambda: output_path.exists() and output_path.unlink())

        completed = subprocess.run(
            [sys.executable, 'sentiment.py'],
            cwd=finance_dir,
            capture_output=True,
            text=True,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertTrue(output_path.exists(), completed.stdout)

    def test_sector_score_script_runs_from_finance_dir(self) -> None:
        finance_dir = Path(__file__).resolve().parent
        output_path = finance_dir / 'sector_score_output.json'
        if output_path.exists():
            output_path.unlink()
        self.addCleanup(lambda: output_path.exists() and output_path.unlink())

        completed = subprocess.run(
            [sys.executable, 'sector_score.py'],
            cwd=finance_dir,
            capture_output=True,
            text=True,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertTrue(output_path.exists(), completed.stdout)


if __name__ == '__main__':
    unittest.main()
