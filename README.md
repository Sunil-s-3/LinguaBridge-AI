# LinguaBridge AI

LinguaBridge AI is a local web app that translates English into Kannada and Hindi at the same time. It is built for a college NLP assignment and runs on a laptop. After setup, translation does not use the internet, a cloud API, or an API key.

The app does **not** train a model. It loads two pretrained Helsinki-NLP OPUS-MT models and runs inference on this computer.

## Features

- English text in, Kannada and Hindi translations side by side
- Copy either translation, or clear the input and results
- Optional reference translations and character-level BLEU scores
- Clickable example sentences with reference translations
- Recent history stored in a local SQLite file
- A short explanation of low-resource translation techniques
- Dark, responsive layout for laptop and phone screens
- A clear message when a model has not been downloaded

## Technologies

- Python 3.11+
- Streamlit
- Hugging Face Transformers and PyTorch
- SentencePiece (used by the Marian tokenizers)
- sacreBLEU
- Pandas (history table)
- Local MarianMT models

## Architecture

```
English text
    |
    v
Streamlit (app.py)
    |
    +--> src/translator.py --> models/kannada --> Kannada
    |
    +--> src/translator.py --> models/hindi --> Hindi
    |
    +--> src/evaluation.py --> character BLEU, only if a reference was typed
    |
    +--> data/translation_history.db
```

`setup_models.py` optionally downloads the models into `models/`. On Streamlit Cloud or any machine without local weights, `src/translator.py` automatically loads `udgamlabs/Paar-en-kn` and `udgamlabs/Paar-en-hi` with Hugging Face `from_pretrained()`. Downloaded files are cached under `data/.hf_cache`, and models are cached by Streamlit so repeated Translate clicks do not reload or download them unnecessarily.

## Installation (Windows)

Open PowerShell in this folder:

```powershell
cd "C:\Users\sunil achar\Desktop\8\LinguaBridge AI"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python setup_models.py
streamlit run app.py
```

Internet is required for `pip install` and `python setup_models.py`, unless those packages and model files are already on the computer. The PyTorch wheel installed from these requirements is the standard Windows wheel (about 130 MB).

If PowerShell blocks the virtual environment, run this once, then activate again:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

## Model download

`python setup_models.py` saves the two local models to:

- `models/kannada` from `udgamlabs/Paar-en-kn`
- `models/hindi` from `udgamlabs/Paar-en-hi`

Each model is a Marian transformer of about 77 million parameters (about 300 MB on disk) with SentencePiece tokenization. TensorFlow weight files are skipped.

If a folder is incomplete, the app shows: the model has not been downloaded yet, and it tells you to run `python setup_models.py`. It does not try to download during translation.

## Offline use

1. Finish `pip install` and `python setup_models.py` while online.
2. Disconnect from the internet.
3. From this folder, with the virtual environment active, run `streamlit run app.py`.
4. Open the local URL Streamlit prints, usually `http://localhost:8501`.

The status pill reads **OFFLINE-READY** when both model folders contain real weights. Fonts, icons, and scripts used by the page are local or already included with Streamlit. History stays in `data/translation_history.db`.

## How to translate

1. Type English in **Enter English Text**.
2. Click **Translate**.
3. Read the Kannada and Hindi cards.
4. Use **Copy** on a card, or **Clear** to reset the input and results.
5. Optionally paste a reference translation to see a BLEU score.
6. Or click an example. That loads the English sentence and both references.

The input limit is 1,500 characters. Empty text and missing models show a short message instead of a Python traceback.

## Sample translations

These lines were produced by the local models during project setup. Your wording should match on the same models. Reference translations used for BLEU practice are stored in `src/examples.py` and are written by hand, not by the model.

| English | Kannada | Hindi |
| --- | --- | --- |
| What is your name? | _(filled after the local test)_ | _(filled after the local test)_ |
| Good morning! | _(filled after the local test)_ | _(filled after the local test)_ |

## BLEU evaluation

When a reference box is empty, the app does not invent a score. It shows: "Add a reference translation to calculate the BLEU score."

When a reference is present, the score is sentence-level sacreBLEU with character tokenization (`tokenize="char"`). Character BLEU is used because Kannada and Hindi change word endings often, and ordinary word BLEU on one short sentence is often zero even when the translation is readable.

- 0–20: Low similarity
- 20–40: Moderate similarity
- 40–60: Good similarity
- 60+: High similarity

BLEU measures text similarity to the reference you typed. It does not perfectly measure translation quality or meaning. A fluent translation can score low if you worded the reference differently.

## Low-resource techniques

The in-app section **Low-Resource Language Optimization** explains:

- Transfer learning from the pretrained OPUS-MT models (inference only)
- Why a pretrained transformer helps when parallel Kannada or Hindi data is limited
- SentencePiece subwords
- Data augmentation and back-translation as training ideas this app does not run
- Laptop inference choices: load once, cache, inference mode, sentence batching, four-beam search

## Limitations

- Quality follows the 2020 OPUS-MT models. Kannada is often less fluent than Hindi because less parallel data was available.
- The models were trained on mixed public text (subtitles, software, government and religious text). They are weaker on technical or very informal language.
- Hindi example references use the conventional textbook masculine form for "I".
- Translations can be slow on CPU for long paragraphs. Very long input is rejected.
- This app does not fine-tune, back-translate, or train from scratch.
- BLEU is not a human judgment of meaning.

## Project layout

```
app.py
requirements.txt
README.md
setup_models.py
src/
  translator.py
  evaluation.py
  history.py
  examples.py
  utils.py
assets/styles.css
models/                 # Local model weights excluded from Git
  kannada/
  hindi/
data/                   # Local SQLite history excluded from Git
  translation_history.db
```
