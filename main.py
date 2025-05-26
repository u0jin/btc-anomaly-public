# Streamlit 전체 코드 - 해석 보완 최종 완성본 (시계열 + 트랜잭션 설명 포함)

import streamlit as st
import plotly.express as px
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

# ──────────────────────────────────────────────
# 기본 설정
# ──────────────────────────────────────────────
st.set_page_config(page_title="Bitcoin Anomaly Detection Tool", layout="wide")

# ──────────────────────────────────────────────
# UI 스타일 개선
# ──────────────────────────────────────────────
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

# ──────────────────────────────────────────────
# 헤더 및 소개
# ──────────────────────────────────────────────
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
- 각 항목마다 0~25점 점수화 → 총합 100점 만점
- 각 기준은 논문 3.4절 기반 이상 탐지 로직을 반영
- 점수 외에도 시계열 흐름 시각화, 요약표, 예시 흐름 안내까지 포함

---

**⚠️ 무료 버전의 한계**

- 실시간 mempool 탐지 기능은 제외됨
- 블랙리스트 주소 대조 및 네트워크 토폴로지 분석은 포함되지 않음
- 비정상적 주소군 간 클러스터링, 패턴 유사도 비교는 향후 고급버전 예정
""")

# ──────────────────────────────────────────────
# 입력 영역
# ──────────────────────────────────────────────
st.markdown("### 📡 분석할 비트코인 주소를 입력하세요")
address = st.text_input("예: 1BoatSLRHtKNngkdXEeobR76b53LETtpyT")

if st.button("🔍 거래 흐름 분석 시작"):
    if address:
        tx_list = get_transactions(address)
        if tx_list:
            st.success(f"총 {len(tx_list)}개의 트랜잭션을 수집했습니다.")

            # 전처리 및 이상 탐지
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

            # ──────────────────────────────────────────────
            # 결과 요약
            # ──────────────────────────────────────────────
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
                <td>{"✅ 정상적 빈도" if freq_score <= 5 else "⚠️ 일정 간격 내 반복 전송 감지"}</td>
              </tr>
              <tr>
                <td>고액 이상</td>
                <td>{amount_score}</td>
                <td>{"✅ 분산된 금액 흐름" if amount_score <= 5 else "⚠️ 특정 시점 고액 급증 감지"}</td>
              </tr>
              <tr>
                <td>텀블러</td>
                <td>{tumbler_score}</td>
                <td>{"✅ 단조 흐름 유지" if tumbler_score <= 5 else "⚠️ 반복적 패턴 및 급변 존재"}</td>
              </tr>
              <tr>
                <td>협박 사기</td>
                <td>{extortion_score}</td>
                <td>{"✅ 균형 있는 간격" if extortion_score <= 5 else "⚠️ burst 이후 침묵 간격 추정"}</td>
              </tr>
            </table>
            """
            st.markdown(table_html, unsafe_allow_html=True)

            st.metric("🔐 종합 위험 점수", f"{total_score} / 100")

            if total_score <= 30:
                st.success("✔️ 분석된 거래 흐름은 정상적인 분산 흐름에 가까우며, 특이 이상점은 확인되지 않았습니다.")
                st.caption("예시 흐름: 정기적 입출금, 일반 개인 지갑 사용 패턴 등")
            elif total_score <= 70:
                st.warning("⚠️ 일부 항목에서 유사 이상 흐름이 감지되었습니다. 참고용으로 활용 바랍니다.")
                st.caption("예시 흐름: 수차례의 일정 간격 전송, 중간 고액 트랜잭션 등")
            else:
                st.error("🚨 복수 기준에서 이상 흐름이 확인되었습니다. 특정 범죄 유형과의 유사성이 존재할 수 있습니다.")
                st.caption("예시 흐름: 고액 집중, 간격 급변, burst 후 침묵 등 — 랜섬웨어 계열 가능성")

            # 시계열 시각화
            st.subheader("📈 고빈도 이상 시점 시계열")
            st.caption("시간축 기준으로 트랜잭션 발생 흐름을 시각화한 그래프입니다. 붉은 점이 표시된 경우, 특정 시간 구간에 반복 전송이 집중되었음을 나타냅니다.")
            st.plotly_chart(
                plot_transaction_timeline(freq_result, anomaly_col='high_freq_flag'),
                use_container_width=True
            )

            # 전처리 데이터 출력
            st.subheader("📋 전체 전처리 트랜잭션")
            st.caption("수집된 트랜잭션에 대해 시간 및 금액 기준으로 정리된 데이터입니다. 이상 탐지 기준이 적용되어 있으며, 각 행은 하나의 실제 거래를 나타냅니다.")
            st.dataframe(df)
        else:
            st.warning("❗ 트랜잭션을 불러오지 못했습니다. 주소를 다시 확인해주세요.")
    else:
        st.info("💡 주소를 입력한 후 '분석 시작'을 눌러주세요.")
