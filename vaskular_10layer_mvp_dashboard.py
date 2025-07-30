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
    </style>
""", unsafe_allow_html=True)

st.title("Allayr - Your Compression Sock 2.0")

# --- Sidebar Controls ---
with st.sidebar.expander("🔧 Simulation Settings", expanded=True):
    temp_celsius = st.slider("Body Temp (°C)", 28.0, 40.0, 36.5, 0.1)
    battery_level = st.slider("Battery (%)", 0.0, 100.0, 80.0, 1.0)
    real_time_mode = st.checkbox("⏱ Real-Time Simulation", value=False)
    show_live_heatmap = st.checkbox("📊 Show Zone Signal Heatmap", value=False)

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

with st.sidebar.expander("💬 Ask Allayr (Recovery Chatbot)", expanded=False):
    st.markdown("_Allayr is your warm, supportive recovery trainer. Ask anything about your performance, recovery plan, or latest compression action._")
    user_input = st.text_input("Ask Allayr a question:", key="chatbox")
    if user_input:
        st.markdown(f"**You:** {user_input}")

        if "why" in user_input.lower():
            st.markdown("**Allayr:** I noticed a perfusion drop in Zone 3. So I increased compression slightly to help your blood flow rebound — nothing to worry about, just looking out for you 💪")
        elif "recovery" in user_input.lower():
            st.markdown("**Allayr:** Right now, your signals look good. If you're still sore, I’d recommend light stretching and compression on Zones 2 and 4. Let’s get you back to 100%.")
        elif "plan" in user_input.lower():
            st.markdown("**Allayr:** Today’s focus is on circulation support. If you had a tough workout, I’ve been gently cycling compression to help flush lactic acid. We’ve got this.")
        elif "score" in user_input.lower():
            st.markdown("**Allayr:** Your last anomaly score was a bit elevated, mostly due to a pressure spike in Zone 4. I adjusted it — you're stable now.")
        elif "name" in user_input.lower():
            st.markdown("**Allayr:** I’m Allayr — your AI recovery trainer. Here to get you back to peak shape, every time.")
        else:
            st.markdown("**Allayr:** I’m here to help however I can. You can ask me about your zones, compression changes, or recovery tips anytime.")

run_sim = st.sidebar.button("▶️ Run Full Stack Simulation")

# --- Sock State ---
sock_state = {
    'battery_level': battery_level,
    'sensor_status': True,
    'ble_connection': True,
    'temp_celsius': temp_celsius,
    'sampling_rate': 10,
    'inference_enabled': True,
    'fallback_enabled': False,
    'control_mode': control_mode,
    'manual_action': manual_action
}

# --- Visual Feedback Placeholder ---
st.markdown("""
### 🧠 Latest Compression Action
""")
if control_mode == "Manual" and manual_action:
    st.markdown(f"**Manual Mode Active:** Compression set to **{manual_action}**")
elif control_mode == "Allayr (Autonomous)":
    st.markdown("**Autonomous Mode Active:** Allayr will make compression decisions based on real-time sensor data.")

