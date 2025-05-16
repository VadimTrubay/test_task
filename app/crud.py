from sqlalchemy import func
from sqlalchemy.orm import Session
from app.database import Name, Country, NameOrigin


def get_name_origins(db: Session, name: str):
    return db.query(Name).filter(Name.name == name).first()


def create_name(db: Session, name: str):
    db_name = Name(name=name)
    db.add(db_name)
    db.commit()
    db.refresh(db_name)
    return db_name


def increment_name_counter(db: Session, name: Name):
    name.request_count += 1
    db.commit()
    db.refresh(name)
    return name


def get_country(db: Session, country_code: str):
    return db.query(Country).filter(Country.country_code == country_code).first()


def create_country(db: Session, country_data: dict):
    db_country = Country(**country_data)
    db.add(db_country)
    db.commit()
    db.refresh(db_country)
    return db_country


def create_name_origin(db: Session, name_id: int, country_id: int, probability: float):
    db_origin = NameOrigin(
        name_id=name_id, country_id=country_id, probability=probability
    )
    db.add(db_origin)
    db.commit()
    db.refresh(db_origin)
    return db_origin


def get_popular_names(db: Session, country_code: str, limit: int = 5):
    country = get_country(db, country_code)
    if not country:
        return []

    return (
        db.query(Name.name, func.count(NameOrigin.id).label("count"))
        .join(NameOrigin)
        .filter(NameOrigin.country_id == country.id)
        .group_by(Name.name)
        .order_by(func.count(NameOrigin.id).desc())
        .limit(limit)
        .all()
    )
