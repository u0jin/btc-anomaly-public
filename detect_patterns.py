# 4가지 이상 거래 탐지 로직

import pandas as pd

def detect_high_frequency(df, threshold_per_min=5):
    """
    confirmed 기준으로 1분 단위 내 발생한 트랜잭션 수 계산 후,
    threshold를 넘는 경우 이상 거래로 간주
    """
    if df.empty or 'confirmed' not in df.columns:
        return pd.DataFrame()

    # 시간 기준 정렬
    df = df.sort_values('confirmed')

    # 시간 인덱스 설정
    df = df.set_index('confirmed')

    # 1분 rolling count 계산
    df['rolling_count'] = df['tx_hash'].rolling('1min').count()

    # 이상 여부 판단
    df['high_freq_flag'] = df['rolling_count'] > threshold_per_min

    # 인덱스 복구
    df = df.reset_index()

    return df[['tx_hash', 'confirmed', 'btc_value', 'rolling_count', 'high_freq_flag']]

def detect_high_amount(df, z_threshold=2.0):
    mean = df['btc_value'].mean()
    std = df['btc_value'].std()
    df['z_score'] = (df['btc_value'] - mean) / std
    df['high_amount_flag'] = df['z_score'].abs() > z_threshold
    return df
