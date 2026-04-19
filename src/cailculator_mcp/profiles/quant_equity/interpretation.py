"""
Quant Equity Interpretation
Domain Projection Layer for CAILculator v2.0

Interprets technical indicators and generates domain-specific trading signals.
"""

from typing import Dict, Any, List

def interpret_rsi(value: float) -> Dict[str, Any]:
    """Interpret RSI momentum."""
    if value > 70:
        return {"signal": "overbought", "strength": "strong", "action": "consider_selling"}
    elif value < 30:
        return {"signal": "oversold", "strength": "strong", "action": "consider_buying"}
    return {"signal": "neutral", "strength": "none", "action": "hold"}

def interpret_macd(macd: float, signal: float) -> Dict[str, Any]:
    """Interpret MACD crossover."""
    if macd > signal:
        return {"signal": "bullish", "crossover": "above", "action": "consider_buying"}
    return {"signal": "bearish", "crossover": "below", "action": "consider_selling"}

def interpret_bollinger(price: float, upper: float, lower: float) -> Dict[str, Any]:
    """Interpret price position relative to volatility bands."""
    width = upper - lower
    pos = (price - lower) / width if width > 0 else 0.5
    if pos > 0.95:
        return {"signal": "overbought", "position": "near_upper", "action": "consider_selling"}
    elif pos < 0.05:
        return {"signal": "oversold", "position": "near_lower", "action": "consider_buying"}
    return {"signal": "neutral", "position": "middle", "action": "hold"}

def generate_aggregate_interpretation(results: Dict[str, Any], signals: Dict[str, Any]) -> str:
    """Combines all signals into a human-readable summary."""
    bullish = 0
    bearish = 0
    for s in signals.values():
        if s.get("signal") in ["bullish", "overbought", "oversold"]: # Simplified
             if s["signal"] == "bullish": bullish += 1
             if s["signal"] == "bearish": bearish += 1
    
    sentiment = "NEUTRAL"
    if bullish > bearish: sentiment = "BULLISH"
    elif bearish > bullish: sentiment = "BEARISH"
    
    return f"Aggregate sentiment: {sentiment} ({bullish} bullish, {bearish} bearish signals)."
