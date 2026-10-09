import os
import random
import requests
import dropbox
from flask import Flask, render_template_string, Response

app = Flask(__name__)

# Recupero credenziali dalle variabili d'ambiente di Render
DBX_TOKEN = os.environ.get("DROPBOX_REFRESH_TOKEN")
DBX_KEY = os.environ.get("DROPBOX_APP_KEY")
DBX_SECRET = os.environ.get("DROPBOX_APP_SECRET")
HF_API_KEY = os.environ.get("HUGGINGFACE_API_KEY")

HF_API_URL = "https://huggingface.co"

def chiedi_all_ai_cosa_trasmettere(canzoni):
    if not canzoni:
        return ""
    headers = {"Authorization": f"Bearer {HF_API_KEY}"}
    prompt = f"Sei la regia di Radio Fuori Onda Faenza. Scegli un file da questo elenco: {canzoni}. Rispondi SOLO con il nome esatto del file, senza aggiungere commenti o saluti."
    try:
        payload = {"inputs": prompt, "parameters": {"max_new_tokens": 50}}
        response = requests.post(HF_API_URL, json=payload, headers=headers, timeout=5)
        output = response.json()
        if isinstance(output, list) and len(output) > 0 and "generated_text" in output:
            scelta = output["generated_text"].replace(prompt, "").strip()
            for f in canzoni:
                if f in scelta:
                    return f
    except:
        pass
    return random.choice(canzoni)

def ottieni_file_dropbox():
    file_trovati = []
    try:
        dbx = dropbox.Dropbox(oauth2_refresh_token=DBX_TOKEN, app_key=DBX_KEY, app_secret=DBX_SECRET)
        
        # 1. Prova a leggere la cartella dell'applicazione (ROOT principale)
        try:
            for entry in dbx.files_list_folder('').entries:
                if entry.name.lower().endswith('.mp3'):
                    file_trovati.append(entry.name)
        except:
            pass
            
        # 2. Prova a leggere anche la cartella sottostante chiamata /musica
        try:
            for entry in dbx.files_list_folder('/musica').entries:
                if entry.name.lower().endswith('.mp3'):
                    file_trovati.append('musica/' + entry.name)
        except:
            pass
            
        return file_trovati
    except:
        return []

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
            audio { margin-top: 20px; width: 320px; }
        </style>
    </head>
    <body>
        <div class="card">
            <h2>🎙️ Radio Fuori Onda Faenza</h2>
            <p>Regia Automatica Cloud via IA</p>
            <audio controls src="/stream_audio" id="player"></audio>
        </div>
        <script>
            var audio = document.getElementById('player');
            audio.onended = function() {
                audio.src = "/stream_audio?cache=" + new Date().getTime();
                audio.play();
            };
        </script>
    </body>
    </html>
    '''
    return render_template_string(html)

@app.route('/stream_audio')
def stream_audio():
    file_disponibili = ottieni_file_dropbox()
    
    # Se Dropbox è vuoto o scatta un errore, trasmetti un MP3 di test sicuro per sbloccare il player
    if not file_disponibili:
        print("Dropbox vuoto. Trasmissione traccia di test.")
        r = requests.get("https://soundhelix.com", stream=True)
        return Response(r.iter_content(chunk_size=1024), mimetype="audio/mpeg")
        
    file_scelto = chiedi_all_ai_cosa_trasmettere(file_disponibili)
    if not file_scelto:
        file_scelto = random.choice(file_disponibili)
        
    try:
        dbx = dropbox.Dropbox(oauth2_refresh_token=DBX_TOKEN, app_key=DBX_KEY, app_secret=DBX_SECRET)
        percorso = file_scelto if '/' in file_scelto else '/' + file_scelto
        
        # Scarica l'audio dal server Render in tempo reale e passalo al browser come flusso diretto
        metadata, res = dbx.files_download(path=percorso)
        return Response(res.content, mimetype="audio/mpeg")
    except:
        r = requests.get("https://soundhelix.com", stream=True)
        return Response(r.iter_content(chunk_size=1024), mimetype="audio/mpeg")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
