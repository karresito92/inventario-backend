"""
Models module - SQLAlchemy ORM models
"""

from sqlalchemy.orm import declarative_base

# Shared Base for all models
Base = declarative_base()

# Import all models to register them with Base
from .user import User, UserProfile
from .product import MarketProduct, MarketCategory
from .order import MarketOrder, MarketOrderItem
from .notification import Notification

# Optional: Cart and Listing models (if needed later)
# from .cart import MarketCart, MarketCartItem
# from .listing import MarketListing, MarketFavorite, MarketReview

__all__ = [
    "Base",
    "User",
    "UserProfile",
    "MarketProduct",
    "MarketCategory",
    "MarketOrder",
    "MarketOrderItem",
    "Notification",
]