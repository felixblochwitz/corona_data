import re
import csv
import requests as req
from bs4 import BeautifulSoup as bs

url = "https://www.rki.de/DE/Content/InfAZ/N/Neuartiges_Coronavirus/Fallzahlen.html"
html = req.get(url).content
soup = bs(html, 'lxml')

dates = soup.find("div", {"id": "main"}).find_all("strong", string=re.compile(r"\d*.\d*.\d{4}"))
date = re.search(r"\d*.\d*.\d{4}", dates[0].get_text())[0]

rows = soup.find("tbody").find_all("tr")
data = [[x.get_text() for x in y.find_all("td")] for y in rows]
final_data = [[date] + [x for x in y] for y in data]

with open('first_data.csv', 'w') as file:
    for line in final_data:
        print(line)
        writer = csv.writer(file)
        writer.writerow(line[:4])
