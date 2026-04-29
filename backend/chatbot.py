from flask import Flask, request, jsonify
from flask_cors import CORS
from rag import load_vectorstore, search_manual
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
vectorstore = load_vectorstore()
print("Vector store loaded successfully!")

SYSTEM_PROMPT = """
You are a friendly and knowledgeable virtual assistant for Vacations for YOU, a vacation rental company with over 23 years of experience managing 550+ properties across the U.S.

TONE: Warm, friendly, and professional. Always be helpful and accurate. If you don't know something, direct the guest to contact support rather than guessing.

ABOUT VACATIONS FOR YOU:
- Family-owned company built on honesty, integrity, and transparency
- Manages 550+ vacation rentals across a family of brands
- Phone: 888-509-0039 | Email: info@vacationsforyou.com
- Guests can book direct at vacationsforyou.com to save

DESTINATIONS & PROPERTY TYPES:
1. Smoky Mountains (Tennessee) — Cabins and condos in Gatlinburg, Pigeon Forge, Sevierville, and Wears Valley. Options range from romantic honeymoon hideaways to large group lodges. Amenities include game tables, movie theaters, private indoor pools, hot tubs, firepits, and mountain views. Brand: cabinsforyou.com
2. North Georgia (Blue Ridge Mountains) — Cabins, condos, and lodges in Blue Ridge, Ellijay, Big Canoe, and Bent Tree. Features include hot tubs, game rooms, wet bars, mountain views, and projectors. Big Canoe and Bent Tree are gated communities with golf courses, lakes, hiking trails, pools, tennis courts, and more. Brand: georgiacfy.com
3. Florida Emerald Coast — Beach houses and condos in Destin, Panama City Beach, and Perdido Key. Many properties are walkable to the beach. Features include resort pools, private balconies, and ocean views. Brand: floridacfy.com
4. Alabama Gulf Coast — Beach houses and condos in Gulf Shores and Orange Beach along 57+ miles of shoreline. Pet-friendly options available. Brand: alabamacfy.com

NEARBY ACTIVITIES BY DESTINATION:
- Smoky Mountains: Great Smoky Mountains National Park, Dollywood, Ober Gatlinburg ski resort, whitewater rafting, hiking, Cades Cove, moonshine distilleries, dinner shows, The Island in Pigeon Forge
- North Georgia: Blue Ridge Scenic Railway, Mercier Orchards, Chattahoochee National Forest, hiking, kayaking, fly fishing, whitewater rafting, craft breweries, antique shopping
- Florida Emerald Coast: Gulfarium Marine Adventure Park, The Village of Baytowne Wharf, world-class golf, fishing, jet skiing, paddleboarding, parasailing, snorkeling
- Alabama Gulf Coast: Fort Morgan, Dauphin Island, dolphin cruises, parasailing, paddleboarding, snorkeling, The Whiskey Wreck dive site, zoo, Mardi Gras events

REWARDS PROGRAM:
- Vacations for YOU Rewards membership costs $220/year (includes 1 free month)
- Benefits: vacation rental discounts, FREE attraction tickets with every stay (2 per attraction), free nights (1 per 10 nights stayed), lower pet fees, no blackout dates
- To join: call 1-855-692-9102
- Perks apply across all brands and destinations
- Free nights: earn 1 per 10 nights stayed; only 1 can be used per reservation
- Membership renews automatically; can be cancelled after paid in full
- Attraction tickets are facilitated through Xplorie — guests call Xplorie with their name, phone number, and rental name to book

RESERVATION QUESTIONS:
- You have access to reservation lookup tools — use them when a guest provides a confirmation number and last name
- You can share details like dates, property info, and check-in/check-out times from the reservation data

OUT OF SCOPE (politely decline and redirect):
- Pricing, payments, or refunds → say: "For pricing and payment questions please contact us at 888-509-0039 or info@vacationsforyou.com"
- Competitor comparisons → politely decline
- Anything unrelated to VacationsForYOU properties, policies, or destinations → politely decline

IF YOU DON'T KNOW THE ANSWER:
Say: "I'm sorry, I don't have that information. Please contact our support team at 888-509-0039 or info@vacationsforyou.com for assistance."

IMPORTANT: When answering policy questions, always base your response on the provided manual context. If the manual context does not contain the answer, say you don't know rather than guessing.

Keep responses friendly, warm, and concise — aim for under 150 words. Always prioritize accuracy.
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
    session_id = body.get("session_id")

    if not user_message:
        return jsonify({"error": "Please enter a message."}), 400
    
    if session_id not in sessions:
        session_id = str(uuid.uuid4())
        sessions[session_id] = {
            "reservation": None, 
            "history": [],
            "state": "normal",
            "pending_confirmation": None,
            "last_active": datetime.utcnow()
        }
    
    session = sessions[session_id]
    state = session.get("state", "normal")

    # Session timeout handling (30 minutes of inactivity)
    time_out_minutes = 30
    last_active = session.get("last_active", datetime.utcnow())
    if (datetime.utcnow() - last_active).total_seconds() > time_out_minutes * 60:
        sessions.pop(session_id)
        return jsonify({"error": "Session expired due to inactivity. Please start a new conversation."}), 401
    
    # Update last active time
    session["last_active"] = datetime.utcnow()
    
    # State: waiting for confirmation number
    if state == "waiting_for_confirmation":

        confirmation = user_message.upper()
        session["pending_confirmation"] = confirmation
        session["state"] = "waiting_for_last_name"
        reply = f"Thanks! Now please provide the last name on the reservation for confirmation number {confirmation}."
        confidence = "HIGH_CONFIDENCE"

        log_interaction(session_id, user_message, reply, confidence)

        return jsonify({
            "reply": reply, "confidence": confidence, "session_id": session_id
        })
    
    # State: waiting for last name
    if state == "waiting_for_last_name":
        confirmation = session.get("pending_confirmation")
        last_name = user_message.strip()
        session["pending_confirmation"] = None
        session["state"] = "normal"

        # Mock reservation lookup for demo
        mock_reservations = {
            "VFY-10042": {"first_name": "Sarah", "last_name": "Mitchell", "property": "Sunset Cove Cottage", "check_in": "April 12, 2026", "check_out": "April 19, 2026"},
            "VFY-10087": {"first_name": "James", "last_name": "Torres", "property": "Blue Ridge Mountain Cabin", "check_in": "May 3, 2026", "check_out": "May 10, 2026"},
            "VFY-10155": {"first_name": "Linda", "last_name": "Park", "property": "Gulf Shore Villa", "check_in": "June 21, 2026", "check_out": "June 28, 2026"},
        }

        

        reservation = mock_reservations.get(confirmation)

        if not reservation:
            reply = f"Sorry, I couldn't find a reservation with confirmation number {confirmation}. Please check the number and try again."
            confidence = "OUT_OF_SCOPE"
        elif reservation["last_name"].lower() != last_name.lower():
            reply = f"Sorry, the last name {last_name} does not match our records for confirmation number {confirmation}. Please check and try again."
            confidence = "OUT_OF_SCOPE"
        else:
            session["reservation"] = reservation
            reply = f"Thanks {reservation['first_name']}! I've found your reservation for {reservation['property']} from {reservation['check_in']} to {reservation['check_out']}. How can I assist you with your stay?"
            confidence = "HIGH_CONFIDENCE"

        log_interaction(session_id, user_message, reply, confidence)

        return jsonify({
            "reply": reply, 
            "confidence": confidence,
            "session_id": session_id,
        })
    
    # Detect Reservation Lookup Intent
    reservation_keywords = ["i have a reservation", "look up my booking", "my booking",
                            "check my reservation", "find my reservation", "my confirmation"]

    if any(keyword in user_message.lower() for keyword in reservation_keywords):
        session["state"] = "waiting_for_confirmation"
        reply = "Sure! Please share your confirmation number and I'll pull up your reservation."
        log_interaction(session_id, user_message, reply, "HIGH_CONFIDENCE")
        return jsonify({"reply": reply, "session_id": session_id})
    
    manual_context = ""
    
    try:
        # load relevant manual context based on user message
        manual_context = search_manual(user_message, vectorstore)

        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT + "\n\nRelevant information from the manual:\n" + manual_context},
                {"role": "user", "content": user_message}
            ],
            max_tokens=500,
            temperature=0.3,
        )
        reply = response.choices[0].message.content

        #log which mannual sections were used for context in the response for better traceability
        log_interaction(session_id, user_message, reply, detect_confidence(reply))
        print(f"CONTEXT USED: {manual_context[:200]}...")

    except Exception as e:
        print(f"Error generating response: {e}")
        reply = "Sorry, I'm having trouble generating a response right now."

    confidence = detect_confidence(reply)
    return jsonify({
        "reply": reply, 
        "confidence": confidence,
        "session_id": session_id,
        "justification": manual_context[:300] if manual_context else None
    })

@app.route("/logs", methods=["GET"])
def logs():
    return jsonify(list(sessions.values()))

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