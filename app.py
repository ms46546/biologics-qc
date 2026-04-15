import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="Biologics QC Control Chart", layout="wide")
st.title("🧪 Biologics Analysis Control Chart")

# 1. 샘플 데이터 생성
def get_sample_data():
    np.random.seed(42)
    data = {
        "분석법": ["CE-SDS"] * 10 + ["HPLC"] * 10 + ["icIEF"] * 10,
        "장비번호": ["PA800-01", "PA800-01", "PA800-02"] * 10,
        "분석자": ["홍길동", "김철수"] * 15,
        "의뢰번호": [f"REQ-{i:03d}" for i in range(1, 31)],
        "Material_Lot": ["Lot-A", "Lot-B", "Lot-A"] * 10,
        "분석일자": pd.date_range("2024-01-01", periods=30, freq="D"),
        "결과값": np.random.normal(95, 1, 30)
    }
    return pd.DataFrame(data)

# 2. 사이드바 - 파일 업로드
st.sidebar.header("📁 Data Upload & Filter")

uploaded_file = st.sidebar.file_uploader(
    "CSV 파일 업로드", 
    type=["csv"],
    help="분석법, 결과값 컬럼이 필수입니다"
)

# 3. 데이터 로드
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.sidebar.success("✅ 파일 업로드 완료!")
else:
    df = get_sample_data()
    st.sidebar.info("📊 샘플 데이터를 사용합니다")

# 4. 필수 컬럼 확인
required_cols = ["분석법", "결과값"]
if not all(col in df.columns for col in required_cols):
    st.error(f"❌ 필수 컬럼이 없습니다: {required_cols}")
    st.write("현재 컬럼:", df.columns.tolist())
    st.stop()

# 5. 사이드바 - 필터
method = st.sidebar.selectbox(
    "분석법 선택", 
    options=df["분석법"].unique().tolist()
)

# 6. 데이터 필터링
selected_df = df[df["분석법"] == method].reset_index(drop=True)

if len(selected_df) == 0:
    st.warning("⚠️ 선택한 분석법의 데이터가 없습니다")
    st.stop()

# 7. 관리도 계산 (Mean ± 3SD)
mean_val = selected_df["결과값"].mean()
std_val = selected_df["결과값"].std()
ucl = mean_val + (3 * std_val)
lcl = mean_val - (3 * std_val)

# 8. 이상치 탐지
selected_df["이상여부"] = (selected_df["결과값"] > ucl) | (selected_df["결과값"] < lcl)

# 9. 차트 시각화
fig = go.Figure()

# 결과값 라인
fig.add_trace(go.Scatter(
    x=selected_df.index, 
    y=selected_df["결과값"],
    mode='lines+markers', 
    name='Result',
    marker=dict(
        size=10,
        color=['red' if v else 'blue' for v in selected_df["이상여부"]]
    ),
    hovertext=selected_df.get("의뢰번호", range(len(selected_df)))
))

# 관리선
fig.add_hline(y=mean_val, line_dash="dash", line_color="green", annotation_text="Mean")
fig.add_hline(y=ucl, line_dash="dot", line_color="red", annotation_text="UCL (3SD)")
fig.add_hline(y=lcl, line_dash="dot", line_color="red", annotation_text="LCL (3SD)")

fig.update_layout(
    title=f"{method} Control Chart", 
    xaxis_title="Sequence", 
    yaxis_title="Value",
    height=500
)

st.plotly_chart(fig, use_container_width=True)

# 10. 통계 요약
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Mean", f"{mean_val:.2f}")
with col2:
    st.metric("UCL", f"{ucl:.2f}")
with col3:
    st.metric("LCL", f"{lcl:.2f}")

# 11. 데이터 미리보기
st.subheader("📋 데이터 미리보기")
st.dataframe(selected_df.head(10))

# 12. 이상치 알림
if selected_df["이상여부"].any():
    oos_count = selected_df["이상여부"].sum()
    st.error(f"⚠️ 관리한계 초과 데이터 {oos_count}개 발견!")
    st.write("이상치 상세:")
    st.write(selected_df[selected_df["이상여부"]])
else:
    st.success("✅ 모든 데이터가 관리한계 내입니다")































