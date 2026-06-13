# Custom CSS to apply premium calming styles to the Streamlit app

APP_CSS = """
<style>
/* Calming aesthetic configuration */
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&family=Inter:wght@300;400;500;600&display=swap');

/* Set font family */
html, body, [class*="css"], .stMarkdown {
    font-family: 'Inter', sans-serif;
}

h1, h2, h3, .stHeading {
    font-family: 'Outfit', sans-serif;
    font-weight: 600;
    color: #2D3748;
}

/* Glassmorphism Cards */
.wellness-card {
    background: rgba(255, 255, 255, 0.7);
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    border: 1px solid rgba(226, 232, 240, 0.8);
    border-radius: 16px;
    padding: 24px;
    margin-bottom: 20px;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.02);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.wellness-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05), 0 4px 6px -2px rgba(0, 0, 0, 0.02);
}

.wellness-card-accent {
    border-left: 6px solid #805AD5 !important;
}

.wellness-card-sage {
    border-left: 6px solid #319795 !important;
}

.wellness-card-blue {
    border-left: 6px solid #3182CE !important;
}

/* Customized Metric Layout */
.metric-container {
    display: flex;
    justify-content: space-between;
    margin-bottom: 20px;
}

.metric-box {
    flex: 1;
    background: white;
    border-radius: 12px;
    padding: 16px;
    text-align: center;
    border: 1px solid #E2E8F0;
    margin: 0 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.02);
}

.metric-value {
    font-size: 24px;
    font-weight: 800;
    color: #4A5568;
    margin-top: 4px;
}

.metric-label {
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: #A0AEC0;
}

/* Calming background overrides if in light mode */
.stApp {
    background: linear-gradient(135deg, #F7FAFC 0%, #EDF2F7 50%, #E2E8F0 100%);
}

/* Sidebar styling overrides */
section[data-testid="stSidebar"] {
    background-color: #1A202C !important;
}

section[data-testid="stSidebar"] h1, 
section[data-testid="stSidebar"] h2, 
section[data-testid="stSidebar"] h3, 
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] label {
    color: #EDF2F7 !important;
}

/* Buttons custom styling */
div.stButton > button {
    background-color: #6B46C1;
    color: white;
    border-radius: 10px;
    padding: 8px 20px;
    border: none;
    font-weight: 600;
    transition: background-color 0.2s;
}

div.stButton > button:hover {
    background-color: #553C9A;
    color: white;
}

/* Custom Tag bubbles */
.tag {
    display: inline-block;
    background-color: #E2E8F0;
    color: #4A5568;
    padding: 4px 10px;
    border-radius: 9999px;
    font-size: 12px;
    font-weight: 500;
    margin-right: 6px;
    margin-bottom: 6px;
}

.tag-emotion {
    background-color: #EBF8FF;
    color: #2B6CB0;
}

.tag-trigger {
    background-color: #FFF5F5;
    color: #C53030;
}

/* Chat bubble aesthetics */
div[data-testid="chatAvatarIcon-user"] {
    background-color: #805AD5 !important;
}

div[data-testid="chatAvatarIcon-assistant"] {
    background-color: #319795 !important;
}

</style>
"""

# HTML/CSS/JS Component for guided box breathing
BREATHING_HTML = """
<!DOCTYPE html>
<html>
<head>
<style>
body {
    background: transparent;
    margin: 0;
    padding: 0;
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100vh;
    font-family: 'Outfit', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    overflow: hidden;
}

.breathing-card {
    text-align: center;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    width: 100%;
    height: 100%;
}

.bubble-container {
    position: relative;
    width: 250px;
    height: 250px;
    display: flex;
    justify-content: center;
    align-items: center;
}

.breathing-circle {
    width: 140px;
    height: 140px;
    border-radius: 50%;
    background-color: rgba(107, 70, 193, 0.6);
    box-shadow: 0 0 30px rgba(107, 70, 193, 0.4);
    transition: transform 4s cubic-bezier(0.4, 0, 0.2, 1), background-color 4s ease, box-shadow 4s ease;
    display: flex;
    justify-content: center;
    align-items: center;
}

.text-container {
    position: absolute;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    pointer-events: none;
}

.breathing-text {
    font-size: 22px;
    font-weight: 700;
    color: #2D3748;
    text-shadow: 0 2px 4px rgba(255,255,255,0.8);
    margin: 0;
}

.breathing-timer {
    font-size: 36px;
    font-weight: 800;
    color: #1A202C;
    margin-top: 4px;
    text-shadow: 0 2px 4px rgba(255,255,255,0.8);
}

.instruction-hint {
    margin-top: 25px;
    font-size: 14px;
    color: #718096;
    font-weight: 500;
    max-width: 300px;
    line-height: 1.4;
}
</style>
</head>
<body>

<div class="breathing-card">
    <div class="bubble-container">
        <div id="breathing-circle" class="breathing-circle"></div>
        <div class="text-container">
            <div id="breathing-text" class="breathing-text">Inhale...</div>
            <div id="breathing-timer" class="breathing-timer">4</div>
        </div>
    </div>
    <div id="breathing-hint" class="instruction-hint">Box Breathing: Calms the nervous system by aligning cycles.</div>
</div>

<script>
const circle = document.getElementById('breathing-circle');
const text = document.getElementById('breathing-text');
const timer = document.getElementById('breathing-timer');
const hint = document.getElementById('breathing-hint');

const phases = [
  { text: "Breathe In", duration: 4, action: "inhale", hint: "Fill your lungs slowly with fresh energy." },
  { text: "Hold", duration: 4, action: "hold-in", hint: "Keep your breath suspended. Relax your shoulders." },
  { text: "Breathe Out", duration: 4, action: "exhale", hint: "Slowly release all tension, doubts, and fatigue." },
  { text: "Hold", duration: 4, action: "hold-out", hint: "Rest in the empty stillness before the next breath." }
];

let phaseIndex = 0;
let timeLeft = phases[phaseIndex].duration;

function updateBreathe() {
  const current = phases[phaseIndex];
  text.innerText = current.text;
  timer.innerText = timeLeft;
  hint.innerText = current.hint;
  
  if (current.action === "inhale") {
    circle.style.transform = "scale(1.6)";
    circle.style.backgroundColor = "rgba(128, 90, 213, 0.75)"; // Calming Purple
    circle.style.boxShadow = "0 0 45px rgba(128, 90, 213, 0.6)";
  } else if (current.action === "hold-in") {
    circle.style.transform = "scale(1.6)";
    circle.style.backgroundColor = "rgba(49, 151, 149, 0.75)"; // Calming Sage/Teal
    circle.style.boxShadow = "0 0 45px rgba(49, 151, 149, 0.6)";
  } else if (current.action === "exhale") {
    circle.style.transform = "scale(1.0)";
    circle.style.backgroundColor = "rgba(49, 130, 206, 0.75)"; // Soothing Blue
    circle.style.boxShadow = "0 0 45px rgba(49, 130, 206, 0.6)";
  } else if (current.action === "hold-out") {
    circle.style.transform = "scale(1.0)";
    circle.style.backgroundColor = "rgba(113, 128, 150, 0.75)"; // Peaceful Grey-Slate
    circle.style.boxShadow = "0 0 45px rgba(113, 128, 150, 0.6)";
  }
  
  timeLeft--;
  if (timeLeft < 0) {
    phaseIndex = (phaseIndex + 1) % phases.length;
    timeLeft = phases[phaseIndex].duration;
  }
}

// Tick every second
setInterval(updateBreathe, 1000);

// Init execution
updateBreathe();
</script>

</body>
</html>
"""
