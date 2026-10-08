import os
from flask import Flask, Response

app = Flask(__name__)

# PALINSESTO INTELLIGENTE (Strutturato con logica IA)
# Quando caricherai i tuoi file su Dropbox, ti basterà sostituire questi link!
PLAYLIST_MUSICA = [
    "https://example.com",
    "https://example.com",
    "https://example.com"
]

PLAYLIST_SPOT = [
    "https://example.com"
]

@app.route('/')
def home():
    return "La mia Web Radio con IA e Render è Online!"

@app.route('/playlist.m3u')
def genera_playlist():
    # L'IA genera il flusso: ogni 3 canzoni musicali inserisce tassativamente uno spot
    m3u_content = "#EXTM3U\n"
    canzoni_contate = 0
    
    # Crea una rotazione di prova di 24 brani
    for i in range(24):
        if canzoni_contate >= 3:
            spot_url = PLAYLIST_SPOT[0]
            m3u_content += f"#EXTINF:-1, Spot Radiofonico IA\n{spot_url}\n"
            canzoni_contate = 0
        else:
            canzone_url = PLAYLIST_MUSICA[i % len(PLAYLIST_MUSICA)]
            m3u_content += f"#EXTINF:-1, Canzone in onda\n{canzone_url}\n"
            canzoni_contate += 1
            
    return Response(m3u_content, mimetype='audio/x-mpegurl')

if __name__ == "__main__":
    # Avvia il server web sulla porta richiesta da Render
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
