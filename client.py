# client.py
import requests

def send_log(message: str):
    url = "http://127.0.0.1:8000/logs"
    data = {"message": message}
    response = requests.post(url, json=data)
    print(f"📤 送信: {message} → レスポンス: {response.json()}")
    # print(f"id: {response.id} ,msg: {response.message}, ts: {response.timestamp}")
    # print(response)
    # print(response.json()["message"])

if __name__ == "__main__":
    # テスト送信
    send_log("キー入力: A")
    send_log("キー入力: B")
