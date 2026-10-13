"""Minimal supplier onboarding API for a live demo."""

import os

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

app = FastAPI(title="supplier-onboarding")

# supplier_code -> capabilities that supplier supports.
# AIR1 is a fictional airline, HOTEL1 is a fictional hotel chain, and CAR1 is
# a fictional car rental. AIR1 and HOTEL1 support SEARCH, BOOK, and CANCEL.
# CAR1 supports SEARCH and BOOK. No supplier supports ANCILLARIES.
SUPPLIER_CAPABILITIES = {
    "AIR1": {"SEARCH", "BOOK", "CANCEL"},
    "HOTEL1": {"SEARCH", "BOOK", "CANCEL"},
    "CAR1": {"SEARCH", "BOOK"},
}


class OnboardingRequest(BaseModel):
    supplier_code: str = Field(min_length=1)
    capability: str = Field(min_length=1)


class OnboardingResponse(BaseModel):
    approved: bool
    reason: str


# Counts POST /onboarding/check calls while FEATURE_Y is true. Calls 1, 2, 6, 7, ...
# fail, which is 2 of every 5 (40 percent). Health never consults this.
_onboarding_calls = 0


def _feature_y_failure() -> JSONResponse | None:
    global _onboarding_calls
    if os.getenv("FEATURE_Y") != "true":
        return None
    _onboarding_calls += 1
    if _onboarding_calls % 5 in (1, 2):
        return JSONResponse(status_code=500, content={"detail": "onboarding unavailable"})
    return None


@app.get("/health")
def health():
    if os.getenv("FEATURE_X") == "true":
        return JSONResponse(status_code=500, content={"status": "error"})
    return {"status": "ok"}


@app.post("/onboarding/check", response_model=None)
def check_onboarding(body: OnboardingRequest) -> OnboardingResponse | JSONResponse:
    failure = _feature_y_failure()
    if failure is not None:
        return failure

    capabilities = SUPPLIER_CAPABILITIES.get(body.supplier_code)
    if capabilities is None:
        return OnboardingResponse(
            approved=False,
            reason=f"Supplier {body.supplier_code} is not onboarded",
        )

    if body.capability not in capabilities:
        return OnboardingResponse(
            approved=False,
            reason=(
                f"Capability {body.capability} is not supported "
                f"for supplier {body.supplier_code}"
            ),
        )

    return OnboardingResponse(
        approved=True,
        reason=(
            f"Capability {body.capability} is supported "
            f"for supplier {body.supplier_code}"
        ),
    )
