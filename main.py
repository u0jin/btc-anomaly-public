# Streamlit 전체 코드 – 레이더 차트 포함 최종 시각화 버전

import streamlit as st
import plotly.graph_objects as go
from fetch_data import get_transactions
from preprocess import preprocess
from detect_patterns import detect_high_frequency, detect_high_amount
from calculate_score import (
    score_high_frequency, score_high_amount,
    score_tumbler, score_extortion,
    calculate_total_score
)
from pattern_identifier import (
    identify_ransomware_pattern,
    identify_sextortion_pattern,
    identify_tumbler_pattern,
    identify_extortion_pattern
)
from visualize import (
    plot_transaction_timeline,
    plot_risk_scores
)

# 수평 막대 그래프
def plot_score_bars(scores: dict):
    labels = list(scores.keys())
    values = list(scores.values())
    fig = go.Figure(go.Bar(
        x=values,
        y=labels,
        orientation='h',
        marker=dict(color='indianred'),
        text=values,
        textposition='outside'
    ))
    fig.update_layout(
        title="위험 항목별 점수 비교",
        xaxis=dict(title="점수 (0~25)", range=[0, 25]),
        yaxis=dict(title=""),
        height=400
    )
    return fig

# 레이더 차트
def plot_radar_chart(scores: dict):
    categories = list(scores.keys())
    values = list(scores.values())
    values += values[:1]
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories + [categories[0]],
        fill='toself',
        name='위험 점수'
    ))
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 25])
        ),
        showlegend=False,
        height=450,
        title="📡 위험 항목별 정량 구성 (레이더 차트)"
    )
    return fig

# 설정
st.set_page_config(page_title="Bitcoin Anomaly Detection Tool", layout="wide")

# 스타일
st.markdown("""
<style>
    html, body, .main, .block-container {
        background-color: #ffffff;
        color: #1c1c1e;
        font-family: 'Apple SD Gothic Neo', 'Roboto', sans-serif;
        font-size: 16px;
    }
    .title { font-size: 36px; font-weight: 700; color: #5e0000; margin-top: 0.5em; }
    .subtitle { font-size: 20px; font-weight: 400; color: #333333; }
    .badge { font-size: 15px; color: #777777; margin-bottom: 20px; }
    a { color: #5e0000; font-weight: 500; }
    a:hover { text-decoration: underline; }
    .stButton>button {
        background-color: #5e0000; color: white; border: none; border-radius: 6px;
        padding: 0.6em 1.2em; font-size: 16px; font-weight: 600;
    }
    .stButton>button:hover { background-color: #7b0000; }
    table {
        border-collapse: collapse;
        width: 100%;
        margin-top: 1em;
        margin-bottom: 1em;
    }
    th, td {
        border: 1px solid #ddd;
        padding: 10px;
        text-align: center;
    }
    th {
        background-color: #f9f9f9;
    }
</style>
""", unsafe_allow_html=True)

# 헤더
st.image("signalLogo.png", width=360)
st.markdown('<div class="title">Bitcoin Anomaly Detection Tool</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">고려대학교 정보보호학과 · Signal Research Lab</div>', unsafe_allow_html=True)
st.markdown('<div class="badge">논문 기반 · 실시간 트랜잭션 흐름 이상 감지 도구</div>', unsafe_allow_html=True)
st.markdown("[🌐 Signal Lab 홈페이지 바로가기](https://signal.korea.ac.kr/home)")

with st.expander("📘 도구 설명 및 한계 보기"):
    st.markdown("""
본 분석 도구는 논문  
**「비트코인 범죄 유형별 지갑 네트워크의 거래 패턴 분석 및 시계열-토폴로지 기반 모델링」(2025)**  
을 기반으로, 4가지 범죄 흐름 유형에 대한 정량 분석 기준을 실제 구현한 실습 도구입니다.

---

**✔️ 구성 방식 요약**

- 총 4가지 패턴 기준 (고빈도 / 고액 이상치 / 텀블러 / 협박 사기)
- 각 항목마다 0~25점 점수화 → 총합 100점 기반 분석 (정량 기준 기반 참고)
- 각 기준은 논문 3.4절 기반 이상 탐지 로직을 반영
- 점수 외에도 시계열 흐름 시각화, 요약표, 예시 흐름 안내 포함

---

**⚠️ 무료 버전의 한계**

- 실시간 mempool 탐지 기능은 제외됨
- 블랙리스트 주소 대조 및 네트워크 토폴로지 분석은 포함되지 않음
- 비정상적 주소군 간 클러스터링, 패턴 유사도 비교는 향후 고급버전 예정
""")

# 입력
st.markdown("### 📡 분석할 비트코인 주소를 입력하세요")
address = st.text_input("예: 1BoatSLRHtKNngkdXEeobR76b53LETtpyT")

if st.button("🔍 거래 흐름 분석 시작"):
    if address:
        tx_list = get_transactions(address)
        if tx_list:
            st.success(f"총 {len(tx_list)}개의 트랜잭션을 수집했습니다.")

            # 전처리 및 탐지
            df = preprocess(tx_list)
            freq_result = detect_high_frequency(df)
            freq_score = score_high_frequency(freq_result)

            amount_result = detect_high_amount(df)
            amount_score = score_high_amount(amount_result)

            ransomware_df = identify_ransomware_pattern(df)
            ransomware_hits = ransomware_df['ransomware_flag'].sum()

            sextortion_df = identify_sextortion_pattern(df)
            sextortion_hits = sextortion_df['sextortion_flag'].sum()

            tumbler_df = identify_tumbler_pattern(df)
            tumbler_hits = tumbler_df['tumbler_flag'].sum()
            tumbler_score = score_tumbler(tumbler_df)

            extortion_df = identify_extortion_pattern(df)
            extortion_hits = extortion_df['extortion_flag'].sum()
            extortion_score = score_extortion(extortion_df)

            total_score = calculate_total_score(
                freq_score, amount_score, tumbler_score, extortion_score
            )

            # 요약표
            st.divider()
            st.subheader("📊 기준별 이상 탐지 요약표")

            table_html = f"""
            <table>
              <tr>
                <th>분석 기준</th>
                <th>점수 (0~25)</th>
                <th>자동 해석</th>
              </tr>
              <tr>
                <td>고빈도</td>
                <td>{freq_score}</td>
                <td>{"✅ 정상적 빈도" if freq_score <= 5 else "⚠️ 반복 전송 감지"}</td>
              </tr>
              <tr>
                <td>고액 이상</td>
                <td>{amount_score}</td>
                <td>{"✅ 안정된 금액 흐름" if amount_score <= 5 else "⚠️ 특정 시점 고액 급증"}</td>
              </tr>
              <tr>
                <td>텀블러</td>
                <td>{tumbler_score}</td>
                <td>{"✅ 단조 흐름 유지" if tumbler_score <= 5 else "⚠️ 급격한 금액/간격 변동"}</td>
              </tr>
              <tr>
                <td>협박 사기</td>
                <td>{extortion_score}</td>
                <td>{"✅ 안정 간격" if extortion_score <= 5 else "⚠️ burst 후 장기 침묵 추정"}</td>
              </tr>
            </table>
            """
            st.markdown(table_html, unsafe_allow_html=True)

            st.metric("📌 참고용 위험 점수", f"{total_score} / 100")
            st.caption("※ 본 점수는 정량 기준 기반 탐지 결과로, 거래 맥락에 따라 실제 해석이 달라질 수 있습니다.")

            # 해석 메시지
            if total_score <= 30:
                st.success("✔️ 정량 기준 기반 분석 결과, 명확한 이상 패턴은 감지되지 않았습니다.")
                st.caption("예시 흐름: 정기적 입출금, 일반 개인 지갑 사용 패턴 등")
                st.info("※ 총 점수가 30점 이하일 경우, 이상 트랜잭션 비율이 낮거나 탐지 기준(high_freq_flag 등)을 충족하지 않습니다.")
            elif total_score <= 70:
                st.warning("⚠️ 일부 기준에서 이상 흐름과 유사한 움직임이 감지되었습니다. 참고용으로 활용 바랍니다.")
                st.caption("예시 흐름: 수차례 일정 간격 전송, 일시적 고액 트랜잭션 등")
                st.info("※ 점수가 31~70점일 경우, 탐지 기준을 부분적으로 충족하는 흐름이 존재합니다.")
            else:
                st.error("🚨 복수 기준에서 이상 흐름이 확인되었습니다. 관련 거래 검토가 권장됩니다.")
                st.caption("예시 흐름: 고액 집중, 간격 급변, burst 후 침묵 등 — 랜섬웨어 계열 가능성")
                st.info("※ 총점이 70점을 초과하면 복수 항목에서 명확한 이상 패턴이 탐지 기준을 만족했음을 의미합니다.")

            # 막대그래프
            st.subheader("📶 항목별 점수 비교 그래프")
            st.caption("각 기준별 점수를 수평 막대그래프로 비교합니다.")
            st.plotly_chart(plot_score_bars({
                "고빈도": freq_score,
                "고액 이상": amount_score,
                "텀블러": tumbler_score,
                "협박 사기": extortion_score
            }), use_container_width=True)

            # 레이더 차트
            st.subheader("🛰 위험 항목별 정량 구성 (레이더 차트)")
            st.caption("분석 기준별 점수의 분포를 방사형으로 표현합니다. 특정 축이 클수록 해당 패턴과 유사도가 높음을 의미합니다.")
            radar_fig = plot_radar_chart({
                "고빈도": freq_score,
                "고액 이상": amount_score,
                "텀블러": tumbler_score,
                "협박 사기": extortion_score
            })
            st.plotly_chart(radar_fig, use_container_width=True)

            # 시계열 시각화
            st.subheader("📈 고빈도 이상 시점 시계열")
            st.caption("시간 흐름에 따른 거래 패턴을 나타냅니다. 붉은 점은 짧은 간격 내 반복 전송을 의미합니다.")
            st.plotly_chart(
                plot_transaction_timeline(freq_result, anomaly_col='high_freq_flag'),
                use_container_width=True
            )

            # 전처리 결과
            st.subheader("📋 분석 대상 트랜잭션 (전처리 후 데이터)")
            st.caption("""
이 표는 BlockCypher API에서 수집한 원본 트랜잭션을 분석에 적합하도록 가공한 결과입니다.  
시간 정보는 datetime 형식으로 변환되었고, 금액 단위는 Satoshi → BTC로 통일되었으며  
이상 탐지 기준(high_freq_flag, high_amount_flag 등)이 부여되어 각 거래의 이상 여부를 플래그로 확인할 수 있습니다.
""")
            st.dataframe(df)
        else:
            st.warning("❗ 트랜잭션을 불러오지 못했습니다. 주소를 다시 확인해주세요.")
    else:
        st.info("💡 주소를 입력한 후 '분석 시작'을 눌러주세요.")
