# Streamlit 전체 코드 - 교수님 피드백 완전 반영 + 구조 정리 최종 버전

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

# 기본 설정
st.set_page_config(page_title="Bitcoin Anomaly Detection Tool", layout="wide")

# UI 스타일 설정
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
        background-color: #f2f2f2;
    }
</style>
""", unsafe_allow_html=True)

# 헤더
st.image("signalLogo.png", width=360)
st.markdown('<div class="title">Bitcoin Anomaly Detection Tool</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">고려대학교 정보보호학과 · Signal Research Lab</div>', unsafe_allow_html=True)
st.markdown('<div class="badge">논문 기반 · 트랜잭션 흐름 분석 도구 · 실시간 이상 탐지</div>', unsafe_allow_html=True)
st.markdown("[🌐 Signal Lab 홈페이지 바로가기](https://signal.korea.ac.kr/home)")

st.info("본 도구는 논문 '비트코인 범죄 유형별 지갑 네트워크의 거래 패턴 분석 및 시계열-토폴로지 기반 모델링'(2025)을 기반으로 구축되었습니다. 위험 판정은 정량적 기준에 따른 가능성 중심으로 구성되며, 점수와 해석은 참조 용도로 활용됩니다.")

st.divider()

# 입력
st.markdown("### 📡 분석할 비트코인 주소를 입력하세요")
address = st.text_input("예: 1BoatSLRHtKNngkdXEeobR76b53LETtpyT")

if st.button("🔍 거래 흐름 분석 시작"):
    if address:
        tx_list = get_transactions(address)
        if tx_list:
            st.success(f"총 {len(tx_list)}개의 트랜잭션을 수집했습니다.")

            # 분석
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

            # 요약표 출력
            st.divider()
            st.subheader("📊 기준별 이상 탐지 요약")

            table_html = f"""
            <table>
              <tr>
                <th>분석 기준</th>
                <th>점수 (0~25)</th>
                <th>해석</th>
              </tr>
              <tr>
                <td>고빈도</td>
                <td>{freq_score}</td>
                <td>{"✔️ 정상 범위" if freq_score <= 5 else "⚠️ 반복 흐름 있음"}</td>
              </tr>
              <tr>
                <td>고액 이상</td>
                <td>{amount_score}</td>
                <td>{"✔️ 안정적 분포" if amount_score <= 5 else "⚠️ 일시적 비정상 금액 감지"}</td>
              </tr>
              <tr>
                <td>텀블러</td>
                <td>{tumbler_score}</td>
                <td>{"✔️ 단조 흐름" if tumbler_score <= 5 else "⚠️ 패턴 반복 및 급변 추정"}</td>
              </tr>
              <tr>
                <td>협박 사기</td>
                <td>{extortion_score}</td>
                <td>{"✔️ 안정 간격" if extortion_score <= 5 else "⚠️ 집중 후 장기 침묵 가능성"}</td>
              </tr>
            </table>
            """
            st.markdown(table_html, unsafe_allow_html=True)

            # 총합 및 해석
            st.metric("🔐 총 위험 점수", f"{total_score} / 100")

            if total_score <= 30:
                st.success("✔️ 전체적으로 정상 범위에 해당하며, 현재까지 이상 징후는 확인되지 않았습니다.")
            elif total_score <= 70:
                st.warning("⚠️ 일부 항목에서 유사한 흐름이 감지되었으며, 상황에 따라 참고가 필요할 수 있습니다.")
            else:
                st.error("🚨 복수 항목에서 이상 흐름이 확인되었으며, 관련 거래 내역 확인이 권장됩니다.")

            # 시각화
            st.subheader("⏱ 거래 시간축 흐름 시각화")
            st.plotly_chart(
                plot_transaction_timeline(freq_result, anomaly_col='high_freq_flag'),
                use_container_width=True
            )

            # 전처리 트랜잭션 테이블
            st.subheader("📋 전체 전처리 트랜잭션")
            st.dataframe(df)
        else:
            st.warning("❗ 트랜잭션을 불러오지 못했습니다. 주소를 다시 확인해주세요.")
    else:
        st.info("💡 주소를 입력한 후 '분석 시작'을 눌러주세요.")
