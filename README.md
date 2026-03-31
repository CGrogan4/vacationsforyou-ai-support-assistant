# Vacations for YOU — AI Support Assistant

A post-booking guest support chatbot built for Vacations for YOU. Guests can ask questions about their reservations, properties, policies, and more through a conversational AI interface.

---

## Project Status

**Milestone 2 — Working Prototype**

- Functional web chat interface (React + Flask)
- Reservation lookup and validation (mock data + StreamlineVRS hooks)
- AI-driven responses powered by OpenAI GPT-4o-mini
- Logging and confidence handling
- Demonstrable end-to-end flow using test data

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React + TypeScript + Vite |
| Backend | Python + Flask |
| AI | OpenAI GPT-4o-mini |
| Reservation Data | StreamlineVRS API (mock fallback included) |
| Environment | python-dotenv |

---

## Project Structure

```
vacationsforyou-ai-support-assistant/
├── frontend/
│   └── src/
│       ├── App.tsx          # Chat widget toggle
│       ├── ChatUI.tsx       # Main chat interface
│       └── ChatUI.css       # Chat styling
├── backend/
│   ├── chatbot.py           # Flask API server
│   ├── test_connection.py   # StreamlineVRS connection tester
│   ├── .env                 # Local environment variables (never commit)
│   └── .env.example         # Environment variable template
├── SETUP.md                 # Team setup instructions
└── README.md
```

---

**Backend:**
```bash
cd backend
python -m venv venv
.\venv\Scripts\activate
pip install flask flask-cors openai python-dotenv requests
py chatbot.py
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

Then open **http://localhost:5173** and click the 💬 button.

---

## Environment Variables

Create a `.env` file in the `backend` folder:

```
OPENAI_API_KEY=your_openai_key_here
STREAMLINE_TOKEN_KEY=your_token_key_here
STREAMLINE_TOKEN_SECRET=your_token_secret_here
STREAMLINE_BASE_URL=...
```

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/chat` | Send a message, get an AI response |
| POST | `/lookup` | Validate a reservation by confirmation number + last name |

---

## Test Reservations (Demo Data)

| Confirmation | Last Name | Property |
|---|---|---|
| VFY-10042 | Mitchell | Sunset Cove Cottage |
| VFY-10087 | Torres | Blue Ridge Mountain Cabin |
| VFY-10155 | Park | Gulf Shore Villa |

---

## Confidence Handling

Every AI response is tagged with a confidence level:

| Tag | Meaning |
|---|---|
| `HIGH_CONFIDENCE` | Answer is grounded in available data |
| `PARTIAL_CONFIDENCE` | Answer may be incomplete |
| `OUT_OF_SCOPE` | Question is outside the chatbot's scope |

All interactions are logged to the backend console for review.

---

## StreamlineVRS Integration

The backend is built to connect to the StreamlineVRS sandbox API. The system automatically falls back to mock data if the live API is unavailable. Once IP whitelisting is confirmed, the live connection will activate automatically with no code changes required.
