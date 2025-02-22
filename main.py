from fastapi import FastAPI, BackgroundTasks, Request
from pydantic import BaseModel
import httpx
import json
import random
import logging

app = FastAPI()

TELEX_WEBHOOK_URL = "https://ping.telex.im/v1/webhooks/01952a91-7a83-7e8f-a413-2ed9c2c983cd"  # Replace if needed


def load_challenges():
    with open("coding_challenges.json") as file:
        return json.load(file)


class MonitorPayload(BaseModel):
    channel_id: str
    return_url: str
    settings: list


@app.get("/integration.json")
def get_integration_json(request: Request):
    base_url = str(request.base_url).rstrip("/")
    return {
        "data": {
            "description": "Sends a random coding challenge every day.",
            "app_name": "Fun Coding Challenge",
            "app_logo": "https://res.cloudinary.com/drujauolr/image/upload/v1740162155/interval_clo1tq.webp",
            "app_url": base_url,
            "background_color": "#fff",
            "integration_type": "interval",
            "settings": [
                {
                    "label": "Time Interval",
                    "type": "number",
                    "required": True,
                    "default": 1,
                }
            ],
            "tick_url": f"{base_url}/tick"
        }
    }


@app.post("/receive")
async def receive_data_from_telex(data: dict):
    print("Received data from Telex:", data)
    return {"message": "Data received successfully"}


@app.post("/check", status_code=202)
def check(payload: MonitorPayload, background_tasks: BackgroundTasks):
    background_tasks.add_task(process_challenge, payload)
    return {"status": "accepted"}

logging.basicConfig(level=logging.INFO)

async def process_challenge(payload: MonitorPayload):
    logging.info("Processing challenge...")

    challenges = load_challenges()
    challenge = random.choice(challenges)["challenge"]

    logging.info(f"Sending challenge to Telex: {challenge}")

    message_data = {
        "message": f"🚀 Today's coding challenge:\n\n{challenge}\n\nGood luck!",
        "username": "Fun Coding Bot",
        "event_name": "coding_challenge",
        "status": "success"
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(payload.return_url, json=message_data)
            logging.info(f"Response from Telex: {response.status_code}, {response.text}")
        except Exception as e:
            logging.error(f"An error occurred: {e}")


@app.get("/")
def home():
    return {"message": "Telex Fun Coding Challenge Integration is running!"}
