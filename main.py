# Streamlit UI 진입점

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
# UI 스타일 개선 – 전문적이고 신뢰감 있는 디자인 적용
# ──────────────────────────────────────────────
st.markdown("""
<style>
    html, body, .main, .block-container {
        background-color: #ffffff;
        color: #1c1c1e;
        font-family: 'Apple SD Gothic Neo', 'Roboto', sans-serif;
        font-size: 16px;
    }
    .title {
        font-size: 36px;
        font-weight: 700;
        color: #5e0000;
        margin-top: 0.5em;
    }
    .subtitle {
        font-size: 20px;
        font-weight: 400;
        color: #333333;
    }
    .badge {
        font-size: 15px;
        color: #777777;
        margin-bottom: 20px;
    }
    a {
        color: #5e0000;
        font-weight: 500;
    }
    a:hover {
        text-decoration: underline;
    }
    .stButton>button {
        background-color: #5e0000;
        color: white;
        border: none;
        border-radius: 6px;
        padding: 0.6em 1.2em;
        font-size: 16px;
        font-weight: 600;
        transition: 0.2s ease-in-out;
    }
    .stButton>button:hover {
        background-color: #7b0000;
    }
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────
# 헤더: 연구실 정보 및 프로젝트 타이틀
# ──────────────────────────────────────────────
st.image("signalLogo.png", width=360)
st.markdown('<div class="title">Bitcoin Anomaly Detection Tool</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">고려대학교 정보보호학과 · Signal Research Lab</div>', unsafe_allow_html=True)
st.markdown('<div class="badge">논문 기반 · 트랜잭션 흐름 분석 도구 · 실시간 이상 탐지</div>', unsafe_allow_html=True)
st.markdown("[🌐 Signal Lab 홈페이지 바로가기](https://signal.korea.ac.kr/home)")

st.info("이 도구는 '비트코인 범죄 유형별 지갑 네트워크의 거래 패턴 분석 및 시계열-토폴로지 기반 모델링' 논문을 기반으로 구축된 무료 공개 버전입니다. 정량화된 4가지 이상 거래 기준(랜섬웨어, 섹스토션, 텀블러, 협박 사기)을 실제 구현하여 시각화하지만, 이 버전은 무료 API 기반으로 작동하며 다음과 같은 한계가 존재합니다:")

st.markdown("""
- 📉 실시간 mempool 데이터 분석 불가
- 🧩 토폴로지 기반의 네트워크 연결 관계 미포함
- 🔕 알려진 블랙리스트 주소와의 연결성 탐색 제외
- ⚠️ 일부 알려진 패턴(예: 저빈도 burst 계좌) 감지율 제한
- 🔓 탐지 기준은 보수적이며 false-negative 가능성 존재

> 해당 한계는 고급 유료 버전에서 확장 구현될 예정입니다.
""")

# 추가 시각적 안내: 기준별 정상 vs 이상 흐름 예시 설명
st.markdown("""
### 📊 기준 예시 시각 안내

| 기준 항목 | 정상 거래 흐름 예시 | 이상 거래 흐름 예시 |
|-----------|------------------|---------------------|
| 고빈도 전송 | 하루 3~4건 거래 분포 | 1분 내 3건 이상 집중 거래 |
| 고액 이상치 | 일정한 송금액 범위 유지 |突발적 고액 전송 (예: 50배 초과) |
| 텀블러 패턴 | 정기적인 입출금 또는 균일 간격 흐름 | 동일 금액 반복 후 급격한 시간 변동 |
| 협박 사기 | 간헐적이고 장기 간격 거래 | 특정 시점 burst 이후 장시간 침묵 |

> 이 도구는 위 기준을 기반으로 거래 흐름을 수치화하고 이상성을 시각적으로 표시합니다.
""")


# ──────────────────────────────────────────────
# 언어 텍스트 정의 (단일 한국어 모드)
# ──────────────────────────────────────────────
L = {
    "input_title": "### 📡 분석할 비트코인 주소를 입력하세요",
    "input_placeholder": "예: 1BoatSLRHtKNngkdXEeobR76b53LETtpyT",
    "button": "🔍 거래 흐름 분석 시작",
    "fetch_fail": "❗ 트랜잭션을 불러오지 못했습니다. 주소를 다시 확인해주세요.",
    "no_input": "💡 주소를 입력한 후 '분석 시작'을 눌러주세요.",
    "tx_success": "총 {count}개의 트랜잭션을 수집했습니다.",
    "section_scores": "📊 기준별 이상 탐지 결과",
    "total_score": "🔐 총 위험 점수",
    "most_match": "✅ 이 주소는 **{type}** 유형의 흐름과 가장 유사합니다.",
    "no_match": "⚠️ 일치하는 범죄 유형이 발견되지 않았습니다.",
    "time_chart": "⏱ 거래 시간축 흐름 시각화",
    "tx_table": "📋 전체 전처리 트랜잭션",
    "score_guide": "#### 📘 점수화 방식 설명\n각 항목별로 0~25점 범위의 위험 점수를 부여하며, 총합 100점을 기준으로 이상 가능성을 평가합니다.\n- 고빈도 반복 전송: 단위 시간 내 빈도 증가 여부 (ex. 1분 내 3건 이상)\n- 고액 이상치: z-score > 2.5 이상일 때 이상치로 판단\n- 텀블러: 동일 금액/간격 패턴 반복 + 급변 시 탐지\n- 협박 사기: 단기 burst 이후 장기 침묵 패턴 등"
}

# ──────────────────────────────────────────────
# 주소 입력창
# ──────────────────────────────────────────────
st.markdown(L["input_title"])
address = st.text_input(L["input_placeholder"])

if st.button(L["button"]):
    if address:
        tx_list = get_transactions(address)
        if tx_list:
            st.success(L["tx_success"].format(count=len(tx_list)))

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

            st.divider()
            st.subheader(L["section_scores"])

            col1, col2, col3, col4 = st.columns(4)
            col1.metric("고빈도", f"{freq_score} / 25")
            col2.metric("고액 이상", f"{amount_score} / 25")
            col3.metric("텀블러", f"{tumbler_score} / 25")
            col4.metric("협박 사기", f"{extortion_score} / 25")

            st.metric(L["total_score"], f"{total_score} / 100")
            st.plotly_chart(plot_risk_scores({
                "고빈도": freq_score,
                "고액 이상": amount_score,
                "텀블러": tumbler_score,
                "협박 사기": extortion_score
            }), use_container_width=True)

            pattern_scores = {
                '🛑 랜섬웨어': int(ransomware_hits),
                '🚨 섹스토션': int(sextortion_hits),
                '🔁 텀블러': int(tumbler_score),
                '📦 협박 사기': int(extortion_score)
            }
            pattern_scores = {k: v for k, v in pattern_scores.items() if v > 0}

            st.subheader("🧠 범죄 흐름 자동 분류 결과")
            if pattern_scores:
                most_likely = max(pattern_scores, key=pattern_scores.get)
                st.success(L["most_match"].format(type=most_likely))
            else:
                st.info(L["no_match"])

            st.subheader(L["time_chart"])
            st.plotly_chart(
                plot_transaction_timeline(freq_result, anomaly_col='high_freq_flag'),
                use_container_width=True
            )

            st.subheader(L["tx_table"])
            st.dataframe(df)

            st.divider()
            st.markdown(L["score_guide"])
        else:
            st.warning(L["fetch_fail"])
    else:
        st.info(L["no_input"])
