// Tab switching
document.querySelectorAll(".tab").forEach((btn) => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".tab").forEach((t) => t.classList.remove("active"));
    document.querySelectorAll(".tab-panel").forEach((p) => p.classList.remove("active"));
    btn.classList.add("active");
    document.getElementById("tab-" + btn.dataset.tab).classList.add("active");
  });
});

const recordBtn = document.getElementById("recordBtn");
const statusEl = document.getElementById("status");
const mlOut = document.getElementById("mlOutput");
const enOut = document.getElementById("enOutput");

let mediaRecorder = null;
let chunks = [];
let recording = false;

function setStatus(text, type = "success") {
  statusEl.textContent = text;
  statusEl.className = "status " + (type === "success" ? "" : type);
}

async function startRecording() {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorder = new MediaRecorder(stream);
    chunks = [];

    mediaRecorder.ondataavailable = (e) => {
      if (e.data.size > 0) chunks.push(e.data);
    };

    mediaRecorder.onstop = async () => {
      stream.getTracks().forEach((t) => t.stop());
      const blob = new Blob(chunks, { type: mediaRecorder.mimeType || "audio/webm" });
      await sendAudio(blob);
    };

    mediaRecorder.start();
    recording = true;
    recordBtn.classList.add("recording");
    recordBtn.querySelector(".label").textContent = "Stop Recording";
    setStatus("Listening... click again to stop.", "active");
  } catch (err) {
    setStatus("Microphone access denied or unavailable: " + err.message, "error");
  }
}

function stopRecording() {
  if (mediaRecorder && mediaRecorder.state !== "inactive") {
    mediaRecorder.stop();
  }
  recording = false;
  recordBtn.classList.remove("recording");
  recordBtn.querySelector(".label").textContent = "Start Recording";
  setStatus("Processing...", "active");
}

async function sendAudio(blob) {
  const fd = new FormData();
  fd.append("audio", blob, "recording.webm");

  try {
    const r = await fetch("/api/transcribe", { method: "POST", body: fd });
    const data = await r.json();
    if (data.error) {
      setStatus(data.error, "error");
      return;
    }
    mlOut.textContent = data.malayalam;
    setStatus("Translating...", "active");
    await translate(data.malayalam);
  } catch (err) {
    setStatus("Network error: " + err.message, "error");
  }
}

async function translate(text) {
  try {
    const r = await fetch("/api/translate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text }),
    });
    const data = await r.json();
    if (data.error) {
      setStatus(data.error, "error");
      return;
    }
    enOut.textContent = data.english;
    setStatus("Done.", "success");
  } catch (err) {
    setStatus("Translation request failed: " + err.message, "error");
  }
}

recordBtn.addEventListener("click", () => (recording ? stopRecording() : startRecording()));

document.getElementById("translateTypedBtn").addEventListener("click", async () => {
  const text = document.getElementById("typedInput").value.trim();
  if (!text) {
    setStatus("Please type some Malayalam text.", "error");
    return;
  }
  mlOut.textContent = text;
  enOut.textContent = "";
  setStatus("Translating...", "active");
  await translate(text);
});
