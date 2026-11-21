import os
os.environ["PYTHONUTF8"] = "1"
os.environ["PYTHONIOENCODING"] = "utf-8"

from pathlib import Path
from transformers import MarianMTModel, MarianTokenizer

BASE_DIR = Path(__file__).parent
MODEL_DIR = BASE_DIR / "models"

MODELS = {
    "kannada": "udgamlabs/Paar-en-kn",
    "hindi": "udgamlabs/Paar-en-hi",
}

def download_model(language, model_id):
    local_path = MODEL_DIR / language
    local_path.mkdir(parents=True, exist_ok=True)

    print(f"\nDownloading {language} model: {model_id}")

    tokenizer = MarianTokenizer.from_pretrained(model_id)
    model = MarianMTModel.from_pretrained(model_id)

    tokenizer.save_pretrained(local_path)
    model.save_pretrained(local_path)

    print(f"{language.capitalize()} model downloaded successfully!")

if __name__ == "__main__":
    MODEL_DIR.mkdir(parents=True, exist_ok=True)

    for language, model_id in MODELS.items():
        try:
            download_model(language, model_id)
        except Exception as e:
            print(f"\nFailed to download {language} model:")
            print(e)

    print("\nModel setup completed.")