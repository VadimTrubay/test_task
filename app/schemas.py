from pydantic import BaseModel
from typing import List, Optional


class CountryBase(BaseModel):
    country_code: str
    country_name: str
    probability: float


class CountryDetails(CountryBase):
    official_name: Optional[str]
    region: Optional[str]
    subregion: Optional[str]
    independent: Optional[bool]
    google_maps_link: Optional[str]
    openstreetmap_link: Optional[str]
    capital_name: Optional[str]
    capital_coordinates: Optional[str]
    flag_png: Optional[str]
    flag_svg: Optional[str]
    flag_alt: Optional[str]
    coat_of_arms_png: Optional[str]
    coat_of_arms_svg: Optional[str]
    borders: Optional[List[str]]


class NameResponse(BaseModel):
    name: str
    countries: List[CountryDetails]
    request_count: int


class PopularName(BaseModel):
    name: str
    count: int


class PopularNamesResponse(BaseModel):
    country: str
    names: List[PopularName]
