# 🧠 Aura - AI-Powered Student Mental Wellness Tracker

Aura is a Generative AI-powered digital wellness companion designed to help students monitor and improve their mental well-being during high-stakes competitive exams (e.g., JEE, NEET, UPSC, GATE, CAT, and Board Exams). 

It analyzes open-ended daily journaling and mood logs using Google's Gemini API to uncover hidden stress triggers and emotional patterns, and provides hyper-personalized, contextual coping strategies, guided mindfulness breaks, and an empathetic wellness chatbot companion.

---

## ✨ Features

1. **📝 Contextual Daily Journaling**: Students write freely about their day, mock test scores, or study progress. Aura's GenAI analyzes logs to gauge stress load, detect complex emotional states (burnout, self-doubt), and isolate primary triggers.
2. **📊 Wellness Dashboard & Trends**: Visually tracks mood distribution, stress levels over time, and trigger frequencies with interactive plots.
3. **💬 'Aura' Empathetic Companion**: An always-available chatbot that references student profile settings (target exam, study hours, stressors) and recent journal entries to hold natural, supportive conversations.
4. **🧘 Guided Breathing & Mindfulness**: Interactive, calming Box Breathing animation cycle and structured cognitive-grounding guides (such as the 5-4-3-2-1 technique).
5. **📋 Persistent Storage**: Powered by a lightweight local SQLite database to persist journal logs, profile info, and chat records.

---

## 🛠️ Tech Stack & Requirements

- **Python**: v3.10+
- **Streamlit**: Web interface framework
- **Requests**: Standard library HTTP client (avoids heavy SDK dependencies)
- **SQLite3**: Integrated lightweight DB (zero-setup)
- **Pandas / Altair**: Data processing and dashboard visualizations

---

## 🚀 Setup & Launch Instructions

### 1. Install Dependencies
Run the following in your terminal:
```bash
pip install streamlit pandas altair requests
```

### 2. Configure Your API Key
The app leverages Google Gemini to analyze logs and chat. You can provide your key in three ways:
1. **Sidebar Input**: Enter the key in the application's sidebar password field while running.
2. **Environment Variable**: Export the key before launching the app:
   ```powershell
   $env:GEMINI_API_KEY="your-api-key-here"
   ```
3. **Local `.env` File**: Create a `.env` file in the root directory:
   ```env
   GEMINI_API_KEY=your-api-key-here
   ```

### 3. Run the Application
Start the Streamlit application:
```bash
python -m streamlit run app.py
```
This will spin up a local server and automatically open the app in your default browser (typically at `http://localhost:8501`).

### 4. Running the Test Suite
You can execute the automated test suite locally to verify the database schema and API client logic:
```bash
python -m unittest test_wellness.py
```

---

## 📂 Architecture & File Structure

- [app.py](file:///c:/Users/akhun/OneDrive/Desktop/mental-wellness-01/app.py): Entrypoint managing Streamlit rendering, page routing, and form inputs.
- [database.py](file:///c:/Users/akhun/OneDrive/Desktop/mental-wellness-01/database.py): Handles SQLite database connection pool, schema initialization, and CRUD operations.
- [gemini_client.py](file:///c:/Users/akhun/OneDrive/Desktop/mental-wellness-01/gemini_client.py): Direct API controller making secure requests to Gemini endpoints.
- [styles.py](file:///c:/Users/akhun/OneDrive/Desktop/mental-wellness-01/styles.py): Hosts custom styling classes and the embedded HTML5 breathing component.
- [test_wellness.py](file:///c:/Users/akhun/OneDrive/Desktop/mental-wellness-01/test_wellness.py): Comprehensive unit testing suite for database CRUD and API response parsing.
