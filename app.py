"""LinguaBridge AI — local English to Kannada and Hindi translation."""

from __future__ import annotations

import os
os.environ.setdefault("PYTHONUTF8", "1")
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
os.environ.setdefault("HF_HUB_DISABLE_XET", "1")

import html
import json
from pathlib import Path

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

from src.evaluation import MISSING_REFERENCE, score_translation
from src.examples import EXAMPLES
from src.history import add_translation, clear_history, recent_translations
from src.translator import TranslationError, load_model, translate_text
from src.utils import (
    MAX_CHARS,
    all_models_ready,
    character_count,
    missing_model_message,
    validate_reference,
    validate_source,
    word_count,
)

ROOT = Path(__file__).resolve().parent
EMPTY_TRANSLATION = "Your translation will appear here."


@st.cache_resource(show_spinner=False)
def get_bundle(language: str):
    """Load and cache one local or Hugging Face model bundle."""
    return load_model(language)


def inject_css() -> None:
    css_path = ROOT / "assets" / "styles.css"
    css = css_path.read_text(encoding="utf-8")
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


def init_state() -> None:
    defaults = {
        "english_input": "",
        "ref_kn": "",
        "ref_hi": "",
        "kn_out": "",
        "hi_out": "",
        "status_note": "",
        "form_error": "",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def clear_form() -> None:
    st.session_state.english_input = ""
    st.session_state.ref_kn = ""
    st.session_state.ref_hi = ""
    st.session_state.kn_out = ""
    st.session_state.hi_out = ""
    st.session_state.status_note = ""
    st.session_state.form_error = ""


def use_example(index: int) -> None:
    example = EXAMPLES[index]
    st.session_state.english_input = example["en"]
    st.session_state.ref_kn = example["kn"]
    st.session_state.ref_hi = example["hi"]
    st.session_state.kn_out = ""
    st.session_state.hi_out = ""
    st.session_state.status_note = ""
    st.session_state.form_error = ""


def render_header(models_ready: bool) -> None:
    pill_class = "ready" if models_ready else "missing"
    pill_text = "OFFLINE-READY" if models_ready else "MODELS MISSING"
    st.markdown(
        f"""
        <div class="lb-header">
          <div class="lb-brand">
            <div class="lb-mark" aria-hidden="true">
              <svg width="28" height="28" viewBox="0 0 28 28" fill="none">
                <path d="M4 18c4-6 6-6 10-6s6 0 10 6" stroke="#F8FAFC" stroke-width="1.8" stroke-linecap="round"/>
                <path d="M7 14.5c2.2-3 3.4-3 7-3s4.8 0 7 3" stroke="#C4B5FD" stroke-width="1.8" stroke-linecap="round"/>
                <circle cx="14" cy="8" r="2" fill="#20C997"/>
              </svg>
            </div>
            <div>
              <h1>LinguaBridge AI</h1>
              <p class="lb-sub">English to Kannada &amp; Hindi Translation</p>
            </div>
          </div>
          <div class="lb-pill {pill_class}">● {pill_text}</div>
        </div>
        <p class="lb-tag">Translate across languages. No cloud required.</p>
        """,
        unsafe_allow_html=True,
    )


def copy_button(text: str) -> None:
    payload = json.dumps(text)
    components.html(
        f"""
        <button id="copy" type="button">Copy</button>
        <script>
        const button = document.getElementById("copy");
        button.onclick = async () => {{
          try {{
            await navigator.clipboard.writeText({payload});
            button.textContent = "Copied";
          }} catch (err) {{
            button.textContent = "Select the text to copy";
          }}
        }};
        </script>
        <style>
          html, body {{
            margin: 0;
            background: #151c2e;
          }}
          button {{
            width: 100%;
            min-height: 44px;
            border: 1px solid rgba(148, 163, 184, 0.28);
            border-radius: 12px;
            background: #1b2438;
            color: #f8fafc;
            font: 700 15px "Segoe UI", sans-serif;
            cursor: pointer;
          }}
          button:hover {{ background: #243049; }}
        </style>
        """,
        height=52,
    )


def render_translation_card(title: str, script: str, text: str) -> None:
    if text.strip():
        body = f'<div class="lb-output">{html.escape(text)}</div>'
    else:
        body = f'<div class="lb-output empty">{EMPTY_TRANSLATION}</div>'
    st.markdown(
        f"""
        <div class="lb-card">
          <div class="lb-kicker">
            <h2>{html.escape(title)}</h2>
            <span class="lb-script">{html.escape(script)}</span>
          </div>
          {body}
        </div>
        """,
        unsafe_allow_html=True,
    )
    if text.strip():
        copy_button(text)


def band_class(label: str) -> str:
    mapping = {
        "Low similarity": "low",
        "Moderate similarity": "moderate",
        "Good similarity": "good",
        "High similarity": "high",
    }
    return mapping.get(label, "moderate")


def render_score(title: str, result: dict | None, reference_error: str | None) -> None:
    if reference_error:
        body = f"<p>{html.escape(reference_error)}</p>"
    elif result is None:
        body = f"<p>{html.escape(MISSING_REFERENCE)}</p>"
    elif result.get("empty_hypothesis"):
        body = "<p>Translate the English text before calculating the BLEU score.</p>"
    else:
        kind = band_class(result["label"])
        width = max(0, min(100, float(result["score"])))
        body = f"""
        <div class="lb-score-value">{result["score"]:.1f}</div>
        <div class="lb-score-label band-{kind}">{html.escape(result["label"])}</div>
        <div class="lb-meter" aria-hidden="true"><span class="fill-{kind}" style="width:{width:.1f}%"></span></div>
        """
    st.markdown(
        f'<div class="lb-score"><h3>{html.escape(title)}</h3>{body}</div>',
        unsafe_allow_html=True,
    )


def low_resource_section() -> None:
    st.markdown(
        """
        <div class="lb-section">
          <div class="lb-card">
            <h2>Low-Resource Language Optimization</h2>
            <p>
              Kannada and Hindi have far less clean parallel text than languages
              such as French or German. LinguaBridge does not train a model.
              It runs two pretrained Marian translation models and explains the
              ideas that make that possible.
            </p>
            <div class="lb-techniques">
              <article class="lb-technique">
                <h3>Transfer learning</h3>
                <p>
                  Helsinki-NLP trained these OPUS-MT models on public parallel
                  sentences. The weights already map English subwords to Kannada
                  or Hindi subwords. This app loads those weights and translates.
                  It does not fine-tune them.
                </p>
              </article>
              <article class="lb-technique">
                <h3>Multilingual knowledge transfer</h3>
                <p>
                  Each model is bilingual, but both reuse the same Marian
                  transformer design and a large shared SentencePiece vocabulary.
                  Hindi has more published parallel data than Kannada, so Hindi
                  output is often steadier. Kannada still benefits from the same
                  pretrained encoder-decoder recipe instead of an empty network.
                </p>
              </article>
              <article class="lb-technique">
                <h3>Subword tokenization</h3>
                <p>
                  SentencePiece splits words into frequent pieces before they
                  enter the transformer. A rare name or an inflected Kannada
                  form can be built from pieces the model has seen, which matters
                  when the parallel corpus does not contain every word.
                </p>
              </article>
              <article class="lb-technique">
                <h3>Data augmentation</h3>
                <p>
                  Low-resource training often expands a small corpus with synonym
                  replacement, word dropout, or spelling changes. Those steps
                  happen during research training. This application does not
                  augment data or update weights.
                </p>
              </article>
              <article class="lb-technique">
                <h3>Back-translation</h3>
                <p>
                  A common training idea is to translate extra monolingual
                  Kannada or Hindi into English, then train the forward model on
                  those synthetic pairs. LinguaBridge does not back-translate and
                  does not create training data.
                </p>
              </article>
              <article class="lb-technique">
                <h3>Inference on a laptop</h3>
                <p>
                  Each model is loaded once, cached, and run with PyTorch
                  inference mode. Sentences in a paragraph are batched. Beam
                  search uses four beams. On CPU, PyTorch is limited to four
                  threads so the laptop stays usable.
                </p>
              </article>
            </div>
            <p class="lb-callout">
              Low-resource translation is still hard: Kannada is agglutinative,
              both languages use their own scripts, and the OPUS mix of subtitles,
              software, and public text does not match every domain. BLEU below
              compares characters. It does not prove that the meaning is right.
            </p>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def run_translation() -> None:
    source = st.session_state.english_input
    error = validate_source(source)
    if error:
        st.session_state.form_error = error
        st.session_state.status_note = ""
        return
    if not all_models_ready():
        st.session_state.form_error = missing_model_message()
        st.session_state.status_note = ""
        return

    st.session_state.form_error = ""
    try:
        with st.spinner("Loading translation models and translating..."):
            get_bundle("kannada")
            get_bundle("hindi")
            kannada = translate_text(source, "kannada")
            hindi = translate_text(source, "hindi")
        st.session_state.kn_out = kannada
        st.session_state.hi_out = hindi
        add_translation(source, kannada, hindi)
        st.session_state.status_note = "Both translations were generated on this computer."
    except TranslationError as exc:
        st.session_state.form_error = str(exc)
        st.session_state.status_note = ""
    except Exception as exc:
        st.session_state.form_error = (
            f"Translation could not be completed: {exc}. Try a shorter sentence."
        )
        st.session_state.status_note = ""


def main() -> None:
    st.set_page_config(
        page_title="LinguaBridge AI",
        page_icon="🌐",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    inject_css()
    init_state()

    models_ready = all_models_ready()
    render_header(models_ready)
    if not models_ready:
        st.error(missing_model_message())

    st.text_area(
        "Enter English Text",
        height=220,
        placeholder="Type a sentence, paragraph, or message in English...",
        key="english_input",
    )
    source = st.session_state.english_input
    count_class = "lb-counts warn" if len(source) > MAX_CHARS else "lb-counts"
    st.markdown(
        f'<p class="{count_class}">{word_count(source)} words · '
        f"{character_count(source)} / {MAX_CHARS} characters</p>",
        unsafe_allow_html=True,
    )

    translate_col, clear_col = st.columns(2)
    translate_clicked = translate_col.button(
        "Translate",
        type="primary",
        use_container_width=True,
    )
    clear_col.button(
        "Clear",
        use_container_width=True,
        on_click=clear_form,
    )
    if translate_clicked:
        run_translation()

    if st.session_state.form_error:
        st.error(st.session_state.form_error)
    elif st.session_state.status_note:
        st.success(st.session_state.status_note)

    kannada_col, hindi_col = st.columns(2)
    with kannada_col:
        render_translation_card(
            "Kannada Translation",
            "ಕನ್ನಡ",
            st.session_state.kn_out,
        )
    with hindi_col:
        render_translation_card(
            "Hindi Translation",
            "हिन्दी",
            st.session_state.hi_out,
        )

    st.markdown(
        """
        <div class="lb-section">
          <h2>Translation Evaluation</h2>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p class='lb-note'>BLEU measures how similar the characters are to a "
        "reference translation. It does not perfectly measure translation quality "
        "or meaning. Scores use character-level sacreBLEU, which is steadier for "
        "Kannada and Hindi than word BLEU on one short sentence. "
        "0–20 low, 20–40 moderate, 40–60 good, 60+ high.</p>",
        unsafe_allow_html=True,
    )
    ref_left, ref_right = st.columns(2)
    with ref_left:
        st.text_area(
            "Reference Kannada translation",
            height=110,
            placeholder="Paste a Kannada reference translation (optional)",
            key="ref_kn",
        )
    with ref_right:
        st.text_area(
            "Reference Hindi translation",
            height=110,
            placeholder="Paste a Hindi reference translation (optional)",
            key="ref_hi",
        )

    kn_ref_error = validate_reference(st.session_state.ref_kn, "Kannada")
    hi_ref_error = validate_reference(st.session_state.ref_hi, "Hindi")
    kn_score = None if kn_ref_error else score_translation(
        st.session_state.kn_out,
        st.session_state.ref_kn,
    )
    hi_score = None if hi_ref_error else score_translation(
        st.session_state.hi_out,
        st.session_state.ref_hi,
    )
    score_left, score_right = st.columns(2)
    with score_left:
        render_score("Kannada BLEU", kn_score, kn_ref_error)
    with score_right:
        render_score("Hindi BLEU", hi_score, hi_ref_error)

    st.markdown(
        """
        <div class="lb-section">
          <h2>Translation Examples</h2>
          <p class="lb-note">Choose a sentence to load it with reference translations.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    for start in range(0, len(EXAMPLES), 3):
        columns = st.columns(3)
        for offset, column in enumerate(columns):
            index = start + offset
            if index >= len(EXAMPLES):
                continue
            column.button(
                EXAMPLES[index]["en"],
                key=f"example_{index}",
                use_container_width=True,
                on_click=use_example,
                args=(index,),
            )

    low_resource_section()

    st.markdown(
        """
        <div class="lb-section">
          <h2>Translation History</h2>
          <p class="lb-note">Recent translations stay in a local SQLite file on this computer.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    rows = recent_translations()
    if st.button("Clear history", disabled=not rows, use_container_width=False):
        clear_history()
        st.rerun()
    if rows:
        st.dataframe(
            pd.DataFrame(rows),
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.markdown(
            "<p class='lb-note'>No translations yet. New results will be saved on this computer.</p>",
            unsafe_allow_html=True,
        )


if __name__ == "__main__":
    main()
