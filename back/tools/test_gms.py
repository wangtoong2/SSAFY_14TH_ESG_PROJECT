import os
import requests
from dotenv import load_dotenv
load_dotenv()

# 환경 변수에서 GMS_KEY 로드
GMS_KEY = os.getenv("GMS_KEY")
assert GMS_KEY, "GMS_KEY 환경 변수가 설정되어 있지 않습니다."

url = "https://gms.ssafy.io/gmsapi/api.openai.com/v1/chat/completions"

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {GMS_KEY}",
}

payload = {
    "model": "gpt-4.1-mini",
    "messages": [
        {
            "role": "system",
            "content": "Answer in Korean"
        },
        {
            "role": "user",
            "content": "사용자의 입력에 따라 취업할 기업을 추천해줘"
        }
    ],
    "max_tokens": 4096,
    "temperature": 0.3
}

response = requests.post(url, headers=headers, json=payload)

print("STATUS:", response.status_code)
print("RESPONSE:")
print(response.json())
