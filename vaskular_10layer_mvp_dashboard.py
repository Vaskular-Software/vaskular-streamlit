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
import openai
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
        .chat-box {
            border: 1px solid #333;
            border-radius: 10px;
            padding: 1rem;
            margin-top: 2rem;
            background-color: #111;
        }
    </style>
""", unsafe_allow_html=True)

st.title("🧦 Allayr - Smart Compression Sock 2.0")
st.markdown("##### Compression that thinks.")

st.markdown("""
<div style='display: flex; justify-content: space-between; padding: 0.5rem 1rem; background-color: #1a1a1a; border-radius: 8px;'>
    <div>Battery ⚡ 80%</div>
    <div>Temp 🌡️ 36.5°C</div>
    <div>Status: ✅ Stable</div>
</div>
""", unsafe_allow_html=True)

with st.sidebar.expander("🔧 Simulation Settings", expanded=True):
    temp_celsius = st.slider("Body Temp (°C)", 28.0, 40.0, 36.5, 0.1)
    battery_level = st.slider("Battery (%)", 0.0, 100.0, 80.0, 1.0)
    real_time_mode = st.checkbox("⏱ Real-Time Simulation", value=False)
    show_live_heatmap = st.checkbox("📊 Show Zone Signal Heatmap", value=False)
    enable_goal_tracker = st.checkbox("🎯 Show Goal Tracker", value=True)
    enable_export = st.checkbox("💾 Enable Recovery Log Export", value=False)
    enable_step_sim = st.checkbox("🔬 Enable Step-by-Step Simulation", value=True)

with st.sidebar.expander("🧠 Control Mode", expanded=False):
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

buffer = deque(maxlen=100)
anomaly_scores = []
anomaly_flags = []

zone_values = {
    'Zone 1 (Ankle - Doppler)': 'N/A',
    'Zone 2 (Mid-Calf - NIRS)': 'N/A',
    'Zone 3 (Lower Calf - PPG)': 'N/A',
    'Zone 4 (Mid-Calf - Pressure)': 'N/A'
}

if "step_number" not in st.session_state:
    st.session_state.step_number = 1

if enable_step_sim:
    step = st.button("▶️ Run Next Step")
    if step:
        fake_data = [random.randint(1000, 1500) for _ in range(4)]
        buffer.append(fake_data)
        flat = np.array(buffer).flatten()
        score = np.mean(np.square(flat - np.mean(flat))) / 1000
        threshold = 0.5
        is_anomaly = score > threshold

        zones = ["Zone 1 (Ankle - Doppler)",
                 "Zone 2 (Mid-Calf - NIRS)",
                 "Zone 3 (Lower Calf - PPG)",
                 "Zone 4 (Mid-Calf - Pressure)"]
        zone_values = dict(zip(zones, fake_data))

        if control_mode == "Allayr (Autonomous)":
            if score > threshold:
                target_zone = max(zone_values, key=zone_values.get)
                action = f"🔺 Increase compression at {target_zone}"
            elif score < threshold * 0.7:
                target_zone = min(zone_values, key=zone_values.get)
                action = f"🔻 Decrease compression at {target_zone}"
            else:
                action = "✅ Maintain compression across all zones"
        elif control_mode == "Manual":
            action = f"Manual override: {manual_action} compression across all zones"

        explanation = (
            f"**Step {st.session_state.step_number}**  \n"
            f"• Score: **{score:.2f}** | Threshold: **{threshold:.2f}**  \n"
            f"• Raw Sensor Values: {zone_values}  \n"
            f"• **Action:** {action}  \n"
            f"🧪 *Interpretation: Signal variation analyzed across multiple biometric inputs.*"
        )

        st.markdown(explanation)
        st.session_state.step_number += 1

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

st.markdown("> _\"Every decision I make is one step closer to your recovery. Let’s keep moving.\" — Allayr_")

st.markdown("""
<div class='chat-box'>
    <h4>💬 Ask Allayr</h4>
    <p>Need advice on your recovery? Ask me anything based on your real-time data.</p>
</div>
""", unsafe_allow_html=True)

user_prompt = st.text_input("Ask Allayr something:", "What's my recovery status today?")
if user_prompt:
    openai.api_key = "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"

    system_prompt = f"""
    You are Allayr, a warm but precise athletic recovery assistant. Based on the following sensor metrics, generate a natural language recovery update or advice:

    - Body Temp: {temp_celsius} °C
    - Battery Level: {battery_level}%
    - Zone 1 (Doppler - Ankle): {zone_values.get('Zone 1 (Ankle - Doppler)', 'N/A')}
    - Zone 2 (NIRS - Mid-Calf): {zone_values.get('Zone 2 (Mid-Calf - NIRS)', 'N/A')}
    - Zone 3 (PPG - Lower Calf): {zone_values.get('Zone 3 (Lower Calf - PPG)', 'N/A')}
    - Zone 4 (Pressure - Mid-Calf): {zone_values.get('Zone 4 (Mid-Calf - Pressure)', 'N/A')}
    """

    try:
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.6
        )
        ai_response = response.choices[0].message.content
        st.success("Allayr says: " + ai_response)
    except Exception as e:
        st.error(f"OpenAI API error: {e}")
