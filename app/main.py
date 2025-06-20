from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from api.v1.router import api_router
from utils.assistant_manager import AssistantManager
import os
from dotenv import load_dotenv
from utils.logging import setup_logger
from typing import cast

import time
import requests
from collections import defaultdict
from datetime import datetime

logger = setup_logger("debug")

load_dotenv()
assistant_id = os.getenv("ASSISTANT_ID")
api_key = os.getenv("OPENAI_API_KEY")

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.assistant_manager = cast(AssistantManager, AssistantManager(
        assistant_id=assistant_id,
        openai_api_key=api_key
    ))
    logger.info("🚀 AssistantManager initialized")
    yield

    logger.info("🛑 Shutting down")


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")

API_URL = "https://public-api.prozorro.gov.ua/api/2.5/tenders"
HEADERS = {"Accept": "application/json"}
CPV_TARGET = "45000000-7"
CURRENT_YEAR = "2025"
CURRENT_MONTH = "05"

def fetch_monthly_construction_tenders():
    url = API_URL + "?descending=1"
    previous_offset = None
    matched_tenders = set()
    region_set = set()

    while url:
        response = requests.get(url, headers=HEADERS)
        if response.status_code == 429:
            time.sleep(5)
            continue
        response.raise_for_status()

        result = response.json()
        next_offset = result["next_page"]["offset"]
        if next_offset == previous_offset:
            break
        previous_offset = next_offset

        for tender in result["data"]:
            date_modified = tender["dateModified"]
            if not (date_modified.startswith(f"{CURRENT_YEAR}-{CURRENT_MONTH}")):
                logger.info("Finished scanning for %s-%s.", CURRENT_YEAR, CURRENT_MONTH)
                log_regions(region_set)
                return

            tender_id = tender["id"]
            detail_url = f"{API_URL}/{tender_id}"
            time.sleep(0.3)
            detail_resp = requests.get(detail_url, headers=HEADERS)
            if detail_resp.status_code == 429:
                time.sleep(5)
                continue
            detail_resp.raise_for_status()
            data = detail_resp.json()["data"]

            if tender_id in matched_tenders:
                continue

            items = data.get("items", [])
            for item in items:
                cpv = item.get("classification", {}).get("id", "")
                if cpv == CPV_TARGET:
                    region = item.get("deliveryAddress", {}).get("region", "Unknown region")
                    region_set.add(region)
                    matched_tenders.add(tender_id)
                    break

        url = f"{API_URL}?offset={next_offset}&descending=1"
        time.sleep(0.3)

def log_regions(region_set):
    logger.info("\nRegions with CPV 45000000-7 tenders in the selected month:")
    for region in sorted(region_set):
        logger.info(region)


fetch_monthly_construction_tenders()
