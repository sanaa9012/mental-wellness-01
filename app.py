import streamlit as st
import os
import sqlite3
import pandas as pd
import altair as alt
from datetime import datetime, date
import html

# Import custom modules
import database
import styles
from gemini_client import GeminiClient

# Page configuration
st.set_page_config(
    page_title="Aura - Student Exam Wellness Companion",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject custom CSS
st.markdown(styles.APP_CSS, unsafe_allow_html=True)

# Initialize Database
database.init_db()

# Read API key from environment if available
env_api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")

# Initialize session state variables
if "api_key" not in st.session_state:
    st.session_state.api_key = env_api_key or ""
if "page" not in st.session_state:
    st.session_state.page = "dashboard"
if "report_cache" not in st.session_state:
    st.session_state.report_cache = ""
if "refresh_report" not in st.session_state:
    st.session_state.refresh_report = True

# Helper to read from .env if present (fallback)
def load_env_file():
    if os.path.exists(".env"):
        try:
            with open(".env", "r") as f:
                for line in f:
                    if "=" in line and not line.startswith("#"):
                        key, val = line.strip().split("=", 1)
                        if key.strip() in ["GEMINI_API_KEY", "GOOGLE_API_KEY"]:
                            return val.strip()
        except Exception:
            pass
    return None

if not st.session_state.api_key:
    dot_env_key = load_env_file()
    if dot_env_key:
        st.session_state.api_key = dot_env_key

# Instantiate Gemini Client
client = GeminiClient(api_key=st.session_state.api_key)

# ----------------- SIDEBAR -----------------
st.sidebar.markdown("<h2 style='text-align: center; color: white; margin-top: 0;'>🧠 Aura</h2>", unsafe_allow_html=True)
st.sidebar.markdown("<p style='text-align: center; color: #A0AEC0; font-size: 14px;'>Exam Wellness Companion</p>", unsafe_allow_html=True)
st.sidebar.markdown("---")

# Main Navigation
st.sidebar.subheader("Navigation")
nav_choice = st.sidebar.radio(
    "Go to:",
    ["📊 Dashboard & Trends", "📝 Daily Journal & Mood Logs", "💬 AI Coping Companion", "🧘 Mindfulness & Breathing"],
    label_visibility="collapsed"
)

# Map radio choices to page names
page_map = {
    "📊 Dashboard & Trends": "dashboard",
    "📝 Daily Journal & Mood Logs": "journal",
    "💬 AI Coping Companion": "companion",
    "🧘 Mindfulness & Breathing": "mindfulness"
}
st.session_state.page = page_map[nav_choice]

st.sidebar.markdown("---")

# Profile Settings
st.sidebar.subheader("👤 Exam Profile")
profile = database.get_profile()

target_exam = st.sidebar.selectbox(
    "Target Exam:",
    ["JEE (Main/Advanced)", "NEET", "UPSC (Civil Services)", "GATE", "CAT", "CUET", "Board Exams (10th/12th)", "Other Competitive Exam"],
    index=["JEE (Main/Advanced)", "NEET", "UPSC (Civil Services)", "GATE", "CAT", "CUET", "Board Exams (10th/12th)", "Other Competitive Exam"].index(profile["target_exam"]) if profile["target_exam"] in ["JEE (Main/Advanced)", "NEET", "UPSC (Civil Services)", "GATE", "CAT", "CUET", "Board Exams (10th/12th)", "Other Competitive Exam"] else 0
)

study_hours = st.sidebar.slider(
    "Daily Study Hours:",
    min_value=1.0,
    max_value=16.0,
    value=float(profile["study_hours"]),
    step=0.5
)

main_stressor = st.sidebar.selectbox(
    "Main Stress Trigger:",
    ["Time Management", "Syllabus Coverage", "Mock Test Scores", "Peer Pressure / Comparison", "Fear of Failure", "Lack of Sleep / Fatigue", "Family Expectations", "Unclear Career Goals"],
    index=["Time Management", "Syllabus Coverage", "Mock Test Scores", "Peer Pressure / Comparison", "Fear of Failure", "Lack of Sleep / Fatigue", "Family Expectations", "Unclear Career Goals"].index(profile["main_stressor"]) if profile["main_stressor"] in ["Time Management", "Syllabus Coverage", "Mock Test Scores", "Peer Pressure / Comparison", "Fear of Failure", "Lack of Sleep / Fatigue", "Family Expectations", "Unclear Career Goals"] else 0
)

if st.sidebar.button("💾 Save Profile", use_container_width=True):
    database.save_profile(target_exam, study_hours, main_stressor)
    st.sidebar.success("Profile saved successfully!")
    st.session_state.refresh_report = True
    st.rerun()

st.sidebar.markdown("---")

# API Configuration
st.sidebar.subheader("🔑 API Setup")
api_input = st.sidebar.text_input(
    "Gemini API Key:",
    value=st.session_state.api_key,
    type="password",
    help="Provide your Gemini API key from Google AI Studio. It is kept securely in session memory."
)

if api_input != st.session_state.api_key:
    st.session_state.api_key = api_input
    client = GeminiClient(api_key=api_input)
    st.sidebar.success("API Key updated!")
    st.rerun()

if not st.session_state.api_key:
    st.sidebar.warning("⚠️ Gemini API Key is missing. Please enter one to enable Generative AI features (Journal Analysis, Chat Companion, and Wellness Reports).")

st.sidebar.markdown(
    "<br><br><div style='text-align: center; color: #718096; font-size: 11px;'>Aura Companion v1.0.0<br>Made with 💜 for students</div>",
    unsafe_allow_html=True
)

# ----------------- PAGE ROUTER -----------------

if st.session_state.page == "dashboard":
    st.markdown("<h1 style='margin-bottom: 5px;'>📊 Dashboard & Wellness Trends</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #4A5568;'>Monitor your emotional metrics, stress patterns, and view personalized AI-generated reports.</p>", unsafe_allow_html=True)
    st.markdown("---")

    # Load all entries and profile
    all_entries = database.get_journal_entries(limit=500)
    profile_data = database.get_profile()

    if not all_entries:
        # Beautiful empty state
        escaped_exam = html.escape(profile_data['target_exam'])
        st.markdown(
            f"""
            <div class="wellness-card wellness-card-accent" style="text-align: center; padding: 40px;">
                <h2 style="color: #6B46C1; margin-top: 0;">Welcome to Aura, your wellness companion! 🌟</h2>
                <p style="font-size: 16px; color: #4D5568; max-width: 600px; margin: 0 auto 24px auto;">
                    Preparing for <b>{escaped_exam}</b> requires tremendous dedication. However, your mental health is
                    just as important as your exam score. Aura is designed to analyze your daily journal logs to reveal hidden
                    stress triggers, provide direct coping mechanisms, and support you along the way.
                </p>
                <p style="font-weight: 600; color: #2D3748;">To get started, navigate to the 📝 Daily Journal tab and log your first entry.</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        # ── TIMEFRAME FILTER ──────────────────────────────────────
        filter_col, spacer = st.columns([2, 5])
        with filter_col:
            timeframe = st.selectbox(
                "📅 View Period:",
                ["All Time", "Last 30 Days", "Last 7 Days"],
                label_visibility="visible"
            )

        # Filter entries based on timeframe selection
        df_all = pd.DataFrame(all_entries)
        df_all["date_parsed"] = pd.to_datetime(df_all["date"])
        today = pd.Timestamp.now().normalize()

        if timeframe == "Last 7 Days":
            cutoff = today - pd.Timedelta(days=7)
            df = df_all[df_all["date_parsed"] >= cutoff].copy()
        elif timeframe == "Last 30 Days":
            cutoff = today - pd.Timedelta(days=30)
            df = df_all[df_all["date_parsed"] >= cutoff].copy()
        else:
            df = df_all.copy()

        if df.empty:
            st.info(f"No journal entries found for {timeframe}. Try selecting a wider time range.")
        else:
            # Compute aggregate stats
            avg_stress = df["stress_level"].mean()
            max_stress = df["stress_level"].max()
            total_entries = len(df)
            most_common_mood = df["mood"].value_counts().index[0]

            all_triggers = []
            for triggers_list in df["triggers"]:
                if isinstance(triggers_list, list):
                    all_triggers.extend(triggers_list)
            all_emotions = []
            for emotions_list in df["emotions"]:
                if isinstance(emotions_list, list):
                    all_emotions.extend(emotions_list)

            top_trigger = pd.Series(all_triggers).value_counts().index[0] if all_triggers else "None detected yet"
            top_emotion = pd.Series(all_emotions).value_counts().index[0] if all_emotions else "N/A"

            # ── STRESS ALERT BANNER ───────────────────────────────
            if avg_stress >= 7.5:
                st.markdown(
                    """
                    <div role="alert" aria-live="assertive" style="background:#FFF0F0; border-left:6px solid #9B1C1C;
                        border-radius:10px; padding:16px 20px; margin-bottom:20px; display:flex; align-items:center; gap:12px;">
                        <span style="font-size:28px;">🚨</span>
                        <div>
                            <strong style="color:#9B1C1C; font-size:15px;">High Stress Period Detected</strong>
                            <p style="margin:4px 0 0 0; color:#7B1C1C; font-size:13px;">
                                Your average stress is critically high. Consider taking a longer study break today and
                                talking with a trusted person. Tap 🧘 Mindfulness for immediate relief exercises.
                            </p>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            elif avg_stress >= 5.5:
                st.markdown(
                    """
                    <div role="alert" aria-live="polite" style="background:#FFFBEB; border-left:6px solid #92400E;
                        border-radius:10px; padding:16px 20px; margin-bottom:20px; display:flex; align-items:center; gap:12px;">
                        <span style="font-size:28px;">⚠️</span>
                        <div>
                            <strong style="color:#92400E; font-size:15px;">Moderate Stress Detected</strong>
                            <p style="margin:4px 0 0 0; color:#78350F; font-size:13px;">
                                You're managing but showing signs of sustained pressure. Make sure you're taking
                                regular breaks and staying hydrated. Small wins matter — celebrate them!
                            </p>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    """
                    <div role="status" aria-live="polite" style="background:#F0FDF4; border-left:6px solid #166534;
                        border-radius:10px; padding:16px 20px; margin-bottom:20px; display:flex; align-items:center; gap:12px;">
                        <span style="font-size:28px;">✅</span>
                        <div>
                            <strong style="color:#166534; font-size:15px;">Stress is Well Managed</strong>
                            <p style="margin:4px 0 0 0; color:#14532D; font-size:13px;">
                                Great work! Your stress levels look balanced for this period.
                                Keep up the regular journaling and healthy study habits.
                            </p>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            # ── METRICS ROW ───────────────────────────────────────
            col1, col2, col3, col4, col5 = st.columns(5)
            escaped_exam = html.escape(profile_data['target_exam'])
            escaped_mood = html.escape(most_common_mood)
            escaped_trigger = html.escape(top_trigger)
            escaped_emotion = html.escape(top_emotion)
            stress_text_color = "#9B1C1C" if avg_stress >= 7.5 else "#92400E" if avg_stress >= 5.5 else "#166534"
            stress_bg = "#FFF0F0" if avg_stress >= 7.5 else "#FFFBEB" if avg_stress >= 5.5 else "#F0FDF4"

            with col1:
                st.markdown(f"""
                <div class="wellness-card wellness-card-accent" style="padding:14px; text-align:center;">
                    <div class="metric-label">Target Exam</div>
                    <div class="metric-value" style="font-size:16px;">{escaped_exam}</div>
                </div>""", unsafe_allow_html=True)
            with col2:
                st.markdown(f"""
                <div class="wellness-card wellness-card-sage" style="padding:14px; text-align:center; background:{stress_bg};">
                    <div class="metric-label">Avg Stress ({timeframe})</div>
                    <div class="metric-value" style="color:{stress_text_color};">{avg_stress:.1f} / 10</div>
                </div>""", unsafe_allow_html=True)
            with col3:
                st.markdown(f"""
                <div class="wellness-card wellness-card-blue" style="padding:14px; text-align:center;">
                    <div class="metric-label">Dominant Mood</div>
                    <div class="metric-value" style="font-size:15px;">{escaped_mood}</div>
                </div>""", unsafe_allow_html=True)
            with col4:
                st.markdown(f"""
                <div class="wellness-card" style="padding:14px; text-align:center; border-left:6px solid #6B46C1;">
                    <div class="metric-label">Top Trigger</div>
                    <div class="metric-value" style="font-size:14px;" title="{escaped_trigger}">{escaped_trigger}</div>
                </div>""", unsafe_allow_html=True)
            with col5:
                st.markdown(f"""
                <div class="wellness-card" style="padding:14px; text-align:center; border-left:6px solid #319795;">
                    <div class="metric-label">Entries Logged</div>
                    <div class="metric-value">{total_entries}</div>
                </div>""", unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # ── TRIGGER-SPECIFIC INSTANT TIP ─────────────────────
            TRIGGER_TIPS = {
                "Mock Test Performance": "💡 After each mock, spend 10 min reviewing *only* wrong answers — not full re-reads. Pattern spotting is more efficient than re-solving.",
                "Mock Test": "💡 After each mock, spend 10 min reviewing *only* wrong answers — not full re-reads. Pattern spotting is more efficient than re-solving.",
                "Time Management": "💡 Try the 2-minute rule: if a question takes >2 mins, mark it, move on, return at the end. You preserve flow and collect easy marks first.",
                "Syllabus Coverage": "💡 Break the syllabus into 4-day sprint blocks. Completing a sprint gives a dopamine hit that fights overwhelm better than looking at the full list.",
                "Lack of Sleep / Fatigue": "💡 A 20-min nap between 2–4 PM boosts alertness for 3 hours. Protect your sleep window — it's not optional, it's a performance tool.",
                "Peer Pressure / Comparison": "💡 Your journey is a different route, not a slower one. Block peer score updates and focus on your own weekly delta — did you improve from last week?",
                "Family Expectations": "💡 Schedule one 15-min weekly check-in with family to update them on progress. Structure lowers surprise anxiety from both sides.",
                "Fear of Failure": "💡 Reframe: 'What's the worst realistic outcome, and can I survive it?' Usually yes. Fear loses power when you've rehearsed surviving it.",
                "Procrastination Guilt": "💡 Start with 5-min study blocks. Often you'll continue past 5 mins. The activation energy is the barrier, not the work itself.",
                "Unclear Career Goals": "💡 Pause one evening this week. Write down 3 futures you'd be okay with — gives the brain multiple safe paths to work toward.",
            }
            tip_text = None
            for key in TRIGGER_TIPS:
                if key.lower() in top_trigger.lower():
                    tip_text = TRIGGER_TIPS[key]
                    break
            if not tip_text and top_trigger != "None detected yet":
                tip_text = f"💡 You identified **{html.escape(top_trigger)}** as your main stressor. Log more entries so Aura can build personalized tips for you."

            if tip_text:
                st.markdown(
                    f"""
                    <div class="wellness-card wellness-card-blue" style="background:#EFF6FF; padding:14px 18px; margin-bottom:20px;">
                        <strong style="color:#1E40AF; font-size:13px; text-transform:uppercase; letter-spacing:.05em;">
                            🎯 Aura's Tip — Based on your top trigger: {html.escape(top_trigger)}
                        </strong>
                        <p style="margin:6px 0 0 0; color:#1E3A5F; font-size:14px;">{tip_text}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            # ── CHARTS ────────────────────────────────────────────
            df_plot = df.sort_values("date_parsed")

            left_col, right_col = st.columns([3, 2])

            with left_col:
                st.markdown("<h3 style='margin-top:0;'>📈 Stress Level Over Time</h3>", unsafe_allow_html=True)

                base = alt.Chart(df_plot).encode(
                    x=alt.X("date_parsed:T", title="Date", axis=alt.Axis(format="%b %d", labelAngle=-30))
                )
                stress_line = base.mark_line(
                    point=True, color="#6B46C1", strokeWidth=2.5
                ).encode(
                    y=alt.Y("stress_level:Q", title="Stress Level (1–10)", scale=alt.Scale(domain=[0, 10])),
                    tooltip=[
                        alt.Tooltip("date_parsed:T", title="Date", format="%b %d"),
                        alt.Tooltip("mood:N", title="Mood"),
                        alt.Tooltip("stress_level:Q", title="Stress")
                    ]
                )
                # Rolling 3-day average line if enough entries
                if len(df_plot) >= 3:
                    rolling_df = df_plot.copy()
                    rolling_df["rolling_avg"] = rolling_df["stress_level"].rolling(3, min_periods=1).mean()
                    avg_line = alt.Chart(rolling_df).mark_line(
                        strokeDash=[4, 2], color="#D6BCFA", strokeWidth=2
                    ).encode(
                        x=alt.X("date_parsed:T"),
                        y=alt.Y("rolling_avg:Q")
                    )
                    chart = (stress_line + avg_line).properties(height=280).interactive()
                else:
                    chart = stress_line.properties(height=280).interactive()

                st.altair_chart(chart, use_container_width=True)
                if len(df_plot) >= 3:
                    st.caption("Dashed line = 3-entry rolling average")

            with right_col:
                st.markdown("<h3 style='margin-top:0;'>🔥 Top Stress Triggers</h3>", unsafe_allow_html=True)
                if all_triggers:
                    trigger_counts = pd.Series(all_triggers).value_counts().head(7).reset_index()
                    trigger_counts.columns = ["Trigger", "Count"]
                    trigger_chart = alt.Chart(trigger_counts).mark_bar(
                        cornerRadiusTopRight=4, cornerRadiusBottomRight=4
                    ).encode(
                        x=alt.X("Count:Q", title="Occurrences", axis=alt.Axis(tickMinStep=1)),
                        y=alt.Y("Trigger:N", sort="-x", title=""),
                        color=alt.Color(
                            "Count:Q",
                            legend=None,
                            scale=alt.Scale(scheme="purples")
                        ),
                        tooltip=["Trigger:N", "Count:Q"]
                    ).properties(height=280)
                    st.altair_chart(trigger_chart, use_container_width=True)
                else:
                    st.info("No triggers detected yet. Log more entries.")

            # ── MOOD DISTRIBUTION ─────────────────────────────────
            st.markdown("<h3 style='margin-top:0;'>😊 Mood Distribution</h3>", unsafe_allow_html=True)
            mood_counts = df["mood"].value_counts().reset_index()
            mood_counts.columns = ["Mood", "Count"]
            mood_chart = alt.Chart(mood_counts).mark_arc(innerRadius=60, outerRadius=110).encode(
                theta=alt.Theta("Count:Q"),
                color=alt.Color("Mood:N", scale=alt.Scale(scheme="purplebluegreen")),
                tooltip=["Mood:N", "Count:Q"]
            ).properties(height=260)
            mood_text = alt.Chart(mood_counts).mark_text(radius=140, fontSize=11).encode(
                theta=alt.Theta("Count:Q", stack=True),
                text=alt.Text("Mood:N"),
                color=alt.value("#4A5568")
            )
            mood_col, emo_col = st.columns([1, 1])
            with mood_col:
                st.altair_chart(mood_chart, use_container_width=True)
            with emo_col:
                st.markdown("<h3 style='margin-top:0;'>🧠 Top Emotions Logged</h3>", unsafe_allow_html=True)
                if all_emotions:
                    emo_counts = pd.Series(all_emotions).value_counts().head(8).reset_index()
                    emo_counts.columns = ["Emotion", "Count"]
                    emo_chart = alt.Chart(emo_counts).mark_bar(
                        cornerRadiusTopLeft=4, cornerRadiusTopRight=4
                    ).encode(
                        x=alt.X("Emotion:N", sort="-y", title="", axis=alt.Axis(labelAngle=-30)),
                        y=alt.Y("Count:Q", title="Occurrences", axis=alt.Axis(tickMinStep=1)),
                        color=alt.Color("Count:Q", legend=None, scale=alt.Scale(scheme="blues")),
                        tooltip=["Emotion:N", "Count:Q"]
                    ).properties(height=260)
                    st.altair_chart(emo_chart, use_container_width=True)

            # ── RECENT ENTRIES TIMELINE ───────────────────────────
            st.markdown("---")
            st.markdown("<h3>📋 Recent Entries at a Glance</h3>", unsafe_allow_html=True)
            recent_5 = df.sort_values("date_parsed", ascending=False).head(5)
            for _, row in recent_5.iterrows():
                stress = row["stress_level"]
                s_color = "#9B1C1C" if stress >= 8 else "#92400E" if stress >= 5 else "#166534"
                s_bg = "#FFF0F0" if stress >= 8 else "#FFFBEB" if stress >= 5 else "#F0FDF4"
                mood_str = html.escape(str(row["mood"]))
                date_str = html.escape(str(row["date"]))
                snippet = html.escape(str(row["journal_text"])[:120]) + "..."
                triggers_str = html.escape(", ".join(row["triggers"]) if isinstance(row["triggers"], list) else "")
                st.markdown(
                    f"""
                    <div style="display:flex; align-items:flex-start; gap:14px; padding:12px 0;
                                border-bottom:1px solid #E2E8F0; margin-bottom:4px;">
                        <div style="min-width:80px; text-align:center; padding:8px 10px;
                                    background:{s_bg}; border-radius:10px;">
                            <div style="font-size:20px; font-weight:800; color:{s_color};">{stress}</div>
                            <div style="font-size:10px; color:{s_color}; text-transform:uppercase;">stress</div>
                        </div>
                        <div style="flex:1;">
                            <div style="font-weight:600; color:#2D3748; font-size:13px;">{date_str} &nbsp;·&nbsp; {mood_str}</div>
                            <div style="color:#718096; font-size:13px; margin-top:3px; font-style:italic;">"{snippet}"</div>
                            <div style="margin-top:5px; font-size:12px; color:#6B46C1;">🔍 {triggers_str if triggers_str else 'No triggers detected'}</div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            # ── AI WELLNESS INSIGHTS REPORT ───────────────────────
            st.markdown("---")
            st.markdown("### 📝 AI-Generated Wellness & Emotional Analysis")
            st.markdown("Get a long-term analysis of your mental logs, detecting subconscious patterns and recommending specific study-life changes.")

            if not st.session_state.api_key:
                st.warning("Please provide your Gemini API key in the sidebar to generate your wellness report.")
            else:
                if st.session_state.refresh_report or not st.session_state.report_cache:
                    with st.spinner("Aura is analyzing your journal history and synthesizing insights..."):
                        try:
                            history = sorted(all_entries, key=lambda x: x["date"])
                            report = client.generate_wellness_report(history, profile_data)
                            st.session_state.report_cache = report
                            st.session_state.refresh_report = False
                        except Exception as e:
                            st.error(f"Error generating report: {e}")

                if st.session_state.report_cache:
                    with st.container(border=True):
                        st.markdown(st.session_state.report_cache)

                    if st.button("🔄 Regenerate Report"):
                        st.session_state.refresh_report = True
                        st.rerun()

elif st.session_state.page == "journal":
    st.markdown("<h1 style='margin-bottom: 5px;'>📝 Daily Journal & Mood Logger</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #4A5568;'>Log your daily notes, study progress, or emotional stress. Aura will analyze your text to uncover patterns.</p>", unsafe_allow_html=True)
    st.markdown("---")
    
    col_entry, col_history = st.columns([1, 1])
    
    with col_entry:
        st.markdown("<h3 style='margin-top:0;'>Log Today's Entry</h3>", unsafe_allow_html=True)
        
        # Form inputs
        entry_date = st.date_input("Date:", date.today())
        
        mood_opts = {
            "🚀 Motivated / Confident": "🚀 Motivated",
            "🙂 Calm / Peaceful": "🙂 Calm",
            "😐 Neutral / Okay": "😐 Neutral",
            "😕 Anxious / Worried": "😕 Anxious",
            "😴 Exhausted / Burned Out": "😴 Exhausted",
            "😭 Severe Stress / Panic": "😭 Stressed"
        }
        selected_mood_label = st.radio(
            "How is your overall mood today?",
            list(mood_opts.keys())
        )
        selected_mood = mood_opts[selected_mood_label]
        
        journal_text = st.text_area(
            "Journal entry (Write freely about your prep, mock tests, time pressure, doubts, or wins):",
            placeholder="Today I solved 40 physics questions but felt stuck on calculus... I'm worried I won't finish the NEET syllabus in time. My classmates seem to be scoring higher...",
            height=200
        )
        
        submit_btn = st.button("✨ Analyze & Log Entry", use_container_width=True)
        
        if submit_btn:
            if not journal_text.strip():
                st.error("Please write a journal entry first.")
            elif not st.session_state.api_key:
                st.error("Gemini API Key is required. Please set it in the sidebar.")
            else:
                with st.spinner("Aura is listening, analyzing and preparing your coping strategies..."):
                    try:
                        profile_data = database.get_profile()
                        
                        # AI Analysis
                        analysis = client.analyze_journal_entry(
                            journal_text=journal_text,
                            mood_emoji=selected_mood,
                            target_exam=profile_data["target_exam"],
                            current_stressor=profile_data["main_stressor"]
                        )
                        
                        # Save to db
                        database.add_journal_entry(
                            date_str=entry_date.strftime("%Y-%m-%d"),
                            mood=selected_mood,
                            journal_text=journal_text,
                            stress_level=analysis["stress_level"],
                            emotions=analysis["emotions"],
                            triggers=analysis["triggers"],
                            empathy_note=analysis["empathy_note"],
                            coping_strategy="\n".join([f"- {s}" for s in analysis["coping_strategy"]]),
                            mindfulness_prompt=analysis["mindfulness_prompt"]
                        )
                        
                        st.session_state.refresh_report = True
                        st.success("Entry logged successfully!")
                        st.session_state.latest_analysis = analysis
                    except Exception as e:
                        st.error(f"Error analyzing entry: {e}")
        
        # Display the result of the LATEST log submission immediately below
        if "latest_analysis" in st.session_state:
            ans = st.session_state.latest_analysis
            st.markdown("---")
            st.markdown("### 🌟 Quick Insights on Your Entry")
            
            # Stress level color coding
            stress_color = "#2F855A" if ans['stress_level'] <= 4 else "#DD6B20" if ans['stress_level'] <= 7 else "#C53030"
            st.markdown(f"**Calculated Stress Load:** <span style='font-size: 20px; font-weight:800; color:{stress_color};'>{ans['stress_level']} / 10</span>", unsafe_allow_html=True)
            
            # Emotions tags
            emotions_html = "".join([f"<span class='tag tag-emotion'>{html.escape(e)}</span>" for e in ans["emotions"]])
            st.markdown(f"**Detected Emotions:** {emotions_html}", unsafe_allow_html=True)
            
            # Triggers tags
            triggers_html = "".join([f"<span class='tag tag-trigger'>{html.escape(t)}</span>" for t in ans["triggers"]])
            st.markdown(f"**Stress Triggers:** {triggers_html}", unsafe_allow_html=True)
            
            # Empathy block
            escaped_empathy = html.escape(ans['empathy_note'])
            st.markdown(
                f"""
                <div class="wellness-card wellness-card-accent" style="margin-top: 15px;">
                    <p style="font-style: italic; color: #4A5568; margin: 0;">"{escaped_empathy}"</p>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            # Coping tips
            st.markdown("**Personalized Coping Strategies:**")
            for tip in ans["coping_strategy"]:
                st.markdown(f"- {tip}")
                
            # Mindfulness block
            escaped_mindfulness = html.escape(ans['mindfulness_prompt'])
            st.markdown(
                f"""
                <div class="wellness-card wellness-card-sage" style="margin-top: 15px; background-color: #F0FDF4;">
                    <h5 style="margin-top: 0; color: #234E52;">🧘 Suggested Mindfulness Exercise</h5>
                    <p style="color: #2C5282; margin: 0; font-size: 14px;">{escaped_mindfulness}</p>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            if st.button("Clear Response View"):
                del st.session_state.latest_analysis
                st.rerun()

    with col_history:
        st.markdown("<h3 style='margin-top:0;'>Past Journal Logs</h3>", unsafe_allow_html=True)
        past_entries = database.get_journal_entries()
        
        if not past_entries:
            st.info("No logs written yet. Write down how you are feeling in the left pane.")
        else:
            for item in past_entries:
                mood_indicator = item["mood"]
                stress_lvl = item["stress_level"]
                # Color code header stress
                st_color = "#2F855A" if stress_lvl <= 4 else "#DD6B20" if stress_lvl <= 7 else "#C53030"
                
                expander_label = f"📅 {item['date']} | Mood: {mood_indicator} | Stress: {stress_lvl}/10"
                
                with st.expander(expander_label):
                    st.markdown(f"**Journal Log:**")
                    escaped_journal = html.escape(item['journal_text'])
                    st.markdown(f"<p style='color: #4A5568; font-style: italic; padding: 10px; background:#F8FAFC; border-radius:8px;'>{escaped_journal}</p>", unsafe_allow_html=True)
                    
                    # Tag items
                    e_tags = "".join([f"<span class='tag tag-emotion'>{html.escape(e)}</span>" for e in item["emotions"]])
                    t_tags = "".join([f"<span class='tag tag-trigger'>{html.escape(t)}</span>" for t in item["triggers"]])
                    st.markdown(f"**Identified States:** {e_tags}{t_tags}", unsafe_allow_html=True)
                    
                    st.markdown("---")
                    st.markdown(f"**Aura's Analysis:**")
                    escaped_empathy_note = html.escape(item['empathy_note'])
                    st.markdown(f"<p style='color: #4A5568;'><b>Empathy note:</b> {escaped_empathy_note}</p>", unsafe_allow_html=True)
                    
                    st.markdown("**Personalized Coping Advice:**")
                    st.markdown(item["coping_strategy"])
                    
                    if item["mindfulness_prompt"]:
                        escaped_mindfulness_prompt = html.escape(item['mindfulness_prompt'])
                        st.markdown(
                            f"""
                            <div class="wellness-card wellness-card-sage" style="padding: 12px; margin-top: 10px; background-color: #F0FDF4; border-radius: 8px;">
                                <span style="font-weight:600; font-size: 13px; color:#234E52;">🧘 Quick Mindfulness Step:</span>
                                <p style="color:#2C5282; margin: 4px 0 0 0; font-size:13px;">{escaped_mindfulness_prompt}</p>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                    
                    # Action row
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.button(f"🗑️ Delete Entry", key=f"del_{item['id']}"):
                        database.delete_journal_entry(item["id"])
                        st.session_state.refresh_report = True
                        st.success("Entry deleted successfully.")
                        st.rerun()

elif st.session_state.page == "companion":
    st.markdown("<h1 style='margin-bottom: 5px;'>💬 Talk with Aura</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #4A5568;'>Aura is your empathetic, always-available digital companion. Chat about your exam stress, study blocks, or self-doubt.</p>", unsafe_allow_html=True)
    st.markdown("---")
    
    # Check for API key
    if not st.session_state.api_key:
        st.warning("Please configure your Gemini API Key in the sidebar to talk with Aura.")
    else:
        # Load conversation history from database
        history = database.get_chat_history()
        
        # Sidebar control inside chatbot tab for ease of access
        col_header, col_clear = st.columns([5, 1])
        with col_clear:
            if st.button("🗑️ Clear Chat History", use_container_width=True):
                database.clear_chat_history()
                st.success("Conversation cleared!")
                st.rerun()
                
        with col_header:
            st.markdown(
                "<span style='font-size:14px; color:#718096;'>Topic ideas: <i>'I failed my chemistry mock test and feel like giving up'</i> or <i>'I have exam anxiety, help me calm down'</i></span>",
                unsafe_allow_html=True
            )
            
        st.markdown("<br>", unsafe_allow_html=True)

        # Container for chat messages
        chat_container = st.container()

        # Display history
        with chat_container:
            # If no history, show warm greeting
            if not history:
                st.chat_message("assistant").markdown(
                    f"Hi there! I'm Aura, your mental wellness companion. I know preparing for competitive exams like "
                    f"**{profile['target_exam']}** is incredibly stressful, and sometimes the pressure can feel overwhelming. "
                    f"Whether you need to vent, want a quick mindfulness break, or need coping tips, I'm here for you. "
                    f"How are you holding up today?"
                )
            else:
                for msg in history:
                    st.chat_message(msg["role"]).markdown(msg["content"])

        # Accept user input
        if prompt := st.chat_input("Tell Aura what's on your mind..."):
            # Display user message
            st.chat_message("user").markdown(prompt)
            # Add to database
            database.add_chat_message("user", prompt)
            
            # Generate response from Gemini
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                with st.spinner("Aura is typing..."):
                    try:
                        # Fetch recent entries to provide wellness history context
                        recent_logs = database.get_journal_entries(limit=3)
                        # Fetch complete chat history (updated with new user prompt)
                        current_chat_history = database.get_chat_history()
                        
                        # Generate response
                        response = client.generate_companion_response(
                            conversation_history=current_chat_history,
                            profile=profile,
                            recent_entries=recent_logs
                        )
                        message_placeholder.markdown(response)
                        # Save to database
                        database.add_chat_message("assistant", response)
                    except Exception as e:
                        st.error(f"Error generating response: {e}")
            
            # Trigger rerun to sync chatbot state cleanly
            st.rerun()

elif st.session_state.page == "mindfulness":
    st.markdown("<h1 style='margin-bottom: 5px;'>🧘 Mindfulness & Breathing Space</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #4A5568;'>Take a step back from the books. Rest your eyes, align your breathing, and reset your mind.</p>", unsafe_allow_html=True)
    st.markdown("---")
    
    col_bubble, col_techniques = st.columns([1, 1])
    
    with col_bubble:
        st.markdown(
            """
            <div class="wellness-card" style="padding: 20px; text-align: center; background: white;">
                <h3 style="margin-top: 0; color: #6B46C1;">🌬️ Visual Breathing Helper</h3>
                <p style="color: #718096; font-size:14px; margin-bottom: 20px;">
                    Follow the expanding and contracting circle. Sync your breathing to regulate stress.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # Embed the HTML component
        st.components.v1.html(styles.BREATHING_HTML, height=350, scrolling=False)
        
    with col_techniques:
        st.markdown("<h3 style='margin-top:0;'>Quick Calm Exercises</h3>", unsafe_allow_html=True)
        
        with st.expander("🧩 5-4-3-2-1 Grounding Technique"):
            st.markdown(
                """
                When feeling intense panic or exam overload, use this cognitive grounding method to re-center in the physical room. 
                Identify:
                - **5 Things You Can See**: Look around you. (e.g., your desk lamp, a pen, the window, a calendar, your study note).
                - **4 Things You Can Touch**: Feel your immediate surroundings. (e.g., the texture of your study desk, your keyboard, your cotton shirt, your hair).
                - **3 Things You Can Hear**: Tune in to background details. (e.g., the hum of the fan, distant traffic, your own heartbeat).
                - **2 Things You Can Smell**: Breathe in. (e.g., coffee, pages of an old book, fresh air).
                - **1 Thing You Can Taste**: Focus on your mouth. (e.g., a sip of water, a mint).
                
                *This technique pulls your brain out of future-worry loops and anchors it in the sensory present.*
                """
            )
            
        with st.expander("⚡ Progressive Muscle Relaxation (PMR)"):
            st.markdown(
                """
                Stress causes physical tension in the neck, back, and shoulders which feeds back into study fatigue. PMR systematically releases this.
                
                **Instructions (3-Minute Break):**
                1. **Feet**: Clench your toes tightly for 5 seconds. Release and notice the relaxation flow in.
                2. **Calves & Thighs**: Tense your leg muscles for 5 seconds. Release.
                3. **Fists & Arms**: Clench both fists and flex your bicep muscles. Hold for 5 seconds. Release.
                4. **Shoulders & Neck**: Pull your shoulders up toward your ears. Hold for 5 seconds. Let them drop heavily.
                5. **Face**: Squint your eyes and clench your jaw. Hold for 5 seconds. Let go, letting your jaw hang loose.
                
                *Take a deep breath and feel the physical weight lifted from your upper body.*
                """
            )
            
        with st.expander("📅 Exam-Day Panic Controls (Immediate Help)"):
            st.markdown(
                """
                If you feel a panic attack or extreme block in the middle of a mock exam or the real test:
                
                1. **Stop Writing Immediately**: Put down your pen. Close your eyes. Trying to push through panic increases error rates.
                2. **The Double-Inhale (Cyclic Sighing)**: Take a deep breath in through your nose, and then immediately *sip in* a tiny bit more air to fully inflate the lungs. Release with a long, slow exhale through your mouth. Repeat 3 times. This is the fastest biological hack to trigger the parasympathetic system.
                3. **Ground Your Sight**: Focus on one stationary physical object in the exam hall (like the clock, or a corner of the desk). Study its shape for 10 seconds.
                4. **Tell Yourself**: *'This is just stress hormones. They are here to give me energy, not hurt me. I will tackle one question at a time.'*
                """
            )

        with st.expander("⏰ The 50/10 Rule for Burnout"):
            st.markdown(
                """
                To prevent cognitive fatigue during GATE, UPSC, JEE, or NEET preparation:
                
                - **50 Minutes Study**: Pure focused study, completely distraction-free. No phone, no social media.
                - **10 Minutes Break**: Fully step away from your study chair. Do NOT check your phone (this creates cognitive clutter). Instead:
                  - Do a 2-minute stretch.
                  - Drink a glass of water.
                  - Do a 3-cycle breathing exercise using the visual helper on the left.
                
                *This resets your brain's workspace memory, keeping your retention high throughout the day.*
                """
            )
