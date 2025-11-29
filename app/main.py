import httpx
import requests
import datetime
import os
import base64
from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from typing import Optional
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = FastAPI()
API_BASE = "https://negbot-backend-ajdxh9axb0ddb0e9.westeurope-01.azurewebsites.net/api"
TEAM_ID = 641754
CONFIG = {"vendor_name": "Custom Vendor ZHANK"}


@app.get("/health")
def read_root():
    return {"status": "ok"}


@app.post("/openai/materials")
async def openai_materials(
    user_message: str = Form(...),
    file: Optional[UploadFile] = File(None)
):
    """
    Analyzes an image to identify materials and returns a JSON list.
    """
    system_message = {
        "role": "system",
        "content": "You are an expert in material identification. Based on the user's request and the provided image, identify the materials needed. Your response must be a JSON string list in the format: [{'name': 'Material Name', 'quantity': float}]"
    }

    messages = [system_message]

    if file:
        # Check for allowed content types
        if file.content_type not in ["image/jpeg", "image/png", "application/pdf", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"]:
            raise HTTPException(status_code=400, detail="Invalid file type. Please upload a JPEG, PNG, PDF, or Excel file.")

        # Encode the image
        base64_image = base64.b64encode(await file.read()).decode('utf-8')
        messages.append({
            "role": "user",
            "content": [
                {"type": "text", "text": user_message},
                {"type": "image_url", "image_url": {"url": f"data:{file.content_type};base64,{base64_image}"}}
            ]
        })
    else:
        messages.append({"role": "user", "content": user_message})

    try:
        response = client.chat.completions.create(
            model="gpt-5.1-chat-latest",
            messages=messages
        )
        return response.choices[0].message.content
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/message")
def get_ai_message():
    pass


@app.post("/conversation")
def create_conversation():
    url = f"{API_BASE}/conversations/?team_id={TEAM_ID}"
    response = requests.post(url, json={
        "vendor_id": CONFIG["vendor_id"],
        "title": f"Breakdown-{datetime.datetime.now()}"
    })

    CONFIG["conversation_id"] = response.json()["id"]

    return response


@app.post("/upload-document/")
async def upload_document(file: UploadFile = File(...)):
    url = f"{API_BASE}/documents/{CONFIG['vendor_id']}/upload"
    files = {'file': (file.filename, await file.read())}

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, files=files)
            response.raise_for_status()
            return response.json()
        except httpx.RequestError as exc:
            raise HTTPException(status_code=503, detail=f"Error connecting to the document service: {exc}")
        except httpx.HTTPStatusError as exc:
            raise HTTPException(status_code=exc.response.status_code, detail=f"Document service returned an error: {exc.response.text}")
