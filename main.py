import os
import random
import requests
import dropbox
from flask import Flask, render_template_string, jsonify

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
            .btn-play { background: #25d366; color: white; border: none; padding: 15px 30px; font-size: 18px; border-radius: 30px; cursor: pointer; font-weight: bold; margin-top: 20px; }
            .btn-play:hover { background: #20ba59; }
            .status { margin-top: 15px; font-size: 14px; color: #aaa; }
        </style>
    </head>
    <body>
        <div class="card">
            <h2>🎙️ Radio Fuori Onda Faenza</h2>
            <p>Regia Cloud Continuativa via IA</p>
            <button class="btn-play" id="playBtn" onclick="avviaRadio()">▶️ ASCOLTA ORA</button>
            <div class="status" id="statusTxt">Pronto per lo streaming</div>
        </div>

        <script>
            var audioStream = new Audio();
            var btn = document.getElementById('playBtn');
            var statusTxt = document.getElementById('statusTxt');
            var isPlaying = false;

            function caricaEInizia() {
                statusTxt.innerText = "L'IA sta scegliendo il brano...";
                // Richiesta asincrona rapida per evitare il freeze del browser
                fetch('/get_next_track')
                    .then(response => response.json())
                    .then(data => {
                        statusTxt.innerText = "Brano caricato, riproduzione in corso.";
                        audioStream.src = data.url;
                        audioStream.load();
                        audioStream.play().catch(e => {
                            statusTxt.innerText = "Clicca di nuovo per sbloccare l'audio.";
                        });
                    })
                    .catch(err => {
                        // Fallback istantaneo se qualcosa fallisce
                        audioStream.src = "https://soundhelix.com";
                        audioStream.play();
                    });
            }

            function avviaRadio() {
                if (!isPlaying) {
                    isPlaying = true;
                    btn.innerText = "⏸️ IN PAUSA";
                    btn.style.background = "#ff3333";
                    caricaEInizia();
                } else {
                    isPlaying = false;
                    audioStream.pause();
                    btn.innerText = "▶️ ASCOLTA ORA";
                    btn.style.background = "#25d366";
                    statusTxt.innerText = "Radio in pausa.";
                }
            }

            // Quando un brano finisce, carica automaticamente il successivo scelto dall'IA
            audioStream.onended = function() {
                if (isPlaying) {
                    caricaEInizia();
                }
            };
        </script>
    </body>
    </html>
    '''
    return render_template_string(html)

@app.route('/get_next_track')
def get_next_track():
    fallback_url = "https://soundhelix.com"
    file_disponibili = ottieni_file_dropbox()
    
    if not file_disponibili:
        return jsonify({"url": fallback_url})
        
    file_scelto = chiedi_all_ai_cosa_trasmettere(file_disponibili)
    if not file_scelto:
        file_scelto = random.choice(file_disponibili)
        
    try:
        dbx = dropbox.Dropbox(oauth2_refresh_token=DBX_TOKEN, app_key=DBX_KEY, app_secret=DBX_SECRET)
        # Ottieni un link di streaming diretto temporaneo di Dropbox (durata 4 ore)
        media_link = dbx.files_get_temporary_link('/' + file_scelto)
        return jsonify({"url": media_link.link})
    except:
        return jsonify({"url": fallback_url})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000, threaded=True)
