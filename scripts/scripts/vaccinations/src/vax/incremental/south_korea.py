import requests
from bs4 import BeautifulSoup
import pandas as pd

from vax.utils.incremental import enrich_data, increment, clean_count
from vax.utils.dates import localdate


def read(source: str) -> pd.Series:
    soup = BeautifulSoup(requests.get(source).content, "html.parser")
    return parse_data(soup)


def parse_data(soup: BeautifulSoup) -> pd.Series:

    people_vaccinated = clean_count(
        soup
        .find(class_="status_infoArea")
        .find(class_="round1")
        .find(class_="big")
        .text
    )

    people_fully_vaccinated = clean_count(
        soup
        .find(class_="status_infoArea")
        .find(class_="round2")
        .find(class_="big")
        .text
    )

    total_vaccinations = people_vaccinated + people_fully_vaccinated

    date = localdate("Asia/Seoul")

    data = {
        "date": date,
        "people_vaccinated": people_vaccinated,
        "people_fully_vaccinated": people_fully_vaccinated,
        "total_vaccinations": total_vaccinations,
    }
    return pd.Series(data=data)


def enrich_location(ds: pd.Series) -> pd.Series:
    return enrich_data(ds, "location", "South Korea")


def enrich_vaccine(ds: pd.Series) -> pd.Series:
    return enrich_data(ds, "vaccine", "Oxford/AstraZeneca, Pfizer/BioNTech")


def enrich_source(ds: pd.Series) -> pd.Series:
    return enrich_data(ds, "source_url", "http://ncv.kdca.go.kr/")


def pipeline(ds: pd.Series) -> pd.Series:
    return (
        ds
        .pipe(enrich_location)
        .pipe(enrich_vaccine)
        .pipe(enrich_source)
    )


def main(paths):
    source = "http://ncv.kdca.go.kr/"
    data = read(source).pipe(pipeline)
    increment(
        paths=paths,
        location=data["location"],
        total_vaccinations=data["total_vaccinations"],
        people_vaccinated=data["people_vaccinated"],
        people_fully_vaccinated=data["people_fully_vaccinated"],
        date=data["date"],
        source_url=data["source_url"],
        vaccine=data["vaccine"]
    )


if __name__ == "__main__":
    main()
