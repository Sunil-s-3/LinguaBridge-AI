"""Input checks and local model availability."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODELS_DIR = ROOT / "models"
MAX_CHARS = 1500
MAX_REFERENCE_CHARS = 5000

MODEL_DIRS = {
    "kannada": MODELS_DIR / "kannada",
    "hindi": MODELS_DIR / "hindi",
}

LANGUAGE_NAMES = {
    "kannada": "Kannada",
    "hindi": "Hindi",
}


def word_count(text: str) -> int:
    stripped = text.strip()
    if not stripped:
        return 0
    return len(stripped.split())


def character_count(text: str) -> int:
    return len(text)


def validate_source(text: str) -> str | None:
    """Return a user-facing error, or None when the English text can be translated."""
    if text is None or not text.strip():
        return "Enter some English text before translating."
    if len(text) > MAX_CHARS:
        return (
            f"This text is too long for local translation. "
            f"Please use {MAX_CHARS:,} characters or fewer."
        )
    return None


def validate_reference(text: str, language: str) -> str | None:
    """Return a user-facing error for a reference that cannot be scored."""
    if text is None or not str(text).strip():
        return None
    if "\x00" in text:
        return f"The {language} reference contains invalid characters."
    if len(text) > MAX_REFERENCE_CHARS:
        return (
            f"The {language} reference is too long to score. "
            "Use a shorter reference translation."
        )
    return None


def _real_weight_file(path: Path) -> bool:
    return path.is_file() and path.stat().st_size > 1_000_000


def weights_present(model_dir: Path) -> bool:
    if not (model_dir / "config.json").is_file():
        return False
    has_tokenizer = (model_dir / "source.spm").is_file() or (
        model_dir / "tokenizer_config.json"
    ).is_file()
    has_weights = _real_weight_file(model_dir / "pytorch_model.bin") or _real_weight_file(
        model_dir / "model.safetensors"
    )
    return has_tokenizer and has_weights


def model_availability() -> dict[str, bool]:
    return {code: weights_present(path) for code, path in MODEL_DIRS.items()}


def all_models_ready() -> bool:
    status = model_availability()
    return all(status.values())


def missing_model_message() -> str:
    status = model_availability()
    missing = [LANGUAGE_NAMES[code] for code, ready in status.items() if not ready]
    if not missing:
        return ""
    names = " and ".join(missing)
    return (
        f"The {names} model has not been downloaded yet. "
        "Connect to the internet once and run: python setup_models.py"
    )
