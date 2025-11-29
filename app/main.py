import httpx
import requests
from fastapi import FastAPI, UploadFile, File, HTTPException
from typing import Optional
from contextlib import asynccontextmanager
from fastapi import Form # Import Form

app = FastAPI()
API_BASE = "https://negbot-backend-ajdxh9axb0ddb0e9.westeurope-01.azurewebsites.net/api"
TEAM_ID = 641754
CONFIG = {"vendor_name": "Custom Vendor ZHANK"}


@app.get("/health")
def read_root():
    return {"status": "ok"}



@app.post("/message")
async def get_ai_message(
    user_message: str = Form(""),  # <--- CHANGED: Explicitly tell FastAPI this comes from the Form body
    file: Optional[UploadFile] = File(...)
):
    pass
