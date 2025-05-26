import pandas as pd

def identify_ransomware_pattern(df, value_z=2.5, time_gap_min=10):
    """
    랜섬웨어 패턴 탐지:
    - 고액 전송 (z-score > 2.5)
    - 짧은 시간 간격 (10분 이내)
    """
    if df.empty or 'btc_value' not in df.columns or 'confirmed' not in df.columns:
        return pd.DataFrame()

    df = df.copy()
    df = df.sort_values('confirmed')
    df['time_diff_min'] = df['confirmed'].diff().dt.total_seconds() / 60.0

    mean_val = df['btc_value'].mean()
    std_val = df['btc_value'].std()
    df['z_score'] = (df['btc_value'] - mean_val) / std_val

    df['ransomware_flag'] = (df['z_score'] > value_z) & (df['time_diff_min'] < time_gap_min)

    return df[['tx_hash', 'confirmed', 'btc_value', 'time_diff_min', 'z_score', 'ransomware_flag']]


def identify_sextortion_pattern(df, avg_gap_min=60, burst_threshold=5):
    """
    섹스토션 패턴 탐지:
    - 전반적으로 거래 간격이 김 (평균 간격 ≥ avg_gap_min)
    - 특정 시점에 burst 발생 (1분 내 burst_threshold건 이상)
    """
    if df.empty or 'confirmed' not in df.columns:
        return pd.DataFrame()

    df = df.sort_values('confirmed').copy()

    df['time_diff'] = df['confirmed'].diff().dt.total_seconds() / 60.0
    avg_gap = df['time_diff'].mean()

    df = df.set_index('confirmed')
    df['rolling_count'] = df['tx_hash'].rolling('1min').count()
    df = df.reset_index()

    df['sextortion_flag'] = (avg_gap >= avg_gap_min) & (df['rolling_count'] >= burst_threshold)

    return df[['tx_hash', 'confirmed', 'btc_value', 'time_diff', 'rolling_count', 'sextortion_flag']]


def identify_tumbler_pattern(df, std_threshold_val=0.0002, std_threshold_time=5.0, burst_z=2.5, burst_count=4):
    """
    텀블러 패턴 탐지:
    - 거래 금액과 간격이 일정 (표준편차 매우 작음)
    - 특정 시점에서 급등 거래 또는 burst 발생
    """
    if df.empty or 'btc_value' not in df.columns or 'confirmed' not in df.columns:
        return pd.DataFrame()

    df = df.sort_values('confirmed').copy()

    df['time_diff'] = df['confirmed'].diff().dt.total_seconds() / 60.0

    std_val = df['btc_value'].std()
    std_time = df['time_diff'].std()
    mean_val = df['btc_value'].mean()
    df['z_score'] = (df['btc_value'] - mean_val) / std_val if std_val > 0 else 0

    df = df.set_index('confirmed')
    df['rolling_count'] = df['tx_hash'].rolling('1min').count()
    df = df.reset_index()

    df['tumbler_flag'] = (
        (std_val < std_threshold_val) &
        (std_time < std_threshold_time) &
        ((df['z_score'].abs() > burst_z) | (df['rolling_count'] >= burst_count))
    )

    return df[['tx_hash', 'confirmed', 'btc_value', 'time_diff', 'z_score', 'rolling_count', 'tumbler_flag']]


def identify_extortion_pattern(df, burst_threshold=3, gap_threshold=100, std_threshold=20):
    """
    협박 사기 패턴 탐지:
    - 시간 간격 분산이 큼
    - 특정 시점에 burst 발생
    - 이후 긴 공백 존재
    """
    if df.empty or 'confirmed' not in df.columns:
        return pd.DataFrame()

    df = df.sort_values('confirmed').copy()

    df['time_diff'] = df['confirmed'].diff().dt.total_seconds() / 60.0
    std_time = df['time_diff'].std()

    df = df.set_index('confirmed')
    df['rolling_count'] = df['tx_hash'].rolling('1min').count()
    df = df.reset_index()

    df['extortion_flag'] = (
        (std_time >= std_threshold) &
        (df['rolling_count'] >= burst_threshold) &
        (df['time_diff'] >= gap_threshold)
    )

    return df[['tx_hash', 'confirmed', 'btc_value', 'time_diff', 'rolling_count', 'extortion_flag']]
