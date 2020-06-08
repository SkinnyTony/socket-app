import requests
from bs4 import BeautifulSoup

def getPics(search):
    r = requests.get(f"https://www.google.no/search?q={search}&hl=no&sxsrf=ALeKk00v6hr7vMiy8QIQbpd1zS7WwJB5RA:1582923392428&source=lnms&tbm=isch&sa=X&ved=2ahUKEwipmYyUkfXnAhUL7KYKHdw8CBcQ_AUoAXoECBoQAw&biw=2560&bih=1298")
    soup = BeautifulSoup(r.text, "html.parser")
    links = soup.findAll("img")

    images = []
    for i in range(4, 8):
        link = links[i].get("src")
        images.append(link)
    images.append("_"* len(search))
    images.append(search)
    return images
