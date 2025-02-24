# api_client.py
import requests
from datetime import datetime, timedelta


class APIClient:
    def __init__(self,  client_api_key, client_id, client_secret):
        self.BASE_URL = "https://openapi.playauto.io/api"
        self.client_api_key = client_api_key
        self.client_id = client_id
        self.client_secret = client_secret
        self.token = None

    def get_token(self):
        url = f"{self.BASE_URL}/auth"
        headers = {
            "Content-Type": "application/json; charset=UTF-8",
            "x-api-key": self.client_api_key,
        }
        body = {
            "email": self.client_id,
            "password": self.client_secret,
        }

        response = requests.post(url, headers=headers, json=body)

        if response.status_code == 200:
            self.token = response.json()[0].get("token")
            return self.token
        else:
            raise Exception(f"Failed to obtain token. {response.status_code}")

    def get_data(self, endpoint, search_word):
        if not self.token:
            self.get_token()
        
        url = f"{self.BASE_URL}/{endpoint}"

        headers = {
            "Content-Type": "application/json; charset=UTF-8",
            "x-api-key": self.client_api_key,
            "Authorization": f"Token {self.token}",
        }
        # 현재 날짜를 기준으로 3개월 전 날짜 계산
        three_months_ago = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
        # 내일 날짜 계산
        tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')

        body = {
            "sdate": three_months_ago,  # 3개월 전 날짜
            "edate": tomorrow,  # 내일 날짜
            "start": 0,
            "length": 500,
            "date_type": "wdate",
            "status": ["ALL"],
            "multi_type": "invoice_no",
            "multi_search_word": search_word,
        }
        response = requests.post(url, headers=headers, json=body)
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 401:
            # Token might be expired, try to get a new one
            self.get_token()
            headers = {
                "Content-Type": "application/json; charset=UTF-8",
                "x-api-key": self.client_api_key,
                "Authorization": f"Token {self.token}",
            }            
            response = requests.post(url, headers=headers, json=body)

            if response.status_code == 200:
                return response.json()
        
        raise Exception(f"Failed to get data: {response.status_code}")
    
    def process_data(self, order_list):

        # results와 results_prod 배열 추출
        results = order_list.get('results', [])
        results_prod = order_list.get('results_prod', [])

        # uniq 필드를 키로 사용하여 results를 딕셔너리로 변환
        results_dict = {item['uniq']: item for item in results}

        # 조인된 데이터를 저장할 리스트
        joined_data = []

        # results_prod의 각 항목에 대해 results와 조인
        for prod in results_prod:
            uniq = prod.get('uniq')
            if uniq in results_dict:
                joined_item = {**results_dict[uniq], **prod}
                joined_data.append(joined_item)

        # 필요한 필드만 추출하여 리스트로 변환
        return [(item['shop_sale_name'], item['sku_cd'], item['stock_cd'], item['stock_cnt_real']) for item in joined_data]
