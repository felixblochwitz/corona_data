import re
from datetime import datetime
import psycopg2
import requests as req
from bs4 import BeautifulSoup as bs

def scraper():
    """Scrapes daily reported corona cases in Germany. Source is the Robert Koch Institute.

        Returns:
        list -- All reported cases and deaths. Both reported manually and electronically.
                Number of cases for states and the whole republic.
    """
    url = "https://www.rki.de/DE/Content/InfAZ/N/Neuartiges_Coronavirus/Fallzahlen.html"
    html = req.get(url).content
    soup = bs(html, 'lxml')

    date_par = soup.find("div", {"id": "main"}).find("p")
    date = re.search(r"\d*.\d*.\d{4}", date_par.get_text())[0]
    date = datetime.strptime(date, "%d.%m.%Y")
    rows = soup.find("tbody").find_all("tr")
    data = [[x.get_text() for x in y.find_all("td")] for y in rows]
    final_data = [[date.date()] + [None if x == "" else x for x in y][:2] + y[4:5] for y in data]
    for row in final_data:
        row[1] = row[1].replace("\N{SOFT HYPHEN}", "")
        row[2:2] = [None, None]
        row[4] = row[4].replace(".", "")
        row[5] = row[5].replace(".", "")
        if row[4] == "":
            row[4] = None
        elif row[5] == "":
            row[5] = None

    return final_data

def update_db(data):
    """Updates postgres database of corona cases in germany.
    """
    try:
        conn = psycopg2.connect(dbname="corona_de", user="postgres")
    except psycopg2.OperationalError as e:
        print(f"Can't connect because: {e}")

    cur = conn.cursor()
    cur.executemany("""INSERT INTO cases_de (date, land, cases, deaths, cases_electronic, deaths_electronic)
    VALUES(%s, %s, %s, %s, %s, %s)""", data)
    conn.commit()
