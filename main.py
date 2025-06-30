from visualize import plot_transaction_network
import json
import requests
import pandas as pd
import os
from dotenv import load_dotenv
import streamlit as st
import plotly.graph_objects as go
from fetch_data import get_transactions , parse_blockcypher_transactions
from preprocess import preprocess
from detect_patterns import detect_high_frequency, detect_high_amount, detect_tumbler_pattern, detect_extortion_pattern
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
    plot_risk_scores,
    plot_transaction_network,
    plot_mini_transaction_network
)

# ✅ 블랙리스트 불러오기
def load_sanctioned_addresses(path="bitcoin_sanctioned_all.txt"):
    try:
        with open(path, "r") as f:
            return set(line.strip() for line in f if line.strip())
    except:
        return set()

# ✅ 바 그래프 시각화
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

# ✅ 레이더 차트 시각화
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

# ✅ 이상 패턴 탐지 + 점수 계산 함수
def run_analysis(df):
    df = detect_high_frequency(df)
    df = detect_high_amount(df)
    df = detect_tumbler_pattern(df)
    df = detect_extortion_pattern(df)

    freq_score = score_high_frequency(df)
    amount_score = score_high_amount(df)
    tumbler_score = score_tumbler(df)
    extortion_score = score_extortion(df)

    total_score = calculate_total_score(freq_score, amount_score, tumbler_score, extortion_score)
    return df, freq_score, amount_score, tumbler_score, extortion_score, total_score

# ✅ Streamlit 시작
st.set_page_config(page_title="Bitcoin Anomaly Detection Tool", layout="wide")
st.image("signalLogo.png", width=360)
st.title("Bitcoin Anomaly Detection Tool")
st.markdown("고려대학교 정보보호학과 · Signal Research Lab")

with st.expander("📘 도구 설명 및 한계 보기"):
    st.markdown("""
**논문 기반 정량 분석 도구**  
- 「비트코인 범죄 유형별 지갑 네트워크의 거래 패턴 분석 및 시계열-토폴로지 기반 모델링」(2025)

**✔️ 분석 기준**  
- 고빈도 반복 전송  
- 고액 이상 전송  
- 텀블링 패턴  
- 협박/사기형 패턴  

**⚠️ 무료버전 한계**  
- 실시간 mempool 불포함  
- 제재 주소 클러스터링 미완성  
    """)

with st.expander("🛡 블랙리스트 출처 보기"):
    st.markdown("""
- OFAC (미국 재무부 제재 주소)
- 김수키 등 북한 해커 조직 관련 주소
    """)

sanctioned = load_sanctioned_addresses()
address = st.text_input("📡 분석할 비트코인 주소를 입력하세요")
if st.button("🔍 거래 흐름 분석 시작"):
    if not address or address.strip() == "":
        st.info("💡 주소를 입력한 후 '분석 시작'을 눌러주세요.")
    elif address in sanctioned:
        st.error("🚨 이 주소는 블랙리스트에 포함된 고위험 주소입니다.")
        st.warning("이 주소는 OFAC 등에서 확인된 위협 또는 제재 대상입니다.")
        st.metric("📌 최종 위험 점수", "100 / 100")
    else:
        tx_json = get_transactions(address)
        tx_list = get_transactions(address)
        if not tx_list or "txs" not in tx_json:
            st.warning("❗ 트랜잭션을 불러오지 못했습니다. 주소를 다시 확인해주세요.")
        else:
            st.success(f"총 {len(tx_list)}개의 트랜잭션을 수집했습니다.")


            # 전처리 진행
            df = parse_blockcypher_transactions(tx_json)
            if df.empty:
                st.warning("⚠️ 변환된 트랜잭션 데이터가 없습니다.")
            else:
                st.subheader("🔬 전처리 결과 중간 점검")
                st.dataframe(df.head())


                if df["btc_value"].dropna().shape[0] > 0:
                    st.line_chart(df["btc_value"])  # 예시: 히스토그램 대신 라인차트도 가능
                else:
                    st.info("📭 시각화할 BTC 값이 없습니다. (btc_value 컬럼에 유효한 숫자가 없음)")










            

             # ✅ 중간 점검 (디버깅용)
           

            st.write("📌 df.describe()")
            st.code(df.describe().to_string())

            if "btc_value" in df.columns:
                st.write("📊 btc_value 분포")
                st.code(df["btc_value"].describe().to_string())
            else:
                st.warning("⚠️ 'btc_value' 컬럼이 없습니다.")

            if "address" in df.columns:
                st.write("📊 address 값 분포 (Top 10)")
                st.code(df["address"].value_counts().head(10).to_string())
            else:
                st.warning("⚠️ 'address' 컬럼이 없습니다.")

            if df.empty:
                st.error("❌ 전처리된 데이터프레임이 비어 있습니다. 파서 또는 입력 데이터에 문제가 있을 수 있습니다.")
            else:
                df, freq_score, amount_score, tumbler_score, extortion_score, total_score = run_analysis(df)




            st.divider()
            st.subheader("📊 기준별 이상 탐지 요약표")

            table_html = f"""
            <table>
              <tr><th>분석 기준</th><th>점수 (0~25)</th><th>자동 해석</th></tr>
              <tr><td>고빈도</td><td>{freq_score}</td><td>{"✅ 정상" if freq_score <= 5 else "⚠️ 반복 전송 감지"}</td></tr>
              <tr><td>고액 이상</td><td>{amount_score}</td><td>{"✅ 안정 흐름" if amount_score <= 5 else "⚠️ 고액 급증"}</td></tr>
              <tr><td>텀블러</td><td>{tumbler_score}</td><td>{"✅ 단조 흐름" if tumbler_score <= 5 else "⚠️ 변동성 있음"}</td></tr>
              <tr><td>협박 사기</td><td>{extortion_score}</td><td>{"✅ 안정 간격" if extortion_score <= 5 else "⚠️ burst 후 침묵"}</td></tr>
            </table>
            """
            st.markdown(table_html, unsafe_allow_html=True)
            st.metric("📌 참고용 위험 점수", f"{total_score} / 100")

            if total_score <= 30:
                st.success("✔️ 명확한 이상 패턴은 감지되지 않았습니다.")
            elif total_score <= 70:
                st.warning("⚠️ 일부 이상 흐름이 탐지되었습니다.")
            else:
                st.error("🚨 복수 기준에서 이상 패턴이 확인되었습니다.")

            st.subheader("📶 항목별 점수 비교 그래프")
            st.plotly_chart(plot_score_bars({
                "고빈도": freq_score,
                "고액 이상": amount_score,
                "텀블러": tumbler_score,
                "협박 사기": extortion_score
            }), use_container_width=True)

            st.subheader("🛰 레이더 차트")
            st.plotly_chart(plot_radar_chart({
                "고빈도": freq_score,
                "고액 이상": amount_score,
                "텀블러": tumbler_score,
                "협박 사기": extortion_score
            }), use_container_width=True)

            st.subheader("📈 고빈도 이상 시점 시계열")
            st.plotly_chart(
                plot_transaction_timeline(df, anomaly_col='high_freq_flag'),
                use_container_width=True
            )

            st.subheader("📋 전처리된 트랜잭션 데이터")
            st.dataframe(df)

            # ✅ 네트워크 그래프 (전체)
            if not df.empty:
                st.subheader("🌐 전체 네트워크 그래프")
                try:
                    fig_network = plot_transaction_network(tx_json["txs"])
                    if fig_network:
                        st.plotly_chart(fig_network, use_container_width=True)
                except:
                    pass  # 디버깅 문구 제거

            # ✅ 요약형 네트워크 (Top 10 주소 기준)
            if not df.empty:
                st.subheader("💎 Top 10 요약형 네트워크")
                try:
                    mini_fig = plot_mini_transaction_network(tx_json["txs"])
                    if mini_fig:
                        st.plotly_chart(mini_fig, use_container_width=True)
                except:
                    pass

                





                
