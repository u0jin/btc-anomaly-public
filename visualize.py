# Plotly 시각화 함수

import plotly.express as px
import plotly.graph_objects as go

def plot_transaction_timeline(df, anomaly_col=None):
    """
    ⏱ 거래 시간축 시각화
    - X축: confirmed (거래 시간)
    - Y축: btc_value (거래 금액)
    - anomaly_col이 지정되면 해당 이상 거래를 색상으로 구분
    """
    if df.empty or 'confirmed' not in df.columns or 'btc_value' not in df.columns:
        return None

    # 데이터 복사 및 시간 기준 정렬
    plot_df = df.copy()
    plot_df = plot_df.sort_values('confirmed')

    # 이상 여부에 따라 색상 구분
    if anomaly_col and anomaly_col in df.columns:
        plot_df['anomaly'] = plot_df[anomaly_col].map({True: '이상', False: '정상'})
    else:
        plot_df['anomaly'] = '거래'

    # Plotly 시각화
    fig = px.scatter(
        plot_df,
        x='confirmed',
        y='btc_value',
        color='anomaly',
        title='비트코인 거래 시간축 시각화',
        labels={'confirmed': '시간', 'btc_value': 'BTC 금액'},
        height=400
    )

    return fig


def plot_risk_scores(score_dict):
    """
    📊 기준별 위험 점수 막대그래프
    - 입력: {"기준명": 점수, ...} 형태의 dict
    - 출력: Plotly Bar Chart로 시각화
    - 각 기준은 0~25점 사이의 정량 점수
    """
    if not score_dict:
        return None

    categories = list(score_dict.keys())   # 기준명 (ex: 고빈도, 고액 이상치)
    values = list(score_dict.values())     # 점수

    # Plotly Bar 시각화 생성
    fig = go.Figure(data=[
        go.Bar(x=categories, y=values, marker_color='indianred')
    ])

    fig.update_layout(
        title='기준별 위험 점수 분포',
        xaxis_title='분석 기준',
        yaxis_title='점수 (0 ~ 25)',
        yaxis=dict(range=[0, 25]),
        height=400
    )

    return fig
