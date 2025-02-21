from flask import Flask, jsonify
from flask_cors import CORS
import json
import requests
import random


app = Flask(__name__)
CORS(app)


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

    return jsonify(payload), 200


if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)