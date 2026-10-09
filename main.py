import os
import random
import requests
import dropbox
from flask import Flask, render_template_string, jsonify

app = Flask(__name__)

# Configurazione Dropbox e AI
DBX_TOKEN = os.environ.get("DROPBOX_REFRESH_TOKEN")
DBX_KEY = os.environ.get("DROPBOX_APP_KEY")
DBX_SECRET = os.environ.get("DROPBOX_APP_SECRET")
HF_API_KEY = os.environ.get("HUGGINGFACE_API_KEY")

HF_API_URL = "https://huggingface.co"

def chiedi_all_ai_cosa_trasmettere(canzoni, spot):
    """L'AI decide se trasmettere musica o pubblicità pescando dalle liste"""
    headers = {"Authorization": f"Bearer {HF_API_KEY}"}
    prompt = f"Sei la regia di Radio Fuori Onda Faenza. Scegli un file tra questi musicali: {canzoni} o questi spot: {spot}. Rispondi SOLO con il nome esatto del file scelto, senza aggiungere altro testo."
    try:
        payload = {"inputs": prompt, "parameters": {"max_new_tokens": 50}}
        response = requests.post(HF_API_URL, json=payload, headers=headers)
        output = response.json()
        if isinstance(output, list) and "generated_text" in output:
            scelta = output[0]["generated_text"].replace(prompt, "").strip()
            return scelta
    except:
        pass
    return random.choice(canzoni) if canzoni else ""

def ottieni_file_dropbox():
    """Legge i file mp3 presenti nel tuo Dropbox"""
    try:
        dbx = dropbox.Dropbox(oauth2_refresh_token=DBX_TOKEN, app_key=DBX_KEY, app_secret=DBX_SECRET)
        canzoni, spot = [], []
        # Cerca i file nelle tue cartelle Dropbox
        for entry in dbx.files_list_folder('/musica').entries:
            if entry.name.endswith('.mp3'): canzoni.append(entry.name)
        for entry in dbx.files_list_folder('/spot').entries:
            if entry.name.endswith('.mp3'): spot.append(entry.name)
        return canzoni, spot
    except:
        return [], []

@app.route('/')
def home():
    # Struttura del tuo sito web con il player audio
    html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Radio Fuori Onda Faenza</title>
        <style>
            body { background: #121212; color: white; font-family: sans-serif; text-align: center; padding-top: 50px; }
            .player-card { background: #1e1e1e; padding: 30px; display: inline-block; border-radius: 10px; }
        </style>
    </head>
    <body>
        <div class="player-card">
            <h2>🎙️ La mia Web Radio con IA</h2>
            <p>In onda dal cloud a PC spento</p>
            <audio id="audioPlayer" controls autoplay src="/stream_audio"></audio>
        </div>
        <script>
            // Logica per far ripartire il brano successivo quando uno finisce
            document.getElementById('audioPlayer').onended = function() {
                this.src = "/stream_audio?t=" + new Date().getTime();
                this.play();
            };
        </script>
    </body>
    </html>
    '''
    return render_template_string(html)

@app.route('/stream_audio')
def stream_audio():
    canzoni, spot = ottieni_file_dropbox()
    file_scelto = chiedi_all_ai_cosa_trasmettere(canzoni, spot)
    
    # Genera il link temporaneo di Dropbox per far suonare il file direttamente nel browser dell'utente
    try:
        dbx = dropbox.Dropbox(oauth2_refresh_token=DBX_TOKEN, app_key=DBX_KEY, app_secret=DBX_SECRET)
        cartella = "/spot/" if file_scelto in spot else "/musica/"
        media_link = dbx.files_get_temporary_link(cartella + file_scelto)
        return jsonify({"url": media_link.link}), 200, {'Location': media_link.link}
    except:
        # Traccia di fallback se Dropbox è vuoto
        link_fallback = "https://soundhelix.com"
        return jsonify({"url": link_fallback}), 200, {'Location': link_fallback}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
