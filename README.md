# VacationsForYOU AI Guest Support Assistant

A conversational AI support chatbot for [Vacations for YOU](https://vacationsforyou.com), designed to reduce call center load by handling routine guest inquiries through a web-based chat interface. The system answers questions about properties, policies, amenities, and reservations — before and after booking.

---

## Overview

This repository contains the Phase 1 proof-of-concept implementation. The system is production-architecture ready with mock data standing in for live StreamlineVRS data while IP whitelisting is finalized with the sponsor.

**Phase 1 evaluation results:**
- 20/20 test cases passing (100% accuracy)
- 0% hallucination rate across controlled testing
- Confidence tagging and escalation working on all out-of-scope queries

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React + TypeScript + Vite |
| Backend | Python + Flask |
| AI | OpenAI GPT-4o-mini |
| Knowledge Base | LangChain + ChromaDB (RAG on call center manual) |
| Reservation Data | StreamlineVRS API (mock fallback active in Phase 1) |
| Environment | python-dotenv |

---

## Repository Structure

```
vacationsforyou-ai-support-assistant/
├── backend/
│   ├── chatbot.py           # Flask API — /chat, /lookup, /logs endpoints
│   ├── rag.py               # RAG pipeline — ChromaDB vector store and search
│   ├── ingest.py            # One-time script to load manual into vector store
│   ├── evaluate.py          # Automated evaluation framework (20 test cases)
│   ├── test_connection.py   # StreamlineVRS connection tester
│   ├── .env.example         # Environment variable template
│   └── VFYmanual.pdf        # Call center manual (gitignored — obtain from team lead)
├── frontend/
│   └── src/
│       ├── App.tsx          # Chat widget toggle
│       ├── ChatUI.tsx       # Main chat interface and session management
│       └── ChatUI.css       # Chat widget styles
├── SETUP.md                 # Developer setup guide
├── WHITELIST_CHECK.md       # StreamlineVRS IP whitelist testing guide
└── README.md
```

---

## Quick Start

> See [SETUP.md](./SETUP.md) for full setup instructions including RAG configuration.

**Backend**
```bash
cd backend
python -m venv venv
.\venv\Scripts\activate
pip install flask flask-cors openai python-dotenv requests langchain langchain-openai langchain-community langchain-chroma chromadb pypdf
py ingest.py       # Run once to build the RAG vector store
py chatbot.py      # Start the API server on port 5000
```

**Frontend**
```bash
cd frontend
npm install
npm run dev
```

Open **http://localhost:5173** and click the 💬 button.

---

## Environment Variables

Copy `.env.example` to `.env` in the `backend` folder and fill in your values:

```
OPENAI_API_KEY=your_openai_key_here
STREAMLINE_TOKEN_KEY=your_token_key_here
STREAMLINE_TOKEN_SECRET=your_token_secret_here
STREAMLINE_BASE_URL=https://[month]-web.4vrs.com/api/json
```

>  `.env` is gitignored. Never commit credentials to version control.

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/chat` | Send a message, receive an AI response with confidence tag |
| POST | `/lookup` | Validate a reservation by confirmation number and last name |
| GET | `/logs` | View all active sessions and interaction history |

---

## RAG Architecture

Policy responses are grounded in the company call center manual using a Retrieval-Augmented Generation (RAG) pipeline. On each request, the top 5 most relevant manual chunks are retrieved from ChromaDB and injected into the system prompt before calling OpenAI. This eliminates hallucination on policy questions.

To update the knowledge base, replace `VFYmanual.pdf` and rerun `py ingest.py`. No code changes required.

---

## Test Reservations

Three mock reservations are available for development and demo purposes:

| Confirmation | Last Name | Property |
|---|---|---|
| VFY-10042 | Mitchell | Sunset Cove Cottage |
| VFY-10087 | Torres | Blue Ridge Mountain Cabin |
| VFY-10155 | Park | Gulf Shore Villa |

---

## Confidence Handling

Every AI response is classified before delivery:

| Tag | Meaning | Escalated |
|---|---|---|
| `HIGH_CONFIDENCE` | Response grounded in available data | No |
| `PARTIAL_CONFIDENCE` | Response may be incomplete | No |
| `OUT_OF_SCOPE` | Question outside defined scope | Yes |

All interactions are logged with timestamp, session ID, user message, bot reply, confidence tag, and escalation flag.

---

## StreamlineVRS Integration

The system is architected for live StreamlineVRS data with a mock fallback for Phase 1. To activate the live connection:

1. Add valid credentials to `.env`
2. Confirm your IP is whitelisted — see [WHITELIST_CHECK.md](./WHITELIST_CHECK.md)
3. No code changes required

> StreamlineVRS credentials rotate monthly. If you see `E0010 — Token invalid` at the start of a new month, contact the sponsor for updated credentials.

---

## Evaluation

Run the automated evaluation framework against the live server:

```bash
py evaluate.py
```

Expected output: 20/20 passing across Properties, Policies, Activities, Rewards, Reservation, and Out of Scope categories. Results are saved to `evaluation_results.json`.

---

## Roadmap

| Phase | Focus |
|---|---|
| Phase 2 | Live StreamlineVRS integration, persistent chat logging, agent dashboard |
| Phase 3 | Production deployment, multi-language support, analytics |
| Phase 4 | SMS/voice channels, expansion to additional brands |

---

## Acknowledgments

Built by Cassidie Grogan, Kendal Elison, Ezra Begashaw, Benjamin Dulcio, and Wilfred Faltz as a senior capstone project at Kennesaw State University, College of Computing and Software Engineering, Spring 2026.

Developed in partnership for the Vacations for YOU team.
