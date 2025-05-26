# Risk Score 계산 함수 모음 (각 기준별 0~25점 → 총합 100점 구조)

def score_high_frequency(df):
    """
    [기준 1] 고빈도 반복 전송 점수화
    - 기준: high_freq_flag == True인 트랜잭션 비율
    - 방식: 비율 × 25 → 정수화 → 최대 25점 제한
    """
    if df.empty or 'high_freq_flag' not in df.columns:
        return 0
    total = len(df)
    flagged = df['high_freq_flag'].sum()
    ratio = flagged / total if total > 0 else 0
    score = min(int(ratio * 25), 25)
    return score


def score_high_amount(df):
    """
    [기준 2] 고액 이상치 점수화
    - 기준: high_amount_flag == True인 거래 비율
    - 방식: 비율 × 25 → 정수화 → 최대 25점 제한
    """
    if df.empty or 'high_amount_flag' not in df.columns:
        return 0
    total = len(df)
    flagged = df['high_amount_flag'].sum()
    ratio = flagged / total if total > 0 else 0
    score = min(int(ratio * 25), 25)
    return score


def score_tumbler(df):
    """
    [패턴 3] 텀블러 패턴 점수화
    - 기준: tumbler_flag == True 비율
    - 방식: 비율 × 25 → 최대 25점 제한
    """
    if df.empty or 'tumbler_flag' not in df.columns:
        return 0
    ratio = df['tumbler_flag'].sum() / len(df)
    return min(int(ratio * 25), 25)


def score_extortion(df):
    """
    [패턴 4] 협박 사기 패턴 점수화
    - 기준: extortion_flag == True 비율
    - 방식: 비율 × 25 → 최대 25점 제한
    """
    if df.empty or 'extortion_flag' not in df.columns:
        return 0
    ratio = df['extortion_flag'].sum() / len(df)
    return min(int(ratio * 25), 25)


def calculate_total_score(freq_score, amount_score, tumbler_score, extortion_score):
    """
    [종합 Risk Score 계산]
    - 각 기준(4개) 점수 합산
    - 최대 100점 제한
    """
    total = freq_score + amount_score + tumbler_score + extortion_score
    return min(total, 100)
