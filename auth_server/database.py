"""
Database models and connection for CAILculator Auth Server
Uses PostgreSQL (provided by Railway)
"""

import os
from datetime import datetime
from enum import Enum
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Enum as SQLEnum, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

# Database URL from environment (Railway sets this automatically)
DATABASE_URL = os.getenv("DATABASE_URL")

# Railway uses postgres:// but SQLAlchemy 1.4+ needs postgresql://
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Fallback for local development
if not DATABASE_URL:
    DATABASE_URL = "postgresql://localhost/cailculator_dev"
    print(f"WARNING: Using local database: {DATABASE_URL}")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# =============================================================================
# ENUMS
# =============================================================================

class SubscriptionTier(str, Enum):
    INDIVIDUAL = "individual"
    JOURNALIST = "journalist"
    ACADEMIC = "academic"
    COMMERCIAL = "commercial"
    ENTERPRISE = "enterprise"
    QUANT_EXPLORER = "quant_explorer"
    QUANT_PROFESSIONAL = "quant_professional"
    QUANT_ELITE = "quant_elite"

# =============================================================================
# MODELS
# =============================================================================

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=True)
    tier = Column(SQLEnum(SubscriptionTier), default=SubscriptionTier.INDIVIDUAL, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Email verification
    email_verified = Column(Integer, default=0, nullable=False)  # 0=pending, 1=verified
    verification_token = Column(String, nullable=True, index=True)
    verification_token_expires = Column(DateTime, nullable=True)

    # Geographic and security
    country_code = Column(String(2), nullable=True)  # ISO 2-letter country code
    signup_ip = Column(String, nullable=True)
    requires_manual_approval = Column(Integer, default=0, nullable=False)  # 0=auto, 1=manual

    # Request tracking for rate limiting
    request_count_current_period = Column(Integer, default=0, nullable=False)
    period_start_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    period_end_date = Column(DateTime, nullable=True)

    # Stripe subscription tracking
    stripe_subscription_id = Column(String, nullable=True, index=True)
    subscription_status = Column(String, nullable=True)  # active, canceled, past_due, unpaid; None = legacy/non-Stripe

    # Relationships
    api_keys = relationship("APIKey", back_populates="user")
    usage_logs = relationship("UsageLog", back_populates="user")

class APIKey(Base):
    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    key_hash = Column(String, unique=True, index=True, nullable=False)  # SHA256 hash
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_used_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="api_keys")

class UsageLog(Base):
    __tablename__ = "usage_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    tool_name = Column(String, nullable=False)
    dimension = Column(Integer, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationships
    user = relationship("User", back_populates="usage_logs")

class SignupAttempt(Base):
    __tablename__ = "signup_attempts"

    id = Column(Integer, primary_key=True, index=True)
    ip_address = Column(String, index=True, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    success = Column(Integer, default=0, nullable=False)  # 0=failed, 1=success

class ProcessedStripeEvent(Base):
    __tablename__ = "processed_stripe_events"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(String, unique=True, index=True, nullable=False)
    event_type = Column(String, nullable=False)
    processed_at = Column(DateTime, default=datetime.utcnow, nullable=False)

# =============================================================================
# DATABASE HELPERS
# =============================================================================

def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)

def get_db():
    """Dependency for FastAPI endpoints"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
