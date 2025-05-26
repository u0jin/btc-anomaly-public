# 🧠 Bitcoin Anomaly Detection Tool (Free Version)

> 논문 기반 비트코인 이상 거래 탐지 · 시계열 기반 분석 시스템  
> 고려대학교 Signal Research Lab ｜ 무료 공개 Streamlit 버전

---

## 📘 개요

본 도구는 논문  
**“비트코인 범죄 유형별 지갑 네트워크의 거래 패턴 분석 및 시계열-토폴로지 기반 모델링”**  
의 실험 모델을 기반으로 구축된 실습형 분석 도구입니다.

- 📊 거래 시계열 기반 이상 거래 탐지
- 🧠 범죄 유형 자동 분류 (랜섬웨어, 섹스토션, 텀블러, 협박 사기)
- 📈 직관적 Plotly 시각화
- 💡 학술/교육/연구실 배포용으로 설계

---

## 🔍 분석 대상 범죄 유형

| 유형         | 정의 요약 |
|--------------|-----------|
| 🛑 랜섬웨어   | 고액 송금 + 짧은 시간 간격 |
| 🚨 섹스토션   | 저빈도 흐름 + 특정 시점 burst |
| 🔁 텀블러     | 반복 금액 전송 + 급격한 간격 변화 |
| 📦 협박 사기 | burst 이후 장시간 공백 발생 |

---

## ⚙️ 주요 기능

| 기능                | 설명 |
|---------------------|------|
| ✅ 주소 입력 기반 실시간 분석 | BlockCypher API로 트랜잭션 수집 |
| 🧪 이상 패턴 탐지 알고리즘   | 논문 기반 정량 기준 적용 |
| 📊 0~100점 위험도 점수화     | 항목별 25점씩 총합 계산 |
| 📈 Plotly 시각화            | 시계열 그래프 + 점수 그래프 출력 |
| 🧠 범죄 유형 자동 분류       | 가장 유사한 흐름 판단 |
| 📘 기준 설명 + 예시 비교     | 정상/이상 흐름 시각 비교 테이블 제공 |

---

## ⚠️ 한계 (무료 버전)

- 실시간 mempool 분석 ❌
- 네트워크 토폴로지 구조 탐지 ❌
- 블랙리스트 주소 대조 탐지 ❌
- 일부 저빈도 패턴 감지 누락 가능성 있음

> 위 기능은 향후 고급 유료 버전에서 확장될 예정입니다.

---

## 🛠 실행 방법

1. **패키지 설치**

```bash
pip install -r requirements.txt
''
BLOCKCYPHER_TOKEN=your_api_token
Streamlit 실행

bash
복사
편집
streamlit run main.py



---

## 
📂 프로젝트 구조
bash
복사
편집
btc_anomaly_free/
├── main.py                    # Streamlit 진입점
├── fetch_data.py              # API 연결
├── preprocess.py              # 전처리
├── detect_patterns.py         # 고빈도/고액 탐지
├── pattern_identifier.py      # 4가지 패턴 탐지
├── calculate_score.py         # 점수화 함수
├── visualize.py               # Plotly 시각화
├── .env (gitignore)           # API 키 보관용
├── requirements.txt
└── README.md
📫 문의 및 기여
이 도구는 고려대학교 정보보호학과 연구 목적과 학술 활용을 위해 제작되었습니다.
기여를 원하시는 분은 이슈를 남겨주세요.

