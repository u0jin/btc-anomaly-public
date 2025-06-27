# 데이터 전처리 및 정제

import pandas as pd
from dateutil.parser import parse

def preprocess(tx_list):
    """
    BlockCypher txrefs 리스트를 받아서 분석용 DataFrame으로 전처리
    """
    if not tx_list:
        return pd.DataFrame()
    
    df = pd.DataFrame(tx_list)

    # 날짜 문자열 → datetime 변환 (Z 포함 안전 처리)
    def safe_parse(ts):
        try:
            return parse(ts)
        except:
            return pd.NaT

    if 'confirmed' in df.columns:
        df['confirmed'] = df['confirmed'].apply(safe_parse)
        df = df[df['confirmed'].notna()]  # NaT 제거
        df = df.sort_values(by='confirmed').reset_index(drop=True)

    # 사토시 → BTC 변환
    if 'value' in df.columns:
        df['btc_value'] = df['value'] / 1e8

    # 필요한 컬럼만 추출
    cols_to_keep = ['tx_hash', 'confirmed', 'btc_value', 'tx_input_n', 'tx_output_n', 'spent']
    for col in cols_to_keep:
        if col not in df.columns:
            df[col] = None

    return df[cols_to_keep]
