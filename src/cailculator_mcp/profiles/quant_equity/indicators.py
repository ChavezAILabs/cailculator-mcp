"""
Quant Equity Indicators
Domain Projection Layer for CAILculator v2.0

Professional technical analysis indicators for financial markets.
Uses pandas_ta library for industry-standard calculations.
"""

import logging
from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)

def calculate_indicators(df: pd.DataFrame, indicators_requested: List[str], custom_periods: Dict[str, int]) -> Dict[str, Any]:
    """
    Calculate technical indicators for the given OHLCV DataFrame.
    """
    try:
        import pandas_ta as ta
    except ImportError:
        raise ImportError("pandas_ta library not installed. Run: pip install pandas-ta")

    results = {}
    for indicator in indicators_requested:
        indicator_upper = indicator.upper()
        try:
            if indicator_upper == "RSI":
                period = custom_periods.get("rsi", 14)
                rsi = ta.rsi(df['close'], length=period)
                results["rsi"] = {
                    "values": rsi.dropna().tolist(),
                    "current": float(rsi.iloc[-1]) if not pd.isna(rsi.iloc[-1]) else None,
                    "period": period
                }

            elif indicator_upper == "MACD":
                fast = custom_periods.get("macd_fast", 12)
                slow = custom_periods.get("macd_slow", 26)
                signal = custom_periods.get("macd_signal", 9)
                macd = ta.macd(df['close'], fast=fast, slow=slow, signal=signal)
                results["macd"] = {
                    "macd": macd[f'MACD_{fast}_{slow}_{signal}'].dropna().tolist(),
                    "signal": macd[f'MACDs_{fast}_{slow}_{signal}'].dropna().tolist(),
                    "histogram": macd[f'MACDh_{fast}_{slow}_{signal}'].dropna().tolist(),
                    "current_macd": float(macd[f'MACD_{fast}_{slow}_{signal}'].iloc[-1]),
                    "current_signal": float(macd[f'MACDs_{fast}_{slow}_{signal}'].iloc[-1])
                }

            elif indicator_upper in ["BOLLINGER", "BBANDS"]:
                period = custom_periods.get("bollinger_period", 20)
                std = custom_periods.get("bollinger_std", 2)
                bbands = ta.bbands(df['close'], length=period, std=std)
                
                # Find columns by prefix
                bbu = [c for c in bbands.columns if c.startswith(f'BBU_{period}')][0]
                bbm = [c for c in bbands.columns if c.startswith(f'BBM_{period}')][0]
                bbl = [c for c in bbands.columns if c.startswith(f'BBL_{period}')][0]

                results["bollinger_bands"] = {
                    "upper": bbands[bbu].dropna().tolist(),
                    "middle": bbands[bbm].dropna().tolist(),
                    "lower": bbands[bbl].dropna().tolist(),
                    "current_upper": float(bbands[bbu].iloc[-1]),
                    "current_price": float(df['close'].iloc[-1])
                }

            # ... other indicators following same pattern ...

        except Exception as e:
            logger.error(f"Error calculating {indicator}: {e}")
            results[indicator] = {"error": str(e)}

    return results

def prepare_dataframe(data: Any) -> pd.DataFrame:
    """Helper to convert OHLCV data formats to DataFrame."""
    if isinstance(data, pd.DataFrame):
        return data
    if isinstance(data, dict):
        return pd.DataFrame(data)
    if isinstance(data, list) and len(data) > 0 and isinstance(data[0], list):
        if len(data[0]) == 6:
            return pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        elif len(data[0]) == 5:
            return pd.DataFrame(data, columns=['open', 'high', 'low', 'close', 'volume'])
    raise ValueError("Unsupported data format for OHLCV")
