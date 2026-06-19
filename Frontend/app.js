let token = "";
let lastUploadedImage = null;

const sessionOutput = document.getElementById("session-output");
const protectedCards = document.querySelectorAll(".requires-auth");
const statusInline = document.getElementById("status-inline");
const authFeedback = document.getElementById("auth-feedback");
const logoutBtn = document.getElementById("logout-btn");
const chatImageMetadataInput = document.querySelector("#chat-form input[name='image_metadata']");

function setAuthFeedback(message, state = "") {
    authFeedback.textContent = message;
    authFeedback.classList.remove("ok", "error");
    if (state) {
        authFeedback.classList.add(state);
    }
}

function formatChatResponse(data) {
    return data.answer || "No answer returned.";
}

function formatStatusResponse(data) {
    return [
        "System Status",
        `- API Health: ${data.api_health}`,
        `- Database: ${data.database_connectivity}`,
        `- RAG Readiness: ${data.rag_readiness}`,
        `- App Version: ${data.app_version}`,
        `- Environment: ${data.environment}`,
    ].join("\n");
}

function formatUploadResponse(data) {
    return [
        "Upload Result",
        `- Message: ${data.message}`,
        `- Filename: ${data.filename}`,
        `- Content Type: ${data.content_type}`,
        `- Size: ${data.size} bytes`,
        "- Linked To Chat: Metadata auto-filled",
    ].join("\n");
}

function setChatImageMetadataFromUpload(uploadData) {
    if (!chatImageMetadataInput) {
        return;
    }
    chatImageMetadataInput.value = [
        `uploaded file: ${uploadData.filename}`,
        `type: ${uploadData.content_type}`,
        `size: ${uploadData.size} bytes`,
    ].join(" | ");
}

function clearChatImageMetadata() {
    if (chatImageMetadataInput) {
        chatImageMetadataInput.value = "";
    }
    lastUploadedImage = null;
}

function renderSession() {
    sessionOutput.textContent = token
        ? "Authenticated. Protected chat/upload routes are enabled."
        : "Not authenticated. Please login to access protected routes.";

    protectedCards.forEach((card) => {
        card.classList.toggle("locked", !token);
    });

    logoutBtn.style.display = token ? "block" : "none";
}

async function apiCall(path, options = {}) {
    const headers = options.headers || {};
    if (token) {
        headers.Authorization = `Bearer ${token}`;
    }
    const response = await fetch(path, { ...options, headers });
    const data = await response.json().catch(() => ({}));
    if (!response.ok) {
        if (response.status === 401 && token) {
            token = "";
            clearChatImageMetadata();
            renderSession();
            setAuthFeedback("Session expired or invalid token. Please login again.", "error");
        }
        throw new Error(data.detail || "Request failed");
    }
    return data;
}

document.getElementById("signup-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    const form = new FormData(event.target);
    try {
        await apiCall("/api/signup", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                full_name: form.get("full_name"),
                email: form.get("email"),
                password: form.get("password"),
            }),
        });
        setAuthFeedback("Signup successful. You can login now.", "ok");
        event.target.reset();
    } catch (error) {
        setAuthFeedback(`Signup failed: ${error.message}`, "error");
    }
});

document.getElementById("login-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    const form = new FormData(event.target);
    try {
        const data = await apiCall("/api/login", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                email: form.get("email"),
                password: form.get("password"),
            }),
        });
        token = data.access_token;
        renderSession();
        setAuthFeedback("Login successful. Protected routes are unlocked.", "ok");
    } catch (error) {
        setAuthFeedback(`Login failed: ${error.message}`, "error");
    }
});

document.getElementById("logout-btn").addEventListener("click", async () => {
    if (!token) {
        return;
    }
    try {
        await apiCall("/api/logout", { method: "POST" });
        setAuthFeedback("Logged out.");
    } finally {
        token = "";
        clearChatImageMetadata();
        renderSession();
    }
});

document.getElementById("chat-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    const output = document.getElementById("chat-output");
    const form = new FormData(event.target);
    output.textContent = "Loading chat response...";
    try {
        const data = await apiCall("/api/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                question: form.get("question"),
                image_metadata: form.get("image_metadata") || "",
            }),
        });
        output.textContent = formatChatResponse(data);
    } catch (error) {
        output.textContent = error.message;
    }
});

document.getElementById("upload-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    const output = document.getElementById("upload-output");
    const form = new FormData(event.target);
    output.textContent = "Uploading...";
    try {
        const data = await apiCall("/api/upload", {
            method: "POST",
            body: form,
        });
        lastUploadedImage = {
            filename: data.filename,
            content_type: data.content_type,
            size: data.size,
        };
        setChatImageMetadataFromUpload(lastUploadedImage);
        output.textContent = formatUploadResponse(data);
    } catch (error) {
        output.textContent = error.message;
    }
});

async function loadStatus() {
    const output = document.getElementById("status-output");
    statusInline.classList.remove("ok", "error");
    statusInline.textContent = "Checking live status...";
    output.textContent = "Loading status...";
    try {
        const data = await apiCall("/api/status");
        output.textContent = formatStatusResponse(data);
        statusInline.classList.add("ok");
        statusInline.textContent = `Status: ${data.api_health} | DB: ${data.database_connectivity}`;
    } catch (error) {
        output.textContent = error.message;
        statusInline.classList.add("error");
        statusInline.textContent = "Status check failed";
    }
}

document.getElementById("status-btn").addEventListener("click", loadStatus);

renderSession();
setAuthFeedback("Waiting for login...");
loadStatus();
