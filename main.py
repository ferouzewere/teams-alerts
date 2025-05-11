import os
from fastapi import FastAPI, Request
from dotenv import load_dotenv
import httpx
from jinja2 import Environment, FileSystemLoader
import json
from datetime import datetime

# Load env vars
load_dotenv()

app = FastAPI()

# Jinja2 setup
env = Environment(loader=FileSystemLoader("templates"))
template = env.get_template("message_card.json.j2")

# Webhook URL
TEAMS_WEBHOOK_URL = os.getenv("TEAMS_WEBHOOK_ALERTS")

@app.post("/webflow-alert")
async def receive_alert(request: Request):
    data = await request.json()

    title = data.get("title", "Alert")
    message = data.get("message", "No message provided.")
    image_url = data.get("image_url", "")
    severity = data.get("severity", "info")

    # Render Jinja2 template and convert to JSON
    # card_payload = template.render(
    #     title=title,
    #     message=message,
    #     severity=severity
    # )

    card_payload = template.render(
    title=title,
    message=message,
    severity=severity,
    sender=data.get("sender", "Infotrace Analytics"),
    image_url=("https://media.licdn.com/dms/image/v2/C4D0BAQEZ3zNQuEum7g/company-logo_200_200/company-logo_200_200/0/1630534320267/infotrace_analytics_logo?e=2147483647&v=beta&t=-0G2Nnkwfjz3SZYi0cOZaVF6pJ4ghYqdZRyMI0ZVY-c"),
    link=data.get("link", None),
    timestamp=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S EAT")
)
    
    json_payload = json.loads(card_payload)

    # Send to Teams
    async with httpx.AsyncClient() as client:
        response = await client.post(
            TEAMS_WEBHOOK_URL,
            json=json_payload,
            headers={
                "Content-Type": "application/json"
            }
        )

    return {"status": response.status_code, "teams_response": response.text}