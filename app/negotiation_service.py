import re
import time
import base64
from io import BytesIO
from typing import Dict, List, Optional, Tuple

import requests
from gtts import gTTS

from .models import (
    DetectedItem,
    MarketCandidate,
    UserPreferences,
    Solution,
)
from .services import ProcurementOptimizer

# --- Configuration for the Partner API ---
NEGBOT_API_BASE = "https://negbot-backend-ajdxh9axb0ddb0e9.westeurope-01.azurewebsites.net/api"
TEAM_ID = "641754"


def generate_tts_audio(text: str) -> str:
    """
    Converts text to speech using gTTS and returns it as a Base64 encoded string.
    """
    try:
        tts = gTTS(text=text, lang='en')
        audio_fp = BytesIO()
        tts.write_to_fp(audio_fp)
        audio_fp.seek(0)
        audio_bytes = audio_fp.read()
        return base64.b64encode(audio_bytes).decode('utf-8')
    except Exception as e:
        print(f"Error generating TTS audio: {e}")
        return ""


class NegotiationService:
    """
    Manages the interactive negotiation process with the NegBot API.
    """

    def __init__(self):
        self.session = requests.Session()
        self.team_params = {"team_id": TEAM_ID}

    def _get_or_create_vendor(self, vendor_name: str) -> Optional[int]:
        try:
            # 1. Check if exists
            response = self.session.get(f"{NEGBOT_API_BASE}/vendors/", params=self.team_params)
            response.raise_for_status()
            for vendor in response.json():
                if vendor.get("name") == vendor_name:
                    return vendor["id"]

            # 2. Create if not exists (WITH REQUIRED FIELDS)
            new_vendor_payload = {
                "name": vendor_name,
                "description": f"A generic supplier of office equipment: {vendor_name}",
                "behavioral_prompt": (
                    "You are a helpful sales representative. "
                    "You want to close deals quickly and are willing to offer bulk discounts "
                    "if the quantity is high."
                )
            }

            response = self.session.post(
                f"{NEGBOT_API_BASE}/vendors/",
                params=self.team_params,
                json=new_vendor_payload,
            )
            response.raise_for_status()
            return response.json()["id"]
        except requests.RequestException as e:
            print(f"API Error in _get_or_create_vendor: {e}")
            if e.response is not None:
                print(f"Server Response: {e.response.text}")
            return None

    def _extract_price_from_text(self, text: str) -> Optional[float]:
        matches = re.findall(r'\$(\s*\d+\.?\d*)', text)
        if matches:
            return float(matches[-1].strip())
        return None

    def start_conversation(self, candidate_name: str) -> Optional[int]:
        """
        Creates a vendor if needed and starts a new conversation.
        """
        time.sleep(1)  # Basic rate limiting
        vendor_id = self._get_or_create_vendor(candidate_name)
        if not vendor_id:
            print(f"Failed to get vendor ID for {candidate_name}")
            return None

        try:
            response = self.session.post(
                f"{NEGBOT_API_BASE}/conversations/",
                params=self.team_params,
                json={"vendor_id": vendor_id, "title": f"Price Negotiation for {candidate_name}"},
            )
            response.raise_for_status()
            return response.json()["id"]
        except requests.RequestException as e:
            print(f"API Error in start_conversation: {e}")
            return None

    def send_message(self, conversation_id: int, message: str) -> Optional[Tuple[str, str, Optional[float]]]:
        """
        Sends a message to a conversation and gets the vendor's reply.
        """
        time.sleep(1)  # Basic rate limiting
        try:
            response = self.session.post(
                f"{NEGBOT_API_BASE}/messages/{conversation_id}",
                params=self.team_params,
                data={"content": message},
            )
            response.raise_for_status()
            bot_reply_text = response.json()["content"]

            # Generate TTS and parse for price
            audio_base64 = generate_tts_audio(bot_reply_text)
            parsed_price = self._extract_price_from_text(bot_reply_text)

            return bot_reply_text, audio_base64, parsed_price
        except requests.RequestException as e:
            print(f"API Error in send_message: {e}")
            return None