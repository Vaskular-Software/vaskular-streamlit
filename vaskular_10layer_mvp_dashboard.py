import streamlit as st
import numpy as np
import pandas as pd
import random
import matplotlib.pyplot as plt
import seaborn as sns
from collections import deque
from datetime import datetime
import json
import os
import time
import streamlit.components.v1 as components

st.set_page_config(layout="wide")
st.markdown("""
    <style>
        html, body, [class*="css"]  {
            font-family: 'Inter', sans-serif;
            background-color: #0a0a0a;
            color: #f5f5f5;
        }
        .stButton>button {
            background-color: #111;
            color: #fff;
            border-radius: 12px;
            padding: 0.5em 1.5em;
            font-weight: 600;
        }
        .stPlotlyChart, .stMarkdown, .stDataFrame {
            background-color: #0a0a0a !important;
            color: #f5f5f5 !important;
        }
        .main .block-container {
            padding: 2rem 1rem;
        }
    </style>
""", unsafe_allow_html=True)

st.title("Allayr - Your Compression Sock 2.0")
st.markdown("##### Compression that thinks.")

# --- Status Bar ---
st.markdown("""
<div style='display: flex; justify-content: space-between; padding: 0.5rem 1rem; background-color: #1a1a1a; border-radius: 8px;'>
    <div>Battery ⚡ 80%</div>
    <div>Temp 🌡️ 36.5°C</div>
    <div>Status: ✅ Stable</div>
</div>
""", unsafe_allow_html=True)

# --- Sidebar Controls ---
with st.sidebar.expander("🔧 Simulation Settings", expanded=True):
    temp_celsius = st.slider("Body Temp (°C)", 28.0, 40.0, 36.5, 0.1)
    battery_level = st.slider("Battery (%)", 0.0, 100.0, 80.0, 1.0)
    real_time_mode = st.checkbox("⏱ Real-Time Simulation", value=False)
    show_live_heatmap = st.checkbox("📊 Show Zone Signal Heatmap", value=False)
    enable_goal_tracker = st.checkbox("🎯 Show Goal Tracker", value=True)
    enable_export = st.checkbox("💾 Enable Recovery Log Export", value=False)

with st.sidebar.expander(" Control Mode", expanded=False):
    control_mode = st.radio("Compression Control:", ["Allayr (Autonomous)", "Manual"], index=0)
    manual_action = None
    if control_mode == "Manual":
        manual_action = st.radio("Manual Compression Action:", ["Increase", "Decrease", "Maintain"])

with st.sidebar.expander("📘 Sensor Glossary", expanded=False):
    st.markdown("""
    #### Sensor Zones
    **Zone 1 – Ankle (Doppler Ultrasound)**  
    • Measures blood flow velocity to detect occlusions or clot precursors.

    **Zone 2 – Mid-Calf (Near-Infrared Spectroscopy - NIRS)**  
    • Measures tissue oxygen saturation (SpO₂).

    **Zone 3 – Lower Calf (Photoplethysmography - PPG)**  
    • Tracks microvascular blood flow (i.e., perfusion).

    **Zone 4 – Mid-Calf (Pressure Sensors)**  
    • Maps venous pressure dynamically across calf regions.
    """)

with st.sidebar.expander("💬 Ask Allayr (Recovery Chatbot)", expanded=False):
    st.markdown("_Allayr is your warm, supportive recovery trainer. Ask anything about your performance, recovery plan, or latest compression action._")
    enable_voice = st.checkbox("🔊 Enable Voice", value=False)
    user_input = st.text_input("Ask Allayr a question:", key="chatbox")
    if user_input:
        st.markdown(f"**You:** {user_input}")

        if "why" in user_input.lower():
            response = "I noticed a perfusion drop in Zone 3. So I increased compression slightly to help your blood flow rebound — nothing to worry about, just looking out for you 💪"
        elif "recovery" in user_input.lower():
            response = "Right now, your signals look good. If you're still sore, I’d recommend light stretching and compression on Zones 2 and 4. Let’s get you back to 100%."
        elif "plan" in user_input.lower():
            response = "Today’s focus is on circulation support. If you had a tough workout, I’ve been gently cycling compression to help flush lactic acid. We’ve got this."
        elif "score" in user_input.lower():
            response = "Your last anomaly score was a bit elevated, mostly due to a pressure spike in Zone 4. I adjusted it — you're stable now."
        elif "name" in user_input.lower():
            response = "I’m Allayr — your AI recovery trainer. Here to get you back to peak shape, every time."
        else:
            response = "I’m here to help however I can. You can ask me about your zones, compression changes, or recovery tips anytime."

        st.markdown(f"**Allayr:** {response}")

        def speak(text):
            speech_script = f"""
            <script>
                var msg = new SpeechSynthesisUtterance("{response}");
                msg.pitch = 1.1;
                msg.rate = 0.95;
                msg.voice = speechSynthesis.getVoices().find(voice => voice.lang.includes('en') && voice.name.includes('Female'));
                window.speechSynthesis.speak(msg);
            </script>
            """
            components.html(speech_script)

        if enable_voice:
            speak(response)

# placeholder sections
if enable_goal_tracker:
    st.markdown("""
    <div style='margin-top: 2rem; background-color: #111; padding: 1rem; border-radius: 8px;'>
        <h4 style='margin-bottom: 0.5rem;'>🏁 Daily Goal Tracker</h4>
        <ul>
            <li>🎯 60-min light compression achieved</li>
            <li>🥤 Hydration reminder met</li>
            <li>🛏️ Sleep goal pending</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

if enable_export:
    st.download_button(
        label="📥 Export Recovery Log",
        data=json.dumps({"status": "demo only"}, indent=2),
        file_name="allayr_recovery_log.json",
        mime="application/json"
    )

st.markdown("""
> _"Every decision I make is one step closer to your recovery. Let’s keep moving." — Allayr_
""")
