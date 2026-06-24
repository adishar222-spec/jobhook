"""Unified course provider package."""
from .edx import EdxProvider
from .youtube import YouTubeProvider

PROVIDERS = {
    "edx": EdxProvider,
    "youtube": YouTubeProvider,
}

__all__ = ["EdxProvider", "YouTubeProvider", "PROVIDERS"]
