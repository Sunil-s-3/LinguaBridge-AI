from pathlib import Path
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

BASE_DIR = Path(__file__).resolve().parent.parent

MODEL_PATHS = {
    "kannada": BASE_DIR / "models" / "kannada",
    "hindi": BASE_DIR / "models" / "hindi",
}

models = {}
tokenizers = {}


class TranslationError(Exception):
    pass


def _validate_model_files(language: str, model_path: Path) -> None:
    required_files = ("config.json",)
    for filename in required_files:
        if not (model_path / filename).is_file():
            raise TranslationError(
                f"Model folder is incomplete for {language}: missing {filename}"
            )

    has_weights = (
        (model_path / "model.safetensors").is_file()
        or (model_path / "pytorch_model.bin").is_file()
    )
    if not has_weights:
        raise TranslationError(
            f"Model folder is incomplete for {language}: missing model weights"
        )


def load_model(language: str):
    normalized_language = language.strip().lower()
    if normalized_language not in MODEL_PATHS:
        raise TranslationError(f"Unsupported language: {language}")

    if normalized_language not in models:
        model_path = MODEL_PATHS[normalized_language]

        if not model_path.is_dir():
            raise TranslationError(
                f"Model folder not found: {model_path}. Recheck the local models directory."
            )

        _validate_model_files(normalized_language, model_path)

        try:
            tokenizer = AutoTokenizer.from_pretrained(
                str(model_path),
                local_files_only=True,
            )
            model = AutoModelForSeq2SeqLM.from_pretrained(
                str(model_path),
                local_files_only=True,
            )
            model.eval()
            models[normalized_language] = model
            tokenizers[normalized_language] = tokenizer
        except Exception as exc:
            raise TranslationError(
                f"Failed to load {normalized_language} model locally: {exc}"
            ) from exc

    return models[normalized_language], tokenizers[normalized_language]


def translate_text(text: str, language: str) -> str:
    if not text or not text.strip():
        raise TranslationError("Please enter text to translate.")

    model, tokenizer = load_model(language)

    try:
        inputs = tokenizer(
            text.strip(),
            return_tensors="pt",
            truncation=True,
            max_length=128,
        )

        with torch.no_grad():
            output = model.generate(
                **inputs,
                max_new_tokens=128,
                num_beams=4,
                early_stopping=True,
            )

        result = tokenizer.decode(output[0], skip_special_tokens=True)
        if not result.strip():
            raise TranslationError(f"The {language} model returned an empty translation.")
        return result.strip()
    except TranslationError:
        raise
    except Exception as exc:
        raise TranslationError(
            f"Translation failed for {language}: {exc}"
        ) from exc