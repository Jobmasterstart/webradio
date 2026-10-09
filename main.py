import os
import random
import requests
import dropbox
from flask import Flask, render_template_string, redirect

app = Flask(__name__)

DBX_TOKEN = os.environ.get("DROPBOX_REFRESH_TOKEN")
DBX_KEY = os.environ.get("DROPBOX_APP_KEY")
DBX_SECRET = os.environ.get("DROPBOX_APP_SECRET")
HF_API_KEY = os.environ.get("HUGGINGFACE_API_KEY")

HF_API_URL = "https://huggingface.co"

def chiedi_all_ai_cosa_trasmettere(canzoni, spot):
    """L'AI decide se trasmettere musica o pubblicità pescando dalle liste"""
    if not canzoni and not spot:
        return ""
    
    headers = {"Authorization": f"Bearer {HF_API_KEY}"}
    prompt = f"Sei la regia di Radio Fuori Onda Faenza. Scegli un file tra questi musicali: {canzoni} o questi spot: {spot}. Rispondi SOLO con il nome esatto del file scelto, senza aggiungere nient'altro."
    try:
        payload = {"inputs": prompt, "parameters": {"max_new_tokens": 50}}
        response = requests.post(HF_API_URL, json=payload, headers=headers)
        output = response.json()
        if isinstance(output, list) and len(output) > 0 and "generated_text" in output[0]:
            scelta = output[0]["generated_text"].replace(prompt, "").strip()
            # Pulisce eventuali rimescolamenti dell'AI
            for f in canzoni + spot:
                if f in scelta:
                    return f
    except:
        pass
    return random.choice(canzoni) if canzoni else ""

def ottieni_file_dropbox():
    """Legge i file mp3 presenti nel tuo Dropbox"""
    try:
        dbx = dropbox.Dropbox(oauth2_refresh_token=DBX_TOKEN, app_key=DBX_KEY, app_secret=DBX_SECRET)
        canzoni, spot = [], []
        
        try:
            for entry in dbx.files_list_folder('/musica').entries:
                if entry.name.endswith('.mp3'): canzoni.append(entry.name)
        except:
            print("Cartella /musica non trovata o vuota")
            
        try:
            for entry in dbx.files_list_folder('/spot').entries:
                if entry.name.endswith('.mp3'): spot.append(entry.name)
        except:
            print("Cartella /spot non trovata o vuota")
            
        return canzoni, spot
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
            .player-card { background: #1e1e1e; padding: 40px; display: inline-block; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.5); }
            audio { margin-top: 20px; width: 300px; }
        </style>
    </head>
    <body>
        <div class="player-card">
            <h2>🎙️ Radio Fuori Onda Faenza</h2>
            <p>Regia Automatica Cloud gestita dall'IA</p>
            <audio id="audioPlayer" controls src="/stream_audio"></audio>
        </div>
        <script>
            // Quando il brano finisce, chiede automaticamente il successivo all'AI
            var player = document.getElementById('audioPlayer');
            player.onended = function() {
                player.src = "/stream_audio?t=" + new Date().getTime();
                player.play();
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
    
    link_fallback = "https://soundhelix.com"
    
    if not file_scelto:
        return redirect(link_fallback)
        
    try:
        dbx = dropbox.Dropbox(oauth2_refresh_token=DBX_TOKEN, app_key=DBX_KEY, app_secret=DBX_SECRET)
        cartella = "/spot/" if file_scelto in spot else "/musica/"
        media_link = dbx.files_get_temporary_link(cartella + file_scelto)
        return redirect(media_link.link)
    except Exception as e:
        print(f"Errore Dropbox temporaneo: {e}")
        return redirect(link_fallback)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
