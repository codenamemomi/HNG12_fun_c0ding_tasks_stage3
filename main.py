import logging
import random
import json
import threading
import requests
import psutil  # CPU Usage Tracking
import time  # For request latency
from flask import Flask, g, Response, jsonify, request
from flask_cors import CORS
import concurrent.futures


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)



TELEX_WEBHOOK_URL = "https://ping.telex.im/v1/webhooks/01952a91-7a83-7e8f-a413-2ed9c2c983cd"

@app.before_request
def start_timer():
    ''' Start the timer before processing a request '''
    g.start_time = time.time()


@app.route("/")
def get_integration_json():
    base_url = request.url_root.rstrip("/")
    return jsonify({
        'data': {
            'date':{
                'created': '2025-02-21',
                'updated': '2025-02-21'
            },
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
            'author': 'codenamemomi',
            'website': base_url,
            'settings': [
                {"label": "challenge-type", "type": "text", "required": True, "default": "algorithm"},
                {"label": "difficulty", "type": "text", "required": True, "default": "medium"},
                {"label": "interval", "type": "text", "required": True, "default": "* * * * *"}
            ],
            'target_url': '',
            'tick_url': f'{base_url}/tick'
        }
    })


executors = concurrent.futures.ThreadPoolExecutor()

@app.route("/tick", methods=["POST", "GET"])
def tick():
    ''' Telex calls this endpoint at scheduled intervals '''
    logger.info(f"Received /tick request at {time.strftime('%Y-%m-%d %H:%M:%S')} with payload: {request.get_json()}")

    if request.content_type and request.content_type != "application/json":
        return jsonify({"status": "error", "message": "Invalid content type"}), 400
    
    payload = request.get_json(silent=True)
    if payload is None:
        return jsonify({"status": "error", "message": "Invalid JSON format"}), 400
    
    executors.submit(process_challenge, payload)
    return jsonify({"status": "accepted"}), 202


def load_challenges():
    ''' Load coding challenges from a JSON file '''
    with open("coding_challenges.json") as file:
        return json.load(file)

def process_challenge(payload):
    ''' Select and send a coding challenge to Telex '''
    logger.info("Processing challenge...")

    try:
        challenges = load_challenges()
        challenge_text = random.choice(challenges)["challenge"]

        message_data = {
            "message": f"🚀 Today's coding challenge:\n\n{challenge_text}\n\nGood luck!",
            "username": "Fun Coding Bot",
            "event_name": "coding_challenge",
            "status": "success"
        }

        response = requests.post(payload["return_url"], json=message_data, headers={
            "Accept": "application/json",
            "Content-Type": "application/json"
        })

        logger.info(f"Challenge sent: {response.status_code}, {response.text}")
    except Exception as e:
        logger.error(f"Error sending challenge: {e}")



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
