
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

# 블랙리스트 불러오기
def load_sanctioned_addresses(path="bitcoin_sanctioned_all.txt"):
    try:
        with open(path, "r") as f:
            return set(line.strip() for line in f if line.strip())
    except:
        return set()

def plot_score_bars(scores):
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
        height=400
    )
    return fig

def plot_radar_chart(scores):
    categories = list(scores.keys())
    values = list(scores.values()) + [list(scores.values())[0]]
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories + [categories[0]],
        fill='toself',
        name='위험 점수'
    ))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 25])),
        showlegend=False,
        height=450,
        title="📡 위험 항목별 정량 구성 (레이더 차트)"
    )
    return fig

st.set_page_config(page_title="Bitcoin Anomaly Detection Tool", layout="wide")
st.image("signalLogo.png", width=360)
st.title("Bitcoin Anomaly Detection Tool")
st.markdown("고려대학교 정보보호학과 · Signal Research Lab")

with st.expander("📘 도구 설명 및 한계 보기"):
    st.markdown("""
본 분석 도구는 논문  
**「비트코인 범죄 유형별 지갑 네트워크의 거래 패턴 분석 및 시계열-토폴로지 기반 모델링」(2025)**  
을 기반으로 정량 탐지 기준에 따라 거래 흐름을 분석합니다.

---

**✔️ 구성 방식**

- 총 4가지 기준 (고빈도, 고액 이상, 텀블러, 협박 사기)
- 항목당 25점, 총합 100점 점수화
- 점수 + 시계열 + 해석 제공

---

**⚠️ 무료 버전 한계**

- 실시간 mempool 분석 미포함
- 블랙리스트 클러스터링은 향후 확장 예정
    """)

with st.expander("🛡 블랙리스트 출처 보기"):
    st.markdown("""
- OFAC (미국 재무부 제재 주소)
- 김수키 관련 북한 연계 해커 조직 주소
    """)

sanctioned = load_sanctioned_addresses()
address = st.text_input("📡 분석할 비트코인 주소를 입력하세요")

if st.button("🔍 거래 흐름 분석 시작"):
    if not address:
        st.info("💡 주소를 입력한 후 '분석 시작'을 눌러주세요.")
    else:
        if address in sanctioned:
            st.error("🚨 이 주소는 블랙리스트에 포함된 고위험 주소입니다.")
            st.warning("이 주소는 OFAC/TRM/김수키 등에서 확인된 위협 또는 제재 대상입니다.")
            st.metric("📌 최종 위험 점수", "100 / 100")
        else:
            tx_list = get_transactions(address)
            if not tx_list:
                st.warning("❗ 트랜잭션을 불러오지 못했습니다. 주소를 다시 확인해주세요.")
            else:
                st.success(f"총 {len(tx_list)}개의 트랜잭션을 수집했습니다.")
                df = preprocess(tx_list)
                freq_result = detect_high_frequency(df)
                freq_score = score_high_frequency(freq_result)
                amount_result = detect_high_amount(df)
                amount_score = score_high_amount(amount_result)
                tumbler_score = score_tumbler(identify_tumbler_pattern(df))
                extortion_score = score_extortion(identify_extortion_pattern(df))
                total_score = calculate_total_score(freq_score, amount_score, tumbler_score, extortion_score)

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

                if total_score <= 30:
                    st.success("✔️ 명확한 이상 패턴은 감지되지 않았습니다.")
                    st.caption("예시 흐름: 정기적 입출금, 일반 개인 지갑 사용 패턴 등")
                elif total_score <= 70:
                    st.warning("⚠️ 일부 기준에서 이상 흐름과 유사한 움직임이 감지되었습니다.")
                    st.caption("예시 흐름: 수차례 일정 간격 전송, 일시적 고액 트랜잭션 등")
                else:
                    st.error("🚨 복수 기준에서 이상 흐름이 확인되었습니다.")
                    st.caption("예시 흐름: 고액 집중, 간격 급변, burst 후 침묵 등")

                st.subheader("📶 항목별 점수 비교 그래프")
                st.plotly_chart(plot_score_bars({
                    "고빈도": freq_score,
                    "고액 이상": amount_score,
                    "텀블러": tumbler_score,
                    "협박 사기": extortion_score
                }), use_container_width=True)

                st.subheader("🛰 위험 항목별 정량 구성 (레이더 차트)")
                st.plotly_chart(plot_radar_chart({
                    "고빈도": freq_score,
                    "고액 이상": amount_score,
                    "텀블러": tumbler_score,
                    "협박 사기": extortion_score
                }), use_container_width=True)

                st.subheader("📈 고빈도 이상 시점 시계열")
                st.caption("시간 흐름에 따른 거래 패턴을 나타냅니다. 붉은 점은 짧은 간격 내 반복 전송을 의미합니다.")
                st.plotly_chart(
                    plot_transaction_timeline(freq_result, anomaly_col='high_freq_flag'),
                    use_container_width=True
                )

                st.subheader("📋 분석 대상 트랜잭션 (전처리 후 데이터)")
                st.caption("""
이 표는 BlockCypher API에서 수집한 원본 트랜잭션을 분석에 적합하도록 가공한 결과입니다.  
시간 정보는 datetime 형식으로 변환되었고, 금액 단위는 Satoshi → BTC로 통일되었으며  
이상 탐지 기준(high_freq_flag, high_amount_flag 등)이 부여되어 각 거래의 이상 여부를 플래그로 확인할 수 있습니다.
                """)
                st.dataframe(df)
