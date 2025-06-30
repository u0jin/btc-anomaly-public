import pandas as pd
import streamlit as st

# 이상 탐지 1: 고빈도 반복 전송 (기준 완화)
def detect_high_frequency(df, threshold_per_min=2):
    if df.empty or 'confirmed' not in df.columns or 'tx_hash' not in df.columns:
        df['high_freq_flag'] = False
        return df

    df = df.sort_values('confirmed')
    df['confirmed'] = pd.to_datetime(df['confirmed'])

    df.set_index('confirmed', inplace=True)
    rolling_count = df['tx_hash'].resample('1min').count()
    df['rolling_count'] = rolling_count.reindex(df.index, method='ffill').fillna(0)

    df['high_freq_flag'] = df['rolling_count'] > threshold_per_min
    df.reset_index(inplace=True)
    return df

# 이상 탐지 2: 고액 이상치 전송 (기준 완화)
def detect_high_amount(df, z_threshold=0.5):
    if df.empty or 'btc_value' not in df.columns:
        df['high_amount_flag'] = False
        return df

    mean = df['btc_value'].mean()
    std = df['btc_value'].std()

    if std == 0 or pd.isna(std):
        df['high_amount_flag'] = False
    else:
        df['z_score'] = (df['btc_value'] - mean) / std
        df['high_amount_flag'] = df['z_score'].abs() > z_threshold
    return df



# 이상 탐지 3: 텀블러 패턴
def detect_tumbler_pattern(df):
    if df.empty or 'confirmed' not in df.columns or 'btc_value' not in df.columns:
        df['tumbler_flag'] = 0
        return df
    df = df.sort_values('confirmed')
    df['interval_diff'] = df['confirmed'].diff().dt.total_seconds().fillna(0)
    df['tumbler_flag'] = ((df['btc_value'] > 0.05) & (df['interval_diff'].abs() > 30)).astype(int)
    return df

# 이상 탐지 4: 협박/사기 패턴
def detect_extortion_pattern(df):
    if 'confirmed' not in df.columns or df['confirmed'].isnull().all():
        df['extortion_flag'] = 0
        return df
    df = df.sort_values('confirmed')
    df['interval_diff'] = df['confirmed'].diff().dt.total_seconds().fillna(0)
    df['extortion_flag'] = (df['interval_diff'] > 120).astype(int)
    return df

# 점수 계산 함수들
def score_high_frequency(df):
    if df.empty or 'high_freq_flag' not in df.columns:
        return 0
    ratio = df['high_freq_flag'].sum() / len(df)
    return min(int(ratio * 25), 25)

def score_high_amount(df):
    if df.empty or 'high_amount_flag' not in df.columns:
        return 0
    ratio = df['high_amount_flag'].sum() / len(df)
    return min(int(ratio * 25), 25)

def score_tumbler(df):
    if df.empty or 'tumbler_flag' not in df.columns:
        return 0
    ratio = df['tumbler_flag'].sum() / len(df)
    return min(int(ratio * 25), 25)

def score_extortion(df):
    if df.empty or 'extortion_flag' not in df.columns:
        return 0
    ratio = df['extortion_flag'].sum() / len(df)
    return min(int(ratio * 25), 25)

def calculate_total_score(freq_score, amount_score, tumbler_score, extortion_score):
    return min(freq_score + amount_score + tumbler_score + extortion_score, 100)

def run_analysis(df):
    st.subheader("📦 데이터 구조 확인")
    st.write(df.head(3))
    st.write("컬럼:", df.columns.tolist())
    st.write("데이터 타입:", df.dtypes)

    df['confirmed'] = pd.to_datetime(df['confirmed'], errors='coerce')

    if df['confirmed'].isnull().all():
        st.error("❌ 모든 confirmed 값이 datetime으로 변환되지 않았습니다.")
        return df, 0, 0, 0, 0, 0

    # btc_value 자동 생성
    if 'btc_value' not in df.columns:
        if 'total' in df.columns:
            df['btc_value'] = df['total'] / 1e8
            st.warning("⚠️ 'btc_value'가 없어 'total'을 기반으로 자동 생성했습니다.")
        else:
            df['btc_value'] = 0.0
            st.error("❌ 'btc_value'와 'total' 모두 없어 0으로 처리되었습니다.")

    # 간격 계산
    df = df.sort_values('confirmed')
    df['interval_diff'] = df['confirmed'].diff().dt.total_seconds().fillna(0)

    st.write("✅ [Debug] 날짜 및 간격 계산 완료")
    st.dataframe(df[['confirmed', 'btc_value', 'interval_diff']].head())
    st.write("📊 [Check] btc_value 통계", df['btc_value'].describe())

    # ✅ high_freq_flag 디버깅
    df = detect_high_frequency(df)
    if 'high_freq_flag' in df.columns:
        st.write("✅ [Debug] high_freq_flag 분포", df['high_freq_flag'].value_counts(dropna=False))
    else:
        st.warning("⚠️ high_freq_flag 컬럼이 생성되지 않았습니다.")

    # ✅ high_amount_flag 디버깅
    df = detect_high_amount(df)
    if 'high_amount_flag' in df.columns:
        st.write("✅ [Debug] high_amount_flag 분포", df['high_amount_flag'].value_counts(dropna=False))
        st.write("📊 [Debug] z-score 예시", df[['btc_value', 'z_score']].head())
    else:
        st.warning("⚠️ high_amount_flag 컬럼이 생성되지 않았습니다.")

    # ✅ tumbler_flag 디버깅
    df = detect_tumbler_pattern(df)
    if 'tumbler_flag' in df.columns:
        st.write("✅ [Debug] tumbler_flag 분포", df['tumbler_flag'].value_counts(dropna=False))
    else:
        st.warning("⚠️ tumbler_flag 컬럼이 생성되지 않았습니다.")

    # ✅ extortion_flag 디버깅
    df = detect_extortion_pattern(df)
    if 'extortion_flag' in df.columns:
        st.write("✅ [Debug] extortion_flag 분포", df['extortion_flag'].value_counts(dropna=False))
    else:
        st.warning("⚠️ extortion_flag 컬럼이 생성되지 않았습니다.")

    # 점수 계산
    freq_score = score_high_frequency(df)
    amount_score = score_high_amount(df)
    tumbler_score = score_tumbler(df)
    extortion_score = score_extortion(df)
    total_score = calculate_total_score(freq_score, amount_score, tumbler_score, extortion_score)

    st.success(f"🎯 [Score] Freq: {freq_score} | Amount: {amount_score} | Tumbler: {tumbler_score} | Extortion: {extortion_score} | Total: {total_score}")

    return df, freq_score, amount_score, tumbler_score, extortion_score, total_score
