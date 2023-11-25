import requests

class PushoverClient:
    def __init__(self):
        self.user_key = self.read_token(".tokens/pushover_user_key.txt")
        self.api_token = self.read_token(".tokens/pushover_api_key.txt")

    def read_token(self, file_path):
        try:
            with open(file_path, 'r') as file:
                return file.read().strip()
        except IOError:
            raise Exception(f"Unable to read token file: {file_path}")

    def send_message(self, message, title=None, url=None, url_title=None, priority=None, sound=None):
        data = {
            "token": self.api_token,
            "user": self.user_key,
            "message": message,
        }

        # オプショナルなパラメータの追加
        if title:
            data["title"] = title
        if url:
            data["url"] = url
        if url_title:
            data["url_title"] = url_title
        if priority:
            data["priority"] = priority
        if sound:
            data["sound"] = sound

        # Pushover APIへのリクエスト送信
        response = requests.post("https://api.pushover.net/1/messages.json", data=data)
        return response.json()

# モジュールの使用例
if __name__ == "__main__":
    # これらの値は実際のユーザーキーとAPIトークンに置き換える必要があります
    client = PushoverClient()
    response = client.send_message("Hello, this is a test message from Python!", title="Test Message")
    print(response)

