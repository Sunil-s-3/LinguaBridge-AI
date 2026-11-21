"""Checks that do not need the translation models."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.evaluation import band_label, score_translation
from src.history import add_translation, clear_history, recent_translations
from src.utils import validate_reference, validate_source


class EvaluationTests(unittest.TestCase):
    def test_bands(self) -> None:
        self.assertEqual(band_label(0), "Low similarity")
        self.assertEqual(band_label(19.9), "Low similarity")
        self.assertEqual(band_label(20), "Moderate similarity")
        self.assertEqual(band_label(39.9), "Moderate similarity")
        self.assertEqual(band_label(40), "Good similarity")
        self.assertEqual(band_label(59.9), "Good similarity")
        self.assertEqual(band_label(60), "High similarity")
        self.assertEqual(band_label(100), "High similarity")

    def test_identical_text_scores_high(self) -> None:
        result = score_translation("ಶುಭೋದಯ!", "ಶುಭೋದಯ!")
        self.assertIsNotNone(result)
        self.assertGreaterEqual(result["score"], 99)
        self.assertEqual(result["label"], "High similarity")

    def test_missing_reference_does_not_score(self) -> None:
        self.assertIsNone(score_translation("सुप्रभात!", ""))
        self.assertIsNone(score_translation("सुप्रभात!", "   "))
        self.assertIsNone(score_translation("", None))

    def test_reference_without_translation(self) -> None:
        result = score_translation("  ", "आपका नाम क्या है?")
        self.assertTrue(result["empty_hypothesis"])

    def test_different_text_is_not_perfect(self) -> None:
        result = score_translation("Hello", "आपका नाम क्या है?")
        self.assertLess(result["score"], 60)


class InputTests(unittest.TestCase):
    def test_empty_and_long_input(self) -> None:
        self.assertIsNotNone(validate_source("   "))
        self.assertIsNone(validate_source("Good morning!"))
        self.assertIsNotNone(validate_source("a" * 1501))

    def test_invalid_reference(self) -> None:
        self.assertIsNone(validate_reference("", "Hindi"))
        self.assertIsNotNone(validate_reference("bad\x00text", "Hindi"))
        self.assertIsNotNone(validate_reference("क" * 5001, "Hindi"))


class HistoryTests(unittest.TestCase):
    def test_round_trip_and_clear(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            db_path = Path(folder) / "history.db"
            add_translation("Hello", "ನಮಸ್ಕಾರ", "नमस्ते", db_path=db_path)
            rows = recent_translations(db_path=db_path)
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["English"], "Hello")
            self.assertEqual(rows[0]["Kannada"], "ನಮಸ್ಕಾರ")
            self.assertEqual(rows[0]["Hindi"], "नमस्ते")
            self.assertTrue(rows[0]["Time"])
            clear_history(db_path=db_path)
            self.assertEqual(recent_translations(db_path=db_path), [])


if __name__ == "__main__":
    unittest.main()
