"""
CAILculator Auth Server - FastAPI Backend for Railway
Handles API key validation and usage tracking
"""

from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, EmailStr
from typing import Optional
import os
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from pathlib import Path
import stripe
import secrets
import hashlib
import requests
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from database import (
    get_db,
    init_db,
    User,
    APIKey,
    UsageLog,
    SubscriptionTier,
    SignupAttempt,
    ProcessedStripeEvent,
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

# Stripe Price IDs (LIVE MODE - Production)
STRIPE_PRICES = {
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

# SendGrid configuration
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
SENDGRID_FROM_EMAIL = os.getenv("SENDGRID_FROM_EMAIL", "iknowpi@gmail.com")

# Auto-approved countries (US, Canada, EU, UK, Australia, Japan, New Zealand)
AUTO_APPROVED_COUNTRIES = {
    "US", "CA",  # North America
    "GB", "IE",  # UK & Ireland
    "AU", "NZ",  # Oceania
    "JP", "KR", "SG",  # Asia (friendly)
    # EU countries
    "AT", "BE", "BG", "HR", "CY", "CZ", "DK", "EE", "FI", "FR",
    "DE", "GR", "HU", "IT", "LV", "LT", "LU", "MT", "NL", "PL",
    "PT", "RO", "SK", "SI", "ES", "SE", "NO", "CH", "IS"
}

# IP rate limiting: max signups per IP per day
MAX_SIGNUPS_PER_IP_PER_DAY = 3

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

class SignupRequest(BaseModel):
    email: EmailStr
    name: Optional[str] = None

class SignupResponse(BaseModel):
    user_id: int
    email: str
    api_key: str
    tier: str
    message: str

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

def get_client_ip(request: Request) -> str:
    """Get client IP address from request"""
    # Check for Railway/proxy forwarded IP first
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()

    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip

    # Fallback to direct connection
    if request.client:
        return request.client.host

    return "unknown"

def get_country_from_ip(ip_address: str) -> Optional[str]:
    """
    Get country code from IP address using free ipapi.co service
    Returns 2-letter ISO country code or None
    """
    if ip_address == "unknown" or ip_address.startswith("127.") or ip_address.startswith("192.168."):
        return "US"  # Default for localhost/development

    try:
        response = requests.get(f"https://ipapi.co/{ip_address}/country/", timeout=2)
        if response.status_code == 200:
            country_code = response.text.strip()
            return country_code if len(country_code) == 2 else None
    except:
        pass

    return None

def check_ip_rate_limit(ip_address: str, db: Session) -> tuple[bool, int]:
    """
    Check if IP has exceeded signup rate limit
    Returns: (is_allowed, signup_count_today)
    """
    # Count signups from this IP in last 24 hours
    twenty_four_hours_ago = datetime.utcnow() - timedelta(hours=24)

    signup_count = db.query(SignupAttempt).filter(
        SignupAttempt.ip_address == ip_address,
        SignupAttempt.timestamp >= twenty_four_hours_ago
    ).count()

    is_allowed = signup_count < MAX_SIGNUPS_PER_IP_PER_DAY
    return is_allowed, signup_count

def send_verification_email(email: str, verification_token: str, base_url: str) -> bool:
    """
    Send email verification link using SendGrid
    Returns True if successful, False otherwise
    """
    if not SENDGRID_API_KEY:
        print("WARNING: SENDGRID_API_KEY not set, skipping email")
        return False

    verification_url = f"{base_url}/verify-email?token={verification_token}"

    message = Mail(
        from_email=SENDGRID_FROM_EMAIL,
        to_emails=email,
        subject="Verify your CAILculator MCP account",
        html_content=f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="text-align: center; margin-bottom: 30px;">
                    <h1 style="color: #667eea;">CAILculator MCP</h1>
                    <p style="color: #666; font-style: italic;">"Better math, less suffering"</p>
                </div>

                <h2>Welcome to CAILculator MCP!</h2>

                <p>Thank you for signing up. You're one step away from accessing high-dimensional mathematical analysis tools.</p>

                <div style="text-align: center; margin: 30px 0;">
                    <a href="{verification_url}"
                       style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                              color: white;
                              padding: 15px 40px;
                              text-decoration: none;
                              border-radius: 5px;
                              display: inline-block;
                              font-weight: bold;">
                        Verify Email Address
                    </a>
                </div>

                <p style="color: #666; font-size: 0.9em;">
                    This link will expire in 24 hours. If you didn't create this account, you can safely ignore this email.
                </p>

                <p style="color: #666; font-size: 0.9em; margin-top: 30px;">
                    Or copy and paste this URL into your browser:<br>
                    <a href="{verification_url}" style="color: #667eea;">{verification_url}</a>
                </p>

                <hr style="margin: 30px 0; border: none; border-top: 1px solid #ddd;">

                <p style="color: #999; font-size: 0.85em; text-align: center;">
                    <strong>Chavez AI Labs</strong><br>
                    Research tools for high-dimensional mathematics<br>
                    <a href="mailto:iknowpi@gmail.com" style="color: #667eea;">iknowpi@gmail.com</a>
                </p>
            </div>
        </body>
        </html>
        """
    )

    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        print(f"Verification email sent to {email}: Status {response.status_code}")
        return response.status_code in [200, 202]
    except Exception as e:
        print(f"Failed to send email to {email}: {str(e)}")
        return False

def send_manual_approval_pending_email(email: str, country_code: str) -> bool:
    """
    Notify user that their signup requires manual approval
    Returns True if successful, False otherwise
    """
    if not SENDGRID_API_KEY:
        print("WARNING: SENDGRID_API_KEY not set, skipping email")
        return False

    message = Mail(
        from_email=SENDGRID_FROM_EMAIL,
        to_emails=email,
        subject="CAILculator MCP - Manual Approval Required",
        html_content=f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="text-align: center; margin-bottom: 30px;">
                    <h1 style="color: #667eea;">CAILculator MCP</h1>
                    <p style="color: #666; font-style: italic;">"Better math, less suffering"</p>
                </div>

                <h2>Email Verified - Approval Pending</h2>

                <p>Thank you for verifying your email address! Your signup from <strong>{country_code or 'your region'}</strong> requires manual approval as part of our security process.</p>

                <div style="background-color: #f7fafc; border-left: 4px solid #667eea; padding: 15px; margin: 20px 0;">
                    <p style="margin: 0; font-weight: bold; color: #667eea;">What happens next?</p>
                    <ul style="margin: 10px 0; padding-left: 20px;">
                        <li>Our team will review your signup within 24 hours</li>
                        <li>You'll receive your API key via email once approved</li>
                        <li>No action required from you - just sit tight!</li>
                    </ul>
                </div>

                <div style="background-color: #fffaf0; border-left: 4px solid #ed8936; padding: 15px; margin: 20px 0;">
                    <p style="margin: 0; color: #7c2d12;"><strong>Why manual approval?</strong></p>
                    <p style="margin: 10px 0 0 0; color: #7c2d12;">We review signups from certain regions to prevent abuse and maintain service quality for legitimate researchers and developers.</p>
                </div>

                <p>We appreciate your patience and look forward to having you explore high-dimensional mathematics with CAILculator MCP!</p>

                <hr style="margin: 30px 0; border: none; border-top: 1px solid #ddd;">

                <p style="color: #999; font-size: 0.85em; text-align: center;">
                    <strong>Chavez AI Labs</strong><br>
                    Research tools for high-dimensional mathematics<br>
                    Questions? Reply to this email or contact <a href="mailto:iknowpi@gmail.com" style="color: #667eea;">iknowpi@gmail.com</a>
                </p>
            </div>
        </body>
        </html>
        """
    )

    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        print(f"Manual approval notification sent to {email}: Status {response.status_code}")
        return response.status_code in [200, 202]
    except Exception as e:
        print(f"Failed to send manual approval email to {email}: {str(e)}")
        return False

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

def send_api_key_email(email: str, api_key: str, tier: str, customer_name: str = None):
    """
    Send API key to customer via email using SendGrid
    """
    if not SENDGRID_API_KEY:
        print(f"⚠️  SendGrid not configured - API key: {api_key}")
        return

    # Friendly tier names
    tier_names = {
        "individual": "Individual",
        "journalist": "Journalist",
        "academic": "Academic",
        "commercial": "Commercial",
        "enterprise": "Enterprise",
        "quant_explorer": "Quant Explorer",
        "quant_professional": "Quant Professional",
        "quant_elite": "Quant Elite"
    }
    tier_display = tier_names.get(tier, tier.replace('_', ' ').title())

    # Email body
    body = f"""
Hello{f' {customer_name}' if customer_name else ''},

Thank you for subscribing to CAILculator {tier_display}!

Your API key is ready:

    {api_key}

To get started:

1. Install Claude Desktop (if you haven't already)
2. Add CAILculator to your MCP configuration:

   Windows: %APPDATA%\\Claude\\claude_desktop_config.json
   Mac/Linux: ~/Library/Application Support/Claude/claude_desktop_config.json

3. Add this configuration:

{{
  "mcpServers": {{
    "cailculator-mcp": {{
      "command": "uvx",
      "args": ["cailculator-mcp"],
      "env": {{
        "CAILCULATOR_API_KEY": "{api_key}"
      }}
    }}
  }}
}}

4. Restart Claude Desktop

Documentation: https://github.com/ChavezAILabs/cailculator-mcp
Support: iknowpi@gmail.com

Features included in your {tier_display} plan:
- All 5 MCP tools (compute, transform, patterns, analysis, visualizations)
- Dual framework support (Cayley-Dickson + Clifford)
- 16D-256D dimensional range
- Chavez Transform data analysis
- Canonical Six pattern detection

Better math, less suffering.

— Chavez AI Labs

---
Need help? Reply to this email or reach out at iknowpi@gmail.com
    """.strip()

    try:
        message = Mail(
            from_email=SENDGRID_FROM_EMAIL,
            to_emails=email,
            subject="Your CAILculator API Key",
            plain_text_content=body
        )

        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)

        if response.status_code in [200, 201, 202]:
            print(f"✅ Sent API key email to {email}")
        else:
            print(f"⚠️  SendGrid returned status {response.status_code}")

    except Exception as e:
        print(f"❌ Failed to send email to {email}: {e}")
        print(f"   API key (manual delivery needed): {api_key}")

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

@app.post("/migrate-db")
async def migrate_database(db: Session = Depends(get_db)):
    """
    One-time database migration to add rate limiting columns
    Safe to run multiple times (uses IF NOT EXISTS)
    """
    from sqlalchemy import text

    migrations = [
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS request_count_current_period INTEGER DEFAULT 0 NOT NULL",
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS period_start_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL",
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS period_end_date TIMESTAMP",
        # Add new enum values to PostgreSQL enum type
        "ALTER TYPE subscriptiontier ADD VALUE IF NOT EXISTS 'individual'",
        "ALTER TYPE subscriptiontier ADD VALUE IF NOT EXISTS 'journalist'",
        "ALTER TYPE subscriptiontier ADD VALUE IF NOT EXISTS 'commercial'",
        # Update old enum values to new ones (cast to text for comparison)
        "UPDATE users SET tier = 'individual' WHERE tier::text = 'free'",
        "UPDATE users SET tier = 'individual' WHERE tier::text = 'indie'",
        "UPDATE users SET tier = 'commercial' WHERE tier::text = 'professional'"
    ]

    results = []
    for migration in migrations:
        try:
            db.execute(text(migration))
            db.commit()
            results.append({"sql": migration, "status": "success"})
        except Exception as e:
            db.rollback()
            results.append({"sql": migration, "status": "failed", "error": str(e)})

    return {
        "message": "Migration completed",
        "migrations": results
    }

@app.post("/signup")
async def signup(signup_request: SignupRequest, request: Request, db: Session = Depends(get_db)):
    """
    Create new user account and send verification email
    API key generated after email verification
    """
    # Get client IP
    client_ip = get_client_ip(request)

    # Check IP rate limit
    is_allowed, signup_count = check_ip_rate_limit(client_ip, db)
    if not is_allowed:
        raise HTTPException(
            status_code=429,
            detail=f"Too many signup attempts from your IP address. Limit: {MAX_SIGNUPS_PER_IP_PER_DAY} per day."
        )

    # Check if user already exists
    existing_user = db.query(User).filter(User.email == signup_request.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Get country from IP
    country_code = get_country_from_ip(client_ip)

    # Check if auto-approved or requires manual approval
    requires_manual = (country_code not in AUTO_APPROVED_COUNTRIES) if country_code else True

    # Generate verification token
    verification_token = secrets.token_urlsafe(32)
    token_expires = datetime.utcnow() + timedelta(hours=24)

    # Create user (WITHOUT API key yet - will be upgraded to paid tier via Stripe webhook)
    user = User(
        email=signup_request.email,
        name=signup_request.name or signup_request.email.split('@')[0],
        tier=SubscriptionTier.INDIVIDUAL,  # Default tier (will be updated by Stripe webhook)
        email_verified=0,
        verification_token=verification_token,
        verification_token_expires=token_expires,
        country_code=country_code,
        signup_ip=client_ip,
        requires_manual_approval=1 if requires_manual else 0
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Log signup attempt
    signup_attempt = SignupAttempt(
        ip_address=client_ip,
        success=1
    )
    db.add(signup_attempt)
    db.commit()

    # Get base URL
    base_url = os.getenv("RAILWAY_PUBLIC_DOMAIN", request.base_url)
    if isinstance(base_url, str) and not base_url.startswith("http"):
        base_url = f"https://{base_url}"
    else:
        base_url = str(base_url).rstrip("/")

    # Send verification email
    email_sent = send_verification_email(signup_request.email, verification_token, base_url)

    if not email_sent:
        # Email failed but user created - they can resend later
        print(f"WARNING: Failed to send verification email to {signup_request.email}")

    response_message = "Account created! Please check your email to verify your account."
    if requires_manual:
        response_message += f" Note: Signups from {country_code or 'your region'} require manual approval. You will receive your API key within 24 hours of approval."

    return {
        "message": response_message,
        "email": signup_request.email,
        "requires_manual_approval": requires_manual,
        "email_sent": email_sent
    }

# Free tier removed - all tiers now require payment
# @app.get("/signup-free", response_class=HTMLResponse)
# async def signup_free_page(request: Request):
#     """
#     Free tier signup page (simple email form) - DEPRECATED
#     """
#     return templates.TemplateResponse(request=request, name="signup_free.html")

@app.get("/verify-email", response_class=HTMLResponse)
async def verify_email(request: Request, token: str, db: Session = Depends(get_db)):
    """
    Verify email address and generate API key
    """
    # Find user by verification token
    user = db.query(User).filter(User.verification_token == token).first()

    if not user:
        return templates.TemplateResponse(request=request, name="verification_result.html", context={
            "success": False,
            "message": "Invalid verification link. The token may have expired or already been used."
        })

    # Check if token expired
    if user.verification_token_expires and user.verification_token_expires < datetime.utcnow():
        return templates.TemplateResponse(request=request, name="verification_result.html", context={
            "success": False,
            "message": "Verification link has expired. Please sign up again."
        })

    # Check if already verified
    if user.email_verified == 1:
        # Find existing API key
        existing_key = db.query(APIKey).filter(APIKey.user_id == user.id).first()
        if existing_key:
            return templates.TemplateResponse(request=request, name="verification_result.html", context={
                "success": True,
                "message": "Email already verified. Your API key was sent previously.",
                "already_verified": True
            })

    # Check if requires manual approval
    if user.requires_manual_approval == 1:
        user.email_verified = 1
        user.verification_token = None
        db.commit()

        # Send manual approval notification email
        send_manual_approval_pending_email(user.email, user.country_code)

        return templates.TemplateResponse(request=request, name="verification_result.html", context={
            "success": True,
            "message": f"Email verified! Your signup from {user.country_code or 'your region'} requires manual approval. You will receive your API key within 24 hours.",
            "requires_approval": True
        })

    # Generate API key
    api_key_plain = f"cail_{secrets.token_urlsafe(32)}"
    api_key_hash = hashlib.sha256(api_key_plain.encode()).hexdigest()

    # Mark as verified
    user.email_verified = 1
    user.verification_token = None

    # Create API key record
    api_key_record = APIKey(
        user_id=user.id,
        key_hash=api_key_hash
    )
    db.add(api_key_record)
    db.commit()

    return templates.TemplateResponse(request=request, name="verification_result.html", context={
        "success": True,
        "api_key": api_key_plain,
        "email": user.email,
        "tier": user.tier.value,
        "message": "Email verified successfully! Your API key is ready."
    })

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
            # Add missing columns if they don't exist
            print("Running database migrations...")

            # Force database reset if RESET_DATABASE env var is set
            reset_db = os.getenv("RESET_DATABASE", "false").lower() == "true"
            if reset_db:
                print("RESET_DATABASE=true detected - recreating all tables...")
                try:
                    conn.execute(text("DROP TABLE IF EXISTS users CASCADE"))
                    conn.execute(text("DROP TABLE IF EXISTS api_keys CASCADE"))
                    conn.execute(text("DROP TABLE IF EXISTS usage_logs CASCADE"))
                    conn.execute(text("DROP TABLE IF EXISTS signup_attempts CASCADE"))
                    conn.execute(text("DROP TYPE IF EXISTS subscriptiontier CASCADE"))
                    conn.commit()
                    print("✓ Database reset complete - tables will be recreated")
                except Exception as reset_error:
                    print(f"Reset error: {str(reset_error)}")
                    conn.rollback()

            conn.execute(text("""
                ALTER TABLE users
                ADD COLUMN IF NOT EXISTS email_verified INTEGER DEFAULT 0 NOT NULL
            """))

            conn.execute(text("""
                ALTER TABLE users
                ADD COLUMN IF NOT EXISTS verification_token VARCHAR
            """))

            conn.execute(text("""
                ALTER TABLE users
                ADD COLUMN IF NOT EXISTS verification_token_expires TIMESTAMP
            """))

            conn.execute(text("""
                ALTER TABLE users
                ADD COLUMN IF NOT EXISTS country_code VARCHAR(2)
            """))

            conn.execute(text("""
                ALTER TABLE users
                ADD COLUMN IF NOT EXISTS signup_ip VARCHAR
            """))

            conn.execute(text("""
                ALTER TABLE users
                ADD COLUMN IF NOT EXISTS requires_manual_approval INTEGER DEFAULT 0 NOT NULL
            """))

            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS ix_users_verification_token
                ON users(verification_token)
            """))

            conn.execute(text("""
                ALTER TABLE users
                ADD COLUMN IF NOT EXISTS stripe_subscription_id VARCHAR
            """))

            conn.execute(text("""
                ALTER TABLE users
                ADD COLUMN IF NOT EXISTS subscription_status VARCHAR
            """))

            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS ix_users_stripe_subscription_id
                ON users(stripe_subscription_id)
            """))

            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS processed_stripe_events (
                    id SERIAL PRIMARY KEY,
                    event_id VARCHAR UNIQUE NOT NULL,
                    event_type VARCHAR NOT NULL,
                    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
                )
            """))

            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS ix_processed_stripe_events_event_id
                ON processed_stripe_events(event_id)
            """))

            conn.commit()
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

def _mark_event_processed(event_id: str, event_type: str, db: Session) -> None:
    """Record a processed Stripe event ID to prevent duplicate handling on retries."""
    try:
        db.add(ProcessedStripeEvent(event_id=event_id, event_type=event_type))
        db.commit()
    except Exception:
        db.rollback()

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
async def success(request: Request, session_id: str):
    """
    Success page after checkout
    """
    try:
        session = stripe.checkout.Session.retrieve(session_id)

        return templates.TemplateResponse(request=request, name="success.html", context={
            "session": session
        })
    except Exception as e:
        return templates.TemplateResponse(request=request, name="success.html", context={
            "error": str(e)
        })

@app.post("/webhook/stripe")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    """
    Handle Stripe webhooks for subscription events.
    Handles both paid and $0 (comped) checkouts via payment_status check.
    API keys are stored in DB; manual email delivery required.
    """
    payload = await request.body()
    sig_header = request.headers.get('stripe-signature')

    try:
        if STRIPE_WEBHOOK_SECRET:
            event = stripe.Webhook.construct_event(
                payload, sig_header, STRIPE_WEBHOOK_SECRET
            )
        else:
            import json
            event = stripe.Event.construct_from(
                json.loads(payload.decode('utf-8')), stripe.api_key
            )
            print("WARNING: STRIPE_WEBHOOK_SECRET not set, webhook signature not verified")
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

    # ------------------------------------------------------------------
    # checkout.session.completed
    # Fires for both paid ($) and $0 (no_payment_required / comped) signups.
    # This is the provisioning entry point for ALL new subscribers.
    # ------------------------------------------------------------------
    if event_type == 'checkout.session.completed':
        session = event['data']['object']
        # Use getattr throughout — newer Stripe SDK (v5+) StripeObjects don't
        # support .get(); calling .get() triggers __getattr__ → KeyError: 'get'
        payment_status = getattr(session, 'payment_status', '') or ''

        # Guard: only provision for paid or $0-comped checkouts
        if payment_status not in ('paid', 'no_payment_required'):
            print(f"   ⚠️  payment_status={payment_status!r} — skipping provisioning")
            _mark_event_processed(event_id, event_type, db)
            return {"status": "skipped"}

        customer_details = getattr(session, 'customer_details', None)
        customer_email = getattr(session, 'customer_email', None) or (
            getattr(customer_details, 'email', None) if customer_details else None
        )
        customer_name = getattr(customer_details, 'name', None) if customer_details else None
        subscription_id = getattr(session, 'subscription', None)
        session_id = getattr(session, 'id', None)

        print(f"   Customer     : {customer_email}")
        print(f"   payment_status: {payment_status}")

        tier = 'individual'
        if subscription_id:
            try:
                subscription = stripe.Subscription.retrieve(subscription_id)
                price_id = subscription['items']['data'][0]['price']['id']
                price_to_tier = {
                    "price_1Tdyrt2NNm10BnLCMe5wP9XN": "individual",
                    "price_1Tdyl42NNm10BnLCRgqZQnUF": "journalist",
                    "price_1TdyvL2NNm10BnLC5704Cv5U": "academic",
                    "price_1TdyxN2NNm10BnLCI9XjeRNt": "commercial",
                    "price_1SQGie2NNm10BnLCyraRcDSA": "quant_explorer",
                    "price_1SXDc82NNm10BnLC36hwqnaA": "quant_professional",
                    "price_1SQGox2NNm10BnLCcROJSo91": "quant_elite",
                }
                tier = price_to_tier.get(price_id, 'individual')
                print(f"   Tier         : {tier}")
                print(f"   Subscription : {subscription_id}")
            except Exception as e:
                print(f"❌ Error resolving tier: {e}")
        else:
            print("⚠️  No subscription ID in session")

        if not customer_email:
            print("❌ No customer email in event — cannot provision key")
            _mark_event_processed(event_id, event_type, db)
            return {"status": "no_email"}

        existing_user = db.query(User).filter(User.email == customer_email).first()
        if existing_user:
            existing_user.tier = SubscriptionTier(tier)
            existing_user.stripe_subscription_id = subscription_id
            existing_user.subscription_status = 'active'
            existing_user.email_verified = 1
            db.commit()
            target_user = existing_user
        else:
            target_user = User(
                email=customer_email,
                name=customer_name or customer_email.split('@')[0],
                tier=SubscriptionTier(tier),
                email_verified=1,
                stripe_subscription_id=subscription_id,
                subscription_status='active',
            )
            db.add(target_user)
            db.commit()
            db.refresh(target_user)

        api_key_plain = f"cail_{tier}_{secrets.token_urlsafe(20)}"
        api_key_hash = hashlib.sha256(api_key_plain.encode()).hexdigest()
        db.add(APIKey(user_id=target_user.id, key_hash=api_key_hash))
        db.commit()

        # ── ACTION REQUIRED LOG ────────────────────────────────────────
        # Railway log alert pattern: "ACTION REQUIRED"
        print("=" * 56)
        print("✅ ACTION REQUIRED — SEND API KEY MANUALLY")
        print(f"   To      : {customer_email}")
        print(f"   Name    : {customer_name or '(not provided)'}")
        print(f"   Tier    : {tier}")
        print(f"   API Key : {api_key_plain}")
        print(f"   Session : {session_id}")
        print("=" * 56)

        _mark_event_processed(event_id, event_type, db)

    # ------------------------------------------------------------------
    # invoice.paid
    # Fires on every renewal, including recurring $0 comps.
    # Keeps access alive for journalist/comped tier each billing cycle.
    # ------------------------------------------------------------------
    elif event_type == 'invoice.paid':
        invoice = event['data']['object']
        subscription_id = getattr(invoice, 'subscription', None)
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
        subscription_id = getattr(subscription, 'id', None)
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
        subscription_id = getattr(subscription, 'id', None)
        status = getattr(subscription, 'status', None)
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

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
