from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
import requests
import time
import json
import aiohttp
import asyncio

import logging
import data.logmanager as lm

lm.get_configured_logger('scraper')

url_site = "https://streamingcommunity.computer/"
url_images = f"{url_site}images/"
url_post = f"{url_site}api/titles/preview/"

# Configurazione del driver
#chrome_options = Options()
#chrome_options.add_argument("--headless")  # Esegui in modalità headless (senza interfaccia grafica)
#service = Service('drivers/chromedriver.exe')  # Sostituisci con il percorso del tuo ChromeDriver
#
## Inizializza il browser
#driver = webdriver.Chrome(service=service, options=chrome_options)

def invia_richiesta_post(id):
    try:
        url = f"{url_post}{id}"
        risposta = requests.post(url)  # Non inviare dati aggiuntivi
        risposta.raise_for_status()  # Controlla per eventuali errori HTTP
        return risposta.json()  # Restituisce la risposta come JSON
    except requests.exceptions.RequestException as e:
        print(f"Errore nella richiesta POST: {e}")
        return "None"
    
    
def get_films():
    films_list = []
    for i in range(10,100):
        # Inizializza film_data come un dizionario vuoto
        film_data = {}
        start_time = time.time()
        film_data = invia_richiesta_post(i)
        end_time = time.time()
        logging.debug(f'execution time {end_time-start_time}')
        
        if film_data != {}:
            films_list.append(Film(film_data))

    return films_list

def get_films_json():
    films_list = []
    for i in range(30,100):
        # Inizializza film_data come un dizionario vuoto
        film_data = {}
        film_data = invia_richiesta_post(i)
        
        if film_data != {}:
            films_list.append(film_data)

    return films_list
    
class Film:                
    def __init__(self, json_data):
        if isinstance(json_data, str):
            self.data = json.loads(json_data)
        elif isinstance(json_data, dict):
            self.data = json_data  # Se è già un dizionario, non serve fare il loading
        else:
            raise TypeError("json_data deve essere una stringa JSON o un dizionario.")
        
        
        self.description = self.data['plot']
        self.image = self.get_image(self.data['images'])
        self.genres = self.data['genres']
        self.release_date = self.data['release_date']
        self.runtime = self.data['runtime']
        self.title_id = self.data['id']
        self.image_url = self.get_img_url()

    def to_dict(self):
        return {
            'title': self.title_id,
            'img_url': self.image_url,
            'description': self.description,
            'runtime': self.runtime,
            'genres': [{'name': genre['name']} for genre in self.genres]  # Assumendo che `genres` sia una lista di nomi
        }

    def get_img_url(self):
        return f"https://cdn.streamingcommunity.computer/images/{self.image}"
    
    def get_image(self, images):
        img = 0
        for image in images:
            if image['type'] == "cover":
                img = image
        return img['filename']
