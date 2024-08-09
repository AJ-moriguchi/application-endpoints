from flask import Flask, request, jsonify
import requests
from dotenv import load_dotenv
import os
import json

app = Flask(__name__)

load_dotenv()

SLACK_BOT_TOKEN = os.getenv('SLACK_BOT_TOKEN')
API_ENDPOINT = os.getenv('API_ENDPOINT')
API_AUTHORIZATION = os.getenv('API_AUTHORIZATION')

@app.route('/slack/events', methods=['POST'])
def slack_events():
    data = request.json
    
    if 'challenge' in data:
        return jsonify({'challenge': data['challenge']})
    
    event = data.get('event', {})
    
    if event.get('type') == 'message' and 'subtype' not in event:
        user_message = event.get('text')
        user_id = event.get('user')
        channel_id = event.get('channel')
        thread_ts = event.get('ts')  # メッセージのタイムスタンプを取得（これがスレッドIDとなる）

        # 自分自身のメッセージであれば無視する
        if user_id == 'U07F52ZK8E7':  # YOUR_BOT_USER_ID はボットのユーザーIDに置き換えてください
            return jsonify({'status': 'ignored'})

        # APIリクエストを送信
        response = requests.get(API_ENDPOINT, headers={'Authorization': API_AUTHORIZATION}, params={'q': user_message})

        if response.status_code == 200:
            # JSONレスポンスを解析
            json_content = response.json()
            # Slackに投稿するテキストを抽出（必要に応じてカスタマイズ）
            api_reply = json.dumps(json_content, ensure_ascii=False, indent=2)  # JSONをフォーマットして文字列に変換
        else:
            api_reply = "APIリクエストに失敗しました。"

        # Slackにスレッド内で返信を投稿
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {SLACK_BOT_TOKEN}'
        }
        slack_data = {
            'channel': channel_id,
            'text': f'<@{user_id}> {api_reply}',  # APIからのレスポンスを送信
            'thread_ts': thread_ts  # スレッドIDを指定
        }
        requests.post('https://slack.com/api/chat.postMessage', headers=headers, json=slack_data)
    
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(port=3000)
