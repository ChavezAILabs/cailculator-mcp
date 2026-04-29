"""
CAILculator MCP - Production Engine v2.0.3
Universal high-precision mathematical data analysis
"""

__version__ = "2.0.4"

from .server import MCPServer, main
from .tools import call_tool, TOOLS_DEFINITIONS
from .core.chavez_transform import ChavezTransform
from .patterns import PatternDetector

__all__ = [
    'MCPServer',
    'main',
    'call_tool',
    'TOOLS_DEFINITIONS',
    'ChavezTransform',
    'PatternDetector'
]
