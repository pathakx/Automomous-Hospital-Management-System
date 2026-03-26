# Hospital AI Chatbot 🏥🤖

An intelligent, state-driven hospital assistant that allows patients and doctors to interact with a hospital's management system through a single, natural language chat interface. 

Built with **Next.js**, **FastAPI**, **PostgreSQL**, and **LangGraph** for multi-step AI workflow orchestration.

---

## 🌟 Features

### For Patients
- **📅 Appointment Management:** Check doctor availability, book, reschedule, or cancel appointments.
- **📄 Medical Records:** View lab reports, radiology reports, and discharge summaries.
- **💊 Prescriptions:** Check latest prescriptions, dosage instructions, and history.
- **💳 Billing:** View pending bills and pay securely online.
- **⚕️ Medical Assistant:** Analyze symptoms, get department recommendations, and ask general medical questions safely (with medical disclaimers).

### For Doctors
- **👥 Patient Management:** View your patients and daily schedules.
- **🩺 Prescribing:** Write and upload prescriptions.
- **📁 Reports:** Upload patient medical reports.

---

## 🏗️ Architecture & Tech Stack

The platform is split into three main layers:

1. **Frontend (User Interface):** 
   - Framework: **Next.js** (React) & **TailwindCSS**
   - Features: Real-time chat interface, message bubbles with rich Markdown rendering (ReactMarkdown), structured responses (appointment lists, detailed reports).

2. **Backend (Core APIs & Database):**
   - Framework: **FastAPI** (Python)
   - Database: **PostgreSQL** via **SQLAlchemy** (ORM) & **Alembic** (Migrations).
   - Features: JWT-based Authentication, robust REST APIs for all hospital services.

3. **AI Layer (Agent Workflow):**
   - Engine: **LangGraph** & **LLM** (Groq / Llama 3)
   - Capabilities: 
     - Intent detection and Entity extraction.
     - Multi-turn conversational memory (remembers context across requests).
     - Conditional tool execution (connects AI securely to backend APIs).
     - Entity validation and Ask-User fallback loops.

---

## 🛠️ Implementation & Setup Steps

### Prerequisites
- Node.js (v18+)
- Python (3.10+)
- PostgreSQL installed and running.
- LLM API Key (e.g., Groq API Key).

### 1. Database Setup
Ensure your local PostgreSQL server is running. Create a new database for the project:
```sql
CREATE DATABASE hospital_chatbot;
```

### 2. Backend Setup
1. Open a terminal and navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create and activate a Python virtual environment:
   ```bash
   python -m venv .venv
   
   # Windows
   .venv\Scripts\activate
   # Mac/Linux
   source .venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Configure Environment Variables:
   Create a `.env` file in the `backend` folder with the following details:
   ```env
   DATABASE_URL=postgresql://postgres:password@localhost:5432/hospital_chatbot
   JWT_SECRET=your_super_secret_key
   GROQ_API_KEY=your_groq_api_key
   ```
5. Run Database Migrations:
   ```bash
   alembic upgrade head
   ```
   *(Optionally, run any seed scripts if provided to populate doctors, patients, and availability).*
6. Start the Backend Server:
   ```bash
   uvicorn app.main:app --reload
   ```
   The backend will run on `http://localhost:8000`. Interactive API docs are available at `http://localhost:8000/docs`.

### 3. Frontend Setup
1. Open a new terminal and navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Configure Environment Variables:
   Create a `.env.local` file in the `frontend` folder:
   ```env
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```
4. Start the Frontend Server:
   ```bash
   npm run dev
   ```
   The frontend will run on `http://localhost:3000`.

---

## 🧠 How the AI Agent Works (LangGraph Workflow)

Unlike standard stateless chatbots, this bot uses a **StateGraph** to handle complex, multi-turn medical workflows contextually:
1. **User Message** → AI extracts the underlying `Intent` and `Entities`.
2. **Entity Validation** → The Agent checks if it has all required data (e.g., specific `date` and `time` for appointments).
3. **Decision Router** → 
   - If data is missing → **Ask_User node** asks follow-up clarifying questions.
   - If data is complete → **Tool_Executor node** directly calls the backend REST API securely.
4. **Response Generator** → Analyzes the tool's raw JSON output and formats it into user-friendly chat text.
5. All conversations and missing fields are persisted across session turns so the bot remembers the context.

---

## 🔒 Security & Privacy
- **JWT Authentication:** Ensures users can only access their own sensitive data, like reports, bills, and prescriptions.
- **Backend Tool Guardrails:** Tools internally validate that the `patient_id` parameter matches the authenticated user.
- **Medical Triage Disclaimers:** The AI Symptom Analyzer automatically appends strict disclaimers clarifying that it provides informational triage, not professional medical diagnosis.
