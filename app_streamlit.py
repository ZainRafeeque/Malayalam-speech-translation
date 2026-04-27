"""
Streamlit web interface for Malayalam Speech-to-English Translation.

Run:
    pip install -r requirements-web.txt
    streamlit run app_streamlit.py

Then open the URL Streamlit prints (usually http://localhost:8501).

Deploy to Streamlit Cloud:
    Push this file to GitHub, connect at https://share.streamlit.io
"""

import io
import tempfile

import streamlit as st
import speech_recognition as sr
from deep_translator import GoogleTranslator


st.set_page_config(
    page_title="Eloquent Speaker - Malayalam Translator",
    page_icon="🎤",
    layout="centered",
)

# ---- styling ----
st.markdown(
    """
    <style>
    .main-header {
        text-align: center;
        background: linear-gradient(90deg, #FFD700, #FFA500);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.5em;
        font-weight: bold;
        margin-bottom: 0.2em;
    }
    .sub-header {
        text-align: center;
        color: #888;
        margin-bottom: 1.5em;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="main-header">Eloquent Speaker</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-header">Malayalam Speech-to-Text + English Translation</div>',
    unsafe_allow_html=True,
)


# ---- helpers ----

def transcribe(audio_bytes: bytes) -> str | None:
    recognizer = sr.Recognizer()
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        tmp.write(audio_bytes)
        tmp_path = tmp.name
    try:
        with sr.AudioFile(tmp_path) as source:
            audio = recognizer.record(source)
        return recognizer.recognize_google(audio, language="ml-IN")
    except sr.UnknownValueError:
        st.error("Could not understand the audio. Please speak clearly in Malayalam.")
    except sr.RequestError as exc:
        st.error(f"Speech recognition API error: {exc}")
    return None


def translate(ml_text: str) -> str | None:
    try:
        return GoogleTranslator(source="ml", target="en").translate(ml_text)
    except Exception as exc:
        st.error(f"Translation failed: {exc}")
        return None


# ---- tabs ----

tab_speak, tab_type, tab_upload = st.tabs(["🎤 Speak", "⌨️ Type", "📁 Upload"])

with tab_speak:
    st.write("Click the microphone, speak in Malayalam, then stop.")
    audio_value = st.audio_input("Record Malayalam audio")

    if audio_value is not None:
        with st.spinner("Transcribing..."):
            ml = transcribe(audio_value.getvalue())
        if ml:
            st.text_area("Malayalam Transcription", ml, height=120)
            with st.spinner("Translating..."):
                en = translate(ml)
            if en:
                st.text_area("English Translation", en, height=120)
                st.success("Done!")

with tab_type:
    ml_input = st.text_area(
        "Type Malayalam text",
        placeholder="നമസ്കാരം, എന്റെ പേര് സൈൻ ആണ്",
        height=140,
    )
    if st.button("Translate", type="primary", key="type_btn"):
        if ml_input.strip():
            with st.spinner("Translating..."):
                en = translate(ml_input)
            if en:
                st.text_area("English Translation", en, height=140)
        else:
            st.warning("Please enter some Malayalam text.")

with tab_upload:
    uploaded = st.file_uploader(
        "Upload an audio file (WAV recommended)",
        type=["wav", "aiff", "aif", "flac"],
    )
    if uploaded is not None:
        st.audio(uploaded)
        with st.spinner("Transcribing..."):
            ml = transcribe(uploaded.read())
        if ml:
            st.text_area("Malayalam Transcription", ml, height=120, key="upload_ml")
            with st.spinner("Translating..."):
                en = translate(ml)
            if en:
                st.text_area("English Translation", en, height=120, key="upload_en")

st.markdown("---")
st.caption(
    "Built with Streamlit, SpeechRecognition, and deep-translator. "
    "[GitHub](https://github.com/ZainRafeeque/Malayalam-speech-translation)"
)
