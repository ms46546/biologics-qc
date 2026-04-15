import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# 1. 페이지 설정
st.set_page_config(page_title="Biologics QC Control Chart", layout="wide")
st.title("🧪 Biologics Analysis Control Chart")
st.sidebar.header("Data Upload & Filter")

# 2. 샘플 데이터 생성 (데이터가 없을 경우를 대비한 예시)
def get_sample_data():
    data = {
        "분석법": ["CE-SDS"] * 10 + ["HPLC"] * 10 + ["icIEF"] * 10,
        "장비번호": ["PA800-01", "PA800-01", "PA800-02"] * 10,
        "분석자": ["홍길동", "김철수"] * 15,
        "의뢰번호": [f"REQ-{i:03d}" for i in range(1, 31)],
        "Material_Lot": ["Lot-A", "Lot-B", "Lot-A"] * 10,
        "결과값": np.random.normal(95, 1, 30) # 예시 데이터 (순도 등)
    }
    return pd.DataFrame(data)

df = get_sample_data()

# 3. 사이드바 필터링
method = st.sidebar.selectbox("분석법 선택", ["HPLC", "CE-SDS", "icIEF"])
selected_df = df[df["분석법"] == method].reset_index(drop=True)

# 4. 관리도 계산 (Mean ± 3SD)
mean_val = selected_df["결과값"].mean()
std_val = selected_df["결과값"].std()
ucl = mean_val + (3 * std_val)
lcl = mean_val - (3 * std_val)

# 5. 차트 시각화 (Plotly)
fig = go.Figure()

# 결과값 라인
fig.add_trace(go.Scatter(x=selected_df.index, y=selected_df["결과값"],
                         mode='lines+markers', name='Result',
                         hovertext=selected_df["의뢰번호"]))

# 관리선 추가
fig.add_hline(y=mean_val, line_dash="dash", line_color="green", annotation_text="Mean")
fig.add_hline(y=ucl, line_dash="dot", line_color="red", annotation_text="UCL (3SD)")
fig.add_hline(y=lcl, line_dash="dot", line_color="red", annotation_text="LCL (3SD)")

fig.update_layout(title=f"{method} Control Chart", xaxis_title="Sequence", yaxis_title="Value")
st.plotly_chart(fig, use_container_width=True)

# 6. 데이터 요약 및 이상징후 체크
col1, col2 = st.columns(2)
with col1:
    st.subheader("Statistical Summary")
    st.write(selected_df.describe())

with col2:
    st.subheader("Key Material/Instrument Analysis")
    # Lot별 또는 장비별 평균값 비교
    comparison = selected_df.groupby("Material_Lot")["결과값"].mean()
    st.bar_chart(comparison)
