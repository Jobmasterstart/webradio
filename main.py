import os
from flask import Flask, Response, render_template_string

app = Flask(__name__)

# PLAYLIST REALI (I tuoi file di Dropbox configurati prima)
PLAYLIST_MUSICA = [
    "https://example.com",
    "https://example.com"
]

PLAYLIST_SPOT = [
    "https://example.com"
]

# PAGINA WEB CON UN VERO LETTORE AUDIO AUTOMATICO!
HTML_PLAYER = """
<!DOCTYPE html>
<html>
<head>
    <title>La mia Web Radio con IA</title>
    <style>
        body { font-family: Arial, sans-serif; text-align: center; background: #121212; color: white; padding-top: 50px; }
        .player-container { background: #1e1e1e; display: inline-block; padding: 30px; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.5); }
        h1 { color: #bb86fc; font-size: 28px; }
        p { color: #a0a0a0; margin-bottom: 25px; }
        audio { width: 300px; margin-top: 10px; }
    </style>
</head>
<body>
    <div class="player-container">
        <h1>📻 La mia Web Radio con IA</h1>
        <p>In onda ora dal Cloud a PC spento</p>
        <!-- Questo lettore fa suonare i tuoi file MP3 direttamente dal browser -->
        <audio controls autoplay src="{{ primo_brano }}">
            Il tuo browser non supporta il lettore audio.
        </audio>
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    # Prende il primo brano della lista per farlo suonare subito nel lettore della pagina web
    primo_brano = PLAYLIST_MUSICA[0] if PLAYLIST_MUSICA else ""
    return render_template_string(HTML_PLAYER, primo_brano=primo_brano)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
