"""
HuggingFace Space entry point for the Malayalam → English translator.
Mirrors app_gradio.py but renamed to app.py so HF auto-detects it.
"""

import gradio as gr
import speech_recognition as sr
from deep_translator import GoogleTranslator


def transcribe_and_translate(audio_path):
    if audio_path is None:
        return "", ""
    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(audio_path) as source:
            audio = recognizer.record(source)
    except Exception as exc:
        return f"Error reading audio: {exc}", ""
    try:
        ml_text = recognizer.recognize_google(audio, language="ml-IN")
    except sr.UnknownValueError:
        return "Could not understand audio. Speak clearly in Malayalam.", ""
    except sr.RequestError as exc:
        return f"Speech API error: {exc}", ""
    try:
        en_text = GoogleTranslator(source="ml", target="en").translate(ml_text)
    except Exception as exc:
        return ml_text, f"Translation error: {exc}"
    return ml_text, en_text


def translate_text_only(ml_text):
    if not ml_text or not ml_text.strip():
        return ""
    try:
        return GoogleTranslator(source="ml", target="en").translate(ml_text)
    except Exception as exc:
        return f"Translation error: {exc}"


with gr.Blocks(title="Eloquent Speaker - Malayalam Translator") as demo:
    gr.Markdown(
        """
        # Eloquent Speaker
        ### Malayalam Speech-to-Text + English Translation

        Speak (or type) in Malayalam, get the English translation instantly.
        """
    )

    with gr.Tab("Speak"):
        with gr.Row():
            with gr.Column():
                audio_input = gr.Audio(
                    sources=["microphone", "upload"],
                    type="filepath",
                    label="Record Malayalam (or upload audio file)",
                )
                speak_btn = gr.Button("Transcribe & Translate", variant="primary")
            with gr.Column():
                ml_out = gr.Textbox(label="Malayalam Transcription", lines=4, interactive=False)
                en_out = gr.Textbox(label="English Translation", lines=4, interactive=False)

        speak_btn.click(
            transcribe_and_translate, inputs=audio_input, outputs=[ml_out, en_out]
        )

    with gr.Tab("Type"):
        with gr.Row():
            with gr.Column():
                ml_in = gr.Textbox(
                    label="Type Malayalam text", placeholder="നമസ്കാരം", lines=4
                )
                type_btn = gr.Button("Translate", variant="primary")
            with gr.Column():
                en_typed = gr.Textbox(label="English Translation", lines=4, interactive=False)

        type_btn.click(translate_text_only, inputs=ml_in, outputs=en_typed)

    gr.Markdown(
        """
        ---
        Built with [Gradio](https://gradio.app), [SpeechRecognition](https://pypi.org/project/SpeechRecognition/),
        and [deep-translator](https://pypi.org/project/deep-translator/).
        Source: [GitHub @ZainRafeeque](https://github.com/ZainRafeeque/Malayalam-speech-translation)
        """
    )

if __name__ == "__main__":
    demo.launch(theme=gr.themes.Soft(primary_hue="amber", secondary_hue="slate"))
