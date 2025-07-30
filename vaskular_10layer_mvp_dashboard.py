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
st.title("🧦 Vaskular AI - Smart Compression Sock Demo")

# --- Sidebar Controls ---
with st.sidebar.expander("🔧 Simulation Settings", expanded=True):
    temp_celsius = st.slider("Body Temp (°C)", 28.0, 40.0, 36.5, 0.1)
    battery_level = st.slider("Battery (%)", 0.0, 100.0, 80.0, 1.0)
    real_time_mode = st.checkbox("⏱ Real-Time Simulation", value=False)
    show_live_heatmap = st.checkbox("📊 Show Zone Pressure Heatmap", value=False)

run_sim = st.sidebar.button("▶️ Run Full Stack Simulation")

# --- Sock State ---
sock_state = {
    'battery_level': battery_level,
    'sensor_status': True,
    'ble_connection': True,
    'temp_celsius': temp_celsius,
    'sampling_rate': 10,
    'inference_enabled': True,
    'fallback_enabled': False
}

def adjust_sampling_rate(state):
    if state['battery_level'] < 20:
        state['sampling_rate'] = max(1, state['sampling_rate'] - 1)
    elif state['battery_level'] > 80:
        state['sampling_rate'] = min(20, state['sampling_rate'] + 1)
    return state['sampling_rate']

def adjust_inference_behavior(state):
    state['inference_enabled'] = not (state['battery_level'] < 10)
    return state['inference_enabled']

def check_fallback_needed(state):
    state['fallback_enabled'] = not state['ble_connection'] or not state['sensor_status']
    return state['fallback_enabled']

# --- Sensor Simulation ---
num_sensors = 9
def generate_fake_ble_data():
    base = random.randint(1200, 1600)
    return [random.randint(base - 100, base + 100) for _ in range(num_sensors)]

# --- Anomaly Logic ---
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
    matrix = np.array(values).reshape((3, 3))
    zone_sums = {
        'Zone 1 (Toes 👣)': np.sum(matrix[0]),
        'Zone 2 (Arch 👟)': np.sum(matrix[1]),
        'Zone 3 (Heel 🦵)': np.sum(matrix[2])
    }
    if score > threshold:
        target_zone = max(zone_sums, key=zone_sums.get)
        return f"🔺 Increase compression in {target_zone} (high pressure)"
    elif score < threshold * 0.7:
        target_zone = min(zone_sums, key=zone_sums.get)
        return f"🔻 Decrease compression in {target_zone} (low pressure)"
    else:
        return "✅ Maintain current compression (balanced)"

def mercy_shutdown_check(state):
    return state['battery_level'] < 5 or state['temp_celsius'] > 42 or state['temp_celsius'] < 20 or state['fallback_enabled']

def log_data(timestamp, sensor_values, score, anomaly_flag, action):
    entry = {
        'timestamp': str(timestamp),
        'sensor_values': list(map(int, sensor_values)),
        'anomaly_score': float(score),
        'anomaly_detected': bool(anomaly_flag),
        'compression_action': str(action)
    }
    log_file = "vaskular_log.json"
    if not os.path.exists(log_file):
        with open(log_file, 'w') as f:
            json.dump([], f)
    with open(log_file, 'r+') as f:
        data = json.load(f)
        data.append(entry)
        f.seek(0)
        json.dump(data, f, indent=2)

def plot_zone_heatmap(matrix):
    fig, ax = plt.subplots()
    sns.heatmap(matrix, annot=True, fmt=".0f", cmap="YlOrRd", cbar=True,
                xticklabels=["Sensor 1", "Sensor 2", "Sensor 3"],
                yticklabels=["Toes 👣", "Arch 👟", "Heel 🦵"], ax=ax)
    ax.set_title("🧭 Zone Pressure Heatmap")
    st.pyplot(fig)
    # --- Main Simulation Logic ---
buffer = deque(maxlen=100)
anomaly_scores = []
anomaly_flags = []
explain_outputs = []

if run_sim:
    range_loop = range(100) if not real_time_mode else range(1000)
    step_number = 1
    tab1, tab2, tab3 = st.tabs(["📈 Simulation", "🔍 AI Explainability", "🧦 Sock State"])
    chart_area = tab1.empty()

    for _ in range(range_loop.stop):
        fake_data = generate_fake_ble_data()
        buffer.append(fake_data)

        adjust_sampling_rate(sock_state)
        adjust_inference_behavior(sock_state)
        check_fallback_needed(sock_state)

        if len(buffer) == 100:
            score = compute_anomaly_score(buffer)
            threshold = adaptive_threshold(sock_state['temp_celsius']) / 1000
            is_anomaly = score > threshold
            action = recommend_compression_action(fake_data, score, threshold)

            anomaly_scores.append(score)
            anomaly_flags.append(is_anomaly)

            matrix = np.array(fake_data).reshape((3, 3))
            zone_sums = {
                'Zone 1 (Toes 👣)': np.sum(matrix[0]),
                'Zone 2 (Arch 👟)': np.sum(matrix[1]),
                'Zone 3 (Heel 🦵)': np.sum(matrix[2])
            }
            max_zone = max(zone_sums, key=zone_sums.get)
            min_zone = min(zone_sums, key=zone_sums.get)

            explanation = (
                f"**Step {step_number}**  \n"
                f"• Score: **{score:.2f}** | Threshold: **{threshold:.2f}**  \n"
                f"• Highest Pressure: {max_zone} ({zone_sums[max_zone]:.0f})  \n"
                f"• Lowest Pressure: {min_zone} ({zone_sums[min_zone]:.0f})  \n"
                f"• **Action:** {action}  \n"
                f"🧪 *Interpretation: Elevated pressure in {max_zone} may indicate reduced venous return or swelling risk.*"
            )
            explain_outputs.append(explanation)
            log_data(datetime.now().isoformat(), fake_data, float(score), is_anomaly, action)
            step_number += 1

            if real_time_mode:
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
                        st.markdown("### 🗺️ Zone Pressure")
                        plot_zone_heatmap(matrix)

                with tab2:
                    st.markdown("### 🔍 Latest AI Reasoning")
                    st.markdown(explanation)

                with tab3:
                    for key, val in sock_state.items():
                        st.metric(key.replace("_", " ").title(), str(val))
                    if mercy_shutdown_check(sock_state):
                        st.error("⚠️ Mercy-Aligned Shutdown Triggered")
                    else:
                        st.success("✅ System Stable")

                time.sleep(0.3)

    # --- Summary (non-real-time) ---
    if not real_time_mode:
        with tab1:
            st.subheader("📈 Final Anomaly Score Chart with Markers")
            df = pd.DataFrame({
                "Score": anomaly_scores,
                "Threshold": [threshold] * len(anomaly_scores),
                "Anomaly": anomaly_flags
            })
            fig, ax = plt.subplots()
            ax.plot(df["Score"], label="Anomaly Score")
            ax.plot(df["Threshold"], linestyle="--", label="Threshold")
            ax.scatter(df.index[df["Anomaly"]], df["Score"][df["Anomaly"]],
                       color="red", label="Anomalies", zorder=5)
            ax.set_title("Final Anomaly Detection Chart")
            ax.legend()
            st.pyplot(fig)

            if show_live_heatmap:
                st.markdown("### 🗺️ Final Zone Pressure Map")
                plot_zone_heatmap(matrix)

        with tab2:
            st.subheader("🔍 Final AI Explanation")
            st.markdown(explain_outputs[-1], unsafe_allow_html=True)

        with tab3:
            st.subheader("🧦 Sock State Summary")
            for key, val in sock_state.items():
                st.metric(key.replace("_", " ").title(), str(val))
            if mercy_shutdown_check(sock_state):
                st.error("⚠️ Mercy-Aligned Shutdown Triggered")
            else:
                st.success("✅ System Stable")

        # --- Apply AI Fix Button ---
        if st.button("💡 Apply AI Recommendation"):
            st.markdown("### ✅ Simulated Compression Adjustment")
            last_matrix = matrix.copy()
            recommended_action = explain_outputs[-1]
            if "Zone 1" in recommended_action:
                last_matrix[0] *= 0.5
                fixed_zone = "Zone 1 (Toes 👣)"
            elif "Zone 2" in recommended_action:
                last_matrix[1] *= 0.5
                fixed_zone = "Zone 2 (Arch 👟)"
            elif "Zone 3" in recommended_action:
                last_matrix[2] *= 0.5
                fixed_zone = "Zone 3 (Heel 🦵)"
            else:
                st.info("No valid zone to apply action.")
                fixed_zone = None

            if fixed_zone:
                flat = last_matrix.flatten()
                new_score = np.mean(np.square(flat - np.mean(flat))) / 1000
                fig, ax = plt.subplots()
                ax.plot(anomaly_scores, label="Original Anomaly Score")
                ax.axhline(y=new_score, color="green", linestyle="--", label="New Score After Fix")
                ax.set_title(f"✔️ Anomaly Dropped After Fixing {fixed_zone}")
                ax.legend()
                st.pyplot(fig)
                if show_live_heatmap:
                    st.markdown(f"### 🗺️ Adjusted Zone Pressure Map ({fixed_zone})")
                    plot_zone_heatmap(last_matrix)
                st.success(f"✅ Anomalies resolved by reducing pressure in {fixed_zone}")

        st.balloons()
        st.success("✅ Simulation Complete")