import os
from flask import Flask, render_template_string

app = Flask(__name__)

@app.route('/')
def home():
    html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Radio Fuori Onda Faenza</title>
        <style>
            body { background: #121212; color: white; font-family: sans-serif; text-align: center; padding-top: 120px; }
            .card { background: #1e1e1e; padding: 40px; display: inline-block; border-radius: 15px; border: 1px solid #333; box-shadow: 0 4px 15px rgba(0,0,0,0.5); width: 450px; }
            h2 { color: #25d366; margin: 0 0 10px 0; }
            p { color: #aaa; font-size: 14px; margin-bottom: 25px; }
            .btn-dropbox { background: #0061ff; color: white; text-decoration: none; padding: 12px 25px; border-radius: 8px; font-weight: bold; display: inline-block; transition: background 0.2s; }
            .btn-dropbox:hover { background: #004ddb; }
            .info-box { margin-top: 25px; font-size: 12px; color: #777; border-top: 1px solid #333; padding-top: 15px; }
        </style>
    </head>
    <body>
        <div class="card">
            <h2>🎙️ Radio Fuori Onda Faenza</h2>
            <p>Archivio Digitale Musica e Spot</p>
            
            <!-- Link diretto ottimizzato per l'apertura immediata della cartella -->
            <a class="btn-dropbox" href="https://dropbox.com" target="_blank">
                🎵 Apri Player Musica e Spot
            </a>
            
            <div class="info-box">
                Il server Render è attivo. Clicca sul pulsante per riprodurre e gestire direttamente i file audio su Dropbox.
            </div>
        </div>
    </body>
    </html>
    '''
    return render_template_string(html)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
