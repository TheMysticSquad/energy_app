import hmac, hashlib, os, json

SECRET_KEY = os.getenv("SECRET_KEY", "supersecret")

def sign_payload(payload: dict) -> dict:
    body = json.dumps(payload, sort_keys=True)
    signature = hmac.new(SECRET_KEY.encode(), body.encode(), hashlib.sha256).hexdigest()
    payload["signature"] = signature
    return payload

def verify_payload(payload: dict) -> bool:
    sig = payload.pop("signature", None)
    body = json.dumps(payload, sort_keys=True)
    expected = hmac.new(SECRET_KEY.encode(), body.encode(), hashlib.sha256).hexdigest()
    return hmac.compare_digest(sig or "", expected)
