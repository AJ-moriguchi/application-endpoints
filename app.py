from flask import Flask, request, jsonify
import requests
from dotenv import load_dotenv
import os
import json
import logging

app = Flask(__name__)

load_dotenv()

# Logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

SLACK_BOT_TOKEN = os.getenv('SLACK_BOT_TOKEN')
API_ENDPOINT = os.getenv('API_ENDPOINT')
API_AUTHORIZATION = os.getenv('API_AUTHORIZATION')
BOT_USER_ID = 'U07GM5NKDUH'  # ここをボットのユーザーIDに置き換えてください
processed_messages = set()  # 処理済みメッセージのtsを保持するセット

@app.route('/slack/events', methods=['POST'])
def slack_events():
    data = request.json
    logging.info(f"Received event: {data}")
    
    if 'challenge' in data:
        return jsonify({'challenge': data['challenge']})
    
    event = data.get('event', {})
    
    if event.get('type') == 'message' and 'subtype' not in event:
        user_message = event.get('text')
        user_id = event.get('user')
        channel_id = event.get('channel')
        thread_ts = event.get('ts')  # メッセージのタイムスタンプを取得

        logging.info(f"Processing message from user {user_id} in channel {channel_id}: {user_message}")
        
        # メッセージのタイムスタンプで重複チェック
        if thread_ts in processed_messages:
            logging.info(f"Ignored duplicate message with timestamp {thread_ts}")
            return jsonify({'status': 'ignored'})
        processed_messages.add(thread_ts)

        # 自分自身のメッセージであれば無視する
        if user_id == BOT_USER_ID:
            logging.info("Ignored message from bot itself")
            return jsonify({'status': 'ignored'})

        # メッセージがBotへのメンションを含む場合のみ応答する
        if f'<@{BOT_USER_ID}>' in user_message:
            logging.info("Mention detected, sending API request")
            # APIリクエストを送信
            try:
                response = requests.get(API_ENDPOINT, headers={'Authorization': API_AUTHORIZATION}, params={'q': user_message})
                response.raise_for_status()
                json_content = response.json()
                api_reply = json.dumps(json_content, ensure_ascii=False, indent=2).replace('\\n', '\n')
                logging.info("API request successful")
            except requests.exceptions.RequestException as e:
                logging.error(f"API request failed: {e}")
                api_reply = "APIリクエストに失敗しました。"

            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {SLACK_BOT_TOKEN}'
            }
            slack_data = {
                'channel': channel_id,
                'text': f'<@{user_id}> {api_reply}',
                'thread_ts': thread_ts
            }
            response = requests.post('https://slack.com/api/chat.postMessage', headers=headers, json=slack_data)
            if response.status_code == 200:
                logging.info(f"Message successfully posted to Slack channel {channel_id}")
            else:
                logging.error(f"Failed to post message to Slack: {response.status_code} {response.text}")
    
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    logging.info("Starting Flask app on port 3000")
    app.run(port=3000)
