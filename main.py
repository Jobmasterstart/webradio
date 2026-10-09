import os
import urllib.request
import urllib.parse
from flask import Flask, render_template_string, jsonify

app = Flask(__name__)

DBX_TOKEN = os.environ.get("DROPBOX_REFRESH_TOKEN")

@app.route('/')
def home():
    html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Attivazione Radio Faenza</title>
        <style>
            body { background: #121212; color: white; font-family: sans-serif; text-align: center; padding-top: 100px; }
            .card { background: #1e1e1e; padding: 40px; display: inline-block; border-radius: 15px; border: 1px solid #333; box-shadow: 0 4px 15px rgba(0,0,0,0.5); }
            .btn-play { background: #25d366; color: white; border: none; padding: 15px 30px; font-size: 18px; border-radius: 30px; cursor: pointer; font-weight: bold; margin-top: 20px; }
        </style>
    </head>
    <body>
        <div class="card">
            <h2>🎙️ Radio Fuori Onda Faenza</h2>
            <p>Sblocco e Attivazione Cartelle</p>
            <button class="btn-play" onclick="creaCartella()">▶️ ATTIVA CARTELLA APPLICAZIONI</button>
            <p id="risultato" style="margin-top:20px; color:#aaa;"></p>
        </div>
        <script>
            function creaCartella() {
                document.getElementById('risultato').innerText = "Invio segnale a Dropbox...";
                fetch('/crea_su_dropbox')
                    .then(r => r.json())
                    .then(data => {
                        if(data.status === "successo") {
                            document.getElementById('risultato').innerText = "SUCCESSO! Aggiorna il tuo Dropbox, la cartella 'Applicazioni' è apparsa!";
                            document.getElementById('risultato').style.color = "#25d366";
                        } else {
                            document.getElementById('risultato').innerText = "Errore: " + data.dettaglio;
                            document.getElementById('risultato').style.color = "#ff3333";
                        }
                    });
            }
        </script>
    </body>
    </html>
    '''
    return render_template_string(html)

@app.route('/crea_su_dropbox')
def crea_su_dropbox():
    url = "https://dropboxapi.com"
    headers = {
        "Authorization": f"Bearer {DBX_TOKEN}",
        "Dropbox-API-Arg": '{"path": "/inizializzazione.txt","mode": "overwrite","autorename": true,"mute": false,"strict_conflict": false}',
        "Content-Type": "application/octet-stream"
    }
    try:
        req = urllib.request.Request(url, data=b"Radio attiva con successo", headers=headers, method="POST")
        with urllib.request.urlopen(req) as response:
            if response.status == 200:
                return jsonify({"status": "successo"})
            return jsonify({"status": "errore", "dettaglio": f"Status code {response.status}"})
    except Exception as e:
        return jsonify({"status": "errore", "dettaglio": str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
