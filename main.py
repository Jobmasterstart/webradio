import os
import random
import requests
import dropbox
from flask import Flask, render_template_string, jsonify

app = Flask(__name__)

# Recupero variabili d'ambiente da Render
DBX_TOKEN = os.environ.get("DROPBOX_REFRESH_TOKEN")
DBX_KEY = os.environ.get("DROPBOX_APP_KEY")
DBX_SECRET = os.environ.get("DROPBOX_APP_SECRET")
HF_API_KEY = os.environ.get("HUGGINGFACE_API_KEY")

HF_API_URL = "https://huggingface.co"

def chiedi_all_ai_cosa_trasmettere(canzoni):
    if not canzoni:
        return ""
    headers = {"Authorization": f"Bearer {HF_API_KEY}"}
    prompt = f"Sei la regia di Radio Fuori Onda Faenza. Scegli un file da questo elenco: {canzoni}. Rispondi SOLO con il nome esatto del file."
    try:
        payload = {"inputs": prompt, "parameters": {"max_new_tokens": 50}}
        response = requests.post(HF_API_URL, json=payload, headers=headers, timeout=3)
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
        try:
            for entry in dbx.files_list_folder('').entries:
                if entry.name.lower().endswith('.mp3'): file_trovati.append(entry.name)
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
            audio { margin-top: 25px; width: 320px; outline: none; }
            .hint { font-size: 13px; color: #888; margin-top: 15px; }
        </style>
    </head>
    <body>
        <div class="card">
            <h2>🎙️ Radio Fuori Onda Faenza</h2>
            <p>Regia Cloud Continuativa via IA</p>
            
            <!-- Player nativo visibile con sblocco CORS del browser -->
            <audio id="radioPlayer" controls autoplay src="https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3"></audio>
            
            <div class="hint">Usa i controlli del lettore qui sopra per alzare il volume o mettere in pausa.</div>
        </div>

        <script>
            var player = document.getElementById('radioPlayer');
            
            // Logica per agganciare la traccia successiva al termine della canzone
            player.onended = function() {
                fetch('/get_next_track')
                    .then(response => response.json())
                    .then(data => {
                        player.src = data.url;
                        player.load();
                        player.play();
                    })
                    .catch(err => {
                        // Fallback di sicurezza in streaming continuo
                        player.src = "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3";
                        player.load();
                        player.play();
                    });
            };
        </script>
    </body>
    </html>
    '''
    return render_template_string(html)

@app.route('/get_next_track')
def get_next_track():
    fallback_url = "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3"
    file_disponibili = ottieni_file_dropbox()
    
    if not file_disponibili:
        return jsonify({"url": fallback_url})
        
    file_scelto = chiedi_all_ai_cosa_trasmettere(file_disponibili)
    if not file_scelto:
        file_scelto = random.choice(file_disponibili)
        
    try:
        dbx = dropbox.Dropbox(oauth2_refresh_token=DBX_TOKEN, app_key=DBX_KEY, app_secret=DBX_SECRET)
        media_link = dbx.files_get_temporary_link('/' + file_scelto)
        return jsonify({"url": media_link.link})
    except:
        return jsonify({"url": fallback_url})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000, threaded=True)
