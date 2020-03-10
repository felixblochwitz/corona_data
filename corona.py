import re
import psycopg2
import requests as req
from bs4 import BeautifulSoup as bs

def scraper():
    url = "https://www.rki.de/DE/Content/InfAZ/N/Neuartiges_Coronavirus/Fallzahlen.html"
    html = req.get(url).content
    soup = bs(html, 'lxml')

    dates = soup.find("div", {"id": "main"}).find_all("strong", string=re.compile(r"\d*.\d*.\d{4}"))
    date = re.search(r"\d*.\d*.\d{4}", dates[0].get_text())[0]

    rows = soup.find("tbody").find_all("tr")
    data = [[x.get_text() for x in y.find_all("td")] for y in rows]
    final_data = [[date] + [x for x in y][:3] for y in data]
    return final_data

def update_db(data):
    try:
        conn = psycopg2.connect(dbname="corona", user="postgres", host="192.52.34.244")
    except psycopg2.OperationalError as e:
        print(f"Can't connect because: {e}")

    cur = conn.cursor()
    cur.executemany("""INSERT INTO cases (date, land, num_cases, deaths)
    VALUES(%s, %s, %s, %s)""", data)
    conn.commit()
