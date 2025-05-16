from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Float,
    Boolean,
    DateTime,
    ForeignKey,
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from sqlalchemy.sql import func

Base = declarative_base()

engine = create_engine("sqlite:///./database.db")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class Country(Base):
    __tablename__ = "countries"

    id = Column(Integer, primary_key=True, index=True)
    country_code = Column(String(2), unique=True, index=True)
    country_code3 = Column(String(3))
    country_name = Column(String(100))
    official_name = Column(String(150))
    region = Column(String(50))
    subregion = Column(String(50))
    independent = Column(Boolean)
    google_maps_link = Column(String(255))
    openstreetmap_link = Column(String(255))
    capital_name = Column(String(100))
    capital_latitude = Column(Float)
    capital_longitude = Column(Float)
    flag_png = Column(String(255))
    flag_svg = Column(String(255))
    flag_alt = Column(String(255))
    coat_of_arms_png = Column(String(255))
    coat_of_arms_svg = Column(String(255))

    name_origins = relationship("NameOrigin", back_populates="country")


class Name(Base):
    __tablename__ = "names"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), index=True)
    request_count = Column(Integer, default=1)
    last_accessed_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    origins = relationship("NameOrigin", back_populates="name")


class NameOrigin(Base):
    __tablename__ = "name_origins"

    id = Column(Integer, primary_key=True, index=True)
    name_id = Column(Integer, ForeignKey("names.id"))
    country_id = Column(Integer, ForeignKey("countries.id"))
    probability = Column(Float)

    name = relationship("Name", back_populates="origins")
    country = relationship("Country", back_populates="name_origins")
