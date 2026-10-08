```python
import os
import random
import tempfile
import subprocess
import threading
import time

import requests
from flask import Flask, Response, render_template_string

app = Flask(__name__)

# ============================================================
# CONFIGURAZIONE
# ============================================================

# Numero di canzoni prima di trasmettere uno spot
SONGS_BEFORE_SPOT = 3

# Directory temporanea per i file scaricati da Dropbox
CACHE_DIR = os.path.join(tempfile.gettempdir(), "webradio_cache")

os.makedirs(CACHE_DIR, exist_ok=True)


# ============================================================
# PLAYLIST MUSICA
# ============================================================

MUSIC_PLAYLIST = [
    {
        "title": "4 Non Blondes - What's Up",
        "url": "https://www.dropbox.com/scl/fi/9ex1f2mt4ir5cibz8szi8/4-Non-Blondes-What-s-Up.mp3?rlkey=s2whxrc03fof11q4pfdh8bwil&st=x9cvycbp&dl=1",
    },

    {
        "title": "Star - The Slightest Touch",
        "url": "https://www.dropbox.com/scl/fi/my25bypvp5ey2bn66e5c7/5-Star-The-Slightest-Touch.mp3?rlkey=n2yr62nf0873guqcvn2zay7z8&st=v66p1mgk&dl=1",
    },

    {
        "title": "Ft Marvellous D & Sandra Olajide - Why Don't You Stay",
        "url": "https://www.dropbox.com/scl/fi/gropg4ap2cflfk7mj8h9k/101-Ft-Marvellous-D-And-Sandra-Olajide-Why-Don-t-You-Stay.mp3?rlkey=xaok7qjvssnytzgzj70e3ilz5&st=jowtscek&dl=1",
    },

    {
        "title": "Blow - Pressure",
        "url": "https://www.dropbox.com/scl/fi/usadwdkfw8gtomy7r62rz/400-Blow-Pressure.mp3?rlkey=mfszcrltu0pgk8ex767tj6gon&st=mk4fnf59&dl=1",
    },
]


# ============================================================
# PLAYLIST SPOT / JINGLE
# ============================================================

SPOT_PLAYLIST = [
    {
        "title": "Apertura - Sintonizzati con Roby Key",
        "url": "https://www.dropbox.com/scl/fi/l4pu3iwmsuo3n9zct95xq/apertura-Sintonizzati-con-Roby-Key.mp3?rlkey=vy639im1xpbgtuvhbmdprtt3p&st=79x0vcir&dl=1",
    },

    {
        "title": "Jingle Energico",
        "url": "https://www.dropbox.com/scl/fi/0sl6eefihip2mf0vrbf0u/Jingle-Energico.mp3?rlkey=uetfp1g93di9anq5nm648kuv5&st=2581mdc2&dl=1",
    },

    {
        "title": "Jingle Energico 1",
        "url": "https://www.dropbox.com/scl/fi/d6jywlbwnolql4txpwwof/Jingle-Energico-1.mp3?rlkey=wi7eyd4sj5gukxbn8dvgz58yh&st=g42rg35u&dl=1",
    },

    {
        "title": "Sintonizzati con Roby Key 1",
        "url": "https://www.dropbox.com/scl/fi/57pny8jbdjpbu0mbqwnu0/Sintonizzati-con-Roby-Key-1.mp3?rlkey=h4t6sj2d4i6r6joynkrwzatru&st=j3cc8ez0&dl=1",
    },

    {
        "title": "Sintonizzati Jingle",
        "url": "https://www.dropbox.com/scl/fi/jnkcd20r3v27ffjlja22s/Sintonizzati-Jingle.mp3?rlkey=fnu05pmlt9f0winer1sbnp9t0&st=a2kureqm&dl=1",
    },

    {
        "title": "Sintonizzati Jingle 1",
        "url": "https://www.dropbox.com/scl/fi/mocht777uth8vzssk1tb9/Sintonizzati-Jingle-1.mp3?rlkey=4ibtl0bb7pllph7zbp6bpbqhg&st=nab8dopg&dl=1",
    },
]


# ============================================================
# STATO DELLA RADIO
# ============================================================

current_title = "Avvio della radio..."
current_type = "music"

state_lock = threading.Lock()


# ============================================================
# DOWNLOAD DA DROPBOX
# ============================================================

def get_cache_filename(item):
    """
    Crea un nome di file sicuro basato sul titolo.
    """
    safe_name = "".join(
        c if c.isalnum() else "_"
        for c in item["title"]
    )

    return os.path.join(
        CACHE_DIR,
        safe_name + ".mp3"
    )


def download_mp3(item):
    """
    Scarica il file Dropbox e lo salva nella cache locale.
    Se esiste già, utilizza quello presente.
    """

    filename = get_cache_filename(item)

    # Se il file esiste già e non è vuoto, lo utilizziamo
    if os.path.exists(filename):
        if os.path.getsize(filename) > 1000:
            return filename

    print(f"[DOWNLOAD] {item['title']}")

    try:
        response = requests.get(
            item["url"],
            stream=True,
            timeout=60,
            allow_redirects=True
        )

        response.raise_for_status()

        temporary_file = filename + ".tmp"

        with open(temporary_file, "wb") as f:
            for chunk in response.iter_content(chunk_size=1024 * 256):

                if chunk:
                    f.write(chunk)

        # Controlliamo che il file non sia vuoto
        if not os.path.exists(temporary_file):
            raise Exception("File temporaneo non creato")

        if os.path.getsize(temporary_file) < 1000:
            raise Exception("File MP3 troppo piccolo")

        os.replace(temporary_file, filename)

        print(f"[OK] Scaricato: {item['title']}")

        return filename

    except Exception as e:

        print(
            f"[ERRORE DOWNLOAD] {item['title']}: {e}"
        )

        if os.path.exists(temporary_file):
            try:
                os.remove(temporary_file)
            except Exception:
                pass

        raise


# ============================================================
# CONVERSIONE / STREAMING CON FFMPEG
# ============================================================

def ffmpeg_stream(filename):
    """
    Avvia ffmpeg e restituisce i dati MP3
    tramite generator.
    """

    command = [
        "ffmpeg",

        "-hide_banner",
        "-loglevel", "error",

        # Input
        "-i", filename,

        # Output MP3
        "-vn",

        "-acodec", "libmp3lame",

        "-b:a", "128k",

        "-f", "mp3",

        "pipe:1"
    ]

    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        bufsize=0
    )

    try:

        while True:

            data = process.stdout.read(16384)

            if not data:
                break

            yield data

    finally:

        try:
            process.stdout.close()
        except Exception:
            pass

        try:
            process.kill()
        except Exception:
            pass


# ============================================================
# AGGIORNA TITOLO CORRENTE
# ============================================================

def set_current(item, item_type):

    global current_title
    global current_type

    with state_lock:

        current_title = item["title"]
        current_type = item_type

    print(
        f"[ON AIR] {item_type.upper()}: {item['title']}"
    )


# ============================================================
# STREAM PRINCIPALE
# ============================================================

def radio_generator():

    song_counter = 0

    # Per evitare che la prima trasmissione inizi con uno spot,
    # partiamo con una canzone.
    while True:

        try:

            # ------------------------------------------------
            # DOPO 3 CANZONI -> SPOT
            # ------------------------------------------------

            if song_counter >= SONGS_BEFORE_SPOT:

                spot = random.choice(SPOT_PLAYLIST)

                set_current(
                    spot,
                    "spot"
                )

                try:

                    filename = download_mp3(spot)

                    for chunk in ffmpeg_stream(filename):
                        yield chunk

                except Exception as e:

                    print(
                        f"[ERRORE SPOT] {spot['title']}: {e}"
                    )

                # Dopo lo spot ripartiamo da zero
                song_counter = 0

                continue


            # ------------------------------------------------
            # SELEZIONE CANZONE
            # ------------------------------------------------

            song = random.choice(MUSIC_PLAYLIST)

            set_current(
                song,
                "music"
            )

            try:

                filename = download_mp3(song)

                for chunk in ffmpeg_stream(filename):
                    yield chunk

                song_counter += 1

            except Exception as e:

                print(
                    f"[ERRORE CANZONE] {song['title']}: {e}"
                )

                # Se una canzone non è disponibile,
                # non la contiamo come canzone trasmessa.
                continue


        except Exception as e:

            print(
                f"[ERRORE RADIO] {e}"
            )

            # Evita un loop troppo veloce in caso di errore
            time.sleep(2)


# ============================================================
# PAGINA PRINCIPALE
# ============================================================

HTML_PAGE = """
<!DOCTYPE html>

<html lang="it">

<head>

    <meta charset="UTF-8">

    <meta
        name="viewport"
        content="width=device-width, initial-scale=1.0"
    >

    <title>Web Radio</title>

    <style>

        body {
            font-family: Arial, sans-serif;
            background: #111;
            color: white;
            text-align: center;
            padding: 40px 20px;
        }

        .radio {
            max-width: 600px;
            margin: auto;
            padding: 30px;
            border-radius: 20px;
            background: #222;
        }

        h1 {
            margin-bottom: 30px;
        }

        .onair {
            font-size: 14px;
            opacity: 0.7;
            margin-bottom: 10px;
        }

        .title {
            font-size: 22px;
            margin-bottom: 30px;
        }

        audio {
            width: 100%;
        }

    </style>

</head>

<body>

    <div class="radio">

        <h1>🎙️ Web Radio</h1>

        <div class="onair">
            IN ONDA
        </div>

        <div class="title">
            {{ title }}
        </div>

        <audio controls autoplay>
            <source
                src="/stream"
                type="audio/mpeg"
            >
            Il tuo browser non supporta l'audio.
        </audio>

    </div>

</body>

</html>
"""


# ============================================================
# ROUTE HOME
# ============================================================

@app.route("/")
def index():

    with state_lock:
        title = current_title

    return render_template_string(
        HTML_PAGE,
        title=title
    )


# ============================================================
# ROUTE STREAM
# ============================================================

@app.route("/stream")
def stream():

    return Response(
        radio_generator(),
        mimetype="audio/mpeg",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Accept-Ranges": "none",
        }
    )


# ============================================================
# STATO RADIO
# ============================================================

@app.route("/status")
def status():

    with state_lock:

        return {
            "status": "online",
            "type": current_type,
            "title": current_title
        }


# ============================================================
# AVVIO SERVER
# ============================================================

if __name__ == "__main__":

    port = int(
        os.environ.get(
            "PORT",
            10000
        )
    )

    print("=" * 50)
    print("WEB RADIO AVVIATA")
    print("=" * 50)
    print(f"Porta: {port}")
    print(
        f"Spot ogni {SONGS_BEFORE_SPOT} canzoni"
    )
    print(
        f"Canzoni disponibili: {len(MUSIC_PLAYLIST)}"
    )
    print(
        f"Spot/Jingle disponibili: {len(SPOT_PLAYLIST)}"
    )
    print("=" * 50)

    app.run(
        host="0.0.0.0",
        port=port,
        threaded=True
    )
```
