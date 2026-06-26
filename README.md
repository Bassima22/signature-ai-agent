# 🏎️ Signature x Sima Media: AI Coordination Agent
### **Dockerized Domain-Specific AI Agent for Car Detailing & Media Production**

## 📌 Project Overview
This project implements a working, domain-specific AI agent designed for **Signature** (a premium car detailing company) and **Sima Media** (a digital marketing agency). The agent acts as a **Coordinator**, bridging the gap between the detailing shop floor and the media production team.

The agent manages vehicle availability, enforces strict safety protocols for fresh paint protection, coordinates with drivers, and generates production reports based on real-time data.

---

## 🏗️ System Architecture
Following the project requirements (Section 4), the system is built into 7 distinct layers:

1. **Chat Interface:** A professional web UI built with **Gradio**, featuring a live database monitor.
2. **Orchestration Layer:** Built with **LangGraph** to manage state transitions, memory, and tool-calling loops.
3. **LLM Reasoning Core:** Powered by **Llama 3.1 8B (via Groq)** for fast, deterministic reasoning.
4. **Tool Layer:** 6 Custom Python tools for Information Lookup, Safety Analysis, Action Booking, and Reporting.
5. **Memory Layer:** Short-term conversation context (Working Memory) to track user intent and car models.
6. **Data Layer:** Structured **SQLite** database containing vehicles, employees, weather, business rules, and audit logs.
7. **Container Layer:** Fully **Dockerized** deployment using Docker Compose for consistent evaluation.

---

## 🛡️ Business Rules & Safety Logic (Grounded AI)
The agent is "Grounded" in a local SQLite database and follows strict safety-critical logic (Section 4):

* **The 48-Hour Rule:** For outdoor shoots, the agent calculates time since detailing. If < 48 hours, the action is **blocked** to protect chemical bonding.
* **Weather Awareness:** Outdoor shoots are automatically rejected during Rainy or High-Wind conditions.
* **Space Requirements:** Wide-angle media shoots require at least 200m² of space. The agent validates dimensions before approving.
* **Confirmation Gates:** As a **Decision-Support System**, the agent analyzes requests but requires user confirmation before writing to the database.

---

## 🛠️ Tech Stack
- **Framework:** LangGraph / LangChain
- **LLM:** Llama 3.1 8B / Llama 3.3 70B (Groq)
- **UI:** Gradio
- **Database:** SQLite 3
- **Container:** Docker & Docker Compose

---

## 🚀 How to Run (One-Command Startup)

### 1. Prerequisites
- Docker Desktop installed and running.
- A Groq API Key (from console.groq.com).

### 2. Configuration
Create a file named `.env` in the root directory and add your API key:
```text
GROQ_API_KEY=your_gsk_key_here
```


### 3. Launch
Open your terminal in the project folder and run the following command. This will build the container and initialize the database automatically:
```bash
docker compose up --build
```
### 4. Access
Once the terminal shows "Running on 0.0.0.0:7860", open your browser to:
http://localhost:7860

---

## 🧪 Questions for Testing
- What are the official shop rules for outdoor shoots?
- Why can't we take a car outside right after it is polished?
- What cars are in the shop right now?
- Give me the detailing status of the Porsche 911.
- Can we take the Porsche to the Beach for a shoot today?
- The BMW is ready. Let's schedule it for the Beach right now.
- Is the Showroom big enough for a wide-angle media shoot?
- Since it's raining, book the BMW for the Showroom today at 3 PM.
- Schedule the Porsche for the Indoor Showroom tomorrow at 10 AM.
- Check the status of the BMW. (Wait for answer) Okay, book it for the Showroom.
- Generate the production call sheet for the media team.
