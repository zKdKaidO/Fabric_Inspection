"""Business application layer for local textile quality inspection."""

from .database import ProductDatabase
from .service import ProductService

__all__ = ["ProductDatabase", "ProductService"]
