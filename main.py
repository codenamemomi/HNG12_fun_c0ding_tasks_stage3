from flask import Flask, jsonify
from flask_cors import CORS
import json
import requests
import random


app = Flask(__name__)
CORS(app)

TELEX_WEBHOOK_URL = "https://ping.telex.im/v1/webhooks/01952a91-7a83-7e8f-a413-2ed9c2c983cd"  # Replace if needed


def load_challenges():
    with open('coding_challenges.json') as file:
        return json.load(file)
    

@app.route('/', methods=['GET'])
def home():
    return jsonify({'message': 'fun coding challenge Telex Integration is up and running!'})

@app.route('/check', methods=['POST'])
def send_coding_challenge():
    challenges = load_challenges()
    challenge = random.choice(challenges)['challenge']

    payload = {
        'event_name': 'coding_challenge',
        'username': 'codenameBot',
        'status': 'success',
        'message': f' Today\'s coding challenge:\n\n {challenge} \n\n Good luck! 🚀'
    }

    response = requests.post(
    TELEX_WEBHOOK_URL,
    json=payload,
    headers={
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    )

    
    if response.status_code == 202:
        return jsonify({'message': 'Coding challenge sent successfully!'})
    else:
        return jsonify({'message': 'Failed to send coding challenge!', 'details': response.text}), 500

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)