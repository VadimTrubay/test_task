import httpx
from datetime import datetime, timedelta
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.crud import (
    get_name_origins,
    create_name,
    increment_name_counter,
    get_country,
    create_country,
    create_name_origin,
)
from app.schemas import CountryDetails


async def fetch_nationalize_data(name: str):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"https://api.nationalize.io/?name={name}", timeout=10.0
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError:
            raise HTTPException(
                status_code=503, detail="Nationalize.io service unavailable"
            )


async def fetch_country_data(country_code: str):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"https://restcountries.com/v3.1/alpha/{country_code}", timeout=10.0
            )
            response.raise_for_status()
            data = response.json()
            return data[0] if data else None
        except httpx.HTTPError:
            raise HTTPException(
                status_code=503, detail="REST Countries service unavailable"
            )


def process_country_data(country_data: dict):
    return {
        "country_code": country_data.get("cca2", ""),
        "country_code3": country_data.get("cca3", ""),
        "country_name": country_data.get("name", {}).get("common", ""),
        "official_name": country_data.get("name", {}).get("official", ""),
        "region": country_data.get("region", ""),
        "subregion": country_data.get("subregion", ""),
        "independent": country_data.get("independent", False),
        "google_maps_link": country_data.get("maps", {}).get("googleMaps", ""),
        "openstreetmap_link": country_data.get("maps", {}).get("openStreetMaps", ""),
        "capital_name": (
            country_data.get("capital", [""])[0] if country_data.get("capital") else ""
        ),
        "capital_latitude": country_data.get("capitalInfo", {}).get(
            "latlng", [None, None]
        )[0],
        "capital_longitude": country_data.get("capitalInfo", {}).get(
            "latlng", [None, None]
        )[1],
        "flag_png": country_data.get("flags", {}).get("png", ""),
        "flag_svg": country_data.get("flags", {}).get("svg", ""),
        "flag_alt": country_data.get("flags", {}).get("alt", ""),
        "coat_of_arms_png": country_data.get("coatOfArms", {}).get("png", ""),
        "coat_of_arms_svg": country_data.get("coatOfArms", {}).get("svg", ""),
    }


async def process_name_request(db: Session, name: str):
    # Check if name exists in DB and was accessed recently
    db_name = get_name_origins(db, name)
    one_day_ago = datetime.utcnow() - timedelta(days=1)

    if db_name and db_name.last_accessed_at >= one_day_ago:
        increment_name_counter(db, db_name)
        origins = [
            {
                **country.Country.__dict__,
                "probability": origin.probability,
                "borders": country.borders if hasattr(country, "borders") else [],
            }
            for origin in db_name.origins
            for country in [origin.country]
        ]
        return {
            "name": db_name.name,
            "countries": origins,
            "request_count": db_name.request_count,
        }

    # Fetch from nationalize.io
    nationalize_data = await fetch_nationalize_data(name)
    if not nationalize_data.get("country"):
        raise HTTPException(
            status_code=404, detail="No country data found for this name"
        )

    # Create or update name record
    if not db_name:
        db_name = create_name(db, name)
    else:
        increment_name_counter(db, db_name)

    countries = []
    for country_data in nationalize_data["country"]:
        country_code = country_data["country_id"]
        probability = country_data["probability"]

        # Check if country exists in DB
        db_country = get_country(db, country_code)
        if not db_country:
            # Fetch country details
            rest_country_data = await fetch_country_data(country_code)
            if not rest_country_data:
                continue

            # Create country record
            country_details = process_country_data(rest_country_data)
            db_country = create_country(db, country_details)

        # Create name origin record
        create_name_origin(db, db_name.id, db_country.id, probability)

        # Prepare response data
        country_response = CountryDetails(
            country_code=db_country.country_code,
            country_name=db_country.country_name,
            official_name=db_country.official_name,
            region=db_country.region,
            subregion=db_country.subregion,
            independent=db_country.independent,
            google_maps_link=db_country.google_maps_link,
            openstreetmap_link=db_country.openstreetmap_link,
            capital_name=db_country.capital_name,
            capital_coordinates=(
                f"{db_country.capital_latitude},{db_country.capital_longitude}"
                if db_country.capital_latitude and db_country.capital_longitude
                else None
            ),
            flag_png=db_country.flag_png,
            flag_svg=db_country.flag_svg,
            flag_alt=db_country.flag_alt,
            coat_of_arms_png=db_country.coat_of_arms_png,
            coat_of_arms_svg=db_country.coat_of_arms_svg,
            probability=probability,
            borders=rest_country_data.get("borders", []) if db_country else [],
        )
        countries.append(country_response)

    return {
        "name": db_name.name,
        "countries": countries,
        "request_count": db_name.request_count,
    }
