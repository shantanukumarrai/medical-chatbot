/**
 * MediBot — Frontend JavaScript
 * =================================
 * Handles:
 *  - Sending messages to the Flask API
 *  - Rendering user and bot messages
 *  - Managing session ID
 *  - Typing indicator, auto-scroll, textarea auto-resize
 *  - Markdown-lite formatting of responses
 */

// ── Configuration ──────────────────────────────────────
// Change this to your deployed backend URL on Render
// In development: http://localhost:5000
const API_BASE_URL = window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1"
 ? "http://127.0.0.1:5000"
  : "https://your-app-name.onrender.com";  // ← Update with your Render URL

// ── State ──────────────────────────────────────────────
let sessionId = generateSessionId();
let isLoading = false;

// ── DOM References ──────────────────────────────────────
const messageInput    = document.getElementById("messageInput");
const sendBtn         = document.getElementById("sendBtn");
const messagesList    = document.getElementById("messagesList");
const messagesContainer = document.getElementById("messagesContainer");
const welcomeScreen   = document.getElementById("welcomeScreen");
const sessionDisplay  = document.getElementById("sessionDisplay");
const charCount       = document.getElementById("charCount");

// ── Init ───────────────────────────────────────────────
function init() {
  updateSessionDisplay();

  // Send on Enter (not Shift+Enter)
  messageInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  });

  // Auto-resize textarea
  messageInput.addEventListener("input", () => {
    autoResizeTextarea();
    charCount.textContent = `${messageInput.value.length}/1000`;
  });
}

// ── Utility: Generate Session ID ──────────────────────
function generateSessionId() {
  return "sess_" + Math.random().toString(36).substring(2, 11);
}

function updateSessionDisplay() {
  sessionDisplay.textContent = `Session: ${sessionId.substring(0, 12)}…`;
}

// ── Auto-resize Textarea ──────────────────────────────
function autoResizeTextarea() {
  messageInput.style.height = "auto";
  messageInput.style.height = Math.min(messageInput.scrollHeight, 160) + "px";
}

// ── Send Message ──────────────────────────────────────
async function sendMessage() {
  const message = messageInput.value.trim();
  if (!message || isLoading) return;

  // Hide welcome screen on first message
  if (welcomeScreen.style.display !== "none") {
    welcomeScreen.style.display = "none";
  }

  // Render user message
  appendMessage("user", message);

  // Clear input
  messageInput.value = "";
  messageInput.style.height = "auto";
  charCount.textContent = "0/1000";

  // Show loading state
  setLoading(true);
  const typingEl = showTypingIndicator();

  try {
    // ── API Call ──
    const response = await fetch(`${API_BASE_URL}/api/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message: message,
        session_id: sessionId
      })
    });

    if (!response.ok) {
      const err = await response.json().catch(() => ({}));
      throw new Error(err.error || `HTTP error ${response.status}`);
    }

    const data = await response.json();

    // Remove typing indicator
    removeTypingIndicator(typingEl);

    // Render bot response
    const isEmergency = data.safety_triggered && data.answer.includes("emergency");
    appendMessage("bot", data.answer, data.sources || [], isEmergency);

  } catch (error) {
    removeTypingIndicator(typingEl);
    showErrorToast(`Connection error: ${error.message}`);
    appendMessage("bot",
      "⚠️ I'm having trouble connecting right now. Please check your connection and try again.",
      [], false
    );
    console.error("API error:", error);
  } finally {
    setLoading(false);
  }
}

// ── Use Suggestion Chip ───────────────────────────────
function useSuggestion(el) {
  messageInput.value = el.textContent.trim();
  messageInput.focus();
  autoResizeTextarea();
  charCount.textContent = `${messageInput.value.length}/1000`;
}

// ── Start New Chat ────────────────────────────────────
async function startNewChat() {
  try {
    // Tell backend to clear memory
    await fetch(`${API_BASE_URL}/api/chat`, {
      method: "DELETE",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ session_id: sessionId })
    });
  } catch (e) {
    // Silently fail — new session is fine
  }

  // Generate new session
  sessionId = generateSessionId();
  updateSessionDisplay();

  // Clear messages
  messagesList.innerHTML = "";
  welcomeScreen.style.display = "flex";
  welcomeScreen.style.flexDirection = "column";
  welcomeScreen.style.alignItems = "center";
}

// ── Append Message to DOM ─────────────────────────────
function appendMessage(role, content, sources = [], isEmergency = false) {
  const msgEl = document.createElement("div");
  msgEl.className = `message message-${role}${isEmergency ? " message-emergency" : ""}`;

  const avatar = document.createElement("div");
  avatar.className = "message-avatar";
  avatar.textContent = role === "user" ? "👤" : "⚕";

  const bubble = document.createElement("div");
  bubble.className = "message-bubble";

  // Format the content (simple markdown-like rendering)
  bubble.innerHTML = formatMessage(content);

  // Append sources if any
  if (sources && sources.length > 0) {
    const sourcesBlock = document.createElement("div");
    sourcesBlock.className = "sources-block";
    sourcesBlock.innerHTML = `
      <div class="sources-title">Sources</div>
      ${sources.map(s => `<div class="source-item">${escapeHtml(s)}</div>`).join("")}
    `;
    bubble.appendChild(sourcesBlock);
  }

  msgEl.appendChild(avatar);
  msgEl.appendChild(bubble);
  messagesList.appendChild(msgEl);

  // Scroll to bottom
  scrollToBottom();
}

// ── Format Message (markdown-lite) ──────────────────
function formatMessage(text) {
  if (!text) return "";

  // Escape HTML first, except we handle specific patterns
  let html = escapeHtml(text);

  // **bold**
  html = html.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");

  // *italic*
  html = html.replace(/\*(.+?)\*/g, "<em>$1</em>");

  // `code`
  html = html.replace(/`([^`]+)`/g, "<code>$1</code>");

  // Numbered list: "1. item"
  html = html.replace(/^\d+\.\s(.+)$/gm, "<li>$1</li>");
  html = html.replace(/(<li>.*<\/li>)/s, "<ol>$1</ol>");

  // Bullet list: "- item"
  html = html.replace(/^[-•]\s(.+)$/gm, "<li>$1</li>");

  // Horizontal rule
  html = html.replace(/---/g, "<hr/>");

  // Paragraphs from double newlines
  html = html.split("\n\n").map(p => {
    p = p.trim();
    if (!p) return "";
    if (p.startsWith("<")) return p; // Already HTML
    return `<p>${p.replace(/\n/g, "<br/>")}</p>`;
  }).join("");

  return html || text;
}

// ── Escape HTML ───────────────────────────────────────
function escapeHtml(text) {
  const map = { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#039;" };
  return text.replace(/[&<>"']/g, m => map[m]);
}

// ── Typing Indicator ──────────────────────────────────
function showTypingIndicator() {
  const template = document.getElementById("typingTemplate");
  const clone = template.content.cloneNode(true);
  messagesList.appendChild(clone);
  scrollToBottom();
  return document.getElementById("typingMsg");
}

function removeTypingIndicator(el) {
  if (el && el.parentNode) el.remove();
}

// ── Scroll to Bottom ──────────────────────────────────
function scrollToBottom() {
  requestAnimationFrame(() => {
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
  });
}

// ── Loading State ─────────────────────────────────────
function setLoading(state) {
  isLoading = state;
  sendBtn.disabled = state;
  messageInput.disabled = state;
}

// ── Error Toast ───────────────────────────────────────
function showErrorToast(message) {
  const toast = document.createElement("div");
  toast.className = "error-toast";
  toast.textContent = message;
  document.body.appendChild(toast);
  setTimeout(() => toast.remove(), 3500);
}

// ── Run ───────────────────────────────────────────────
init();
