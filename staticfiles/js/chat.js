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
function sendMessage() {
    const input = document.getElementById("user-input");
    const msg = input.value.trim();
    if (!msg) return;

    addMessage(msg, "user");
    input.value = "";

    fetch("/", {
        method: "POST",
        credentials: "same-origin", // 🔴 REQUIRED
        headers: {
            "Content-Type": "application/x-www-form-urlencoded",
            "X-CSRFToken": getCookie("csrftoken")
        },
        body: "message=" + encodeURIComponent(msg)
    })
    .then(res => res.text())
    .then(data => addMessage(data, "bot"))
    .catch(() =>
        addMessage("❌ Server Down: Could not reach the server.", "bot")
    );
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
        if (line.startsWith("👤") || line.startsWith("📊")) {
            html += `<h4 class="profile-title">${line}</h4>`;
        }
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
EXPOSE FUNCTIONS
=============================== */
window.sendQuick = sendQuick;
window.sendMessage = sendMessage;

