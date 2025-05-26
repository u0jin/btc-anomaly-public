# BlockCypher API 연결

import requests
import os
from dotenv import load_dotenv

# .env 파일에서 환경변수 불러오기 (로컬 실행 시 사용됨)
load_dotenv()

# 배포 시에는 환경변수 없을 수 있으므로 fallback 값을 넣어둠
token = os.getenv("BLOCKCYPHER_TOKEN") or "BLOCKCYPHER_TOKEN"

def get_transactions(address, limit=50):
    """
    주어진 비트코인 주소의 최근 트랜잭션 정보를 BlockCypher API에서 가져옴
    """
    url = f"https://api.blockcypher.com/v1/btc/main/addrs/{address}?limit={limit}&includeHex=false&token={token}"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        return data.get("txrefs", [])
    except Exception as e:
        print("🚨 API 호출 실패:", e)
        return []
