"""
Eloquent Speaker - Malayalam Speech to English Translation

A Tkinter GUI application that captures spoken Malayalam, transcribes it
using Google Speech Recognition, and translates the text to English using
the free Google Translate web endpoint (via deep-translator).

Requires an active internet connection.
"""

import threading
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox

import speech_recognition as sr
from deep_translator import GoogleTranslator


def translate_ml_to_en(text: str) -> str:
    """Translate a Malayalam string to English."""
    if not text or not text.strip():
        return ""
    return GoogleTranslator(source="ml", target="en").translate(text)


class EloquentSpeakerApp:
    def __init__(self, root: tk.Tk):
        self.root = root
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
            self.root,
            text="Original Malayalam:",
            font=("Arial", 12, "bold"),
            background="#1E2630",
            foreground="white",
        ).pack(anchor="w", padx=50)
        self.transcription_box = scrolledtext.ScrolledText(
            self.root, wrap=tk.WORD, width=80, height=8, font=("Arial", 14), bg="white"
        )
        self.transcription_box.pack(pady=5)

        ttk.Label(
            self.root,
            text="Translated English:",
            font=("Arial", 12, "bold"),
            background="#1E2630",
            foreground="white",
        ).pack(anchor="w", padx=50)
        self.translation_box = scrolledtext.ScrolledText(
            self.root, wrap=tk.WORD, width=80, height=8, font=("Arial", 14), bg="white"
        )
        self.translation_box.pack(pady=5)

        self.status_label = ttk.Label(
            self.root,
            text="Ready.",
            font=("Arial", 11, "italic"),
            background="#1E2630",
            foreground="#A0E0A0",
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
        self.root.after(0, self._set_status, "Translating...", "#FFD700")

        try:
            translated = translate_ml_to_en(transcription)
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


def main() -> None:
    root = tk.Tk()
    EloquentSpeakerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
