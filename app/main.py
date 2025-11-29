import httpx
import requests
from fastapi import FastAPI, UploadFile, File, HTTPException
from .models import ImageAnalysisResponse
from .services import analyze_image

app = FastAPI()
API_BASE = "https://negbot-backend-ajdxh9axb0ddb0e9.westeurope-01.azurewebsites.net/api"
TEAM_ID = 641754
CONFIG = {"vendor_name": "Custom Vendor ZHANK"}


@app.get("/health")
def read_root():
    return {"status": "ok"}


@app.post("/upload-document/")
async def upload_document(file: UploadFile = File(...)):
    url = f"{API_BASE}/documents/{CONFIG['vendor_id']}/upload"
    files = {'file': (file.filename, await file.read())}

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, files=files)
            response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
            return response.json()
        except httpx.RequestError as exc:
            raise HTTPException(status_code=503, detail=f"Error connecting to the document service: {exc}")
        except httpx.HTTPStatusError as exc:
            raise HTTPException(status_code=exc.response.status_code, detail=f"Document service returned an error: {exc.response.text}")


@app.get("/vendor")
async def send_msg():
    message = """
        You are an agent who only responses with list of strings in json format.
        Your answer should always be json parseable.
        Given photos that are uploaded, response with list of materials required to produce the main Product seen on the photo.
        Your response should only be focused on one product from the photo.

        If no photo is uploaded yet your response should be the following json string:

        {'response': []}

        Else you should give the list of strings of detailed objects of materials, required for producing the product on the photo, e.g.
        {'response': [
            {'name': 'Bolt M12', 'quantity': 12, 'description': 'stainless steel bolts. they should withstand 200 kg stress'},
            {'name': 'Wooden planks 12x12x5', 'quantity': 5, 'description': 'young wood, not older than 15 years.'}
        ]}
    """
    if not "vendor_id" in CONFIG:
        response = requests.get(
            f"{API_BASE}/vendors/?team_id={TEAM_ID}",
            params={"team_id": TEAM_ID}
        ).json()

        if len(response) > 0:
            CONFIG["vendor_id"] = [a for a in response if a["name"] == CONFIG["vendor_name"]][0]["id"]

        if not "vendor_id" in CONFIG:
            response = requests.post(
                f"{API_BASE}/vendors/?team_id={TEAM_ID}",
                params={"team_id": TEAM_ID},
                json={
                    "name": "Custom Vendor ZHANK",
                    "description": "Vendor that breaks down products to a list of materials",
                    "behavioral_prompt": message
                }
            ).json()

            CONFIG["vendor_id"] = response[0]["id"]

    return CONFIG["vendor_id"]
