# supplier-onboarding

Small FastAPI service that checks whether an onboarded supplier supports a capability. Rules live in memory so the demo has no database.

A request is approved when both are true:

- `supplier_code` is onboarded (`AIR1` airline, `HOTEL1` hotel chain, `CAR1` car rental)
- `capability` is supported for that supplier (`SEARCH`, `BOOK`, and `CANCEL` for `AIR1` and `HOTEL1`; `SEARCH` and `BOOK` for `CAR1`; no supplier supports `UPGRADE_BIDDING`)

## Run locally

```bash
cd supplier-onboarding
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The API listens on http://127.0.0.1:8000. Interactive docs are at http://127.0.0.1:8000/docs.

```bash
curl http://127.0.0.1:8000/health

curl -X POST http://127.0.0.1:8000/onboarding/check \
  -H 'Content-Type: application/json' \
  -d '{"supplier_code":"AIR1","capability":"BOOK"}'
```

## Test

From `supplier-onboarding`, with the virtualenv activated:

```bash
pytest
```

## Docker

```bash
docker build -t supplier-onboarding .
docker run --rm -p 8000:8000 supplier-onboarding
```

The image uses `python:3.12-slim` and runs as the non-root user `app`.
