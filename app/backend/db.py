from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.orm import sessionmaker, DeclarativeBase


# engine = create_engine('postgresql+psycopg2://youuser:youpassword@localhost/youdb') # PostgreSQL

# То есть используется следующий формат:
#
# Dialect+driver://username:password@host:port/database

# https://docs.sqlalchemy.org/en/20/core/engines.html#backend-specific-urls

engine = create_engine('sqlite:///ecommerce.db', echo=True)

SessionLocal = sessionmaker(bind=engine)

class Base(DeclarativeBase):
    pass

# Декларативное отображение
# class User(Base):
#     __table__ = "user"
#
#     id = Column(Integer, primary_key=True)
#     username = Column(String)
#     password = Column(String)

# Императивное отображение

#  from sqlalchemy import Table, Column, Integer, String, ForeignKey
# from sqlalchemy.orm import registry
#
# mapper_registry = registry()
#
# user_table = Table(
#     "user",
#     mapper_registry.metadata,
#     Column("id", Integer, primary_key=True),
#     Column("name", String(50)),
#     Column("fullname", String(50)),
#     Column("nickname", String(12)),
# )
#
#
# class User:
#     pass
#
#
# mapper_registry.map_imperatively(User, user_table)