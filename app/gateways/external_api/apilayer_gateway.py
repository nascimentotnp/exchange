import logging
import os

import requests
from dotenv import load_dotenv
from fastapi import HTTPException

load_dotenv()
APIKEY = os.getenv("APIKEY")
API_URL = os.getenv("API_URL")

logger = logging.getLogger(__name__)


def fetch_exchange_rate(from_currency: str, to_currency: str, amount: float):
    url = f"{API_URL}?from={from_currency}&to={to_currency}&amount={amount}"
    headers = {
        'apikey': APIKEY
    }

    try:
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            logger.error(f"Error response from API: {response.status_code} - {response.text}")
            raise HTTPException(status_code=response.status_code, detail="Error fetching exchange rate")

        data = response.json()

        if data.get("success"):
            return {
                "rate": data["info"]["rate"],
                "result": data["result"],
                "query": data["query"],
                "info": data["info"],
                "date": data["date"]
            }
        else:
            raise HTTPException(status_code=400, detail="Failed to fetch valid exchange rate")

    except requests.exceptions.RequestException as e:
        logger.error(f"Request error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Request error: {str(e)}")

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
