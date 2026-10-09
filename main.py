import os
import random
import requests
import dropbox
from flask import Flask, render_template_string, jsonify, redirect

app = Flask(__name__)

# Recupero variabili d'ambiente da Render
DBX_TOKEN = os.environ.get("DROPBOX_REFRESH_TOKEN")
DBX_KEY = os.environ.get("DROPBOX_APP_KEY")
DBX_SECRET = os.environ.get("DROPBOX_APP_SECRET")
HF_API_KEY = os.environ.get("HUGGINGFACE_API_KEY")

HF_API_URL = "https://huggingface.co"

def chiedi_all_ai_cosa_trasmettere(canzoni, spot):
    if not canzoni and not spot:
        return ""
    headers = {"Authorization": f"Bearer {HF_API_KEY}"}
    prompt = f"Sei la regia di Radio Fuori Onda Faenza. Scegli un file da trasmettere tra questi brani: {canzoni} o questi spot: {spot}. Rispondi SOLO con il nome esatto del file."
    try:
        payload = {"inputs": prompt, "parameters": {"max_new_tokens": 50}}
        response = requests.post(HF_API_URL, json=payload, headers=headers, timeout=4)
        output = response.json()
        if isinstance(output, list) and len(output) > 0 and "generated_text" in output:
            scelta = output["generated_text"].replace(prompt, "").strip()
            for f in (canzoni + spot):
                if f in scelta:
                    return f
    except:
        pass
    return random.choice(canzoni) if canzoni else random.choice(spot)

def ottieni_file_dropbox():
    canzoni_trovate = []
    spot_trovati = []
    try:
        dbx = dropbox.Dropbox(oauth2_refresh_token=DBX_TOKEN, app_key=DBX_KEY, app_secret=DBX_SECRET)
        
        # 1. Prova a leggere le cartelle con la maiuscola nella ROOT principale
        try:
            for entry in dbx.files_list_folder('/Musica').entries:
                if entry.name.lower().endswith('.mp3'): canzoni_trovate.append('/Musica/' + entry.name)
            for entry in dbx.files_list_folder('/Spot').entries:
                if entry.name.lower().endswith('.mp3'): spot_trovati.append('/Spot/' + entry.name)
            if canzoni_trovate or spot_trovati:
                return canzoni_trovate, spot_trovati
        except:
            pass

        # 2. Se fallisce, prova a leggere le cartelle in minuscolo nella ROOT
        try:
            for entry in dbx.files_list_folder('/musica').entries:
                if entry.name.lower().endswith('.mp3'): canzoni_trovate.append('/musica/' + entry.name)
            for entry in dbx.files_list_folder('/spot').entries:
                if entry.name.lower().endswith('.mp3'): spot_trovati.append('/spot/' + entry.name)
            if canzoni_trovate or spot_trovati:
                return canzoni_trovate, spot_trovati
        except:
            pass

        # 3. Paracadute: prova a leggere i file sfusi direttamente all'interno della cartella dell'app
        try:
            for entry in dbx.files_list_folder('').entries:
                if entry.name.lower().endswith('.mp3'):
                    canzoni_trovate.append('/' + entry.name)
            return canzoni_trovate, spot_trovati
        except:
            pass

        return [], []
    except:
        return [], []

@app.route('/')
def home():
    html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Radio Fuori Onda Faenza</title>
        <style>
            body { background: #121212; color: white; font-family: sans-serif; text-align: center; padding-top: 100px; }
            .card { background: #1e1e1e; padding: 40px; display: inline-block; border-radius: 15px; border: 1px solid #333; box-shadow: 0 4px 15px rgba(0,0,0,0.5); }
            audio { margin-top: 25px; width: 320px; outline: none; }
            .status { font-size: 14px; color: #25d366; margin-top: 10px; font-weight: bold; }
        </style>
    </head>
    <body>
        <div class="card">
            <h2>🎙️ Radio Fuori Onda Faenza</h2>
            <p>Regia Cloud Continuativa via IA</p>
            <audio id="radioPlayer" controls autoplay src="/get_next_track_url"></audio>
            <div class="status" id="statusTrack">In onda: Connessione in corso...</div>
        </div>

        <script>
            var player = document.getElementById('radioPlayer');
            var statusTrack = document.getElementById('statusTrack');
            
            function caricaTracciaSuccessiva() {
                statusTrack.innerText = "L'IA sta decidendo la prossima traccia...";
                fetch('/get_next_track')
                    .then(response => response.json())
                    .then(data => {
                        statusTrack.innerText = "In onda ora: " + data.name;
                        player.src = data.url;
                        player.load();
                        player.play();
                    })
                    .catch(err => {
                        player.src = "https://soundhelix.com";
                        player.load();
                        player.play();
                        statusTrack.innerText = "In onda: Traccia di emergenza internet";
                    });
            }

            player.onended = function() {
                caricaTracciaSuccessiva();
            };
            
            // Forza l'aggiornamento della scritta al primo avvio
            player.onplay = function() {
                if(statusTrack.innerText.includes("Connessione")) {
                    statusTrack.innerText = "In onda ora: Regia Automatica Cloud";
                }
            };
        </script>
    </body>
    </html>
    '''
    return render_template_string(html)

@app.route('/get_next_track_url')
@app.route('/get_next_track')
def get_next_track():
    fallback_url = "https://soundhelix.com"
    canzoni, spot = ottieni_file_dropbox()
    
    if not canzoni and not spot:
        if 'get_next_track_url' in requests.path:
            return redirect(fallback_url)
        return jsonify({"url": fallback_url, "name": "Traccia di test (Aggiungi file MP3 su Dropbox)"})
        
    file_scelto = chiedi_all_ai_cosa_trasmettere(canzoni, spot)
    if not file_scelto:
        file_scelto = random.choice(canzoni) if canzoni else random.choice(spot)
    
    try:
        dbx = dropbox.Dropbox(oauth2_refresh_token=DBX_TOKEN, app_key=DBX_KEY, app_secret=DBX_SECRET)
        media_link = dbx.files_get_temporary_link(file_scelto)
        
        # Estrae il nome pulito del file da mostrare sul sito
        nome_pulito = file_scelto.split('/')[-1]
        
        if 'get_next_track_url' in requests.path:
            return redirect(media_link.link)
        return jsonify({"url": media_link.link, "name": nome_pulito})
    except:
        if 'get_next_track_url' in requests.path:
            return redirect(fallback_url)
        return jsonify({"url": fallback_url, "name": "Traccia di emergenza"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000, threaded=True)
