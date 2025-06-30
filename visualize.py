# visualize.py

import plotly.express as px
import plotly.graph_objects as go
import networkx as nx

def plot_transaction_timeline(df, anomaly_col=None):
    """
    ⏱ 거래 시간축 시각화
    - X축: confirmed (거래 시간)
    - Y축: btc_value (거래 금액)
    - anomaly_col이 지정되면 해당 이상 거래를 색상으로 구분
    """
    if df.empty or 'confirmed' not in df.columns or 'btc_value' not in df.columns:
        return None

    plot_df = df.copy()
    plot_df = plot_df.sort_values('confirmed')

    if anomaly_col and anomaly_col in df.columns:
        plot_df['anomaly'] = plot_df[anomaly_col].map({True: '이상', False: '정상'})
    else:
        plot_df['anomaly'] = '거래'

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

    categories = list(score_dict.keys())
    values = list(score_dict.values())

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


def extract_edges_from_tx_list(tx_list):
    """
    트랜잭션 리스트에서 송신자 → 수신자 관계 추출
    """
    edges = []

    for tx in tx_list:
        inputs = tx.get("inputs", [])
        outputs = tx.get("outputs", [])
        if not inputs or not outputs:
            continue

        senders = []
        for i in inputs:
            addr_list = i.get("addresses", [])
            if isinstance(addr_list, list) and addr_list:
                senders.append(addr_list[0])  # 첫 번째 주소만 사용

        for o in outputs:
            addr_list = o.get("addresses", [])
            value = o.get("value", 0)
            if isinstance(addr_list, list) and addr_list:
                receiver = addr_list[0]
                for sender in senders:
                    edges.append((sender, receiver, value))

    return edges




def plot_transaction_network(tx_list):
    """
    📡 거래 네트워크 시각화 (Plotly + NetworkX)
    - 노드: 주소
    - 엣지: 거래 흐름
    """
    edges = extract_edges_from_tx_list(tx_list)
    if not edges:
        return None

    G = nx.DiGraph()
    for src, dst, value in edges:
        G.add_edge(src, dst, weight=value)

    pos = nx.spring_layout(G, seed=42)

    edge_x, edge_y = [], []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=0.5, color='#888'),
        hoverinfo='none',
        mode='lines'
    )

    node_x, node_y, text = [], [], []
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        text.append(node)

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        text=text,
        textposition='top center',
        hoverinfo='text',
        marker=dict(
            showscale=False,
            color='skyblue',
            size=10,
            line_width=2
        )
    )

    # ✅ 이 줄이 누락되어 있었음
    fig = go.Figure(data=[edge_trace, node_trace],
                    layout=go.Layout(
                        title=dict(text='📡 거래 네트워크 시각화', font=dict(size=16)),
                        showlegend=False,
                        margin=dict(l=20, r=20, t=40, b=20),
                        hovermode='closest',
                        height=600
                    ))

    return fig




def plot_mini_transaction_network(tx_list, max_edges=10):
    """
    🎨 간단하고 예쁜 미니 네트워크 시각화 (Top N edges)
    - 단순 요약 목적
    """
    edges = extract_edges_from_tx_list(tx_list)
    if not edges:
        return None

    # 금액 기준으로 상위 max_edges 추출
    sorted_edges = sorted(edges, key=lambda x: x[2], reverse=True)[:max_edges]

    G = nx.DiGraph()
    for src, dst, value in sorted_edges:
        G.add_edge(src, dst, weight=value)

    pos = nx.spring_layout(G, seed=1, k=0.8)

    edge_x, edge_y = [], []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=2, color='#CBD5E0'),
        hoverinfo='none',
        mode='lines'
    )

    node_x, node_y, labels = [], [], []
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        labels.append(node[:6] + '...' + node[-4:])  # 주소 축약

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        text=labels,
        textposition='bottom center',
        hoverinfo='text',
        marker=dict(
            size=20,
            color='lightskyblue',
            line=dict(width=2, color='gray')
        )
    )

    fig = go.Figure(data=[edge_trace, node_trace],
                    layout=go.Layout(
                        title=dict(text='💎 상위 거래 요약 네트워크', font=dict(size=16)),
                        showlegend=False,
                        margin=dict(l=20, r=20, t=40, b=20),
                        hovermode='closest',
                        height=500
                    ))

    return fig
