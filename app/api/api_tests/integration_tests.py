import pytest
from fastapi.testclient import TestClient
from app.api.main import app

client = TestClient(app)


def test_single_turn_order_tracking_flow():
    """
    Test the single-turn flow:
    Provide ID -> Expect status.
    """
    session_id = "test_integration_singleturn_123"

    turn = client.post("/chat", json={
        "session_id": session_id,
        "message": "Track my order. My order ID is ORD-0000"
    })

    assert turn.status_code == 200
    data_2 = turn.json()

    assert "test_status" in data_2["response"].lower()

def test_multi_turn_order_tracking_flow():
    """
    Test the multi-turn flow:
    1. Ask to track (no ID) -> Expect prompt.
    2. Provide ID -> Expect status.
    """
    session_id = "test_integration_multiturn_123"

    # --- TURN 1: Initial Request ---
    turn_1 = client.post("/chat", json={
        "session_id": session_id,
        "message": "I want to track my order"
    })

    assert turn_1.status_code == 200

    data_1 = turn_1.json()
    assert "ORD-XXXX" in data_1["response"]  # Checking if it asks for the ID

    # --- TURN 2: Providing the ID ---
    turn_2 = client.post("/chat", json={
        "session_id": session_id,
        "message": "My ID is ORD-0000"
    })

    assert turn_2.status_code == 200
    data_2 = turn_2.json()

    assert "test_status" in data_2["response"].lower()


def test_single_turn_order_cancellation_flow():
    """
    Test the single-turn flow:
    Provide ID -> Expect cancelled.
    """
    session_id = "test_integration_singleturn_321"

    turn = client.post("/chat", json={
        "session_id": session_id,
        "message": "Cancel my order. My order ID is ORD-0000"
    })

    assert turn.status_code == 200
    data_2 = turn.json()

    assert "cancelled" in data_2["response"].lower() or "refunded" in data_2["response"].lower()

def test_multi_turn_order_cancellation_flow():
    """
    Test the multi-turn flow:
    1. Ask to track (no ID) -> Expect prompt.
    2. Provide ID -> Expect status.
    """
    session_id = "test_integration_multiturn_321"

    # --- TURN 1: Initial Request ---
    turn_1 = client.post("/chat", json={
        "session_id": session_id,
        "message": "Can i return my bluetooth headphones?"
    })

    assert turn_1.status_code == 200

    data_1 = turn_1.json()
    assert "ORD-XXXX" in data_1["response"]  # Checking if it asks for the ID

    # --- TURN 2: Providing the ID ---
    turn_2 = client.post("/chat", json={
        "session_id": session_id,
        "message": "My ID is ORD-0000"
    })

    assert turn_2.status_code == 200
    data_2 = turn_2.json()

    assert "cancelled" in data_2["response"].lower() or "refunded" in data_2["response"].lower()

def test_invalid_order_id():
    """Test that the system keeps the user in the pending loop if the ID is wrong."""
    session_id = "test_invalid_user"

    client.post("/chat", json={
        "session_id": session_id,
        "message": "Track my order"
    })

    response = client.post("/chat", json={
        "session_id": session_id,
        "message": "ord-000"
    })

    assert "Please provide Order ID" in response.json()["response"]

def test_session_memory_persistence():
    """Verify that the Orchestrator remembers the Order ID across different intents."""
    session_id = "memory_user_99"

    # 1. Give the ID once while tracking
    client.post("/chat", json={
        "session_id": session_id,
        "message": "Track my order ORD-0000"
    })

    # 2. Ask a follow-up about cancellation WITHOUT providing the ID again
    res = client.post("/chat", json={
        "session_id": session_id,
        "message": "Actually, just cancel it"
    })

    data = res.json()
    # The orchestrator should have pulled ORD-1234 from the context!
    assert "ORD-0000" in data["response"]