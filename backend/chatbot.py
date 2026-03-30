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

    return jsonify({"reply": reply})

if __name__ == "__main__":
        app.run(debug=True, port=5000)

#