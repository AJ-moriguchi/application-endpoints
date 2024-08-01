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

        # Web APIにメッセージを送信して返信を取得
        # response = requests.post(YOUR_API_ENDPOINT, json={'message': user_message})
        # api_reply = response.json().get('reply', 'Sorry, I did not understand that.')

        # Slackに返信を投稿
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {SLACK_BOT_TOKEN}'
        }
        slack_data = {
            'channel': channel_id,
            'text': f'<@{user_id}> {"api_reply"}'
        }
        requests.post('https://slack.com/api/chat.postMessage', headers=headers, json=slack_data)
    
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(port=3000)
