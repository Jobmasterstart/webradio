import os
import random
import requests
import dropbox
from flask import Flask, render_template_string, send_file
import io

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
    prompt = f"Sei la regia di Radio Fuori Onda Faenza. Scegli un file da questo elenco: {canzoni}. Rispondi SOLO con il nome esatto del file, senza aggiungere altro testo."
    try:
        payload = {"inputs": prompt, "parameters": {"max_new_tokens": 50}}
        response = requests.post(HF_API_URL, json=payload, headers=headers, timeout=4)
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
        # Legge i file MP3 nella cartella principale o in /musica
        try:
            for entry in dbx.files_list_folder('').entries:
                if entry.name.lower().endswith('.mp3'): file_trovati.append(entry.name)
        except: pass
        try:
            for entry in dbx.files_list_folder('/musica').entries:
                if entry.name.lower().endswith('.mp3'): file_trovati.append('musica/' + entry.name)
        except: pass
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
            .btn-play { background: #25d366; color: white; border: none; padding: 15px 30px; font-size: 18px; border-radius: 30px; cursor: pointer; font-weight: bold; margin-top: 20px; transition: 0.2s; }
            .btn-play:hover { background: #20ba59; }
            audio { display: none; }
        </style>
    </head>
    <body>
        <div class="card">
            <h2>🎙️ Radio Fuori Onda Faenza</h2>
            <p>Regia Cloud Continuativa via IA</p>
            <button class="btn-play" id="playBtn" onclick="togglePlay()">▶️ ASCOLTA ORA</button>
            <audio id="player" src="/stream_audio"></audio>
        </div>
        <script>
            var player = document.getElementById('player');
            var btn = document.getElementById('playBtn');
            
            function togglePlay() {
                if (player.paused) {
                    player.load();
                    player.play().then(() => {
                        btn.innerText = "⏸️ IN PAUSA";
                    }).catch(e => {
                        console.log("Errore riproduzione:", e);
                    });
                } else {
                    player.pause();
                    btn.innerText = "▶️ ASCOLTA ORA";
                }
            }

            player.onended = function() {
                player.src = "/stream_audio?cache=" + new Date().getTime();
                player.load();
                player.play();
            };
        </script>
    </body>
    </html>
    '''
    return render_template_string(html)

@app.route('/stream_audio')
def stream_audio():
    # Traccia audio di test sicura su internet (SoundHelix) per evitare blocchi
    fallback_url = "https://soundhelix.com"
    
    file_disponibili = ottieni_file_dropbox()
    
    if not file_disponibili:
        r = requests.get(fallback_url)
        return send_file(io.BytesIO(r.content), mimetype="audio/mpeg", as_attachment=False)
        
    file_scelto = chiedi_all_ai_cosa_trasmettere(file_disponibili)
    if not file_scelto:
        file_scelto = random.choice(file_disponibili)
        
    try:
        dbx = dropbox.Dropbox(oauth2_refresh_token=DBX_TOKEN, app_key=DBX_KEY, app_secret=DBX_SECRET)
        percorso = file_scelto if '/' in file_scelto else '/' + file_scelto
        
        # Scarica l'audio nel buffer del server e invialo con supporto nativo del browser
        metadata, res = dbx.files_download(path=percorso)
        return send_file(io.BytesIO(res.content), mimetype="audio/mpeg", as_attachment=False)
    except:
        r = requests.get(fallback_url)
        return send_file(io.BytesIO(r.content), mimetype="audio/mpeg", as_attachment=False)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000, threaded=True)
