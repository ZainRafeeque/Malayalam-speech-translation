"""
Eloquent Speaker (Offline) - Malayalam Speech to English Translation

Uses IndicTrans2 (via ctranslate2) for fully offline neural machine translation
plus Indic NLP for normalization and transliteration. The original research
prototype.

Speech recognition still requires internet (uses Google Speech API by default)
unless replaced with an offline ASR (e.g., Vosk / Whisper).

Setup:
    pip install -r requirements-offline.txt

    Download an IndicTrans2 ml->en model converted to ctranslate2 format and
    place it under ./final_model/. The directory must contain:
        - model.bin
        - config.json
        - vocab/model.SRC   (SentencePiece source model)
        - vocab/model.TGT   (SentencePiece target model)

    Pass --model-dir to override the default location, or set the
    MALAYALAM_MODEL_DIR environment variable.

Run:
    python app_offline.py
    python app_offline.py --model-dir /path/to/final_model
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
SRC_LANG = "mal_Mlym"
TGT_LANG = "eng_Latn"


# --------- Translation pipeline (lifted from the research notebook) ---------

def add_token(sent: str) -> str:
    """Prefix a sentence with source/target language tags (IndicTrans2 format)."""
    return f"{SRC_LANG} {TGT_LANG} {sent}"


def preprocess_sentence(sentence: str, sp_src: spm.SentencePieceProcessor,
                        translator: ctranslate2.Translator) -> str:
    """Normalize, transliterate, tokenize, and translate a Malayalam sentence."""
    normalizer = IndicNormalizerFactory().get_normalizer("ml")
    xliterator = unicode_transliterate.UnicodeIndicTransliterator()

    processed = xliterator.transliterate(
        " ".join(indic_tokenize.trivial_tokenize(normalizer.normalize(sentence.strip()), "ml")),
        "ml",
        "hi",
    ).replace(" ् ", "्")

    encoded = " ".join(sp_src.encode(processed, out_type=str))
    tagged = add_token(encoded.strip())

    words = tagged.split()
    if len(words) > MAX_SEQ_LEN:
        preview = " ".join(words[:5]) + " ... " + " ".join(words[-5:])
        print(f"WARNING: '{preview}' truncated to {MAX_SEQ_LEN} tokens")
        tagged = " ".join(words[:MAX_SEQ_LEN])

    translations = translator.translate_batch(
        [tagged.split(" ")],
        max_batch_size=9216,
        batch_type="tokens",
        max_input_length=160,
        max_decoding_length=256,
        beam_size=5,
    )
    out = " ".join(translations[0].hypotheses[0])
    return out.replace(" ", "").replace("▁", " ").strip()


class TranslationEngine:
    """Lazy-loaded translation backend so model loading is one-shot."""

    def __init__(self, model_dir: str):
        self.model_dir = model_dir
        self._translator: ctranslate2.Translator | None = None
        self._sp_src: spm.SentencePieceProcessor | None = None

    def _load(self) -> None:
        if self._translator is None:
            self._translator = ctranslate2.Translator(self.model_dir, device="cpu")
        if self._sp_src is None:
            self._sp_src = spm.SentencePieceProcessor(
                model_file=os.path.join(self.model_dir, "vocab", "model.SRC")
            )

    def translate(self, text: str) -> str:
        if not text or not text.strip():
            return ""
        self._load()
        assert self._translator is not None and self._sp_src is not None
        return preprocess_sentence(text, self._sp_src, self._translator)


# --------- GUI ---------

class EloquentSpeakerApp:
    def __init__(self, root: tk.Tk, model_dir: str):
        self.root = root
        self.engine = TranslationEngine(model_dir)
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
        self.root.title("Eloquent Speaker (Offline) - Malayalam to English")
        self.root.geometry("1000x700")
        self.root.config(bg="#1E2630")

        ttk.Label(
            self.root,
            text="Eloquent Speaker (Offline NMT)",
            font=("Arial", 24, "bold"),
            background="#1E2630",
            foreground="#FFD700",
        ).pack(pady=20)

        ttk.Label(
            self.root,
            text="Click 'Start Recording' and speak in Malayalam. "
                 "Translation runs locally via IndicTrans2 + ctranslate2.",
            font=("Arial", 12),
            background="#1E2630",
            foreground="white",
        ).pack(pady=5)

        button_frame = tk.Frame(self.root, bg="#1E2630")
        button_frame.pack(pady=10)

        self.start_button = ttk.Button(
            button_frame, text="Start Recording", command=self.start_recording, width=20
        )
        self.start_button.grid(row=0, column=0, padx=5)

        self.clear_button = ttk.Button(
            button_frame, text="Clear", command=self.clear_text, width=20
        )
        self.clear_button.grid(row=0, column=1, padx=5)

        ttk.Label(
            self.root, text="Original Malayalam:",
            font=("Arial", 12, "bold"), background="#1E2630", foreground="white",
        ).pack(anchor="w", padx=50)
        self.transcription_box = scrolledtext.ScrolledText(
            self.root, wrap=tk.WORD, width=80, height=8, font=("Arial", 14), bg="white"
        )
        self.transcription_box.pack(pady=5)

        ttk.Label(
            self.root, text="Translated English:",
            font=("Arial", 12, "bold"), background="#1E2630", foreground="white",
        ).pack(anchor="w", padx=50)
        self.translation_box = scrolledtext.ScrolledText(
            self.root, wrap=tk.WORD, width=80, height=8, font=("Arial", 14), bg="white"
        )
        self.translation_box.pack(pady=5)

        self.status_label = ttk.Label(
            self.root, text="Ready.", font=("Arial", 11, "italic"),
            background="#1E2630", foreground="#A0E0A0",
        )
        self.status_label.pack(pady=5)

        ttk.Button(self.root, text="Exit", command=self.exit_application, width=20).pack(pady=15)

    # ---------- helpers ----------

    def _set_box(self, box: scrolledtext.ScrolledText, text: str) -> None:
        box.config(state=tk.NORMAL)
        box.delete(1.0, tk.END)
        box.insert(tk.END, text)
        box.config(state=tk.DISABLED)

    def _set_status(self, text: str, color: str = "#A0E0A0") -> None:
        self.status_label.config(text=text, foreground=color)

    # ---------- actions ----------

    def clear_text(self) -> None:
        self._set_box(self.transcription_box, "")
        self._set_box(self.translation_box, "")
        self._set_status("Ready.")

    def start_recording(self) -> None:
        self.start_button["state"] = "disabled"
        self.clear_button["state"] = "disabled"
        self._set_box(self.transcription_box, "")
        self._set_box(self.translation_box, "")
        self._set_status("Calibrating microphone...", "#FFD700")
        threading.Thread(target=self.recognize_speech, daemon=True).start()

    def recognize_speech(self) -> None:
        try:
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                self.root.after(0, self._set_status, "Listening... speak now", "#FFD700")
                audio = self.recognizer.listen(source, timeout=10, phrase_time_limit=15)
        except sr.WaitTimeoutError:
            self.root.after(0, self._on_error, "No speech detected (timed out).")
            return
        except Exception as exc:
            self.root.after(0, self._on_error, f"Microphone error: {exc}")
            return

        self.root.after(0, self._set_status, "Transcribing...", "#FFD700")
        try:
            transcription = self.recognizer.recognize_google(audio, language="ml-IN")
        except sr.UnknownValueError:
            self.root.after(0, self._on_error, "Could not understand audio.")
            return
        except sr.RequestError as exc:
            self.root.after(0, self._on_error, f"Speech API error: {exc}")
            return

        self.root.after(0, self._set_box, self.transcription_box, transcription)
        self.root.after(0, self._set_status, "Translating (offline NMT)...", "#FFD700")

        try:
            translated = self.engine.translate(transcription)
        except Exception as exc:
            self.root.after(0, self._on_error, f"Translation error: {exc}")
            return

        self.root.after(0, self._set_box, self.translation_box, translated)
        self.root.after(0, self._set_status, "Done.", "#A0E0A0")
        self.root.after(0, self._reenable_buttons)

    def _on_error(self, message: str) -> None:
        self._set_status(message, "#FF8080")
        self._reenable_buttons()

    def _reenable_buttons(self) -> None:
        self.start_button["state"] = "normal"
        self.clear_button["state"] = "normal"

    def exit_application(self) -> None:
        self.root.quit()


# --------- entry point ---------

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Malayalam->English speech translator (offline NMT)")
    p.add_argument(
        "--model-dir",
        default=os.environ.get("MALAYALAM_MODEL_DIR", "./final_model"),
        help="Path to IndicTrans2 ctranslate2 model directory (or set "
             "MALAYALAM_MODEL_DIR). Default: ./final_model",
    )
    return p.parse_args()


def main() -> None:
    args = parse_args()
    if not os.path.isdir(args.model_dir):
        raise SystemExit(
            f"Model directory not found: {args.model_dir}\n"
            "Download an IndicTrans2 ml->en ctranslate2 model and pass --model-dir "
            "or set MALAYALAM_MODEL_DIR. See README for setup instructions."
        )
    required = ["config.json", "model.bin", os.path.join("vocab", "model.SRC")]
    missing = [f for f in required if not os.path.exists(os.path.join(args.model_dir, f))]
    if missing:
        raise SystemExit(
            f"Model directory '{args.model_dir}' is missing required files: {missing}"
        )

    root = tk.Tk()
    EloquentSpeakerApp(root, model_dir=args.model_dir)
    root.mainloop()


if __name__ == "__main__":
    main()
