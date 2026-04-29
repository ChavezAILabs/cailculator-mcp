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
    SignupAttempt
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
    "individual": "price_1SNlPU2NNm10BnLC1ufwG07s",    # $79.99/month - 25,000 requests
    "academic": "price_1SNlQz2NNm10BnLC3wFUtekN",      # $199/month - 75,000 requests
    "commercial": "price_1SNlUg2NNm10BnLCy2NhebOI",    # $299/month per seat - 250,000 requests
    # Quant Trader Tiers (BETA)
    "quant_explorer": "price_1SQGie2NNm10BnLCyraRcDSA",      # $599/month - 100,000 requests
    "quant_professional": "price_1SXDc82NNm10BnLC36hwqnaA",  # $1,499/month - 500,000 requests
    "quant_elite": "price_1SQGox2NNm10BnLCcROJSo91"          # $3,499/month - Unlimited
    # Enterprise and Quant Enterprise are custom pricing (contact sales)
}

# Monthly request limits by tier
TIER_LIMITS = {
    "individual": 25000,
    "academic": 75000,
    "commercial": 250000,
    "enterprise": 999999999,  # Unlimited (or very high limit)
    # Quant Trader Tiers (BETA)
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
# SUBSCRIPTION LIMITS
# =============================================================================

TIER_LIMITS = {
    "individual": 25_000,       # $79.99/month - 25,000 requests
    "academic": 75_000,         # $199/month - 75,000 requests
    "commercial": 250_000,      # $299/month per seat - 250,000 requests
    "enterprise": -1,           # Custom pricing - Unlimited
    # Quant Trader Tiers (BETA)
    "quant_explorer": 100_000,      # $599/month - 100,000 requests
    "quant_professional": 500_000,  # $1,499/month - 500,000 requests
    "quant_elite": -1               # $3,499/month - Unlimited
}

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

def send_api_key_email(email: str, api_key: str, tier: str) -> bool:
    """
    Send API key to user after paid subscription or manual approval
    Returns True if successful, False otherwise
    """
    if not SENDGRID_API_KEY:
        print("WARNING: SENDGRID_API_KEY not set, skipping email")
        return False

    tier_info = {
        "individual": {"limit": "25,000 requests/month", "price": "$79.99/month"},
        "academic": {"limit": "75,000 requests/month", "price": "$199/month"},
        "commercial": {"limit": "250,000 requests/month per seat", "price": "$299/month per seat"},
        "enterprise": {"limit": "Unlimited", "price": "Custom pricing"},
        # Quant Trader Tiers (BETA)
        "quant_explorer": {"limit": "100,000 requests/month", "price": "$599/month"},
        "quant_professional": {"limit": "500,000 requests/month", "price": "$1,499/month"},
        "quant_elite": {"limit": "Unlimited requests", "price": "$3,499/month"}
    }

    tier_details = tier_info.get(tier, {"limit": "Unknown", "price": "Unknown"})

    message = Mail(
        from_email=SENDGRID_FROM_EMAIL,
        to_emails=email,
        subject="Your CAILculator MCP API Key",
        html_content=f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="text-align: center; margin-bottom: 30px;">
                    <h1 style="color: #667eea;">CAILculator MCP</h1>
                    <p style="color: #666; font-style: italic;">"Better math, less suffering"</p>
                </div>

                <h2>Your API Key is Ready!</h2>

                <p>Welcome to CAILculator MCP! Your account has been approved and your API key is ready to use.</p>

                <div style="background-color: #f7fafc; border-left: 4px solid #667eea; padding: 15px; margin: 20px 0;">
                    <p style="margin: 0; font-weight: bold; color: #667eea;">Your Subscription Details:</p>
                    <p style="margin: 5px 0;"><strong>Tier:</strong> {tier.capitalize()}</p>
                    <p style="margin: 5px 0;"><strong>Price:</strong> {tier_details['price']}</p>
                    <p style="margin: 5px 0;"><strong>Usage Limit:</strong> {tier_details['limit']}</p>
                </div>

                <div style="background-color: #2d3748; color: #e2e8f0; padding: 15px; border-radius: 5px; margin: 20px 0; font-family: monospace; word-break: break-all;">
                    <p style="margin: 0; font-size: 0.9em;"><strong>API Key:</strong></p>
                    <p style="margin: 5px 0; font-size: 1em;">{api_key}</p>
                </div>

                <div style="background-color: #fff5f5; border-left: 4px solid #f56565; padding: 15px; margin: 20px 0;">
                    <p style="margin: 0; color: #c53030;"><strong>⚠️ Important:</strong> Keep this API key secure! It's like a password for your account.</p>
                </div>

                <h3>Getting Started</h3>
                <ol style="line-height: 1.8;">
                    <li>Copy your API key above</li>
                    <li>Add it to your Claude Desktop configuration</li>
                    <li>Restart Claude Desktop</li>
                    <li>Start exploring zero divisors in high-dimensional algebras!</li>
                </ol>

                <p>For setup instructions and documentation, visit: <a href="https://github.com/pchavez2029/CAILculator" style="color: #667eea;">github.com/pchavez2029/CAILculator</a></p>

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
        print(f"API key email sent to {email}: Status {response.status_code}")
        return response.status_code in [200, 202]
    except Exception as e:
        print(f"Failed to send API key email to {email}: {str(e)}")
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
        "academic": "Academic",
        "commercial": "Commercial",
        "enterprise": "Enterprise",
        "quant_explorer": "Quant Explorer (BETA)",
        "quant_professional": "Quant Professional (BETA)",
        "quant_elite": "Quant Elite (BETA)"
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

Documentation: https://github.com/pchavez2029/CAILculator
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
    Handle Stripe webhooks for subscription events
    """
    payload = await request.body()
    sig_header = request.headers.get('stripe-signature')

    # Verify webhook signature for security
    try:
        if STRIPE_WEBHOOK_SECRET:
            event = stripe.Webhook.construct_event(
                payload, sig_header, STRIPE_WEBHOOK_SECRET
            )
        else:
            # Fallback for development (not recommended for production)
            import json
            event = stripe.Event.construct_from(
                json.loads(payload.decode('utf-8')), stripe.api_key
            )
            print("WARNING: STRIPE_WEBHOOK_SECRET not set, webhook signature not verified")
    except ValueError as e:
        # Invalid payload
        print(f"Invalid webhook payload: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        print(f"Invalid webhook signature: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid signature")

    # Handle successful subscription creation
    if event['type'] == 'checkout.session.completed':
        print(f"📥 Received event: checkout.session.completed")
        session = event['data']['object']

        # Get customer email
        customer_email = session.get('customer_email') or session.get('customer_details', {}).get('email')
        customer_name = session.get('customer_details', {}).get('name')
        print(f"   Customer: {customer_email} ({customer_name})")

        # Map price ID to tier (LIVE STRIPE PRICES - updated 2025-10-29)
        subscription_id = session.get('subscription')
        tier = 'individual'  # Default

        if subscription_id:
            try:
                subscription = stripe.Subscription.retrieve(subscription_id)
                price_id = subscription['items']['data'][0]['price']['id']
                print(f"   Subscription ID: {subscription_id}")
                print(f"   Price ID: {price_id}")

                # Map your live price IDs to tiers
                price_to_tier = {
                    "price_1SNlPU2NNm10BnLC1ufwG07s": "individual",   # $79.99/month
                    "price_1SNlQz2NNm10BnLC3wFUtekN": "academic",     # $199/month
                    "price_1SNlUg2NNm10BnLCy2NhebOI": "commercial",   # $299/month
                    # Quant Trader Tiers (BETA)
                    "price_1SQGie2NNm10BnLCyraRcDSA": "quant_explorer",      # $599/month
                    "price_1SXDc82NNm10BnLC36hwqnaA": "quant_professional",  # $1,499/month
                    "price_1SQGox2NNm10BnLCcROJSo91": "quant_elite"          # $3,499/month
                }

                tier = price_to_tier.get(price_id, 'individual')
                print(f"   Mapped to tier: {tier}")
            except Exception as e:
                print(f"❌ Error getting subscription tier: {e}")
                tier = 'individual'
        else:
            print(f"⚠️  No subscription ID in session")

        if customer_email:
            # Check if user already exists
            existing_user = db.query(User).filter(User.email == customer_email).first()

            if existing_user:
                print(f"⚠️  User already exists: {customer_email}")
                # Generate new API key for existing user
                api_key_plain = f"cail_{tier}_{secrets.token_urlsafe(20)}"
                api_key_hash = hashlib.sha256(api_key_plain.encode()).hexdigest()

                api_key_record = APIKey(
                    user_id=existing_user.id,
                    key_hash=api_key_hash
                )
                db.add(api_key_record)
                db.commit()
                print(f"✅ Generated new API key for existing user")
                print(f"✅ DB STORED - existing user key for {customer_email}: {api_key_plain}")
            else:
                # Create user
                print(f"   Creating new user...")
                user = User(
                    email=customer_email,
                    name=customer_name or customer_email.split('@')[0],
                    tier=SubscriptionTier(tier)
                )
                db.add(user)
                db.commit()
                db.refresh(user)
                print(f"✅ Created user: {customer_email}")

                # Generate API key
                api_key_plain = f"cail_{tier}_{secrets.token_urlsafe(20)}"
                api_key_hash = hashlib.sha256(api_key_plain.encode()).hexdigest()

                api_key_record = APIKey(
                    user_id=user.id,
                    key_hash=api_key_hash
                )
                db.add(api_key_record)
                db.commit()
                print(f"✅ Generated API key")
                print(f"✅ DB STORED - new user key for {customer_email}: {api_key_plain}")

            # SendGrid email disabled - retrieve keys from logs and send manually
            # send_api_key_email(customer_email, api_key_plain, tier, customer_name)
            print(f"✅ Complete! API key stored in DB. Manual email delivery needed.")
            print(f"   Customer: {customer_email} | Tier: {tier} | Key: {api_key_plain}")

    return {"status": "success"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
