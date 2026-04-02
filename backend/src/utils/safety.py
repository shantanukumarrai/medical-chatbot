"""
Safety & Disclaimer Utility
============================
Medical chatbots carry real responsibility.
This module handles:
- Emergency keyword detection
- Medical disclaimer injection
- Response safety filtering
"""

import re

# ─────────────────────────────────────────────
# Emergency / Crisis Keywords
# ─────────────────────────────────────────────
EMERGENCY_KEYWORDS = [
    "chest pain", "heart attack", "stroke", "can't breathe", "cannot breathe",
    "difficulty breathing", "shortness of breath", "unconscious", "not breathing",
    "severe bleeding", "bleeding heavily", "suicide", "kill myself", "want to die",
    "overdose", "drug overdose", "poisoning", "anaphylaxis", "allergic reaction",
    "seizure", "convulsion", "head injury", "broken bone", "severe burn",
    "loss of consciousness", "fainting", "collapsed", "emergency"
]

# ─────────────────────────────────────────────
# Diagnosis-seeking Keywords (to redirect)
# ─────────────────────────────────────────────
DIAGNOSIS_KEYWORDS = [
    "do i have", "am i sick", "what disease do i have", "diagnose me",
    "what's wrong with me", "is it cancer", "do i have cancer",
    "what illness do i have", "tell me my diagnosis"
]

# ─────────────────────────────────────────────
# Standard Medical Disclaimer
# ─────────────────────────────────────────────
MEDICAL_DISCLAIMER = (
    "\n\n---\n"
    "⚕️ **Medical Disclaimer**: This information is for educational purposes only "
    "and does not constitute medical advice, diagnosis, or treatment. "
    "Always consult a qualified healthcare professional for personal medical concerns."
)

EMERGENCY_RESPONSE = (
    "🚨 **This sounds like a medical emergency.**\n\n"
    "Please call emergency services immediately:\n"
    "- **India**: 108 (Ambulance) or 112\n"
    "- **US/Canada**: 911\n"
    "- **UK**: 999\n"
    "- **EU**: 112\n\n"
    "Do not wait — please seek immediate medical attention."
)

DIAGNOSIS_REDIRECT = (
    "I understand you're looking for answers, but I'm not able to provide "
    "a personal diagnosis. Only a licensed healthcare professional who examines "
    "you in person can do that.\n\n"
    "I can share general information about symptoms or conditions — "
    "would that be helpful? And please consider speaking with your doctor soon."
)


# ─────────────────────────────────────────────
# Check for Emergency
# ─────────────────────────────────────────────
def is_emergency(message: str) -> bool:
    """
    Returns True if the message contains emergency keywords.
    """
    message_lower = message.lower()
    return any(keyword in message_lower for keyword in EMERGENCY_KEYWORDS)


# ─────────────────────────────────────────────
# Check for Diagnosis Request
# ─────────────────────────────────────────────
def is_diagnosis_request(message: str) -> bool:
    """
    Returns True if the user is asking for a personal diagnosis.
    """
    message_lower = message.lower()
    return any(keyword in message_lower for keyword in DIAGNOSIS_KEYWORDS)


# ─────────────────────────────────────────────
# Main Safety Check Function
# ─────────────────────────────────────────────
def safety_check(message: str):
    """
    Checks a user message for safety concerns.

    Returns:
        (is_safe: bool, response_override: str or None)
        - If is_safe=False, return response_override directly without calling the LLM
        - If is_safe=True, proceed normally (add disclaimer to final response)
    """
    if is_emergency(message):
        return False, EMERGENCY_RESPONSE

    if is_diagnosis_request(message):
        return False, DIAGNOSIS_REDIRECT

    return True, None


# ─────────────────────────────────────────────
# Add Disclaimer to Response
# ─────────────────────────────────────────────
def add_disclaimer(response: str) -> str:
    """
    Appends the standard medical disclaimer to any AI-generated response.
    """
    return response + MEDICAL_DISCLAIMER


# ─────────────────────────────────────────────
# Sanitize Input
# ─────────────────────────────────────────────
def sanitize_input(message: str) -> str:
    """
    Basic input sanitization:
    - Strips extra whitespace
    - Removes potential prompt injection attempts
    - Limits input length
    """
    # Trim whitespace
    message = message.strip()

    # Limit to 1000 characters
    message = message[:1000]

    # Remove common prompt injection patterns
    injection_patterns = [
        r"ignore (previous|above|all) instructions",
        r"forget (everything|your instructions)",
        r"you are now",
        r"act as",
        r"jailbreak",
        r"DAN mode",
    ]
    for pattern in injection_patterns:
        message = re.sub(pattern, "[redacted]", message, flags=re.IGNORECASE)

    return message
