"""
SQLAlchemy Base declaration to avoid circular imports.
"""
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base() 