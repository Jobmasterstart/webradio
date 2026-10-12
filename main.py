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
            body { background: #121212; color: white; font-family: sans-serif; text-align: center; padding-top: 80px; }
            .card { background: #1e1e1e; padding: 40px; display: inline-block; border-radius: 15px; border: 1px solid #333; box-shadow: 0 4px 15px rgba(0,0,0,0.5); width: 400px; }
            .audio-section { margin-top: 30px; text-align: left; }
            label { font-weight: bold; color: #25d366; display: block; margin-bottom: 8px; font-size: 14px; }
            audio { width: 100%; margin-bottom: 25px; outline: none; }
            h2 { color: #25d366; margin: 0 0 5px 0; }
            p { color: #888; margin: 0 0 10px 0; font-size: 14px; }
        </style>
    </head>
    <body>
        <div class="card">
            <h2>🎙️ Radio Fuori Onda Faenza</h2>
            <p>Canale di Trasmissione Diretto</p>
            
            <div class="audio-section">
                <!-- LETTORE MUSICA - Riproduzione diretta dal file sorgente -->
                <label>🎵 FLUSSO MUSICA PRINCIPALE:</label>
                <audio controls autoplay src="https://dropbox.com"></audio>
                
                <!-- LETTORE SPOT - Riproduzione diretta dal file sorgente -->
                <label>📢 SPOT E COMMERCIAL:</label>
                <audio controls src="https://dropbox.com"></audio>
            </div>
        </div>
    </body>
    </html>
    '''
    return render_template_string(html)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
