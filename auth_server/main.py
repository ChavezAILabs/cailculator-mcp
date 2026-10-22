"""
CAILculator Auth Server - FastAPI Backend for Railway
Handles API key validation and usage tracking
"""

from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, EmailStr
from typing import Optional
import os
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from pathlib import Path
import stripe
import secrets
import hashlib

from database import (
    get_db,
    init_db,
    User,
    APIKey,
    UsageLog,
    SubscriptionTier,
    ProcessedStripeEvent,
    CheckoutKeyReveal,
)

app = FastAPI(
    title="CAILculator Auth Server",
    description="Authentication and usage tracking for CAILculator MCP",
    version="1.0.0"
)

# Templates and static files directory
BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# Create static directory if it doesn't exist (for Railway deployment)
static_dir = BASE_DIR / "static"
static_dir.mkdir(parents=True, exist_ok=True)

app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Stripe configuration
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")

# Stripe Price IDs. Each can be overridden by STRIPE_PRICE_ID_<TIER> (e.g.
# STRIPE_PRICE_ID_INDIVIDUAL), so a test-mode or staging deploy can use test-mode prices
# without a code change. The defaults are the LIVE-mode IDs used in production.
_LIVE_PRICES = {
    "individual": "price_1Tdyrt2NNm10BnLCMe5wP9XN",    # $50/month - 25,000 requests
    "journalist": "price_1Tdyl42NNm10BnLCRgqZQnUF",    # $75/month - 50,000 requests
    "academic": "price_1TdyvL2NNm10BnLC5704Cv5U",      # $100/month - 75,000 requests
    "commercial": "price_1TdyxN2NNm10BnLCI9XjeRNt",    # $250/month per seat - 250,000 requests
    # Quant Trader Tiers
    "quant_explorer": "price_1SQGie2NNm10BnLCyraRcDSA",      # $599/month - 100,000 requests
    "quant_professional": "price_1SXDc82NNm10BnLC36hwqnaA",  # $1,499/month - 500,000 requests
    "quant_elite": "price_1SQGox2NNm10BnLCcROJSo91"          # $3,499/month - Unlimited
    # Enterprise and Quant Enterprise are custom pricing (contact sales)
}
STRIPE_PRICES = {tier: os.getenv(f"STRIPE_PRICE_ID_{tier.upper()}", price)
                 for tier, price in _LIVE_PRICES.items()}
if (os.getenv("STRIPE_SECRET_KEY") or "").startswith("sk_test_") and STRIPE_PRICES == _LIVE_PRICES:
    print("WARNING: Stripe test key with live-mode price IDs; set STRIPE_PRICE_ID_<TIER> for test mode")
if not (STRIPE_WEBHOOK_SECRET or "").strip():
    print("WARNING: STRIPE_WEBHOOK_SECRET not set; /webhook/stripe will refuse every event (503)")
PRICE_TO_TIER = {price: tier for tier, price in STRIPE_PRICES.items()}

# Admin endpoints (/admin/...) require this token in the X-Admin-Token header.
# Unset, empty or whitespace-only = admin endpoints disabled (503). Surrounding spaces are ignored.
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN")

# Domain profiles included in each plan. Must match PLAN_PROFILES in
# src/cailculator_mcp/plans.py (checked by tests/golden/test_access.py).
PLAN_PROFILES = {
    "individual": ["general_data", "developer_v1"],
    "journalist": ["journalism", "general_data", "developer_v1"],
    "academic": ["general_data", "developer_v1"],
    "quant_explorer": ["quant_equity", "general_data", "developer_v1"],
    "quant_professional": ["quant_equity", "general_data", "developer_v1"],
    "quant_elite": ["quant_equity", "general_data", "developer_v1"],
    "commercial": ["general_data", "journalism", "quant_equity", "developer_v1"],
    "enterprise": ["general_data", "journalism", "quant_equity", "developer_v1"],
}

PROFILE_DESCRIPTIONS = {
    "general_data": "General Data - general-purpose numerical structure analysis",
    "journalism": "Journalism - measured structural quantities for public-records data",
    "quant_equity": "Quant Equity - market regime analysis from price / OHLCV data",
    "developer_v1": "Developer - template for building a custom profile",
}

# Monthly request limits by tier
TIER_LIMITS = {
    "individual": 25000,
    "journalist": 50000,
    "academic": 75000,
    "commercial": 250000,
    "enterprise": 999999999,  # Unlimited (or very high limit)
    # Quant Trader Tiers
    "quant_explorer": 100000,
    "quant_professional": 500000,
    "quant_elite": -1  # Unlimited
}

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =============================================================================
# REQUEST/RESPONSE MODELS
# =============================================================================

class ValidateRequest(BaseModel):
    api_key: str

class ValidateResponse(BaseModel):
    valid: bool
    user_id: Optional[int] = None
    tier: Optional[str] = None
    usage_count: Optional[int] = None
    limit: Optional[int] = None
    message: str

class UsageRequest(BaseModel):
    api_key: str
    tool_name: str
    dimension: Optional[int] = None

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def check_rate_limit(api_key: str, db: Session) -> tuple[bool, int, int]:
    """
    Check if user has exceeded their rate limit
    Uses monthly billing period aligned with subscription start date
    Returns: (is_allowed, current_usage, limit)
    """
    # Find API key
    key_record = db.query(APIKey).filter(APIKey.key_hash == api_key).first()
    if not key_record:
        return False, 0, 0

    user = db.query(User).filter(User.id == key_record.user_id).first()
    if not user:
        return False, 0, 0

    # Get limit for tier
    limit = TIER_LIMITS.get(user.tier.value, 25000)

    # Check if we need to reset the period (new month)
    now = datetime.utcnow()
    if user.period_end_date is None or now > user.period_end_date:
        # Reset counter for new billing period
        user.request_count_current_period = 0
        user.period_start_date = now
        # Set period end to 30 days from now
        user.period_end_date = now + timedelta(days=30)
        db.commit()

    # Return current usage status
    current_usage = user.request_count_current_period
    is_allowed = current_usage < limit

    return is_allowed, current_usage, limit

# =============================================================================
# API ENDPOINTS
# =============================================================================

@app.get("/", response_class=HTMLResponse)
async def landing_page(request: Request):
    """Landing page with pricing"""
    return templates.TemplateResponse(request=request, name="index.html")

@app.get("/api")
async def api_info():
    """API info endpoint"""
    return {
        "service": "CAILculator Auth Server",
        "status": "operational",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Health check with database connectivity"""
    try:
        # Test database connection
        from sqlalchemy import text
        db.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "database": "connected"
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database error: {str(e)}")

# POST /migrate-db was removed on 2026-10-14: it was unauthenticated and wrote to the
# production database. Schema changes run at startup (see startup()); one-off migrations
# run by hand with migrate_db.py.

@app.post("/validate", response_model=ValidateResponse)
async def validate(request: ValidateRequest, db: Session = Depends(get_db)):
    """
    Validate API key and check rate limits
    Called by MCP server before each request
    """
    # Hash the provided key
    import hashlib
    key_hash = hashlib.sha256(request.api_key.encode()).hexdigest()

    # Find API key
    key_record = db.query(APIKey).filter(APIKey.key_hash == key_hash).first()
    if not key_record:
        return ValidateResponse(
            valid=False,
            message="Invalid API key"
        )

    user = db.query(User).filter(User.id == key_record.user_id).first()
    if not user:
        return ValidateResponse(
            valid=False,
            message="User not found"
        )

    # Block revoked subscriptions; None means legacy/non-Stripe user (allow)
    if user.subscription_status in ('canceled', 'unpaid'):
        return ValidateResponse(
            valid=False,
            user_id=user.id,
            tier=user.tier.value,
            message=f"Subscription {user.subscription_status}"
        )

    # Check rate limit
    is_allowed, usage_count, limit = check_rate_limit(key_hash, db)

    if not is_allowed:
        return ValidateResponse(
            valid=False,
            user_id=user.id,
            tier=user.tier.value,
            usage_count=usage_count,
            limit=limit,
            message=f"Rate limit exceeded ({usage_count}/{limit} requests this month)"
        )

    return ValidateResponse(
        valid=True,
        user_id=user.id,
        tier=user.tier.value,
        usage_count=usage_count,
        limit=limit,
        message="API key valid"
    )

@app.post("/log-usage")
async def log_usage(request: UsageRequest, db: Session = Depends(get_db)):
    """
    Log API usage for billing and analytics
    Called by MCP server after successful request
    Increments the request counter for rate limiting
    """
    # Hash the provided key
    import hashlib
    key_hash = hashlib.sha256(request.api_key.encode()).hexdigest()

    # Find API key
    key_record = db.query(APIKey).filter(APIKey.key_hash == key_hash).first()
    if not key_record:
        raise HTTPException(status_code=401, detail="Invalid API key")

    # Get user and increment request counter
    user = db.query(User).filter(User.id == key_record.user_id).first()
    if user:
        user.request_count_current_period += 1

    # Log usage (for detailed analytics)
    usage = UsageLog(
        user_id=key_record.user_id,
        tool_name=request.tool_name,
        dimension=request.dimension
    )
    db.add(usage)
    db.commit()

    return {"status": "logged"}

@app.get("/usage/{api_key}")
async def get_usage(api_key: str, db: Session = Depends(get_db)):
    """
    Get usage statistics for an API key
    """
    # Hash the provided key
    import hashlib
    key_hash = hashlib.sha256(api_key.encode()).hexdigest()

    # Find API key
    key_record = db.query(APIKey).filter(APIKey.key_hash == key_hash).first()
    if not key_record:
        raise HTTPException(status_code=401, detail="Invalid API key")

    user = db.query(User).filter(User.id == key_record.user_id).first()

    # Count usage in last 30 days
    from datetime import timedelta
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    usage_count = db.query(UsageLog).filter(
        UsageLog.user_id == user.id,
        UsageLog.timestamp >= thirty_days_ago
    ).count()

    limit = TIER_LIMITS.get(user.tier.value, 100)

    return {
        "user_id": user.id,
        "email": user.email,
        "tier": user.tier.value,
        "usage_30_days": usage_count,
        "limit": limit if limit != -1 else "unlimited",
        "remaining": (limit - usage_count) if limit != -1 else "unlimited"
    }

# =============================================================================
# STARTUP/SHUTDOWN
# =============================================================================

@app.on_event("startup")
async def startup():
    """Initialize database on startup"""
    print("Starting CAILculator Auth Server...")

    # Run migrations first
    try:
        from sqlalchemy import text
        from database import engine
        with engine.connect() as conn:
            # Force database reset if RESET_DATABASE env var is set
            reset_db = os.getenv("RESET_DATABASE", "false").lower() == "true"
            if reset_db:
                print("RESET_DATABASE=true detected - recreating all tables...")
                try:
                    conn.execute(text("DROP TABLE IF EXISTS users CASCADE"))
                    conn.execute(text("DROP TABLE IF EXISTS api_keys CASCADE"))
                    conn.execute(text("DROP TABLE IF EXISTS usage_logs CASCADE"))
                    conn.execute(text("DROP TABLE IF EXISTS signup_attempts CASCADE"))
                    conn.execute(text("DROP TABLE IF EXISTS checkout_key_reveals CASCADE"))
                    conn.execute(text("DROP TYPE IF EXISTS subscriptiontier CASCADE"))
                    conn.commit()
                    print("✓ Database reset complete - tables will be recreated")
                except Exception as reset_error:
                    print(f"Reset error: {str(reset_error)}")
                    conn.rollback()

            print("Running database migrations...")
            
            migrations = [
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS email_verified INTEGER DEFAULT 0 NOT NULL",
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS verification_token VARCHAR",
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS verification_token_expires TIMESTAMP",
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS country_code VARCHAR(2)",
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS signup_ip VARCHAR",
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS requires_manual_approval INTEGER DEFAULT 0 NOT NULL",
                "CREATE INDEX IF NOT EXISTS ix_users_verification_token ON users(verification_token)",
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS stripe_subscription_id VARCHAR",
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS subscription_status VARCHAR",
                "CREATE INDEX IF NOT EXISTS ix_users_stripe_subscription_id ON users(stripe_subscription_id)",
                "CREATE TABLE IF NOT EXISTS processed_stripe_events (id SERIAL PRIMARY KEY, event_id VARCHAR UNIQUE NOT NULL, event_type VARCHAR NOT NULL, processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL)",
                "CREATE INDEX IF NOT EXISTS ix_processed_stripe_events_event_id ON processed_stripe_events(event_id)",
                # Ensure all Enum values exist in PostgreSQL type
                "ALTER TYPE subscriptiontier ADD VALUE IF NOT EXISTS 'individual'",
                "ALTER TYPE subscriptiontier ADD VALUE IF NOT EXISTS 'journalist'",
                "ALTER TYPE subscriptiontier ADD VALUE IF NOT EXISTS 'academic'",
                "ALTER TYPE subscriptiontier ADD VALUE IF NOT EXISTS 'commercial'",
                "ALTER TYPE subscriptiontier ADD VALUE IF NOT EXISTS 'enterprise'",
                "ALTER TYPE subscriptiontier ADD VALUE IF NOT EXISTS 'quant_explorer'",
                "ALTER TYPE subscriptiontier ADD VALUE IF NOT EXISTS 'quant_professional'",
                "ALTER TYPE subscriptiontier ADD VALUE IF NOT EXISTS 'quant_elite'",
                # Rate limiting columns
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS request_count_current_period INTEGER DEFAULT 0 NOT NULL",
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS period_start_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL",
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS period_end_date TIMESTAMP"
            ]

            for m in migrations:
                try:
                    conn.execute(text(m))
                    conn.commit()
                except Exception as e:
                    conn.rollback()
                    # Some migrations might fail if type/column already exists but IF NOT EXISTS isn't supported for that syntax
                    # or if ALTER TYPE ADD VALUE is called in a way the DB doesn't like. 
                    # We continue to the next one.
                    if "already exists" not in str(e).lower():
                        print(f"  Migration hint: {m[:40]}... -> {str(e)[:100]}")

            print("✓ Database migrations completed")
    except Exception as e:
        print(f"Migration warning: {str(e)}")

    # Initialize tables
    init_db()
    print("Database initialized!")
    print("Server ready!")

@app.on_event("shutdown")
async def shutdown():
    """Cleanup on shutdown"""
    print("Shutting down CAILculator Auth Server...")

# =============================================================================
# STRIPE HELPERS
# =============================================================================

def safe_get(obj, key, default=None):
    """
    Safely get attribute or key from a StripeObject.
    Newer Stripe SDKs (v5+) raise KeyError from __getattr__ for missing keys,
    which standard getattr() does NOT catch.
    """
    if obj is None:
        return default
    try:
        # Try dict-style access first (most reliable for StripeObject data)
        return obj[key]
    except (KeyError, TypeError):
        try:
            # Fall back to attribute access; catch both potential exceptions
            return getattr(obj, key, default)
        except (AttributeError, KeyError):
            return default

def _mark_event_processed(event_id: str, event_type: str, db: Session) -> None:
    """Record a processed Stripe event ID to prevent duplicate handling on retries."""
    try:
        db.add(ProcessedStripeEvent(event_id=event_id, event_type=event_type))
        db.commit()
    except Exception:
        db.rollback()

# =============================================================================
# API KEY ISSUE AND PROVISIONING
# Keys are shown once and never stored or logged: api_keys holds only the SHA-256.
# =============================================================================

NO_STORE = {"Cache-Control": "no-store", "Pragma": "no-cache", "Referrer-Policy": "no-referrer"}

def _new_api_key(user: User, db: Session, commit: bool = True) -> str:
    """Create an API key for user; store its hash; return the plaintext (caller shows it once)."""
    tier = user.tier.value if hasattr(user.tier, "value") else str(user.tier)
    api_key_plain = f"cail_{tier}_{secrets.token_urlsafe(20)}"
    db.add(APIKey(user_id=user.id, key_hash=hashlib.sha256(api_key_plain.encode()).hexdigest()))
    if commit:
        db.commit()
    return api_key_plain

def _tier_for_subscription(subscription_id: Optional[str]) -> str:
    """Resolve the plan tier from the subscription's price; 'individual' if unknown."""
    if not subscription_id:
        return 'individual'
    try:
        subscription = stripe.Subscription.retrieve(subscription_id)
        price_id = subscription['items']['data'][0]['price']['id']
        return PRICE_TO_TIER.get(price_id, 'individual')
    except Exception as e:
        print(f"❌ Error resolving tier: {e}")
        return 'individual'

def _checkout_customer(session) -> tuple:
    """(email, name, subscription_id) from a Checkout Session."""
    customer_details = safe_get(session, 'customer_details', None)
    email = safe_get(session, 'customer_email', None) or (
        safe_get(customer_details, 'email', None) if customer_details else None
    )
    name = safe_get(customer_details, 'name', None) if customer_details else None
    return email, name, safe_get(session, 'subscription', None)

def _provision_user(db: Session, email: str, name: Optional[str], tier: str,
                    subscription_id: Optional[str]) -> User:
    """Create or update the subscriber's user row (no key). Safe to call twice for one checkout."""
    user = db.query(User).filter(User.email == email).first()
    if user:
        user.tier = SubscriptionTier(tier)
        user.stripe_subscription_id = subscription_id
        user.subscription_status = 'active'
        user.email_verified = 1
        db.commit()
        return user
    user = User(
        email=email,
        name=name or email.split('@')[0],
        tier=SubscriptionTier(tier),
        email_verified=1,
        stripe_subscription_id=subscription_id,
        subscription_status='active',
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        # The webhook and the success page can race to create the same user.
        db.rollback()
        user = db.query(User).filter(User.email == email).first()
        return _provision_user(db, email, name, tier, subscription_id)
    db.refresh(user)
    return user

# =============================================================================
# ADMIN (X-Admin-Token)
# =============================================================================

class AdminIssueRequest(BaseModel):
    email: EmailStr
    rotate: bool = False  # True: revoke the user's existing keys first

def _require_admin(request: Request) -> None:
    token = (ADMIN_TOKEN or "").strip()
    if not token:
        raise HTTPException(status_code=503, detail="Admin endpoints are disabled")
    supplied = request.headers.get("x-admin-token", "")
    if not secrets.compare_digest(supplied.encode(), token.encode()):
        raise HTTPException(status_code=401, detail="Unauthorized")

@app.post("/admin/keys/issue")
async def admin_issue_key(body: AdminIssueRequest, request: Request, db: Session = Depends(get_db)):
    """Issue a key for an existing user (rotate=true revokes their other keys). Returned once."""
    _require_admin(request)
    user = db.query(User).filter(User.email == body.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="No user with that email")
    revoked = 0
    if body.rotate:
        revoked = db.query(APIKey).filter(APIKey.user_id == user.id).delete()
    api_key_plain = _new_api_key(user, db)
    print(f"🔑 Admin issued a key for {user.email} (rotate={body.rotate}, revoked={revoked})")
    return JSONResponse(
        {"email": user.email, "tier": user.tier.value, "api_key": api_key_plain, "revoked": revoked},
        headers=NO_STORE,
    )

@app.get("/admin/keys")
async def admin_list_keys(request: Request, db: Session = Depends(get_db)):
    """List every key: id, owner, dates and the first 12 hex digits of its hash (never the key)."""
    _require_admin(request)
    rows = db.query(APIKey, User).join(User, APIKey.user_id == User.id).order_by(APIKey.id).all()
    return JSONResponse({"keys": [
        {
            "id": k.id, "user_id": u.id, "email": u.email, "tier": u.tier.value,
            "subscription_status": u.subscription_status,
            "created_at": k.created_at.isoformat() if k.created_at else None,
            "last_used_at": k.last_used_at.isoformat() if k.last_used_at else None,
            "hash_prefix": k.key_hash[:12],
        }
        for k, u in rows
    ]}, headers=NO_STORE)

@app.delete("/admin/keys/{key_id}")
async def admin_revoke_key(key_id: int, request: Request, db: Session = Depends(get_db)):
    """Revoke (delete) one key by its id."""
    _require_admin(request)
    deleted = db.query(APIKey).filter(APIKey.id == key_id).delete()
    db.commit()
    if not deleted:
        raise HTTPException(status_code=404, detail="No key with that id")
    print(f"🔑 Admin revoked key id {key_id}")
    return {"revoked": key_id}

# =============================================================================
# STRIPE CHECKOUT
# =============================================================================

@app.get("/create-checkout-session")
async def create_checkout_session(tier: str):
    """
    Create Stripe checkout session for subscription
    """
    if tier not in STRIPE_PRICES:
        raise HTTPException(status_code=400, detail="Invalid subscription tier")

    try:
        # Get the base URL (Railway sets this automatically)
        base_url = os.getenv("RAILWAY_PUBLIC_DOMAIN", "localhost:8000")
        if not base_url.startswith("http"):
            base_url = f"https://{base_url}"

        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price': STRIPE_PRICES[tier],
                'quantity': 1,
            }],
            mode='subscription',
            allow_promotion_codes=True,  # Enable discount/promo codes
            success_url=f"{base_url}/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{base_url}/?canceled=true",
            metadata={
                'tier': tier
            }
        )

        return RedirectResponse(url=checkout_session.url, status_code=303)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/success")
async def success(request: Request, session_id: str, db: Session = Depends(get_db)):
    """
    Success page after checkout. Shows the new API key exactly once.

    The key is created here, not in the webhook, so its plaintext never has to be stored
    or logged: it goes straight to this response, and only its hash is kept. A
    CheckoutKeyReveal row (unique per checkout session) makes the reveal one-time; a reload
    or second visit shows no key.
    """
    def page(**context):
        return templates.TemplateResponse(request=request, name="success.html",
                                          context=context, headers=NO_STORE)

    try:
        session = stripe.checkout.Session.retrieve(session_id)
    except Exception as e:
        print(f"❌ /success: could not retrieve session: {e}")
        return page(error="We couldn't confirm this checkout. If you were charged, email paul@chavezailabs.com.")

    payment_status = safe_get(session, 'payment_status', '') or ''
    if safe_get(session, 'status', '') != 'complete' or payment_status not in ('paid', 'no_payment_required'):
        return page(error="This checkout isn't complete yet. If you were charged, email paul@chavezailabs.com.")

    if db.query(CheckoutKeyReveal).filter(CheckoutKeyReveal.session_id == session_id).first():
        return page(already_revealed=True)

    email, name, subscription_id = _checkout_customer(session)
    if not email:
        return page(error="This checkout has no email address. Please email paul@chavezailabs.com.")

    user = _provision_user(db, email, name, _tier_for_subscription(subscription_id), subscription_id)
    try:
        # One transaction: the reveal row and the key commit together or not at all.
        db.add(CheckoutKeyReveal(session_id=session_id, user_id=user.id))
        api_key_plain = _new_api_key(user, db, commit=False)
        db.commit()
    except IntegrityError:
        db.rollback()  # another request revealed this session's key first
        return page(already_revealed=True)

    print(f"🔑 Key revealed on success page for {email} (session {session_id})")
    return page(api_key=api_key_plain, email=email)

@app.post("/webhook/stripe")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    """
    Handle Stripe webhooks for subscription events.
    Handles both paid and $0 (comped) checkouts via payment_status check.
    The webhook provisions the user only; the API key is created and shown once on the
    success page (/success), and never logged.
    """
    # Fail closed: without a signing secret, anyone could post a forged event. 503 (not 400)
    # so Stripe retries the event once the secret is configured.
    secret = (STRIPE_WEBHOOK_SECRET or "").strip()
    if not secret:
        print("ERROR: STRIPE_WEBHOOK_SECRET not set; webhook refused (503)")
        raise HTTPException(status_code=503, detail="Webhook not configured")

    payload = await request.body()
    sig_header = request.headers.get('stripe-signature')

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, secret)
    except ValueError as e:
        print(f"Invalid webhook payload: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        print(f"Invalid webhook signature: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid signature")

    event_id = event['id']
    event_type = event['type']
    print(f"📥 Stripe event: {event_type} ({event_id})")

    # Idempotency: skip events already handled (covers webhook retries)
    if db.query(ProcessedStripeEvent).filter(
        ProcessedStripeEvent.event_id == event_id
    ).first():
        print(f"   ⏭️  Already processed — skipping")
        return {"status": "already_processed"}

    try:
        # ------------------------------------------------------------------
        # checkout.session.completed
        # Fires for both paid ($) and $0 (no_payment_required / comped) signups.
        # This is the provisioning entry point for ALL new subscribers.
        # ------------------------------------------------------------------
        if event_type == 'checkout.session.completed':
            session = event['data']['object']
            # Use safe_get — newer Stripe SDK (v5+) StripeObjects raise KeyError
            # from __getattr__ for missing keys, which getattr() doesn't catch.
            payment_status = safe_get(session, 'payment_status', '') or ''

            # Guard: only provision for paid or $0-comped checkouts
            if payment_status not in ('paid', 'no_payment_required'):
                print(f"   ⚠️  payment_status={payment_status!r} — skipping provisioning")
                _mark_event_processed(event_id, event_type, db)
                return {"status": "skipped"}

            customer_email, customer_name, subscription_id = _checkout_customer(session)
            session_id = safe_get(session, 'id', None)
            print(f"   Customer     : {customer_email}")
            print(f"   payment_status: {payment_status}")

            if not customer_email:
                print("❌ No customer email in event — cannot provision")
                _mark_event_processed(event_id, event_type, db)
                return {"status": "no_email"}

            tier = _tier_for_subscription(subscription_id)
            _provision_user(db, customer_email, customer_name, tier, subscription_id)

            # No key here: it is created and shown once on /success, never logged.
            print("=" * 56)
            print("✅ NEW SUBSCRIBER — key is shown once on the checkout success page")
            print(f"   To      : {customer_email}")
            print(f"   Name    : {customer_name or '(not provided)'}")
            print(f"   Tier    : {tier}")
            print(f"   Session : {session_id}")
            print("   If they report no key: POST /admin/keys/issue")
            print("=" * 56)

            _mark_event_processed(event_id, event_type, db)

        # ------------------------------------------------------------------
        # invoice.paid
        # Fires on every renewal, including recurring $0 comps.
        # Keeps access alive for journalist/comped tier each billing cycle.
        # ------------------------------------------------------------------
        elif event_type == 'invoice.paid':
            invoice = event['data']['object']
            subscription_id = safe_get(invoice, 'subscription', None)
            if subscription_id:
                user = db.query(User).filter(
                    User.stripe_subscription_id == subscription_id
                ).first()
                if user:
                    user.subscription_status = 'active'
                    db.commit()
                    print(f"✅ invoice.paid: access confirmed for {user.email}")
                else:
                    print(f"⚠️  invoice.paid: no user found for subscription {subscription_id}")
            _mark_event_processed(event_id, event_type, db)

        # ------------------------------------------------------------------
        # customer.subscription.deleted — revoke access on cancellation
        # ------------------------------------------------------------------
        elif event_type == 'customer.subscription.deleted':
            subscription = event['data']['object']
            subscription_id = safe_get(subscription, 'id', None)
            if subscription_id:
                user = db.query(User).filter(
                    User.stripe_subscription_id == subscription_id
                ).first()
                if user:
                    user.subscription_status = 'canceled'
                    db.commit()
                    print(f"✅ subscription.deleted: access revoked for {user.email}")
            _mark_event_processed(event_id, event_type, db)

        # ------------------------------------------------------------------
        # customer.subscription.updated — sync status (past_due, unpaid, etc.)
        # ------------------------------------------------------------------
        elif event_type == 'customer.subscription.updated':
            subscription = event['data']['object']
            subscription_id = safe_get(subscription, 'id', None)
            status = safe_get(subscription, 'status', None)
            if subscription_id and status:
                user = db.query(User).filter(
                    User.stripe_subscription_id == subscription_id
                ).first()
                if user:
                    user.subscription_status = status
                    db.commit()
                    print(f"✅ subscription.updated: status={status!r} for {user.email}")
            _mark_event_processed(event_id, event_type, db)

        return {"status": "success"}

    except Exception as e:
        import traceback
        print(f"❌ WEBHOOK CRASH: {e}")
        traceback.print_exc()
        # Raise 500 to tell Stripe we failed; they will retry.
        # This gives us a chance to fix bugs without losing data.
        raise HTTPException(status_code=500, detail="Internal server error")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
