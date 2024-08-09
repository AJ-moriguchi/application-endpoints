import unittest
import json
from app import app

class SlackEventTestCase(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_challenge_response(self):
        # チャレンジリクエストをシミュレート
        challenge_data = {
            "challenge": "3eZbrw1aBm1zjJskjBb"
        }
        response = self.app.post('/slack/events', data=json.dumps(challenge_data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, challenge_data)

    def test_message_event(self):
        # メッセージイベントをシミュレート
        event_data = {
            "event": {
                "type": "message",
                "text": "Hello",
                "user": "U123456",
                "channel": "C07F27STTDK"
            }
        }
        response = self.app.post('/slack/events', data=json.dumps(event_data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['status'], 'ok')

if __name__ == '__main__':
    unittest.main()
