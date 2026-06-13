import requests
import json
import os

DEFAULT_MODEL = "gemini-2.5-pro"

class GeminiClient:
    def __init__(self, api_key=None):
        # Resolve api_key: first priority parameter, second OS environment
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models"

    def is_configured(self):
        """Check if an API key is set."""
        return bool(self.api_key)

    def _post(self, prompt, system_instruction=None, json_response=False, model=DEFAULT_MODEL):
        """Internal helper to make requests to the Gemini API."""
        if not self.api_key:
            raise ValueError("Gemini API key is not configured. Please provide it in the sidebar or environment.")

        url = f"{self.base_url}/{model}:generateContent"
        
        # Build contents structure
        payload = {
            "contents": [
                {
                    "parts": [{"text": prompt}]
                }
            ]
        }

        # Add system instruction if provided
        if system_instruction:
            payload["systemInstruction"] = {
                "parts": [{"text": system_instruction}]
            }

        # Request JSON mode if specified
        if json_response:
            payload["generationConfig"] = {
                "responseMimeType": "application/json"
            }

        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": self.api_key
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=20)
            response.raise_for_status()
            res_data = response.json()
            
            # Extract text response from Gemini's output JSON structure
            text_response = res_data["candidates"][0]["content"]["parts"][0]["text"]
            return text_response
        except requests.exceptions.RequestException as e:
            # Check for specific error message in response body
            err_msg = str(e)
            try:
                if hasattr(e, 'response') and e.response is not None:
                    err_json = e.response.json()
                    if "error" in err_json:
                        err_msg = err_json["error"].get("message", err_msg)
            except:
                pass
            raise Exception(f"Gemini API Error: {err_msg}")
        except (KeyError, IndexError):
            raise Exception("Failed to parse Gemini API response. Format may have changed.")

    def analyze_journal_entry(self, journal_text, mood_emoji, target_exam, current_stressor):
        """Analyze a journal entry and return structured JSON."""
        system_instruction = (
            "You are an empathetic, clinical-grade mental wellness counselor specializing in helping students "
            "preparing for high-stakes, competitive exams (such as NEET, JEE, UPSC, GATE, CAT, board exams). "
            "You analyze open-ended journaling to find hidden triggers and emotional patterns that simple sliders miss. "
            "Always return a JSON object with the exact format requested. Be deeply empathetic, supportive, and practical."
        )

        prompt = f"""
Analyze this student's journal entry. They are preparing for the {target_exam} exam.
Their self-selected mood today: {mood_emoji}
Their self-declared main stressor: {current_stressor}

Journal Text:
\"\"\"{journal_text}\"\"\"

Return a JSON object containing:
1. "stress_level": An integer from 1 to 10 (1 is completely calm, 10 is severe stress/crisis).
2. "emotions": A list of strings identifying primary emotions felt by the student (e.g. "Anxiety", "Burnout", "Self-doubt", "Exhaustion", "Overwhelmed", "Hopeful", "Frustrated", "Determined"). Limit to top 3-4 emotions.
3. "triggers": A list of strings identifying specific stress triggers/emotional patterns. Look for both explicit and hidden patterns (e.g., "Mock Test Performance", "Vast Syllabus", "Lack of Sleep", "Peer Comparison", "Fear of Failure", "Procrastination Guilt", "Family Expectations", "Time Crunch"). Limit to 2-3 triggers.
4. "empathy_note": A short, deeply understanding response (2-3 sentences) validating their specific struggle. Make it feel like it was written by a real, caring counselor. Do not use generic filler. Mention details from their journal.
5. "coping_strategy": 3 specific, highly actionable, personalized coping tips. Tailor these to their target exam and the situations they wrote about. (e.g., if JEE math is stressing them, recommend a specific strategy).
6. "mindfulness_prompt": A custom-tailored 1-minute mindfulness or breathing exercise prompt based on their current stress level and emotions.

JSON Format:
{{
  "stress_level": integer,
  "emotions": ["emotion1", "emotion2", ...],
  "triggers": ["trigger1", "trigger2", ...],
  "empathy_note": "text",
  "coping_strategy": ["strategy1", "strategy2", "strategy3"],
  "mindfulness_prompt": "text"
}}
"""
        raw_response = self._post(prompt, system_instruction=system_instruction, json_response=True)
        try:
            return json.loads(raw_response)
        except json.JSONDecodeError:
            # Fallback parsing in case the output contains markdown formatting inside
            cleaned = raw_response.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            return json.loads(cleaned.strip())

    def generate_companion_response(self, conversation_history, profile, recent_entries):
        """Generate chatbot response with full student context (profile, journals, chat history)."""
        
        # Prepare context about recent student wellness state
        journal_context_parts = []
        for entry in recent_entries[:3]:
            emotions_str = ", ".join(entry["emotions"])
            triggers_str = ", ".join(entry["triggers"])
            journal_context_parts.append(
                f"- Date: {entry['date']} | Mood: {entry['mood']} | Stress: {entry['stress_level']}/10 | "
                f"Emotions: {emotions_str} | Triggers: {triggers_str} | Journal: \"{entry['journal_text'][:150]}...\""
            )
        
        journal_summary = "\n".join(journal_context_parts) if journal_context_parts else "No journal logs yet. The student is just starting."

        system_instruction = (
            f"You are 'Aura', a warm, deeply empathetic, always-available digital mental wellness companion for a student "
            f"preparing for the high-stakes {profile['target_exam']} competitive exam.\n\n"
            f"Student Profile:\n"
            f"- Study Hours: {profile['study_hours']} hours/day\n"
            f"- Declared Main Stressor: {profile['main_stressor']}\n\n"
            f"Student's Recent Journal Entries (for background context):\n"
            f"{journal_summary}\n\n"
            f"Guidelines for Aura:\n"
            f"1. Tone: Deeply supportive, compassionate, validating, and positive. You are their companion, not an academic teacher. Speak to their heart.\n"
            f"2. Context-awareness: Use the profile and journal history to understand their context, but don't force it or repeat it word-for-word. (e.g., if they mention feeling overwhelmed in mock tests, reference that gently if relevant).\n"
            f"3. Guardrails & Safety: If they express feelings of self-harm, severe clinical depression, or suicidal ideation, you must act safely: express deep empathy and care, and provide them with official wellness contact numbers (e.g., national student helplines, suicide hotlines) and urge them to connect with a trusted adult or professional. Do not diagnose or prescribe treatment.\n"
            f"4. Format: Keep responses relatively brief (1-3 paragraphs) so it's readable. Use bullet points or small paragraphs for clarity. Use markdown format nicely.\n"
            f"5. Avoid robotic opening phrases like 'As your AI assistant' or 'As Aura'. Just speak naturally."
        )

        # Build conversation payload for the prompt
        # We formats the chat history to pass into the prompt
        chat_str = ""
        for msg in conversation_history:
            role_label = "Student" if msg["role"] == "user" else "Aura"
            chat_str += f"{role_label}: {msg['content']}\n"
        
        chat_str += "Aura:"

        prompt = f"""
Here is the conversation so far:
{chat_str}

Please reply to the student's latest message, keeping in mind their exam profile and emotional patterns.
"""
        return self._post(prompt, system_instruction=system_instruction, json_response=False)

    def generate_wellness_report(self, journal_entries, profile):
        """Summarize journal history into a structured Markdown dashboard report."""
        if not journal_entries:
            return "No entries logged yet to generate a report. Start writing in your daily journal to see AI insights!"

        # Keep only the last 10 entries to stay within prompt limits
        history_parts = []
        for entry in journal_entries[:10]:
            emotions_str = ", ".join(entry["emotions"])
            triggers_str = ", ".join(entry["triggers"])
            history_parts.append(
                f"- Date: {entry['date']} | Mood: {entry['mood']} | Stress: {entry['stress_level']}/10\n"
                f"  Emotions: {emotions_str}\n"
                f"  Triggers: {triggers_str}\n"
                f"  Journal content snippet: \"{entry['journal_text'][:200]}\""
            )
        
        history_str = "\n\n".join(history_parts)

        system_instruction = (
            "You are an expert student counselor and data analyst. You synthesize psychological logs into clear, "
            "constructive, calming reports. Speak in a warm, encouraging, analytical tone."
        )

        prompt = f"""
Below is a history of mood logs and journaling for a student preparing for the {profile['target_exam']} exam.
They study {profile['study_hours']} hours per day.

Journal History:
{history_str}

Create an emotional pattern synthesis report for the student. Structure the report using the following markdown sections:

### 1. 📈 Stress & Mood Synthesis
Analyze how their stress level and mood have behaved. Look for links between stress peaks and specific events in their journal (e.g. mock test days, burnout, rest days).

### 2. 🔍 Hidden Stress Triggers
Identify patterns the student might not be consciously tracking (e.g., lack of sleep compounding math anxiety, peer pressure causing procrastination guilt, etc.).

### 3. 🎯 Personalized Study-Life Action Plan
Provide 3-4 specific, highly relevant study-life recommendations (e.g., 'Take a 15-minute screen-free walk after physics blocks', 'Stop studying at least 1 hour before bedtime', 'Shift mock test review to mornings when cognitive energy is higher'). Tailor these specifically to the stressors identified.

Make the report visually appealing with clear bullet points, warm tone, and actionable insights. Do not include introductory text, start directly with the sections.
"""
        return self._post(prompt, system_instruction=system_instruction, json_response=False)
