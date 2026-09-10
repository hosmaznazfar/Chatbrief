"""
Shared digest runtime state.
"""

import asyncio

digest_lock = asyncio.Lock()
