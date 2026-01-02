function addMessage(text, sender) {
    const chatBox = document.getElementById("chat-box");
    const msg = document.createElement("div");
    msg.className = `message ${sender}`;
    msg.innerText = text;
    chatBox.appendChild(msg);
    chatBox.scrollTop = chatBox.scrollHeight;
}

function sendMessage() {
    const input = document.getElementById("user-input");
    const text = input.value.trim();
    if (!text) return;

    addMessage(text, "user");
    input.value = "";

    fetch("/", {
        method: "POST",
        headers: {
            "Content-Type": "application/x-www-form-urlencoded",
            "X-CSRFToken": getCookie("csrftoken")
        },
        body: `message=${encodeURIComponent(text)}`
    })
    .then(res => {
        if (res.headers.get("Content-Type").includes("image")) {
            return res.blob();
        }
        return res.text();
    })
    .then(data => {
        if (data instanceof Blob) {
            const img = document.createElement("img");
            img.src = URL.createObjectURL(data);
            document.getElementById("chat-box").appendChild(img);
        } else {
            addMessage(data, "bot");
        }
    });
}

function sendSuggestion(text) {
    document.getElementById("user-input").value = text;
    sendMessage();
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");
        for (let cookie of cookies) {
            cookie = cookie.trim();
            if (cookie.startsWith(name + "=")) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
