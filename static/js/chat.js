/* ===============================
ADD MESSAGE (TABLE + PROFILE SUPPORT)
=============================== */
function addMessage(text, sender) {
    const box = document.getElementById("chat-box");
    const div = document.createElement("div");
    div.className = "message " + sender;

    // Student Profile Card
    if (text.includes("👤 Student Profile")) {
        div.innerHTML = convertProfileToCard(text);
    }
    // ASCII Table
    else if (text.includes("|") && text.includes("+")) {
        div.innerHTML = convertAsciiTableToHTML(text);
    }
    // Normal text
    else {
        div.innerText = text;
    }

    box.appendChild(div);
    box.scrollTop = box.scrollHeight;
}

/* ===============================
SEND MESSAGE
=============================== */
function setStatus(message) {
    const status = document.getElementById("status-text");
    if (status) status.innerText = message;
}

function sendMessage() {
    const input = document.getElementById("user-input");
    const msg = input.value.trim();
    if (!msg) return;

    addMessage(msg, "user");
    input.value = "";
    setStatus("Thinking...");

    fetch("/", {
        method: "POST",
        headers: {
            "Content-Type": "application/x-www-form-urlencoded",
            "X-CSRFToken": getCookie("csrftoken")
        },
        body: "message=" + encodeURIComponent(msg)
    })
    .then(res => res.text())
    .then(data => {
        addMessage(data, "bot");
        speakText(data);
    })
    .catch(() => addMessage("❌ Server Down: Could not reach the server.", "bot"))
    .finally(() => setStatus("Ready"));
}

function startSpeechRecognition() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
        addMessage("❌ Speech recognition is not supported in this browser. Try Chrome, Edge, or Safari.", "bot");
        setStatus("Ready");
        return;
    }

    try {
        const recognition = new SpeechRecognition();
        recognition.lang = "en-US";
        recognition.interimResults = false;
        recognition.maxAlternatives = 1;
        recognition.continuous = false;

        recognition.onstart = () => {
            document.getElementById("voice-button").innerText = "🎙 Listening...";
            setStatus("Listening... (speak now)");
            console.log("Speech recognition started");
        };

        recognition.onresult = event => {
            const transcript = event.results[0][0].transcript;
            console.log("Recognized text:", transcript);
            document.getElementById("user-input").value = transcript;
            sendMessage();
        };

        recognition.onend = () => {
            document.getElementById("voice-button").innerText = "🎤 Speak";
            console.log("Speech recognition ended");
        };

        recognition.onerror = event => {
            console.error("Speech recognition error:", event.error);
            document.getElementById("voice-button").innerText = "🎤 Speak";
            
            let errorMsg = "❌ Speech recognition error: ";
            switch (event.error) {
                case "no-speech":
                    errorMsg += "No speech detected. Please try again.";
                    break;
                case "network":
                    errorMsg += "Network error. Check your connection.";
                    break;
                case "not-allowed":
                    errorMsg += "Microphone access denied. Check browser permissions.";
                    break;
                case "service-not-allowed":
                    errorMsg += "Speech recognition service not allowed in this context.";
                    break;
                case "bad-grammar":
                    errorMsg += "Grammar error. Please try again.";
                    break;
                default:
                    errorMsg += event.error || "Unknown error.";
            }
            addMessage(errorMsg, "bot");
            setStatus("Ready");
        };

        recognition.start();
    } catch (error) {
        console.error("Error initializing speech recognition:", error);
        addMessage("❌ Error initializing speech recognition: " + error.message, "bot");
        setStatus("Ready");
    }
}

function speakText(text) {
    fetch("/speak/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken")
        },
        body: JSON.stringify({ message: text })
    })
    .then(res => {
        if (!res.ok) throw new Error("TTS request failed");
        return res.blob();
    })
    .then(blob => {
        const url = URL.createObjectURL(blob);
        const audio = new Audio(url);
        setStatus("Speaking...");
        audio.play();
        audio.onended = () => {
            URL.revokeObjectURL(url);
            setStatus("Ready");
        };
    })
    .catch(err => {
        console.warn("TTS not available or failed", err);
        setStatus("Ready");
    });
}

/* ===============================
ENTER KEY SUPPORT
=============================== */
document.addEventListener("DOMContentLoaded", () => {
    const input = document.getElementById("user-input");
    input.addEventListener("keydown", e => {
        if (e.key === "Enter") {
            e.preventDefault();
            sendMessage();
        }
    });
});

/* ===============================
CSRF TOKEN
=============================== */
function getCookie(name) {
    return document.cookie
        .split("; ")
        .find(row => row.startsWith(name + "="))
        ?.split("=")[1];
}

/* ===============================
ASCII → HTML TABLE
=============================== */
function convertAsciiTableToHTML(ascii) {
    const rows = ascii.split("\n").filter(
        line => line.trim().startsWith("|") && line.trim().endsWith("|")
    );

    if (rows.length < 2) return `<pre>${ascii}</pre>`;

    const headers = rows[0].split("|").slice(1, -1).map(h => h.trim());

    let html = `<table class="data-table"><thead><tr>`;
    headers.forEach(h => html += `<th>${h}</th>`);
    html += `</tr></thead><tbody>`;

    for (let i = 1; i < rows.length; i++) {
        const cols = rows[i].split("|").slice(1, -1).map(c => c.trim());
        html += `<tr>`;
        cols.forEach(c => html += `<td>${c === "None" ? "N/A" : c}</td>`);
        html += `</tr>`;
    }

    html += `</tbody></table>`;
    return html;
}

/* ===============================
STUDENT PROFILE CARD
=============================== */
function convertProfileToCard(text) {
    const lines = text.split("\n").map(l => l.trim()).filter(Boolean);

    let html = `<div class="profile-card">`;

    lines.forEach(line => {
        // Section headers
        if (line.startsWith("👤") || line.startsWith("📊")) {
            html += `<h4 class="profile-title">${line}</h4>`;
        }
        // Key-value rows
        else if (line.includes(":")) {
            const idx = line.indexOf(":");
            const key = line.slice(0, idx);
            const value = line.slice(idx + 1);

            html += `
                <div class="profile-row">
                    <span class="label">${key}</span>
                    <span class="value">${value.trim()}</span>
                </div>
            `;
        }
    });

    html += `</div>`;
    return html;
}

/* ===============================
QUICK BUTTON SUPPORT
=============================== */
function sendQuick(text) {
    document.getElementById("user-input").value = text;
    sendMessage();
}

/* ===============================
EXPOSE FUNCTIONS (IMPORTANT)
=============================== */
window.sendQuick = sendQuick;
window.sendMessage = sendMessage;

