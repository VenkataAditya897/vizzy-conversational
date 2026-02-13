const API_BASE = "";

let token = localStorage.getItem("vizzy_token") || "";
let currentConversationId = null;
let lastPromptSent = "";

// UI elements
const authModal = document.getElementById("authModal");
const logoutBtn = document.getElementById("logoutBtn");

const convoList = document.getElementById("convoList");
const newChatBtn = document.getElementById("newChatBtn");

const chat = document.getElementById("chat");
const chatTitle = document.getElementById("chatTitle");
const chatMeta = document.getElementById("chatMeta");

const textInput = document.getElementById("textInput");
const sendBtn = document.getElementById("sendBtn");
const micBtn = document.getElementById("micBtn");
const prefsToggle = document.getElementById("prefsToggle");
const authPrimaryBtn = document.getElementById("authPrimaryBtn");
const authSecondaryBtn = document.getElementById("authSecondaryBtn");

const authTitle = document.getElementById("authTitle");
const authSub = document.getElementById("authSub");
const authHint = document.getElementById("authHint");

const authError = document.getElementById("authError");
const confirmPasswordInput = document.getElementById("confirmPassword");

const uploadBtn = document.getElementById("uploadBtn");
const imageFileInput = document.getElementById("imageFileInput");

const imagePreviewRow = document.getElementById("imagePreviewRow");
const imagePreview = document.getElementById("imagePreview");
const removeImageBtn = document.getElementById("removeImageBtn");
const resetPrefsBtn = document.getElementById("resetPrefsBtn");

let selectedImageUrl = "";
let authMode = "login";
// -----------------------------
// Helpers
// -----------------------------
function setStatus(msg) {
  chatMeta.textContent = msg;
}

function fmtTime(iso) {
  try {
    const d = new Date(iso);
    return d.toLocaleString();
  } catch {
    return "";
  }
}

function scrollToBottom() {
  chat.scrollTop = chat.scrollHeight;
}

function authHeaders() {
  return {
    "Content-Type": "application/json",
    "Authorization": `Bearer ${token}`
  };
}

function showAuth() {
  authModal.classList.add("show");
}

function hideAuth() {
  authModal.classList.remove("show");
}



function showAuthError(msg) {
  authError.textContent = msg;
  authError.style.display = "block";
}

function clearAuthError() {
  authError.textContent = "";
  authError.style.display = "none";
}

function setAuthMode(mode) {
  authMode = mode;
  clearAuthError();

  document.getElementById("email").value = "";
  document.getElementById("password").value = "";
  confirmPasswordInput.value = "";

  if (mode === "login") {
    authTitle.textContent = "Login";
    authSub.textContent = "Login to continue.";
    authPrimaryBtn.textContent = "Login";
    authSecondaryBtn.textContent = "Signup";
    authHint.textContent = "Use signup if you don’t have an account.";
    confirmPasswordInput.style.display = "none";
  } else {
    authTitle.textContent = "Signup";
    authSub.textContent = "Create your account.";
    authPrimaryBtn.textContent = "Create Account";
    authSecondaryBtn.textContent = "Back to Login";
    authHint.textContent = "Already have an account? Login instead.";
    confirmPasswordInput.style.display = "block";
  }
}
function setImageUrl(url) {
  selectedImageUrl = url || "";

  if (selectedImageUrl) {
    imagePreview.src = selectedImageUrl;
    imagePreviewRow.style.display = "flex";
  } else {
    imagePreview.src = "";
    imagePreviewRow.style.display = "none";
  }
}


// -----------------------------
// API calls
// -----------------------------
async function apiLogin(email, password) {
  const res = await fetch(`${API_BASE}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password })
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Login failed");
  }

  return await res.json();
}
async function apiSignup(email, password) {
  const res = await fetch(`${API_BASE}/auth/signup`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password })
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Signup failed");
  }

  return await res.json();
}

async function apiListConversations() {
  const res = await fetch(`${API_BASE}/conversations`, {
    headers: authHeaders()
  });

  if (!res.ok) throw new Error("Failed to load conversations");
  return await res.json();
}
async function apiResetMemory() {
  const res = await fetch(`${API_BASE}/memory/reset`, {
    method: "POST",
    headers: authHeaders()
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Reset failed");
  }

  return await res.json();
}

async function apiGetConversation(conversationId) {
  const res = await fetch(`${API_BASE}/conversations/${conversationId}`, {
    headers: authHeaders()
  });

  if (!res.ok) throw new Error("Failed to load conversation");
  return await res.json();
}

async function apiSendChat(payload) {
  const res = await fetch(`${API_BASE}/chat/send`, {
    method: "POST",
    headers: authHeaders(),
    body: JSON.stringify(payload)
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Send failed");
  }

  return await res.json();
}
async function apiUploadImage(file) {
  const form = new FormData();
  form.append("file", file);

  const res = await fetch(`${API_BASE}/upload/image`, {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${token}`
    },
    body: form
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Upload failed");
  }

  return await res.json();
}

// -----------------------------
// Render UI
// -----------------------------
function renderConversations(convos) {
  convoList.innerHTML = "";

  if (!convos.length) {
    convoList.innerHTML = `<div class="muted small">No conversations yet.</div>`;
    return;
  }

  for (const c of convos) {
    const div = document.createElement("div");
    div.className =
      "convo-item" + (c.id === currentConversationId ? " active" : "");

    div.innerHTML = `
      <div class="convo-row">
        <div class="convo-main">
          <div class="convo-title">${escapeHtml(c.title)}</div>
          <div class="convo-time">${fmtTime(c.created_at)}</div>
        </div>

        <button class="convo-delete" title="Delete chat">
  <span class="trash-icon">✕</span>
</button>

      </div>
    `;

    // click on conversation = open
    div.querySelector(".convo-main").onclick = async () => {
      await openConversation(c.id);
    };

    // delete button
    div.querySelector(".convo-delete").onclick = async (e) => {
      e.stopPropagation();

      const ok = confirm(`Delete "${c.title}"?`);
      if (!ok) return;

      try {
        setStatus("Deleting...");
        await apiDeleteConversation(c.id);

        // if user deleted the currently open conversation
        if (currentConversationId === c.id) {
          await createNewChatUI();
        } else {
          await refreshSidebar();
        }

        setStatus("Deleted");
      } catch (err) {
        console.error(err);
        alert(err.message || "Delete failed");
        setStatus("Error");
      }
    };

    convoList.appendChild(div);
  }
}


function renderMessage(msg) {
  const row = document.createElement("div");
  row.className = `msg-row ${msg.role}`;

  const bubble = document.createElement("div");
  bubble.className = `bubble ${msg.role}`;

  bubble.innerHTML = escapeHtml(msg.text || "");

  // Assets
  if (msg.assets && msg.assets.length) {
    const grid = document.createElement("div");
    grid.className = "asset-grid";

    for (const a of msg.assets) {
      const card = document.createElement("div");
      card.className = "asset-card";

      if (a.type === "image") {
        const img = document.createElement("img");
        img.src = a.url;
        img.alt = "Generated image";

        img.style.cursor = "pointer";
        img.title = "Click to edit this image";

        img.onclick = () => {
          setImageUrl(a.url);
          setStatus("Selected image for editing ✅");
        };

        card.appendChild(img);
      }


      grid.appendChild(card);
    }


    bubble.appendChild(grid);
  }

  const time = document.createElement("div");
  time.className = "time";
  time.textContent = fmtTime(msg.created_at);

  bubble.appendChild(time);
  row.appendChild(bubble);
  chat.appendChild(row);
}

function renderConversation(convo) {
  chat.innerHTML = "";
  chatTitle.textContent = convo.title || "Chat";

  for (const m of convo.messages) {
    renderMessage(m);
  }

  scrollToBottom();
}

// -----------------------------
// Main actions
// -----------------------------
async function refreshSidebar() {
  const convos = await apiListConversations();
  renderConversations(convos);
}

async function openConversation(conversationId) {
  currentConversationId = conversationId;
  setStatus("Loading chat...");
  await refreshSidebar();

  const convo = await apiGetConversation(conversationId);
  renderConversation(convo);

  setStatus("Ready");
}

async function createNewChatUI() {
  currentConversationId = null;
  chat.innerHTML = "";
  chatTitle.textContent = "New Chat";
  setStatus("Ready");
  await refreshSidebar();
}

async function sendMessage() {
  const text = (textInput.value || "").trim();
  const imageUrl = selectedImageUrl || "";

  const usePrefs = prefsToggle.checked;

  if (!text && !imageUrl) {
  alert("Please type something or upload an image.");
  return;
}


  // optimistic UI: show user message immediately
  

  scrollToBottom();

  setStatus("Generating...");
  sendBtn.disabled = true;

  lastPromptSent = text;

  try {
    const payload = {
      conversation_id: currentConversationId,
      text: text || null,
      image_url: imageUrl || null,
      use_preferences: usePrefs
    };

    const resp = await apiSendChat(payload);
    renderMessage(resp.user_message);
    renderMessage(resp.assistant_message);


    // if new conversation created
    currentConversationId = resp.conversation_id;

    // show assistant

    await refreshSidebar();
    setStatus("Done");


    textInput.value = "";
    // keep image url so user can reuse it if needed
  } catch (err) {
    console.error(err);
    setStatus("Error");
    alert(err.message || "Failed");
  } finally {
    sendBtn.disabled = false;
    scrollToBottom();
  }
}

// -----------------------------
// Voice Input (Speech-to-text)
// -----------------------------
let recognition = null;
let isListening = false;

function setupVoice() {
  const SpeechRecognition =
    window.SpeechRecognition || window.webkitSpeechRecognition;

  if (!SpeechRecognition) {
    micBtn.disabled = true;
    micBtn.title = "Speech Recognition not supported in this browser";
    return;
  }

  recognition = new SpeechRecognition();
  recognition.lang = "en-IN";
  recognition.interimResults = false;
  recognition.maxAlternatives = 1;

  recognition.onstart = () => {
    isListening = true;
    micBtn.textContent = "🛑";
    setStatus("Listening...");
  };

  recognition.onend = () => {
    isListening = false;
    micBtn.textContent = "🎙️";
    setStatus("Ready");
  };

  recognition.onerror = (e) => {
    console.log("voice error", e);
    alert("Mic error: " + (e.error || "unknown"));
  };

  recognition.onresult = async (event) => {
    const transcript = event.results[0][0].transcript;
    textInput.value = transcript;
    await sendMessage();
  };
}

micBtn.onclick = () => {
  if (!recognition) return;

  if (!isListening) recognition.start();
  else recognition.stop();
};

// -----------------------------
// Small utilities
// -----------------------------
function escapeHtml(str) {
  return (str || "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

// -----------------------------
// Init
// -----------------------------


logoutBtn.onclick = () => {
  localStorage.removeItem("vizzy_token");
  token = "";
  currentConversationId = null;

  // clear UI completely
  convoList.innerHTML = "";
  chat.innerHTML = "";
  chatTitle.textContent = "New Chat";
  setStatus("Logged out");

  textInput.value = "";
  setImageUrl("");

  showAuth();
  setAuthMode("login");
};


newChatBtn.onclick = async () => {
  await createNewChatUI();
};

sendBtn.onclick = async () => {
  await sendMessage();
};

// Send on Enter (Shift+Enter = new line)
textInput.addEventListener("keydown", async (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    await sendMessage();
  }
});

window.onload = async () => {
  setupVoice();

  if (!token) {
  showAuth();
  setAuthMode("login");
  return;
}


  try {
    await refreshSidebar();
    await createNewChatUI();
  } catch (e) {
    console.log(e);
    showAuth();
    setAuthMode("login");
  }
};
authPrimaryBtn.onclick = async () => {
  clearAuthError();

  const email = document.getElementById("email").value.trim();
  const password = document.getElementById("password").value.trim();
  const confirmPassword = confirmPasswordInput.value.trim();

  if (!email || !password) {
    showAuthError("Please enter email and password.");
    return;
  }

  try {
    if (authMode === "login") {
      setStatus("Logging in...");
      const data = await apiLogin(email, password);

      token = data.access_token;
      localStorage.setItem("vizzy_token", token);

      hideAuth();
      await refreshSidebar();
      await createNewChatUI();
      setStatus("Ready");
    } else {
      // SIGNUP MODE
      if (!confirmPassword) {
        showAuthError("Please confirm your password.");
        return;
      }

      if (password !== confirmPassword) {
        showAuthError("Passwords do not match.");
        return;
      }

      setStatus("Signing up...");
      await apiSignup(email, password);

      // IMPORTANT: after signup -> go back to login
      setStatus("Signup successful. Please login.");
      setAuthMode("login");
      showAuthError("Account created successfully. Now login.");
    }
  } catch (e) {
    showAuthError(e.message || "Something went wrong.");
    setStatus("Auth failed");
  }
};

authSecondaryBtn.onclick = () => {
  if (authMode === "login") setAuthMode("signup");
  else setAuthMode("login");
};

uploadBtn.onclick = () => {
  imageFileInput.click();
};

imageFileInput.onchange = async () => {
  const file = imageFileInput.files?.[0];
  if (!file) return;

  try {
    setStatus("Uploading image...");
    uploadBtn.disabled = true;

    const resp = await apiUploadImage(file);

    // store backend URL (hidden)
    setImageUrl(resp.image_url);

    setStatus("Ready");
  } catch (e) {
    console.error(e);
    setStatus("Upload failed");
    alert(e.message || "Upload failed");
  } finally {
    uploadBtn.disabled = false;
  }
};


removeImageBtn.onclick = () => {
  setImageUrl("");
  imageFileInput.value = "";
};

resetPrefsBtn.onclick = async () => {
  if (!confirm("Reset preferences? This will clear your last 25 memory prompts.")) return;

  try {
    setStatus("Resetting preferences...");
    await apiResetMemory();
    setStatus("Preferences reset");
    alert("Preferences reset successfully!");
  } catch (e) {
    console.error(e);
    setStatus("Reset failed");
    alert(e.message || "Reset failed");
  }
};

async function apiDeleteConversation(conversationId) {
  const res = await fetch(`${API_BASE}/conversations/${conversationId}`, {
    method: "DELETE",
    headers: authHeaders()
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Delete failed");
  }

  return await res.json();
}
