from flask import Flask, jsonify
from flask_cors import CORS
import json
import requests
import random
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)
CORS(app)

TELEX_WEBHOOK_URL = 'https://ping.telex.im/v1/webhooks/019528e7-3b28-7509-971e-312db7e9d0a0'

def load_challenges():
    with open('coding_challenges.json') as file:
        return json.load(file)
    

def send_coding_challenge():
    challenges = load_challenges()
    challenge = random.choice(challenges)['challenge']

    payload = {
        'event_name': 'coding_challenge',
        'username': 'codenameBot',
        'status': 'success',
        'message': f' Today\'s coding challenge:\n\n {challenge} \n\n Good luck! 🚀'
    }
    response = requests.post(TELEX_WEBHOOK_URL, json=payload)

    if response.status_code == 200:
        print('Challenge sent successfully')
    elif response.status_code == 202:
        print('Challenge sent successfully')
    else:
        print(f'Error sending challenge. Status code: {response.status_code}, Response: {response.text}')
sheduler = BackgroundScheduler()
sheduler.add_job(send_coding_challenge, 'interval', minutes=1)
sheduler.start()


@app.route('/check', methods=['GET'])
def home():
    return jsonify({'message': 'fun coding challenge Telex Integration is up and running!'})

@app.route('/', methods=['POST'])
def start():
    send_coding_challenge()
    return jsonify({'message': 'Coding challenge sent!'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)