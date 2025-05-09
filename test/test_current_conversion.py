from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_currency_conversion():
    response = client.get("/convert/USD/BRL/100")
    assert response.status_code == 200
    assert "transaction_id" in response.json()
    assert "amount_to" in response.json()
