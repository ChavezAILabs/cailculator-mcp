"""Auth-server checks: key reveal, webhook, admin endpoints. SQLite in a temp folder, Stripe faked.

A standalone script, not a pytest file (it sets env vars and imports main at load).
Run from a venv with auth_server/requirements.txt installed:
    python auth_server/tests/check_auth.py [path/to/auth_server]
Exits 1 if any check fails.
"""
import contextlib
import hashlib
import io
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

AUTH = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent
tmp = Path(tempfile.mkdtemp(prefix="authtest-"))
os.environ.update({
    "DATABASE_URL": f"sqlite:///{(tmp / 'auth.db').as_posix()}",
    "ADMIN_TOKEN": "test-admin-token",
    "STRIPE_SECRET_KEY": "sk_test_dummy",
})
os.environ.pop("STRIPE_WEBHOOK_SECRET", None)
sys.path.insert(0, str(AUTH))
os.chdir(tmp)

import main  # noqa: E402
from database import engine, SessionLocal, User, APIKey, CheckoutKeyReveal  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

INDIVIDUAL_PRICE = main.STRIPE_PRICES["individual"]
SESSIONS = {}


class FakeSession:
    @staticmethod
    def retrieve(sid):
        if sid not in SESSIONS:
            raise Exception("No such checkout session")
        return SESSIONS[sid]


class FakeSubscription:
    @staticmethod
    def retrieve(sub_id):
        return {"items": {"data": [{"price": {"id": INDIVIDUAL_PRICE}}]}}


main.stripe.checkout.Session = FakeSession
main.stripe.Subscription = FakeSubscription


def checkout(sid, email, status="complete", payment_status="paid"):
    SESSIONS[sid] = {"id": sid, "status": status, "payment_status": payment_status,
                     "customer_email": email, "customer_details": {"email": email, "name": "Test User"},
                     "subscription": f"sub_{sid}"}


def webhook_event(eid, sid):
    return {"id": eid, "type": "checkout.session.completed", "data": {"object": SESSIONS[sid]}}


def count(model, **f):
    with SessionLocal() as db:
        q = db.query(model)
        for k, v in f.items():
            q = q.filter(getattr(model, k) == v)
        return q.count()


results = []


def check(name, cond, detail=""):
    results.append((name, bool(cond), detail))


def extract_key(html):
    start = html.find("cail_")
    return html[start:html.find("<", start)].strip() if start >= 0 else None


ADMIN = {"X-Admin-Token": "test-admin-token"}

with TestClient(main.app) as c:
    # --- Existing (pre-change) key still validates ---
    with SessionLocal() as db:
        u = User(email="legacy@example.com", name="legacy", tier=main.SubscriptionTier("individual"),
                 email_verified=1, subscription_status=None)
        db.add(u); db.commit(); db.refresh(u)
        db.add(APIKey(user_id=u.id, key_hash=hashlib.sha256(b"cail_individual_legacykey").hexdigest()))
        db.commit()
    r = c.post("/validate", json={"api_key": "cail_individual_legacykey"})
    check("existing key validates", r.json().get("valid") is True, r.json())

    # --- Success page: key shown once ---
    checkout("cs_1", "alice@example.com")
    r = c.get("/success", params={"session_id": "cs_1"})
    key1 = extract_key(r.text)
    check("success page shows a key", r.status_code == 200 and key1 and key1.startswith("cail_individual_"), key1)
    check("success page no-store header", r.headers.get("cache-control") == "no-store")
    check("only hash stored", count(APIKey, key_hash=hashlib.sha256(key1.encode()).hexdigest()) == 1)
    r = c.post("/validate", json={"api_key": key1})
    check("revealed key validates", r.json().get("valid") is True, r.json())
    r2 = c.get("/success", params={"session_id": "cs_1"})
    check("reload shows 'already shown', no key", "already shown" in r2.text and extract_key(r2.text) is None)
    with SessionLocal() as db:
        alice = db.query(User).filter(User.email == "alice@example.com").one()
        check("reload created no second key", db.query(APIKey).filter(APIKey.user_id == alice.id).count() == 1)

    # --- Webhook after success page: same user, no key, nothing logged ---
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        r = c.post("/webhook/stripe", content=json.dumps(webhook_event("evt_1", "cs_1")))
    log = buf.getvalue()
    check("webhook ok", r.status_code == 200, r.text)
    check("webhook: one user for alice", count(User, email="alice@example.com") == 1)
    check("webhook created no key", count(APIKey, user_id=alice.id) == 1)
    check("webhook log has no key", "cail_" not in log, log[-300:])

    # --- Webhook BEFORE success page (other order) ---
    checkout("cs_2", "bob@example.com")
    with contextlib.redirect_stdout(io.StringIO()):
        c.post("/webhook/stripe", content=json.dumps(webhook_event("evt_2", "cs_2")))
    check("webhook-first: user created, no key", count(User, email="bob@example.com") == 1)
    r = c.get("/success", params={"session_id": "cs_2"})
    key2 = extract_key(r.text)
    check("webhook-first: success shows key", key2 is not None)
    check("webhook-first: still one user", count(User, email="bob@example.com") == 1)

    # --- Incomplete / unknown sessions ---
    checkout("cs_3", "carol@example.com", status="open", payment_status="unpaid")
    r = c.get("/success", params={"session_id": "cs_3"})
    check("incomplete checkout: no key", extract_key(r.text) is None and "complete yet" in r.text,
          r.text[r.text.find("<h1"):r.text.find("<h1") + 300])
    r = c.get("/success", params={"session_id": "cs_nope"})
    check("unknown session: no key, no raw error", extract_key(r.text) is None and "No such" not in r.text)
    check("no reveal rows for failed pages", count(CheckoutKeyReveal) == 2)

    # --- Admin auth ---
    check("admin: no token -> 401", c.get("/admin/keys").status_code == 401)
    check("admin: wrong token -> 401", c.get("/admin/keys", headers={"X-Admin-Token": "nope"}).status_code == 401)
    saved = main.ADMIN_TOKEN
    main.ADMIN_TOKEN = None
    check("admin: unset -> 503", c.get("/admin/keys", headers=ADMIN).status_code == 503)
    # Fail closed: unset or empty ADMIN_TOKEN refuses every request on every admin endpoint,
    # including no header and an empty header (which would match an empty token).
    for setting in (None, "", "   "):
        main.ADMIN_TOKEN = setting
        for hdrs in ({}, {"X-Admin-Token": ""}, ADMIN):
            codes = [c.get("/admin/keys", headers=hdrs).status_code,
                     c.post("/admin/keys/issue", json={"email": "alice@example.com"}, headers=hdrs).status_code,
                     c.delete("/admin/keys/1", headers=hdrs).status_code]
            check(f"admin: token={setting!r} header={hdrs.get('X-Admin-Token')!r} -> 503 x3",
                  codes == [503, 503, 503], codes)
    main.ADMIN_TOKEN = f" {saved} "
    check("admin: token with surrounding spaces still matches",
          c.get("/admin/keys", headers=ADMIN).status_code == 200)
    main.ADMIN_TOKEN = saved
    check("admin: empty header with token set -> 401",
          c.get("/admin/keys", headers={"X-Admin-Token": ""}).status_code == 401)

    # --- Admin list/issue/rotate/revoke ---
    r = c.get("/admin/keys", headers=ADMIN)
    body = r.text
    check("admin list ok", r.status_code == 200 and len(r.json()["keys"]) == 3, r.json())
    check("admin list contains no key", key1 not in body and key2 not in body and "cail_" not in body)
    check("admin list no-store", r.headers.get("cache-control") == "no-store")
    r = c.post("/admin/keys/issue", json={"email": "alice@example.com"}, headers=ADMIN)
    key3 = r.json().get("api_key")
    check("admin issue returns key", r.status_code == 200 and key3 and r.json()["revoked"] == 0, r.json())
    check("alice now has 2 keys", count(APIKey, user_id=alice.id) == 2)
    r = c.post("/admin/keys/issue", json={"email": "alice@example.com", "rotate": True}, headers=ADMIN)
    key4 = r.json().get("api_key")
    check("admin rotate revokes 2", r.json().get("revoked") == 2, r.json())
    check("old keys invalid after rotate",
          not c.post("/validate", json={"api_key": key1}).json()["valid"]
          and not c.post("/validate", json={"api_key": key3}).json()["valid"])
    check("rotated key valid", c.post("/validate", json={"api_key": key4}).json()["valid"])
    check("admin issue unknown email -> 404",
          c.post("/admin/keys/issue", json={"email": "nobody@example.com"}, headers=ADMIN).status_code == 404)
    with SessionLocal() as db:
        bob_key_id = db.query(APIKey).join(User).filter(User.email == "bob@example.com").one().id
    check("admin revoke ok", c.delete(f"/admin/keys/{bob_key_id}", headers=ADMIN).status_code == 200)
    check("revoked key invalid", not c.post("/validate", json={"api_key": key2}).json()["valid"])
    check("admin revoke again -> 404", c.delete(f"/admin/keys/{bob_key_id}", headers=ADMIN).status_code == 404)
    check("admin revoke needs token", c.delete(f"/admin/keys/{bob_key_id}").status_code == 401)

    # --- /migrate-db gone ---
    check("/migrate-db -> 404", c.post("/migrate-db").status_code == 404)

for name, ok, detail in results:
    print(f"{'PASS' if ok else 'FAIL'}  {name}" + ("" if ok else f"   {detail}"))
passed = sum(ok for _, ok, _ in results)
print(f"\n{passed}/{len(results)} passed")
os.chdir(AUTH)
engine.dispose()  # release the SQLite file so the temp folder can be removed
shutil.rmtree(tmp, ignore_errors=True)
sys.exit(0 if passed == len(results) else 1)
