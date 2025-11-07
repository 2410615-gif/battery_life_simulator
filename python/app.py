import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO

# ---------------------------------------
# 🔧 페이지 기본 설정
# ---------------------------------------
st.set_page_config(
    page_title="🔋 배터리 수명 예측 시뮬레이터",
    layout="wide",
    page_icon="🔋"
)

# ---------------------------------------
# 🎨 사이드바 - 앱 정보 및 옵션
# ---------------------------------------
with st.sidebar:
    st.title("🔧 설정")
    st.markdown("배터리 조건을 조정하세요.")
    
    battery_type = st.selectbox("배터리 종류", [
        "리튬이온 (Li-ion)", 
        "리튬폴리머 (Li-Po)", 
        "니켈수소 (NiMH)", 
        "납축전지 (Pb-Acid)"
    ])

    temperature = st.slider("사용 온도 (°C)", -10, 60, 25)
    depth_of_discharge = st.slider("방전 깊이 (DoD, %)", 10, 100, 80)
    charge_rate = st.slider("충전 속도 (C-rate)", 0.2, 2.0, 1.0, 0.1)
    
    st.markdown("---")
    st.caption("© 2025 BatteryLifeSim by GPT-5")

# ---------------------------------------
# 🧠 메인 타이틀
# ---------------------------------------
st.title("🔋 배터리 수명 예측 시뮬레이터")
st.write("배터리 종류와 사용 조건을 입력하면 예상 수명, 용량 저하, 효율 변화를 시각화합니다.")

# ---------------------------------------
# ⚙️ 수명 계산 모델
# ---------------------------------------
base_life = {
    "리튬이온 (Li-ion)": 1500,
    "리튬폴리머 (Li-Po)": 1200,
    "니켈수소 (NiMH)": 800,
    "납축전지 (Pb-Acid)": 500
}[battery_type]

temp_factor = np.exp(-0.05 * (temperature - 25))
dod_factor = (100 / depth_of_discharge) ** 1.3
charge_factor = 1 / (1 + 0.3 * (charge_rate - 1))
predicted_cycles = int(base_life * temp_factor * dod_factor * charge_factor)

# ---------------------------------------
# 📈 시뮬레이션 데이터 생성
# ---------------------------------------
cycles = np.arange(0, predicted_cycles + 1, max(1, predicted_cycles // 100))
capacity = 100 * np.exp(-cycles / (predicted_cycles / 5))
efficiency = 100 - (100 - capacity) * 0.7  # 효율 감소 가정

df = pd.DataFrame({
    "사이클 수": cycles,
    "용량 유지율 (%)": capacity,
    "에너지 효율 (%)": efficiency
})

# ---------------------------------------
# 📊 예측 결과 표시
# ---------------------------------------
col1, col2, col3 = st.columns(3)
col1.metric("예상 수명", f"{predicted_cycles:,} 사이클")
col2.metric("초기 용량", "100 %")
col3.metric("예상 효율 저하", f"{100 - efficiency[-1]:.1f} %")

st.markdown("---")

# ---------------------------------------
# 📉 시각화
# ---------------------------------------
st.subheader("📊 용량 및 효율 변화 그래프")
tab1, tab2 = st.tabs(["📉 용량 변화", "⚙️ 효율 변화"])

with tab1:
    st.line_chart(df.set_index("사이클 수")[["용량 유지율 (%)"]])

with tab2:
    st.line_chart(df.set_index("사이클 수")[["에너지 효율 (%)"]])

# ---------------------------------------
# 📘 해석 및 팁
# ---------------------------------------
with st.expander("💡 해석 가이드 보기"):
    st.markdown("""
    - **온도 상승**: 25°C 이상에서는 열화가 가속되어 수명이 짧아집니다.
    - **방전 깊이(DoD)**: 깊은 방전(>80%)은 사이클 수명을 크게 줄입니다.
    - **충전 속도(C-rate)**: 너무 빠른 충전은 내부 저항 증가로 열화를 유발합니다.
    - 이 시뮬레이션은 단순 모델 기반으로, 실제 환경과는 차이가 있을 수 있습니다.
    """)

# ---------------------------------------
# 📄 PDF 리포트 다운로드 기능
# ---------------------------------------
st.subheader("📤 리포트 내보내기")

def generate_report():
    buf = BytesIO()
    fig, ax = plt.subplots(figsize=(6,4))
    ax.plot(df["사이클 수"], df["용량 유지율 (%)"], label="용량 유지율 (%)")
    ax.plot(df["사이클 수"], df["에너지 효율 (%)"], label="에너지 효율 (%)", linestyle="--")
    ax.set_title(f"{battery_type} 배터리 수명 시뮬레이션 결과")
    ax.set_xlabel("사이클 수")
    ax.set_ylabel("퍼센트 (%)")
    ax.legend()
    fig.tight_layout()
    fig.savefig(buf, format="pdf")
    buf.seek(0)
    return buf

pdf_buffer = generate_report()
st.download_button(
    label="📥 PDF 리포트 다운로드",
    data=pdf_buffer,
    file_name="battery_life_report.pdf",
    mime="application/pdf"
)

# ---------------------------------------
# 🌡️ 추가 정보: 배터리별 특성 요약
# ---------------------------------------
st.markdown("---")
st.subheader("📚 배터리별 특성 요약")

info = {
    "리튬이온 (Li-ion)": "에너지 밀도가 높고, 메모리 효과가 거의 없지만 고온에서 열화가 빠름.",
    "리튬폴리머 (Li-Po)": "가볍고 자유로운 형태 제작 가능. 과충전에 취약.",
    "니켈수소 (NiMH)": "안정성과 저비용이 장점이지만, 자가 방전률이 높음.",
    "납축전지 (Pb-Acid)": "가격이 저렴하고 출력이 높지만, 무겁고 수명이 짧음."
}

st.info(info[battery_type])
