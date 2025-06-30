import requests
import os
from dotenv import load_dotenv
import pandas as pd
from dateutil.parser import parse
import streamlit as st
import json

# 환경변수 로딩
load_dotenv()
token = os.getenv("BLOCKCYPHER_TOKEN") or "93464419740141a7b00fbcb440e65595"

def get_transactions(address, limit=50):
    """
    주어진 비트코인 주소의 전체 트랜잭션 리스트 (inputs/outputs 포함)를 BlockCypher API로부터 가져옴
    네트워크 시각화에 필요한 구조를 포함함
    """
    url = f"https://api.blockcypher.com/v1/btc/main/addrs/{address}/full?limit={limit}&token={token}"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data  # 전체 응답 반환
    except Exception as e:
        st.error(f"🚨 전체 트랜잭션 API 호출 실패: {e}")
        return {}

def parse_blockcypher_transactions(raw_json):
    """
    BlockCypher에서 받은 txs 리스트(JSON)를 DataFrame으로 변환
    - confirmed: 날짜 (문자열로 변환하여 오류 방지)
    - tx_hash: 트랜잭션 해시
    - btc_value: 전송 금액 (BTC 기준)
    - address: 수신 주소
    """

    if not isinstance(raw_json, dict) or "txs" not in raw_json:
        return pd.DataFrame()

    txs = raw_json.get("txs", [])
    if len(txs) == 0:
        return pd.DataFrame()

    tx_list = []
    for tx in txs:
        tx_hash = tx.get("hash")
        confirmed = str(tx.get("confirmed")) if tx.get("confirmed") else None
        outputs = tx.get("outputs", [])

        for out in outputs:
            address_list = out.get("addresses") or []
            address = address_list[0] if address_list else None

            value_satoshi = out.get("value", None)
            if value_satoshi is None:
                continue
            try:
                btc_value = float(value_satoshi) / 1e8
            except:
                continue

            tx_list.append({
                "tx_hash": tx_hash,
                "confirmed": confirmed,
                "btc_value": btc_value,
                "address": address,
                "tx_input_n": tx.get("vin_sz"),
                "tx_output_n": tx.get("vout_sz"),
                "spent": out.get("spent_by", None)
            })

    return pd.DataFrame(tx_list)
