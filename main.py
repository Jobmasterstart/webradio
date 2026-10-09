import os
import random
import requests
from flask import Flask, render_template_string, jsonify, redirect

app = Flask(__name__)

HF_API_KEY = os.environ.get("HUGGINGFACE_API_KEY")
HF_API_URL = "https://huggingface.co"

# Scaletta di canzoni di test stabili e sicure da internet gestite dall'IA
BRANI_RADIO = [
    {"name": "Mellow Grooves - Canzone 1", "url": "https://soundhelix.com"},
    {"name": "Chill Beats - Canzone 2", "url": "https://soundhelix.com"},
    {"name": "Ambient Lounge - Canzone 3", "url": "https://soundhelix.com"},
    {"name": "Retro Wave - Canzone 4", "url": "https://soundhelix.com"},
    {"name": "Pop Synth - Canzone 5", "url": "https://soundhelix.com"}
]

# Scaletta di spot/jingle radiofonici di prova
SPOT_RADIO = [
    {"name": "Jingle Radio Faenza 1", "url": "https://soundhelix.com"},
    {"name": "Spot Pubblicitario 2", "url": "https://soundhelix.com"}
]

def chiedi_all_ai_cosa_trasmettere(nomi_brani, nomi_spot):
    headers = {"Authorization": f"Bearer {HF_API_KEY}"}
    prompt = f"Sei il regista della regia automatica di Radio Fuori Onda Faenza. Scegli cosa trasmettere adesso tra questi brani: {nomi_brani} o questi spot: {nomi_spot}. Rispondi SOLO con il nome esatto della traccia scelta, senza aggiungere nient'altro."
    try:
        payload = {"inputs": prompt, "parameters": {"max_new_tokens": 50}}
        response = requests.post(HF_API_URL, json=payload, headers=headers, timeout=3)
        output = response.json()
        if isinstance(output, list) and len(output) > 0 and "generated_text" in output:
            scelta = output["generated_text"].replace(prompt, "").strip()
            return scelta
    except:
        pass
    # Paracadute di sicurezza se l'AI è lenta o va in timeout
    return random.choice(nomi_brani)

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
            <div class="status" id="statusTrack">In onda: Avvio regia automatica...</div>
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
                        statusTrack.innerText = "In onda: Canzone di emergenza";
                    });
            }

            player.onended = function() {
                caricaTracciaSuccessiva();
            };
            
            player.onplay = function() {
                if(statusTrack.innerText.includes("Avvio")) {
                    statusTrack.innerText = "In onda ora: Regia Automatica Cloud attiva";
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
    nomi_brani = [b["name"] for b in BRANI_RADIO]
    nomi_spot = [s["name"] for s in SPOT_RADIO]
    
    # L'AI sceglie cosa trasmettere
    scelta_ai = chiedi_all_ai_cosa_trasmettere(nomi_brani, nomi_spot)
    
    # Cerca l'oggetto corrispondente alla scelta dell'AI
    traccia_selezionata = None
    for b in BRANI_RADIO + SPOT_RADIO:
        if b["name"] in scelta_ai:
            traccia_selezionata = b
            break
            
    if not traccia_selezionata:
        traccia_selezionata = random.choice(BRANI_RADIO)
        
    if 'get_next_track_url' in requests.path:
        return redirect(traccia_selezionata["url"])
    return jsonify({"url": traccia_selezionata["url"], "name": traccia_selezionata["name"]})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000, threaded=True)
