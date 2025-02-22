from flask import Flask, request, jsonify
from flask_cors import CORS
import threading
import requests
import random
import json
import logging

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.INFO)

url = 'https://ping.telex.im/v1/webhooks/01952a91-7a83-7e8f-a413-2ed9c2c983cd'

@app.route('/integration.json', methods=['GET'])
def get_integration_json():
    base_url = request.base_url.rstrip('/')
    return jsonify({
        'data': {
            'descriptions': {
                'app_description': 'Sends a random coding challenge every day.',
                'app_name': 'Fun Coding Challenge',
                'app_logo': 'https://res.cloudinary.com/drujauolr/image/upload/v1740162155/interval_clo1tq.webp',
                'app_url': base_url,
                'background_color': '#fff'
            },
            'is_active': True,
            'integration_type': 'interval',
            'integration_category': 'Task Automation',
            'key_features': [
                'Sends a random coding challenge every day',
                'Helps you stay consistent with your coding practice',
                'Keeps you motivated and engaged'
            ],
            'settings': [
                {
                    'label': 'Time Interval',
                    'type': 'text',
                    'required': True,
                    'default': '* * * * *',
                }
            ],
            'target_url': f'{base_url}/receive',
            'tick_url': f'{base_url}/tick'
        }
    })

@app.route('/tick', methods=['POST'])
def tick():
    if request.content_type != 'application/json':
        return jsonify({'status': 'error', 'message': 'Invalid content type'}), 400
    
    payload = request.get_json(silent=True)
    if payload is None:
        return jsonify({'status': 'error', 'message': 'Invalid payload'}), 400
    
    threading.Thread(target=process_challenge, args=(payload,)).start()
    return jsonify({'status': 'success'}), 200

def load_challenges():
    with open('coding_challenges.json') as file:
        return json.load(file)

def process_challenge(payload):
    logging.info('Processing challenge...')

    try:
        challenges = load_challenges()
        challenge_text = random.choice(challenges)["challenge"]

        message_data = {
            'message': f'🚀 Today\'s coding challenge:\n\n{challenge_text}\n\nGood luck!',
            'username': 'Fun Coding Bot',
            'event_name': 'coding_challenge',
            'status': 'success'
        }

        response = requests.post(url, json=message_data, headers={
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })

        logging.info(f'Challenge sent: {response.status_code}, {response.text}')
    except Exception as e:
        logging.error(f'Error sending challenge: {e}')

@app.route('/receive', methods=['POST'])
def receive_data_from_telex():
    if request.content_type != 'application/json':
        return jsonify({'status': 'error', 'message': 'Invalid content type'}), 400
    
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({'status': 'error', 'message': 'Invalid JSON format'}), 400
    
    logging.info(f'Data received from Telex: {data}')
    return jsonify({'status': 'success'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5000)
