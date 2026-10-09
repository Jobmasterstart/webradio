import os
import requests
import dropbox
from flask import Flask, render_template_string, jsonify, redirect

app = Flask(__name__)

DBX_TOKEN = os.environ.get("DROPBOX_REFRESH_TOKEN")
DBX_KEY = os.environ.get("DROPBOX_APP_KEY")
DBX_SECRET = os.environ.get("DROPBOX_APP_SECRET")

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
        </style>
    </head>
    <body>
        <div class="card">
            <h2>🎙️ Radio Fuori Onda Faenza</h2>
            <p>Attivazione Sistema Cloud...</p>
            <button class="btn-play" onclick="avviaTest()">▶️ ATTIVA CARTELLA DROPBOX</button>
        </div>
        <script>
            function avviaTest() {
                alert("Invio impulso a Dropbox in corso. Attendi 10 secondi e rinfresca il tuo Dropbox!");
                fetch('/forza_creazione_cartella');
            }
        </script>
    </body>
    </html>
    '''
    return render_template_string(html)

@app.route('/forza_creazione_cartella')
def forza_creazione_cartella():
    try:
        dbx = dropbox.Dropbox(oauth2_refresh_token=DBX_TOKEN, app_key=DBX_KEY, app_secret=DBX_SECRET)
        # Scarica una traccia audio di test fissa e prova a scriverla su Dropbox per forzare la creazione della cartella
        file_url = "https://soundhelix.com"
        r = requests.get(file_url)
        dbx.files_upload(r.content, "/inizializzazione_radio.mp3", mode=dropbox.files.WriteMode.overwrite)
        return jsonify({"status": "successo"})
    except Exception as e:
        return jsonify({"status": "errore", "dettaglio": str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000, threaded=True)
