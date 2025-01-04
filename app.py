# Copyright 2021 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import signal
import sys
from types import FrameType

from flask import Flask, render_template, request, jsonify

from utils.logging import logger

from api_client import APIClient

from dotenv import load_dotenv
import os


app = Flask(__name__)

load_dotenv()  # .env 파일 로드

# 환경 변수에서 API 키, 이메일, 비밀번호 가져오기
API_KEY = os.getenv('PLTO_API_KEY')
EMAIL = os.getenv('PLTO_ID')
PASSWORD = os.getenv('PLTO_PW')

# APIClient 인스턴스 생성
api_client = APIClient( client_api_key=API_KEY, client_id=EMAIL, client_secret=PASSWORD)

@app.route("/")
def hello() -> str:
    # Use basic logging with custom fields
    logger.info(logField="custom-entry", arbitraryField="custom-entry")

    # https://cloud.google.com/run/docs/logging#correlate-logs
    logger.info("Child logger with trace Id.")

    return render_template('index.html')

@app.route('/result/', methods=['POST'])
def result():
    user_input = request.form['user_input']
    # 여기서 user_input을 사용하여 필요한 처리를 수행합니다.
    # 예를 들어, API에 요청을 보내거나 데이터를 처리할 수 있습니다.
    try:
        # API 클라이언트를 사용하여 데이터를 가져오는 예시
        data = api_client.get_data("orders", user_input)
        order_table = api_client.process_data(data)

        return render_template('result.html', order_table=order_table, user_input=user_input)
    except Exception as e:
        return render_template('error.html', error=str(e))

def shutdown_handler(signal_int: int, frame: FrameType) -> None:
    logger.info(f"Caught Signal {signal.strsignal(signal_int)}")

    from utils.logging import flush

    flush()

    # Safely exit program
    sys.exit(0)


if __name__ == "__main__":
    # Running application locally, outside of a Google Cloud Environment

    # handles Ctrl-C termination
    signal.signal(signal.SIGINT, shutdown_handler)

    app.run(host="localhost", port=8080, debug=True)
else:
    # handles Cloud Run container termination
    signal.signal(signal.SIGTERM, shutdown_handler)
