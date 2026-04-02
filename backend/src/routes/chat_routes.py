"""
Chat API Routes
================
Defines all REST API endpoints for the medical chatbot.

Endpoints:
  POST /api/chat       — Send a message, get a response
  DELETE /api/chat     — Clear conversation history
  GET  /api/chat/history — Get current session history (optional)
"""

import uuid
from flask import Blueprint, request, jsonify
from src.chains.rag_chain import query_chain, clear_memory, get_memory
from src.utils.safety import safety_check, add_disclaimer, sanitize_input

# Create a Blueprint (modular route group)
chat_blueprint = Blueprint("chat", __name__)


# ─────────────────────────────────────────────
# POST /api/chat
# ─────────────────────────────────────────────
@chat_blueprint.route("/chat", methods=["POST"])
def chat():
    """
    Main chat endpoint.
    
    Request body (JSON):
    {
        "message": "What are the symptoms of diabetes?",
        "session_id": "abc123"  ← optional; auto-generated if not provided
    }
    
    Response (JSON):
    {
        "answer": "Diabetes symptoms include...",
        "sources": ["Medical Handbook, page 45"],
        "session_id": "abc123"
    }
    """
    try:
        data = request.get_json()

        # Validate request
        if not data or "message" not in data:
            return jsonify({
                "error": "Missing 'message' field in request body"
            }), 400

        raw_message = data.get("message", "").strip()
        if not raw_message:
            return jsonify({"error": "Message cannot be empty"}), 400

        # Get or generate session ID (tracks conversation history)
        session_id = data.get("session_id") or str(uuid.uuid4())

        # ── Step 1: Sanitize input ──
        message = sanitize_input(raw_message)

        # ── Step 2: Safety check ──
        is_safe, override_response = safety_check(message)

        if not is_safe:
            # Return the safety response directly (no LLM call)
            return jsonify({
                "answer": override_response,
                "sources": [],
                "session_id": session_id,
                "safety_triggered": True
            }), 200

        # ── Step 3: Query the RAG chain ──
        result = query_chain(session_id, message)

        # ── Step 4: Add medical disclaimer ──
        final_answer = add_disclaimer(result["answer"])

        return jsonify({
            "answer": final_answer,
            "sources": result.get("sources", []),
            "session_id": session_id,
            "safety_triggered": False
        }), 200

    except Exception as e:
        # Log the error (in production, use proper logging)
        print(f"❌ Error in /api/chat: {str(e)}")
        return jsonify({
            "error": "An internal error occurred. Please try again.",
            "details": str(e) if __debug__ else None
        }), 500


# ─────────────────────────────────────────────
# DELETE /api/chat
# ─────────────────────────────────────────────
@chat_blueprint.route("/chat", methods=["DELETE"])
def clear_chat():
    """
    Clears the conversation history for a session.
    Call this when the user clicks "New Chat".
    
    Request body (JSON):
    { "session_id": "abc123" }
    """
    data = request.get_json()
    session_id = data.get("session_id") if data else None

    if session_id:
        clear_memory(session_id)
        return jsonify({"message": "Conversation cleared.", "session_id": session_id}), 200

    return jsonify({"error": "Missing session_id"}), 400


# ─────────────────────────────────────────────
# GET /api/chat/history
# ─────────────────────────────────────────────
@chat_blueprint.route("/chat/history", methods=["GET"])
def get_history():
    """
    Returns the conversation history for a session.
    Useful for debugging or displaying past messages on reload.
    
    Query param: ?session_id=abc123
    """
    session_id = request.args.get("session_id")
    if not session_id:
        return jsonify({"error": "Missing session_id query param"}), 400

    try:
        memory = get_memory(session_id)
        messages = memory.chat_memory.messages
        history = [
            {"role": "user" if i % 2 == 0 else "assistant", "content": m.content}
            for i, m in enumerate(messages)
        ]
        return jsonify({"session_id": session_id, "history": history}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
