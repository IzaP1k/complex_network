import requests
from bs4 import BeautifulSoup
import random
import time
import numpy as np
import json


def sleepRandomTime(base_time=7, low_time=0.1, high_time=1.2):
    extra_time = random.uniform(low_time, high_time)
    wait_time = base_time + extra_time
    time.sleep(wait_time)


def getScholarData(urls,
                   header="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"):
    results = []

    for url_ in urls:
        try:
            url = url_
            headers = {
                "User-Agent": header
            }
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            scholar_results = []

            for el in soup.select(".gs_r"):
                scholar_results.append({
                    "title": el.select_one(".gs_rt").text if el.select_one(".gs_rt") else "",
                    "title_link": el.select_one(".gs_rt a")["href"] if el.select_one(".gs_rt a") else "",
                    "displayed_link": el.select_one(".gs_a").text if el.select_one(".gs_a") else "",
                    "cited_by_count": el.select_one(".gs_nph + a").text if el.select_one(".gs_nph + a") else "",
                    "cited_link": "https://scholar.google.com" + el.select_one(".gs_nph + a")["href"] if el.select_one(
                        ".gs_nph + a") else ""
                })

            scholar_results = [{k: v for k, v in result.items() if v} for result in scholar_results]

            results = results + scholar_results

            sleepRandomTime()

        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}")
        except Exception as e:
            print(f"An error occurred: {e}")

    return results


def process_dicts(dicts_list, cites=None):
    filtered_list = [d for d in dicts_list if d]

    if cites is None:
        cites = []

    unique_dicts = []
    seen_titles = set()
    seen_links = set()

    for d in filtered_list:
        title = d.get('title')
        title_link = d.get('title_link')

        if title not in seen_titles and title_link not in seen_links:
            unique_dicts.append(d)
            seen_titles.add(title)
            seen_links.add(title_link)

    for idx, d in enumerate(unique_dicts):
        d['id'] = idx
        d['cites'] = cites

    return unique_dicts


def generate_links(base_url, n):
    links = []
    for i in range(0, n * 10, 10):
        links.append(base_url + f"&start={i}")
    return links


def primaryData(numbers=None, urls=None):
    if numbers is None:
        numbers = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 140]

    if urls is None:
        urls = ["https://scholar.google.com/scholar?hl=pl&as_sdt=0%2C5&q=bci+motor+imagery&oq=BCI"]

    for number in numbers:
        urls.append(f"https://scholar.google.com/scholar?start={number}&q=bci+motor+imagery&hl=pl&as_sdt=0,5")

    results = getScholarData(urls)

    clear_results = process_dicts(results)

    return clear_results


def getCitedData(dataScientificPaper, cited_url, cited_numb):

    wanted_page = 5
    try:
        number = np.floor(int(cited_numb[-1]) / 10)

        if wanted_page < number:
            if number < 1:
                number = 1
        else:
            number = wanted_page
    except ValueError:
        print(cited_numb)
        number = 1

    links = generate_links(cited_url, number)


    result = getScholarData(links)

    # dostaję dane w formie [{"key": "value"}, ...]

    clear_result = process_dicts(result, cited_numb)

    new_dataSP = dataScientificPaper.copy()

    for res1 in clear_result:
        new = True
        for res2 in dataScientificPaper:

            if res1['title'] == res2['title'] or res1['title_link'] == res2['title_link']:
                res2['cites'] += res1['cites']

                new = False

            if new:
                res1['id'] = new_dataSP[-1]['id'] + 1

                new_dataSP.append(res1)


    return new_dataSP, dataScientificPaper[-1]['id']

def get_json(save = True, load = True, data = None):
    if save:
        with open('lista_slownikow.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    if load:
        with open('lista_slownikow.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data


# first_result = primaryData()
print('ok')

first_result = get_json(save=False)
print('Wczytane dane bazowe)')
first_result2 = first_result.copy()

for data in first_result:

    first_result2, idx = getCitedData(first_result2, data['cited_link'], data['cited_by_count'])

get_json(load=False, data=first_result2)
print('Wczytane dane, wszysctkie 1 cytowanai')

first_result3 = first_result2.copy()

for new_paper in first_result2[idx:]:

        first_result3, idx = getCitedData(first_result3, new_paper['cited_link'], new_paper['cited_by_count'])

get_json(load=False, data=first_result3)
print('Wczytane dane, wszystkie 2 cytowania')
