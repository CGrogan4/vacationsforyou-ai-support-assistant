from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
import requests
import os
import uuid
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
CORS(app)

openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

STREAMLINE_BASE_URL = os.getenv("STREAMLINE_BASE_URL")
STREAMLINE_TOKEN_KEY = os.getenv("STREAMLINE_TOKEN_KEY")
STREAMLINE_TOKEN_SECRET = os.getenv("STREAMLINE_TOKEN_SECRET")

sessions = {}

SYSTEM_PROMPT = """
You are a helpful and precise assistant for VacationsForYou, a vacation rental company. 
You help guests both before and after they book, answering questions about properties, availability, and policies.

TONE: warm, friendly, and professional. Always provide accurate information based on the data you have access to.

TOPICS YOU HANDLE:
- Types of properties and locations offered
- How check in and check out works
- Pet policies
- Amenities offered
- Activites and attractions near properties

RESERVATION SPECIFIC QUESTIONS:
- Reservation details (dates, property features)
- Check in and check times
- check in and check out procedures

OUT OF SCOPE:
- Anything related to pricing, payments, or refunds
- Competitor comparisons 
- Anything not directly related to the properties, policies, or procedures of VacationsForYou

IF YOU DONT KNOW THE ANSWER:
- Please respond with "I'm sorry, I don't have that information. Please contact our support team for assistance." Do not attempt to make up an answer.

Keep your responses concise and to the point, while still being friendly and helpful. under 120 words. Always prioritize providing accurate information based on the data you have access to.

"""
# Confidence detection function
def detect_confidence(response_text: str) -> str:
    lower = response_text.lower()
    if "i'm sorry" in lower or "i do not have that information" in lower:
        return "OUT_OF_SCOPE"
    if "i think" in lower or "it seems" in lower or "maybe" in lower:
        return "PARTIAL_CONFIDENCE"
    return "HIGH_CONFIDENCE"

def log_interaction(session_id: str, user_message: str, bot_reply: str, confidence: str):
    timestamp = datetime.utcnow().isoformat()
    log_entry = {
        "timestamp": timestamp,
        "session_id": session_id,
        "user_message": user_message,
        "bot_reply": bot_reply,
        "confidence": confidence
    }
    print(f"LOG: {json.dumps(log_entry)}")

# Front end API routes
@app.route("/chat", methods=["POST"])
def chat():
    body = request.json
    user_message = body.get("message", "").strip()

    if not user_message:
        return jsonify({"error": "Please enter a message."}), 400
    
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message}
            ],
            max_tokens=500,
            temperature=0.3,
        )
        reply = response.choices[0].message.content

    except Exception as e:
        print(f"Error generating response: {e}")
        reply = "Sorry, I'm having trouble generating a response right now."

    confidence = detect_confidence(reply)
    log_interaction("no-session", user_message, reply, confidence)
    return jsonify({"reply": reply, "confidence": confidence,})

# The lookup route
@app.route("/lookup", methods=["POST"])
def lookup():
    body = request.get_json()
    confirmation = body.get("confirmation_number", "").strip().upper()
    last_name = body.get("last_name", "").strip()

    if not confirmation or not last_name:
        return jsonify({"success": False, "error": "Please enter both fields."}), 400

    # Mock reservations for demo
    mock_reservations = {
        "VFY-10042": {"first_name": "Sarah", "last_name": "Mitchell", "property": "Sunset Cove Cottage", "check_in": "April 12, 2026", "check_out": "April 19, 2026"},
        "VFY-10087": {"first_name": "James", "last_name": "Torres", "property": "Blue Ridge Mountain Cabin", "check_in": "May 3, 2026", "check_out": "May 10, 2026"},
        "VFY-10155": {"first_name": "Linda", "last_name": "Park", "property": "Gulf Shore Villa", "check_in": "June 21, 2026", "check_out": "June 28, 2026"},
    }

    reservation = mock_reservations.get(confirmation)

    if not reservation:
        return jsonify({"success": False, "error": "Confirmation number not found."}), 404

    if reservation["last_name"].lower() != last_name.lower():
        return jsonify({"success": False, "error": "Last name does not match."}), 401

    session_id = str(uuid.uuid4())
    sessions[session_id] = {"reservation": reservation, "history": []}

    return jsonify({
        "success": True,
        "session_id": session_id,
        "guest_name": f"{reservation['first_name']} {reservation['last_name']}",
        "property": reservation["property"],
        "check_in": reservation["check_in"],
        "check_out": reservation["check_out"]
    })

if __name__ == "__main__":
        app.run(debug=True, port=5000)