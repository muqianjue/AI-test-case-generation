# Rag检索
import requests
import json

class Rag:
    def __init__(self):
        # API URL
        self.api_url = "http://10.12.3.94/v1/chat-messages"
        # API Key
        self.api_key = "app-L1cDMG3wA4EYG5B13Qezu2CY"

    async def rag_recall(self, requirement_info):
        # Request headers
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
        }

        # Request payload
        data = {
            "inputs": {},
            "query": f"{requirement_info}",
            "response_mode": "blocking",
            "conversation_id": "",
            "user": "abc-123"
        }
        # 发送 POST request
        response = requests.post(self.api_url, headers=headers, data=json.dumps(data))
        response_json = response.json()
        answer = response_json.get('answer', 'No answer found')
        return answer

