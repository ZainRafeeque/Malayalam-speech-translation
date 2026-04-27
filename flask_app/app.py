"""
Flask backend for Malayalam Speech-to-English Translation.

Run:
    pip install -r ../requirements-web.txt
    python app.py

Open http://127.0.0.1:5000 in a modern browser (Chrome / Edge / Firefox).
The browser uses MediaRecorder to capture mic audio and POSTs it to /api/transcribe.
"""

import io
import os
import tempfile

from flask import Flask, jsonify, render_template, request
import speech_recognition as sr
from deep_translator import GoogleTranslator


app = Flask(__name__, static_folder="static", template_folder="templates")
recognizer = sr.Recognizer()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/transcribe", methods=["POST"])
def api_transcribe():
    if "audio" not in request.files:
        return jsonify({"error": "No audio file provided"}), 400

    audio_file = request.files["audio"]
    suffix = os.path.splitext(audio_file.filename or "")[1] or ".webm"

    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        audio_file.save(tmp.name)
        tmp_path = tmp.name

    # Convert to WAV if browser sent webm/ogg/mp3 (SpeechRecognition needs WAV/AIFF/FLAC)
    wav_path = tmp_path
    if suffix.lower() not in (".wav", ".aif", ".aiff", ".flac"):
        try:
            from pydub import AudioSegment
            audio = AudioSegment.from_file(tmp_path)
            wav_path = tmp_path + ".wav"
            audio.export(wav_path, format="wav")
        except Exception as exc:
            return jsonify({"error": f"Audio conversion failed: {exc}. Install ffmpeg."}), 500

    try:
        with sr.AudioFile(wav_path) as source:
            audio = recognizer.record(source)
        ml_text = recognizer.recognize_google(audio, language="ml-IN")
    except sr.UnknownValueError:
        return jsonify({"error": "Could not understand audio."}), 200
    except sr.RequestError as exc:
        return jsonify({"error": f"Speech API error: {exc}"}), 502
    finally:
        for p in (tmp_path, wav_path):
            if p != tmp_path or wav_path == tmp_path:
                try:
                    os.unlink(p)
                except OSError:
                    pass

    return jsonify({"malayalam": ml_text})


@app.route("/api/translate", methods=["POST"])
def api_translate():
    data = request.get_json(silent=True) or {}
    text = (data.get("text") or "").strip()
    if not text:
        return jsonify({"error": "Empty text"}), 400
    try:
        en = GoogleTranslator(source="ml", target="en").translate(text)
    except Exception as exc:
        return jsonify({"error": f"Translation failed: {exc}"}), 502
    return jsonify({"english": en})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
