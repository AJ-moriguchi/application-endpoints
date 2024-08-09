from flask import Flask, request, jsonify
import requests
from dotenv import load_dotenv
import os

app = Flask(__name__)

load_dotenv()

SLACK_BOT_TOKEN = os.getenv('SLACK_BOT_TOKEN')
# YOUR_API_ENDPOINT = os.getenv('YOUR_API_ENDPOINT')

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

        # Slackにスレッド内で返信を投稿
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {SLACK_BOT_TOKEN}'
        }
        slack_data = {
            'channel': channel_id,
            'text': f'<@{user_id}> {user_message}',  # 受信したメッセージをそのまま返す
            'thread_ts': thread_ts  # スレッドIDを指定
        }
        requests.post('https://slack.com/api/chat.postMessage', headers=headers, json=slack_data)
    
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(port=3000)
