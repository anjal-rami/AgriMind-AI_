# AgriMind AI - Multi-Agent Agricultural Intelligence Platform

AgriMind AI is a full-stack precision agriculture platform that integrates LLM intent routing, domain-specific AI agents, ICAR district crop datasets, and OpenWeatherMap climate feeds to empower Indian farmers and agricultural researchers.

---

## 🏗 System Architecture & Phase Breakdown

- **Phase 1 (Completed)**: Core FastAPI backend, SQLAlchemy database, Multi-Agent Intent Orchestrator (`orchestrator.py`), OpenWeatherMap integration (`weather_agent.py`), ICAR crop recommendation engine (`crop_recommendation_agent.py`), Glassmorphic AI Chatbot (`ChatBot.jsx`), and Dashboard shell (`Dashboard.jsx`).
- **Phase 2 (Upcoming)**: CNN Leaf Disease Classifier fine-tuned on PlantVillage (`disease_detection_agent.py`), Agmarknet live price integration (`market_price_agent.py`), Rule-based irrigation schedule engine (`irrigation_agent.py`), PM-KISAN & PMFBY government scheme filter (`scheme_agent.py`).
- **Phase 3 (Upcoming)**: Recharts yield analytics, Docker containerization (`Dockerfile` & `docker-compose.yml`), and production cloud hosting scripts.

---

## ⚙️ Setup & Execution

### Backend Setup (FastAPI & Python 3.13)
```bash
cd backend
python -m pip install fastapi uvicorn sqlalchemy pydantic requests anthropic python-dotenv
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

### Frontend Setup (React.js + Vite)
```bash
cd frontend
npm install
npm run dev -- --host 127.0.0.1 --port 5173
```

Open `http://localhost:5173` to launch AgriMind AI.
