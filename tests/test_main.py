import hmac
import hashlib

from src.security import WEBHOOK_SECRET


API_HEADERS = {"X-API-Key": "mysecret123"}


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200


def test_create_customer(client):
    response = client.post(
        "/customers",
        headers=API_HEADERS,
        json={
            "name": "Arun",
            "email": "arun@example.com",
            "phone": "9876543210",
            "city": "Chennai"
        }
    )
    assert response.status_code == 201
    assert response.json()["name"] == "Arun"


def test_get_customers(client):
    client.post(
        "/customers",
        headers=API_HEADERS,
        json={"name": "Bala", "email": "bala@example.com"}
    )

    response = client.get("/customers", headers=API_HEADERS)
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_get_customer_not_found(client):
    response = client.get("/customers/999", headers=API_HEADERS)
    assert response.status_code == 404


def test_update_customer(client):
    created = client.post(
        "/customers",
        headers=API_HEADERS,
        json={"name": "Arun", "email": "arun@example.com"}
    )

    customer_id = created.json()["id"]

    response = client.put(
        f"/customers/{customer_id}",
        headers=API_HEADERS,
        json={"name": "Arun Kumar"}
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Arun Kumar"


def test_delete_customer(client):
    created = client.post(
        "/customers",
        headers=API_HEADERS,
        json={"name": "Arun", "email": "arun@example.com"}
    )

    customer_id = created.json()["id"]

    response = client.delete(
        f"/customers/{customer_id}",
        headers=API_HEADERS
    )

    assert response.status_code == 200


def test_missing_api_key(client):
    response = client.get("/customers")
    assert response.status_code == 401


def test_duplicate_email(client):
    data = {"name": "Arun", "email": "arun@example.com"}

    client.post("/customers", headers=API_HEADERS, json=data)
    response = client.post("/customers", headers=API_HEADERS, json=data)

    assert response.status_code == 409


def test_invalid_customer_data(client):
    response = client.post(
        "/customers",
        headers=API_HEADERS,
        json={"name": "Arun", "email": "invalid-email"}
    )
    assert response.status_code == 422


def create_signature(payload):
    return hmac.new(
        WEBHOOK_SECRET.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()


def test_valid_webhook(client):
    payload = b'{"event":"customer.created"}'

    response = client.post(
        "/webhooks/customer-events",
        content=payload,
        headers={"X-Signature": create_signature(payload)}
    )

    assert response.status_code == 200
    assert response.json() == {"status": "accepted"}


def test_tampered_webhook(client):
    original = b'{"event":"customer.created"}'
    tampered = b'{"event":"customer.deleted"}'

    response = client.post(
        "/webhooks/customer-events",
        content=tampered,
        headers={"X-Signature": create_signature(original)}
    )

    assert response.status_code == 401


def test_missing_webhook_signature(client):
    response = client.post(
        "/webhooks/customer-events",
        content=b'{"event":"customer.created"}'
    )

    assert response.status_code == 401