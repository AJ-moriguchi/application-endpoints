import streamlit as st
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

# Streamlitのヘッダー
st.title('API Request via Streamlit')

# ユーザーからの入力を受け付ける
user_message = st.text_area("Message to send to API:")

# 送信ボタン
if st.button('Send to API'):
    if user_message.strip():
        # Flask APIにPOSTリクエストを送信
        api_url = os.getenv('WEB_REQUEST_URL')  # Flaskアプリが動作しているサーバーのエンドポイント
        headers = {'Content-Type': 'application/json'}
        payload = {'message': user_message}
        
        try:
            response = requests.post(api_url, headers=headers, data=json.dumps(payload))
            response.raise_for_status()
            api_reply = response.json().get('response', 'No response from API')
            st.success(f"API Response:\n{api_reply}")
        except requests.exceptions.RequestException as e:
            st.error(f"Failed to communicate with API: {e}")
    else:
        st.warning("Please enter a message to send.")
