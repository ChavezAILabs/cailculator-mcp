"""
CAILculator MCP - Production Engine v2.1.3
Universal high-precision mathematical data analysis
"""

__version__ = "2.1.3"

from .server import MCPServer, main

__all__ = [
    'MCPServer',
    'main',
    '__version__',
    'call_tool',
    'TOOLS_DEFINITIONS',
    'ChavezTransform',
    'PatternDetector'
]

def __getattr__(name):
    # Heavy imports deferred until actually used — keeps MCP server startup fast
    if name in ('call_tool', 'TOOLS_DEFINITIONS'):
        from .tools import call_tool as _ct, TOOLS_DEFINITIONS as _td
        globals()['call_tool'] = _ct
        globals()['TOOLS_DEFINITIONS'] = _td
        return globals()[name]
    if name == 'ChavezTransform':
        from .core.chavez_transform import ChavezTransform
        globals()['ChavezTransform'] = ChavezTransform
        return ChavezTransform
    if name == 'PatternDetector':
        from .patterns import PatternDetector
        globals()['PatternDetector'] = PatternDetector
        return PatternDetector
    raise AttributeError(f"module 'cailculator_mcp' has no attribute {name!r}")
