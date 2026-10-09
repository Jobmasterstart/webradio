import os
import random
import requests
import dropbox
from flask import Flask, render_template_string, redirect

app = Flask(__name__)

# Recupero variabili d'ambiente da Render
DBX_TOKEN = os.environ.get("DROPBOX_REFRESH_TOKEN")
DBX_KEY = os.environ.get("DROPBOX_APP_KEY")
DBX_SECRET = os.environ.get("DROPBOX_APP_SECRET")
HF_API_KEY = os.environ.get("HUGGINGFACE_API_KEY")

HF_API_URL = "https://huggingface.co"

def chiedi_all_ai_cosa_trasmettere(canzoni, spot):
    if not canzoni:
        return ""
    headers = {"Authorization": f"Bearer {HF_API_KEY}"}
    prompt = f"Sei la regia di Radio Fuori Onda Faenza. Scegli un file da questo elenco: {canzoni}. Rispondi SOLO con il nome esatto del file, senza aggiungere commenti."
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
        
        # Prova a leggere prima la cartella speciale dell'applicazione
        try:
            for entry in dbx.files_list_folder('').entries:
                if entry.name.lower().endswith('.mp3'):
                    file_trovati.append(entry.name)
        except:
            pass
            
        # Prova a leggere anche una cartella chiamata musica nella root principale
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
    # Pagina HTML stabile con player standard
    html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Radio Fuori Onda Faenza</title>
        <style>
            body { background: #121212; color: white; font-family: sans-serif; text-align: center; padding-top: 100px; }
            .card { background: #1e1e1e; padding: 40px; display: inline-block; border-radius: 15px; border: 1px solid #333; }
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
    # Canzone di test sicura su internet se Dropbox non risponde
    musica_di_test = "https://soundhelix.com"
    
    file_disponibili = ottieni_file_dropbox()
    
    if not file_disponibili:
        print("Nessun MP3 trovato. Riproduzione traccia di test per sbloccare il player.")
        return redirect(musica_di_test)
        
    file_scelto = chiedi_all_ai_cosa_trasmettere(file_disponibili, [])
    if not file_scelto:
        file_scelto = random.choice(file_disponibili)
        
    try:
        dbx = dropbox.Dropbox(oauth2_refresh_token=DBX_TOKEN, app_key=DBX_KEY, app_secret=DBX_SECRET)
        percorso = file_scelto if '/' in file_scelto else '/' + file_scelto
        media_link = dbx.files_get_temporary_link(percorso)
        return redirect(media_link.link)
    except:
        return redirect(musica_di_test)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
