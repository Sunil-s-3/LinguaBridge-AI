from pathlib import Path
import os
import json

import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

# Patch Marian vocabulary loading to UTF-8 explicitly for Hugging Face downloads on Windows
try:
    import transformers.models.marian.tokenization_marian as marian_tokenizer

    def _utf8_load_json(path):
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)

    marian_tokenizer.load_json = _utf8_load_json
except Exception:
    pass

# Set UTF-8 environment variables for the module
os.environ.setdefault("PYTHONUTF8", "1")
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
os.environ.setdefault("HF_HUB_DISABLE_XET", "1")

BASE_DIR = Path(__file__).resolve().parent.parent

MODEL_PATHS = {
    "kannada": BASE_DIR / "models" / "kannada",
    "hindi": BASE_DIR / "models" / "hindi",
}

MODEL_IDS = {
    "kannada": "udgamlabs/Paar-en-kn",
    "hindi": "udgamlabs/Paar-en-hi",
}

HF_CACHE_DIR = BASE_DIR / "data" / ".hf_cache"
models = {}
tokenizers = {}


class TranslationError(Exception):
    pass


def _validate_model_files(model_path: Path) -> bool:
    if not (model_path / "config.json").is_file():
        return False
    has_weights = (
        (model_path / "model.safetensors").is_file()
        or (model_path / "pytorch_model.bin").is_file()
    )
    has_tokenizer = (
        (model_path / "source.spm").is_file()
        or (model_path / "tokenizer_config.json").is_file()
    )
    return has_weights and has_tokenizer


def load_model(language: str):
    normalized_language = language.strip().lower()
    if normalized_language not in MODEL_PATHS:
        raise TranslationError(f"Unsupported language: {language}")

    if normalized_language not in models:
        local_path = MODEL_PATHS[normalized_language]
        source = str(local_path) if _validate_model_files(local_path) else MODEL_IDS[normalized_language]

        try:
            HF_CACHE_DIR.mkdir(parents=True, exist_ok=True)
            local_files_only = _validate_model_files(local_path)
            tokenizers[normalized_language] = AutoTokenizer.from_pretrained(
                source,
                cache_dir=str(HF_CACHE_DIR),
                local_files_only=local_files_only,
            )
            models[normalized_language] = AutoModelForSeq2SeqLM.from_pretrained(
                source,
                cache_dir=str(HF_CACHE_DIR),
                local_files_only=local_files_only,
            )
            models[normalized_language].eval()
        except Exception as exc:
            raise TranslationError(
                f"Could not load the {normalized_language} model locally or from Hugging Face: {exc}"
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
        raise TranslationError(f"Translation failed for {language}: {exc}") from exc