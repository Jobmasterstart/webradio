import time
import shout
import urllib.request

# DATI DEL SERVER STREAMING (Configurati automaticamente su Render)
HOST = "localhost"
PORT = 8000
PASSWORD = "la_tua_password_segreta"
MOUNT = "/live"

# PALINSESTO INTELLIGENTE (Strutturato con logica IA)
PLAYLIST_MUSICA = [
    "https://example.com",
    "https://example.com",
    "https://example.com"
]

PLAYLIST_SPOT = [
    "https://example.com",
    "https://example.com"
]

def trasmetti_file(s, url):
    print(f"In onda: {url}")
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            while True:
                data = response.read(4096)
                if not data:
                    break
                s.send(data)
                s.sync()
    except Exception as e:
        print(f"Errore riproduzione file: {e}")

def avvia_radio():
    s = shout.Shout()
    s.host = HOST
    s.port = PORT
    s.password = PASSWORD
    s.mount = MOUNT
    s.format = shout.FORMAT_MP3
    
    try:
        s.open()
        print("Radio Online nel Cloud!")
    except shout.ShoutException as e:
        print(f"Impossibile connettersi al server: {e}")
        return

    canzoni_trasmesse = 0

    while True:
        # LOGICA IA: Ogni 3 canzoni musicali inserisce tassativamente uno spot
        if canzoni_trasmesse >= 3:
            for spot_url in PLAYLIST_SPOT:
                trasmetti_file(s, spot_url)
            canzoni_trasmesse = 0
        else:
            canzone_url = PLAYLIST_MUSICA[canzoni_trasmesse % len(PLAYLIST_MUSICA)]
            trasmetti_file(s, canzone_url)
            canzoni_trasmesse += 1
            
        time.sleep(1)

if __name__ == "__main__":
    avvia_radio()
