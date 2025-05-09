import pytest
from unittest.mock import patch


@pytest.mark.asyncio
@patch("app.controller.exchange_controller.fetch_exchange_rate")
async def test_convert_currency(mock_fetch, async_client):
    mock_fetch.return_value = {"rate": 5.0, "result": 50.0}
    response = await async_client.get("/exchange/convert/USD/BRL/10")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["amount_to"] == 50.0
    assert json_data["exchange_rate"] == 5.0


@pytest.mark.asyncio
async def test_convert_currency_invalid_currency(async_client):
    response = await async_client.get("/exchange/convert/INVALID/BRL/10")
    assert response.status_code == 400
    assert "Invalid currency" in response.json()["detail"]


@pytest.mark.asyncio
async def test_convert_currency_negative_amount(async_client):
    response = await async_client.get("/exchange/convert/USD/BRL/-5")
    assert response.status_code == 400
    assert "Amount must be non-negative" in response.json()["detail"]
