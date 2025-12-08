"""SQLAlchemy 模型基类"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """SQLAlchemy 声明式基类
    
    所有 ORM 模型都应继承此类
    """
    pass
