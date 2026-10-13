import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

APPROVED = {
    "supplier_code": "AIR1",
    "capability": "BOOK",
}

SUPPORTED = [
    ("AIR1", "SEARCH"),
    ("AIR1", "BOOK"),
    ("AIR1", "CANCEL"),
    ("AIR1", "UPGRADE_BIDDING"),
    ("HOTEL1", "SEARCH"),
    ("HOTEL1", "BOOK"),
    ("HOTEL1", "CANCEL"),
    ("CAR1", "SEARCH"),
    ("CAR1", "BOOK"),
]

UNSUPPORTED = [
    ("HOTEL1", "UPGRADE_BIDDING"),
    ("CAR1", "UPGRADE_BIDDING"),
    ("CAR1", "CANCEL"),
]


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_health_returns_200_when_feature_x_unset_or_false(monkeypatch):
    monkeypatch.delenv("FEATURE_X", raising=False)
    unset = client.get("/health")
    assert unset.status_code == 200
    assert unset.json() == {"status": "ok"}

    monkeypatch.setenv("FEATURE_X", "false")
    disabled = client.get("/health")
    assert disabled.status_code == 200
    assert disabled.json() == {"status": "ok"}


def test_health_returns_500_when_feature_x_is_true(monkeypatch):
    monkeypatch.setenv("FEATURE_X", "true")
    monkeypatch.delenv("FEATURE_Y", raising=False)

    response = client.get("/health")
    assert response.status_code == 500
    assert response.json() == {"status": "error"}

    onboarding = client.post("/onboarding/check", json=APPROVED)
    assert onboarding.status_code == 200
    assert onboarding.json() == {
        "approved": True,
        "reason": "Capability BOOK is supported for supplier AIR1",
    }


@pytest.mark.parametrize("supplier_code,capability", SUPPORTED)
def test_approved_when_supplier_supports_capability(supplier_code, capability):
    response = client.post(
        "/onboarding/check",
        json={"supplier_code": supplier_code, "capability": capability},
    )

    assert response.status_code == 200
    assert response.json() == {
        "approved": True,
        "reason": (
            f"Capability {capability} is supported for supplier {supplier_code}"
        ),
    }


def test_upgrade_bidding_approved_for_air_supplier():
    response = client.post(
        "/onboarding/check",
        json={"supplier_code": "AIR1", "capability": "UPGRADE_BIDDING"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "approved": True,
        "reason": "Capability UPGRADE_BIDDING is supported for supplier AIR1",
    }


def test_upgrade_bidding_not_approved_for_hotel_and_car_suppliers():
    for supplier_code in ("HOTEL1", "CAR1"):
        response = client.post(
            "/onboarding/check",
            json={"supplier_code": supplier_code, "capability": "UPGRADE_BIDDING"},
        )

        assert response.status_code == 200
        body = response.json()
        assert body["approved"] is False
        assert body["reason"] == (
            f"Capability UPGRADE_BIDDING is not supported for supplier {supplier_code}"
        )


def test_not_approved_when_supplier_is_unknown():
    response = client.post(
        "/onboarding/check",
        json={**APPROVED, "supplier_code": "AIR9"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["approved"] is False
    assert body["reason"] == "Supplier AIR9 is not onboarded"


@pytest.mark.parametrize("supplier_code,capability", UNSUPPORTED)
def test_not_approved_when_capability_is_unsupported(supplier_code, capability):
    response = client.post(
        "/onboarding/check",
        json={"supplier_code": supplier_code, "capability": capability},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["approved"] is False
    assert body["reason"] == (
        f"Capability {capability} is not supported for supplier {supplier_code}"
    )


def test_invalid_when_field_is_missing():
    missing_capability = client.post(
        "/onboarding/check",
        json={"supplier_code": "AIR1"},
    )
    missing_supplier = client.post(
        "/onboarding/check",
        json={"capability": "BOOK"},
    )

    assert missing_capability.status_code == 422
    assert missing_supplier.status_code == 422


def test_invalid_when_field_is_empty():
    empty_capability = client.post(
        "/onboarding/check",
        json={**APPROVED, "capability": ""},
    )
    empty_supplier = client.post(
        "/onboarding/check",
        json={**APPROVED, "supplier_code": ""},
    )

    assert empty_capability.status_code == 422
    assert empty_supplier.status_code == 422


def test_invalid_when_field_has_wrong_type():
    supplier_not_string = client.post(
        "/onboarding/check",
        json={**APPROVED, "supplier_code": ["AIR1"]},
    )
    capability_not_string = client.post(
        "/onboarding/check",
        json={**APPROVED, "capability": ["BOOK"]},
    )

    assert supplier_not_string.status_code == 422
    assert capability_not_string.status_code == 422


def test_feature_y_unset_or_false_does_not_change_onboarding(monkeypatch):
    import app.main as main

    monkeypatch.delenv("FEATURE_Y", raising=False)
    main._onboarding_calls = 0

    for _ in range(5):
        response = client.post("/onboarding/check", json=APPROVED)

        assert response.status_code == 200
        assert response.json() == {
            "approved": True,
            "reason": "Capability BOOK is supported for supplier AIR1",
        }

    monkeypatch.setenv("FEATURE_Y", "false")
    for _ in range(5):
        response = client.post("/onboarding/check", json=APPROVED)

        assert response.status_code == 200
        assert response.json() == {
            "approved": True,
            "reason": "Capability BOOK is supported for supplier AIR1",
        }

    health = client.get("/health")
    assert health.status_code == 200
    assert health.json() == {"status": "ok"}


def test_feature_y_fails_two_of_every_five_requests(monkeypatch):
    import app.main as main

    monkeypatch.setenv("FEATURE_Y", "true")
    monkeypatch.delenv("FEATURE_X", raising=False)
    main._onboarding_calls = 0

    codes = []
    for _ in range(10):
        response = client.post("/onboarding/check", json=APPROVED)
        codes.append(response.status_code)
        if response.status_code == 200:
            assert response.json() == {
                "approved": True,
                "reason": "Capability BOOK is supported for supplier AIR1",
            }
        else:
            assert response.status_code == 500
            assert response.json() == {"detail": "onboarding unavailable"}

    assert codes == [500, 500, 200, 200, 200, 500, 500, 200, 200, 200]
    assert codes.count(500) == 4

    health = client.get("/health")
    assert health.status_code == 200
    assert health.json() == {"status": "ok"}
