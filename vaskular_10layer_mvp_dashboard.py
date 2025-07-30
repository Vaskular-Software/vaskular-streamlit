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

st.title("🧦 Allayr - Smart Compression Sock 2.0")

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

# --- Simulation Logic ---
def generate_fake_sensor_data():
    base = random.randint(1000, 1500)
    return [random.randint(base - 150, base + 150) for _ in range(4)]

def compute_anomaly_score(window):
    flat = np.array(window).flatten()
    mean = np.mean(flat)
    score = np.mean(np.square(flat - mean))
    return score / 1000

def adaptive_threshold(temp):
    base = 500
    if temp > 38:
        return base * 1.5
    elif temp < 30:
        return base * 0.8
    return base

def recommend_compression_action(values, score, threshold):
    zones = ["Zone 1 (Ankle 🦶 - Doppler)",
             "Zone 2 (Mid-Calf 🔦 - NIRS)",
             "Zone 3 (Lower-Calf 💓 - PPG)",
             "Zone 4 (Mid-Calf 💥 - Pressure)"]
    zone_signals = dict(zip(zones, values))
    if score > threshold:
        target_zone = max(zone_signals, key=zone_signals.get)
        return f"🔺 Increase compression based on signal from {target_zone}"
    elif score < threshold * 0.7:
        target_zone = min(zone_signals, key=zone_signals.get)
        return f"🔻 Decrease compression based on signal from {target_zone}"
    else:
        return "✅ Maintain current compression (balanced)"

def plot_zone_signals(values):
    zones = ["Ankle 🦶 - Doppler", "Mid-Calf 🔦 - NIRS", "Lower-Calf 💓 - PPG", "Mid-Calf 💥 - Pressure"]
    fig, ax = plt.subplots()
    sns.barplot(x=zones, y=values, palette="coolwarm", ax=ax)
    ax.set_ylabel("Sensor Reading")
    ax.set_title("🔬 Sensor Zone Readings")
    st.pyplot(fig)

if run_sim:
    buffer = deque(maxlen=100)
    anomaly_scores = []
    anomaly_flags = []
    explain_outputs = []
    step_number = 1
    tab1, tab2, tab3 = st.tabs(["📈 Simulation", "🔍 AI Explainability", "🧦 Sock State"])
    chart_area = tab1.empty()

    for _ in range(100):
        fake_data = generate_fake_sensor_data()
        buffer.append(fake_data)

        if len(buffer) == 100:
            score = compute_anomaly_score(buffer)
            threshold = adaptive_threshold(sock_state['temp_celsius']) / 1000
            is_anomaly = score > threshold
            action = recommend_compression_action(fake_data, score, threshold)

            anomaly_scores.append(score)
            anomaly_flags.append(is_anomaly)

            explanation = (
                f"**Step {step_number}**  \n"
                f"• Score: **{score:.2f}** | Threshold: **{threshold:.2f}**  \n"
                f"• Raw Sensor Values: {fake_data}  \n"
                f"• **Action:** {action}  \n"
                f"🧪 *Interpretation: Abnormal signal variance may indicate poor perfusion, swelling, or oxygen drop.*"
            )
            explain_outputs.append(explanation)
            step_number += 1

            with chart_area.container():
                df = pd.DataFrame({
                    "Score": anomaly_scores,
                    "Threshold": [threshold] * len(anomaly_scores)
                })
                fig, ax = plt.subplots()
                ax.plot(df["Score"], label="Anomaly Score")
                ax.plot(df["Threshold"], linestyle="--", label="Threshold")
                anomaly_indices = [i for i, flag in enumerate(anomaly_flags) if flag]
                ax.scatter(anomaly_indices, [anomaly_scores[i] for i in anomaly_indices],
                           color="red", label="Anomalies", zorder=5)
                ax.set_title(f"📊 Live Anomaly Detection — Step {step_number}")
                ax.legend()
                st.pyplot(fig)

                if show_live_heatmap:
                    st.markdown("### 📊 Live Sensor Readings")
                    plot_zone_signals(fake_data)

            with tab2:
                st.markdown("### 🔍 Latest AI Reasoning")
                st.markdown(explanation)

            with tab3:
                for key, val in sock_state.items():
                    st.metric(key.replace("_", " ").title(), str(val))

            time.sleep(0.2)

    st.success("✅ Simulation Complete")
