import streamlit as st
import numpy as np
import pandas as pd

st.set_page_config(page_title="🔋 배터리 수명 예측 시뮬레이터", layout="centered")

st.title("🔋 배터리 수명 예측 시뮬레이터")
st.write("배터리 종류와 사용 조건을 입력하면 예상 수명과 용량 저하를 시각화합니다.")

# 사용자 입력
battery_type = st.selectbox("배터리 종류", ["리튬이온 (Li-ion)", "리튬폴리머 (Li-Po)", "니켈수소 (NiMH)", "납축전지 (Pb-Acid)"])
temperature = st.slider("사용 온도 (°C)", -10, 60, 25)
depth_of_discharge = st.slider("방전 깊이 (DoD, %)", 10, 100, 80)
charge_rate = st.slider("충전 속도 (C-rate)", 0.2, 2.0, 1.0, 0.1)

# 기본 수명
base_life = {
    "리튬이온 (Li-ion)": 1500,
    "리튬폴리머 (Li-Po)": 1200,
    "니켈수소 (NiMH)": 800,
    "납축전지 (Pb-Acid)": 500
}[battery_type]

# 단순 모델 계산
temp_factor = np.exp(-0.05 * (temperature - 25))
dod_factor = (100 / depth_of_discharge) ** 1.3
charge_factor = 1 / (1 + 0.3 * (charge_rate - 1))

predicted_cycles = int(base_life * temp_factor * dod_factor * charge_factor)

st.subheader("📊 예측 결과")
st.success(f"예상 배터리 수명: 약 **{predicted_cycles:,} 사이클**")

# 용량 저하 시뮬레이션
cycles = np.arange(0, predicted_cycles + 1, max(1, predicted_cycles // 100))
capacity = 100 * np.exp(-cycles / (predicted_cycles / 5))

df = pd.DataFrame({"사이클 수": cycles, "용량 유지율 (%)": capacity})
st.line_chart(df.set_index("사이클 수"))

st.info("""
💡 **해석 가이드**
- 온도가 높거나 방전 깊이가 깊을수록, 그리고 충전 속도가 빠를수록 배터리 수명이 짧아집니다.
- 이 모델은 실험 데이터를 단순화한 예시로, 실제 배터리 환경과 다를 수 있습니다.
""")
