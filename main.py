import os
import re
import time
from bs4 import BeautifulSoup
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome import options as chrome_options


def get_page(count=1):
    driver = webdriver.Chrome()
    pages = []

    for page_nb in range(1, count + 1):
        page_url = f"https://www.spoticar.fr/voitures-occasion?page={page_nb}&gps[lat]=48.898908&gps[lon]=2.093761&filters[0][location][lat]=48.898908&filters[0][location][lon]=2.093761&filters[0][location][place]=Saint-Germain-en-Laye,%20France&filters[0][location][radius]=150"
        driver.get(page_url)
        if page_nb == 1:
            time.sleep(10)
        else:
            time.sleep(1)
        pages.append(driver.page_source.encode("utf-8"))
    return pages


def saves_pages(pages):
    os.makedirs("data", exist_ok=True)

    results = pd.DataFrame()

    for page_nb, page in enumerate(pages):
        with open(f"data/page_{page_nb}.html", "wb") as f_out:
            page = f_out.write(page)

    return results


def parse_pages():
    pages_paths = os.listdir("data")

    results = pd.DataFrame()

    for pages_path in pages_paths:
        with open("data/" + pages_path, "rb") as f_in:
            page = f_in.read().decode("utf-8")
            result = parse_page(page)
            results = results.append(result)

    return results


def parse_page(page):
    result = pd.DataFrame()
    soup = BeautifulSoup(page, "html.parser")

    result["prix (€)"] = [
        clean_price(tag) for tag in soup.find_all(attrs={"class": "price"})
    ]

    result["voiture"] = [
        clean_car(tag) for tag in soup.find_all(attrs={"class": "title"})
    ]

    result["kilometrage (km)"] = [
        clean_kilometers(tag) for tag in soup.find_all(attrs={'class': 'miles col-lg-6 col-md-6 col-sm-6 col-xs-6'})
    ]

    result["energie"] = [
        clean_energy(tag) for tag in soup.find_all(attrs={'class': 'miles col-lg-6 col-md-6 col-sm-6 col-xs-6'})
    ]

    return result


def clean_price(tag):
    text = tag.text.strip()
    price = int(text.replace("€", "").replace(" ", ""))
    return price


def clean_car(tag):
    text = tag.text.strip()
    return text.replace(" ", " ")


def clean_kilometers(tag):
    text = tag.text.strip().split("\n")[0]
    kilometers = int(text.replace("km", "").replace(" ", ""))
    return kilometers


def clean_energy(tag):
    text = tag.text.strip().split("\n")[1]
    return text.replace("km", "")


def main():
    pages = get_page(count=30)
    print(pages)
    saves_pages(pages)
    results = parse_pages()
    print(results)


if __name__ == "__main__":
    main()