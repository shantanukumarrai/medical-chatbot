"""
LangChain Medical RAG Chain
============================
This module builds the core AI pipeline:
- ConversationalRetrievalChain with memory
- Custom medical system prompt
- Pinecone retriever integration
- Chat history management
"""

import os
from langchain_groq import ChatGroq
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferWindowMemory
from langchain.prompts import (
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    ChatPromptTemplate,
    PromptTemplate
)
from src.utils.vector_store import get_retriever


# ─────────────────────────────────────────────
# 1. Medical System Prompt
# ─────────────────────────────────────────────
# This is the most important part — it sets the AI's behavior.
# A well-crafted prompt = a safe, helpful medical assistant.

MEDICAL_SYSTEM_PROMPT = """You are MediBot, a knowledgeable and compassionate medical information assistant.

Your role is to:
- Provide accurate, evidence-based medical information from the context provided
- Explain medical terms in simple, understandable language
- Help users understand symptoms, conditions, medications, and general health topics
- Always encourage users to consult qualified healthcare professionals

Your strict guidelines:
- NEVER provide personal medical diagnoses
- NEVER recommend specific treatments or dosages for individual cases
- ALWAYS recommend seeing a doctor for personal health concerns
- If information is not in the context, say "I don't have specific information on that — please consult a doctor"
- Be empathetic and never alarming unnecessarily
- For mental health topics, always mention professional support resources

Context from medical knowledge base:
{context}

Use the above context to answer the user's question accurately and safely.
If the context doesn't contain relevant information, acknowledge the limitation.
"""

CONDENSE_QUESTION_PROMPT = PromptTemplate.from_template("""
Given the following conversation history and a follow-up question, 
rephrase the follow-up question to be a standalone question that captures the full context.

Chat History:
{chat_history}

Follow-up Question: {question}

Standalone question:
""")


# ─────────────────────────────────────────────
# 2. Build the LLM
# ─────────────────────────────────────────────
def get_llm():
    """Creates Groq LLM - FREE and Fast!"""
    return ChatGroq(
        model_name="llama-3.3-70b-versatile",
        temperature=float(os.getenv("LLM_TEMPERATURE", "0.3")),
        max_tokens=int(os.getenv("LLM_MAX_TOKENS", "800")),
        groq_api_key=os.getenv("GROQ_API_KEY"),
    )

# ─────────────────────────────────────────────
# 3. Build the QA Prompt
# ─────────────────────────────────────────────
def get_qa_prompt():
    """
    Constructs the ChatPromptTemplate used inside the QA chain.
    Combines system instructions + medical context + human message.
    """
    messages = [
        SystemMessagePromptTemplate.from_template(MEDICAL_SYSTEM_PROMPT),
        HumanMessagePromptTemplate.from_template("{question}")
    ]
    return ChatPromptTemplate.from_messages(messages)


# ─────────────────────────────────────────────
# 4. Session Memory Store
# ─────────────────────────────────────────────
# Store memory per session_id so different users don't share history
_session_memories = {}

def get_memory(session_id: str):
    """
    Returns a ConversationBufferWindowMemory for a given session.
    Window size = 10 exchanges (keeps last 10 Q&A pairs in memory).
    Creates a new one if session doesn't exist.
    """
    if session_id not in _session_memories:
        _session_memories[session_id] = ConversationBufferWindowMemory(
            k=10,                          # Remember last 10 exchanges
            memory_key="chat_history",     # Must match the chain's expected key
            return_messages=True,          # Return as Message objects (not string)
            output_key="answer"            # Which chain output to save to memory
        )
    return _session_memories[session_id]


def clear_memory(session_id: str):
    """Clears the conversation history for a given session."""
    if session_id in _session_memories:
        del _session_memories[session_id]


# ─────────────────────────────────────────────
# 5. Build the Full Conversational Chain
# ─────────────────────────────────────────────
def get_chain(session_id: str):
    """
    Assembles the full ConversationalRetrievalChain:
    
    User Question
        ↓
    [Condense with history] → standalone question
        ↓
    [Pinecone Retriever] → top-k relevant document chunks
        ↓
    [LLM + System Prompt + Context] → answer
        ↓
    [Memory] → saved for next turn
    
    Args:
        session_id: Unique identifier per user session
    
    Returns:
        ConversationalRetrievalChain ready for .invoke()
    """
    llm = get_llm()
    retriever = get_retriever(k=4)
    memory = get_memory(session_id)
    qa_prompt = get_qa_prompt()

    chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        memory=memory,
        combine_docs_chain_kwargs={"prompt": qa_prompt},
        condense_question_prompt=CONDENSE_QUESTION_PROMPT,
        condense_question_llm=get_llm(),     # Separate LLM call to rephrase question
        return_source_documents=True,         # Include source docs in response
        verbose=os.getenv("FLASK_ENV") == "development"
    )

    return chain


# ─────────────────────────────────────────────
# 6. Run a Query
# ─────────────────────────────────────────────
def query_chain(session_id: str, question: str) -> dict:
    """
    Runs a question through the RAG chain for a given session.

    Args:
        session_id: Unique session identifier
        question: The user's medical question

    Returns:
        {
            "answer": "...",
            "sources": ["page 12 of Medical Handbook", ...]
        }
    """
    chain = get_chain(session_id)

    # Run the chain
    result = chain.invoke({"question": question})

    # Extract source document references (for transparency)
    sources = []
    for doc in result.get("source_documents", []):
        source = doc.metadata.get("source", "Unknown source")
        page = doc.metadata.get("page", "")
        ref = f"{source}" + (f", page {page+1}" if page != "" else "")
        if ref not in sources:
            sources.append(ref)

    return {
        "answer": result.get("answer", "I'm sorry, I couldn't find an answer."),
        "sources": sources
    }
