"""Character-level BLEU for Kannada and Hindi translations."""

from __future__ import annotations

import sacrebleu

MISSING_REFERENCE = "Add a reference translation to calculate the BLEU score."


def band_label(score: float) -> str:
    if score < 20:
        return "Low similarity"
    if score < 40:
        return "Moderate similarity"
    if score < 60:
        return "Good similarity"
    return "High similarity"


def score_translation(hypothesis: str, reference: str) -> dict | None:
    """Score one translation against one reference.

    Returns None when the reference is blank. BLEU is never invented.
    Character sacreBLEU is used because Kannada and Hindi are morphologically
    rich, and word BLEU on a single short sentence is often zero even when the
    translation is readable.
    """
    if reference is None or not str(reference).strip():
        return None

    hypothesis_text = "" if hypothesis is None else str(hypothesis).strip()
    reference_text = str(reference).strip()
    if not hypothesis_text:
        return {"empty_hypothesis": True}

    bleu = sacrebleu.sentence_bleu(
        hypothesis_text,
        [reference_text],
        tokenize="char",
        use_effective_order=True,
    )
    value = round(float(bleu.score), 1)
    return {
        "empty_hypothesis": False,
        "score": value,
        "label": band_label(value),
    }
