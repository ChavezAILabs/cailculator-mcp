"""
API Key Validation for CAILculator MCP
Communicates with hosted auth server to validate subscriptions
"""

import httpx
import logging
from typing import Optional, Tuple

from .config import get_settings
from .plans import FALLBACK_PLAN
from .provenance import is_source_checkout

logger = logging.getLogger(__name__)
settings = get_settings()


async def validate_api_key(api_key: str) -> Tuple[bool, str, Optional[str]]:
    """
    Validate API key against CAILculator auth server.

    Args:
        api_key: User's API key from environment

    Returns:
        Tuple of (is_valid: bool, error_message: str, plan: str or None).
        The plan decides which domain profiles the caller may use (see plans.py).
    """
    # Development mode: accept keys starting with "dev_", only from a source
    # checkout, so setting an env var in an installed package does not unlock it.
    if settings.enable_dev_mode and api_key.startswith("dev_"):
        if is_source_checkout():
            logger.info("Development mode: API key accepted")
            return True, "", "developer"
        logger.warning("Dev API keys are accepted only in a source checkout")
        return False, "Dev API keys are not accepted by the installed package", None

    # Production: validate with auth server
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.post(
                settings.auth_endpoint,
                json={"api_key": api_key},
                headers={"User-Agent": "CAILculator-MCP/0.1.0"}
            )

            if response.status_code == 200:
                data = response.json()

                if data.get("valid", False):
                    # Log usage info
                    usage = data.get("usage", "?")
                    limit = data.get("limit", "?")
                    plan = data.get("tier")
                    logger.info(f"API key valid. Plan: {plan}. Usage: {usage}/{limit}")
                    return True, "", plan
                else:
                    error = data.get("error") or data.get("message") or "Unknown error"
                    logger.warning(f"API key invalid: {error}")
                    return False, error, None
            else:
                logger.error(f"Auth server returned {response.status_code}")
                # Fallback to offline mode if server is having issues (5xx errors)
                if response.status_code >= 500 and settings.enable_offline_fallback:
                    logger.warning(f"Auth server error {response.status_code}, falling back to offline mode")
                    return True, "", FALLBACK_PLAN
                return False, f"Auth server error (HTTP {response.status_code})", None

    except httpx.TimeoutException:
        logger.error("Auth request timed out")
        # Fail open in development to avoid blocking users if server is down
        if settings.enable_offline_fallback:
            logger.warning("Falling back to offline mode due to timeout")
            return True, "", FALLBACK_PLAN
        return False, "Auth server timeout", None

    except httpx.RequestError as e:
        logger.error(f"Auth request failed: {e}")
        if settings.enable_offline_fallback:
            logger.warning("Falling back to offline mode due to connection error")
            return True, "", FALLBACK_PLAN
        return False, f"Cannot reach auth server: {str(e)}", None

    except Exception as e:
        logger.error(f"Unexpected auth error: {e}")
        return False, f"Validation error: {str(e)}", None
