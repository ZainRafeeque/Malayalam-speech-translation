"""
Eloquent Speaker - Malayalam Speech to English Translation
A Tkinter GUI application that captures spoken Malayalam, transcribes it,
and translates the text to English using IndicTrans (ctranslate2).
"""

import argparse
import os
import threading
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox

import speech_recognition as sr
import ctranslate2
import sentencepiece as spm
from indicnlp.tokenize import indic_tokenize
from indicnlp.normalize.indic_normalize import IndicNormalizerFactory
from indicnlp.transliterate import unicode_transliterate

MAX_SEQ_LEN = 256


def add_token(sent: str) -> str:
    """Prefix the sentence with source/target language tags."""
    return "mal_Mlym" + " " + "eng_Latn" + " " + sent


def preprocess_sentence(sentence: str, sp_src, model_dir: str) -> str:
    """Normalize, transliterate, tokenize and translate a Malayalam sentence."""
    normfactory = IndicNormalizerFactory()
    normalizer = normfactory.get_normalizer("ml")
    xliterator = unicode_transliterate.UnicodeIndicTransliterator()

    processed_sent = xliterator.transliterate(
        " ".join(indic_tokenize.trivial_tokenize(normalizer.normalize(sentence.strip()), "ml")),
        "ml",
        "hi",
    ).replace(" ् ", "्")

    sents = [" ".join(sp_src.encode(sent, out_type=str)) for sent in [processed_sent]]
    tagged_sents = [add_token(s.strip()) for s in sents]

    new_sents = []
    for sent in tagged_sents:
        words = sent.split()
        if len(words) > MAX_SEQ_LEN:
            preview = " ".join(words[:5]) + " .... " + " ".join(words[-5:])
            print(f"WARNING: Sentence '{preview}' truncated to {MAX_SEQ_LEN} tokens")
            sent = " ".join(words[:MAX_SEQ_LEN])
        new_sents.append(sent)

    translator = ctranslate2.Translator(model_dir, device="cpu")
    tokenized_sents = [x.strip().split(" ") for x in new_sents]
    translations = translator.translate_batch(
        tokenized_sents,
        max_batch_size=9216,
        batch_type="tokens",
        max_input_length=160,
        max_decoding_length=256,
        beam_size=5,
    )
    translations = [" ".join(x.hypotheses[0]) for x in translations]
    translations = [t.replace(" ", "").replace("▁", " ").strip() for t in translations]
    return translations[0]


def translate_sentence(sentence: str, model_dir: str) -> str:
    """Load the SentencePiece model and translate a single sentence."""
    sp_src = spm.SentencePieceProcessor(
        model_file=os.path.join(model_dir, "vocab", "model.SRC")
    )
    return preprocess_sentence(sentence, sp_src, model_dir)


class EloquentSpeakerApp:
    def __init__(self, root: tk.Tk, model_dir: str):
        self.root = root
        self.model_dir = model_dir
        self.recognizer = sr.Recognizer()
        try:
            self.microphone = sr.Microphone()
        except OSError as exc:
            messagebox.showerror(
                "Microphone Error",
                f"No microphone available. Install PyAudio and connect a mic.\n\n{exc}",
            )
            raise
        self.setup_ui()

    def setup_ui(self) -> None:
        self.root.title("Eloquent Speaker - Malayalam to English Translator")
        self.root.geometry("1000x700")
        self.root.config(bg="#1E2630")

        ttk.Label(
            self.root,
            text="Eloquent Speaker",
            font=("Arial", 28, "bold"),
            background="#1E2630",
            foreground="#FFD700",
        ).pack(pady=20)

        ttk.Label(
            self.root,
            text="Click 'Start Recording' and speak in Malayalam.",
            font=("Arial", 14),
            background="#1E2630",
            foreground="white",
        ).pack(pady=10)

        self.start_button = ttk.Button(
            self.root, text="Start Recording", command=self.start_recording, width=20
        )
        self.start_button.pack(pady=10)

        self.transcription_box = scrolledtext.ScrolledText(
            self.root, wrap=tk.WORD, width=80, height=8, font=("Arial", 14), bg="white"
        )
        self.transcription_box.pack(pady=10)
        self.transcription_box.insert(tk.END, "Original Malayalam Text:\n")
        self.transcription_box.config(state=tk.DISABLED)

        self.translation_box = scrolledtext.ScrolledText(
            self.root, wrap=tk.WORD, width=80, height=8, font=("Arial", 14), bg="white"
        )
        self.translation_box.pack(pady=10)
        self.translation_box.insert(tk.END, "Translated English Text:\n")
        self.translation_box.config(state=tk.DISABLED)

        ttk.Button(self.root, text="Exit", command=self.exit_application, width=20).pack(pady=20)

    def _set_box(self, box: scrolledtext.ScrolledText, text: str) -> None:
        box.config(state=tk.NORMAL)
        box.delete(1.0, tk.END)
        box.insert(tk.END, text)
        box.config(state=tk.DISABLED)

    def start_recording(self) -> None:
        self.start_button["state"] = "disabled"
        self._set_box(self.transcription_box, "Please wait...\n")
        threading.Thread(target=self.recognize_speech, daemon=True).start()

    def update_transcription(self, text: str) -> None:
        self._set_box(self.transcription_box, f"Transcribed Text:\n{text}")
        try:
            translated_text = translate_sentence(text, self.model_dir)
            self._set_box(self.translation_box, f"Translated Text:\n{translated_text}")
        except Exception as exc:
            self._set_box(self.translation_box, f"Translation error: {exc}")
        self.start_button["state"] = "normal"

    def recognize_speech(self) -> None:
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=5)
            self._set_box(self.transcription_box, "Listening...\n")
            audio = self.recognizer.listen(source)
        try:
            transcription = self.recognizer.recognize_google(audio, language="ml-IN")
            self.update_transcription(transcription)
        except sr.UnknownValueError:
            self._set_box(self.transcription_box, "Could not understand audio.")
            self.start_button["state"] = "normal"
        except sr.RequestError as exc:
            self._set_box(self.transcription_box, f"Speech API error: {exc}")
            self.start_button["state"] = "normal"

    def exit_application(self) -> None:
        self.root.quit()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Malayalam to English speech translator")
    parser.add_argument(
        "--model-dir",
        default=os.environ.get("MALAYALAM_MODEL_DIR", "./final_model"),
        help="Path to the IndicTrans ctranslate2 model directory "
             "(or set MALAYALAM_MODEL_DIR env variable). Default: ./final_model",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not os.path.isdir(args.model_dir):
        raise SystemExit(
            f"Model directory not found: {args.model_dir}\n"
            "Download IndicTrans2 ml->en ctranslate2 model and pass --model-dir "
            "or set the MALAYALAM_MODEL_DIR environment variable. See README."
        )
    root = tk.Tk()
    EloquentSpeakerApp(root, model_dir=args.model_dir)
    root.mainloop()


if __name__ == "__main__":
    main()
