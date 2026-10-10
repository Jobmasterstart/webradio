import os
import requests
from flask import Flask, render_template_string, jsonify
from openai import OpenAI
import dropbox

app = Flask(__name__)

# Inizializzazione sicura dei client tramite le variabili d'ambiente di Render
try:
    openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    dbx = dropbox.Dropbox(os.environ.get("DROPBOX_ACCESS_TOKEN"))
except Exception as e:
    print(f"Errore di configurazione iniziale: {e}")

@app.route('/')
def home():
    html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Radio Fuori Onda Faenza - AI Radio</title>
        <style>
            body { background: #121212; color: white; font-family: 'Segoe UI', sans-serif; text-align: center; padding-top: 50px; }
            .container { background: #1e1e1e; padding: 30px; display: inline-block; border-radius: 15px; border: 1px solid #333; box-shadow: 0 4px 15px rgba(0,0,0,0.5); max-width: 500px; }
            h1 { color: #25d366; margin-bottom: 5px; }
            .status { font-size: 0.9em; color: #888; margin-bottom: 25px; }
            .ai-box { background: #2a2a2a; border-left: 4px solid #00bcd4; padding: 15px; text-align: left; margin: 20px 0; border-radius: 4px; }
            audio { width: 100%; margin-top: 15px; outline: none; }
            .btn { background: #25d366; color: black; border: none; padding: 10px 20px; font-weight: bold; border-radius: 5px; cursor: pointer; transition: 0.2s; }
            .btn:hover { background: #20ba5a; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎙️ Radio Fuori Onda Faenza</h1>
            <div class="status">AI Station Engine Attivo</div>
            
            <div class="ai-box">
                <strong>💡 Ultimo Palinsesto AI:</strong>
                <p id="ai-script">Generazione traccia o testo radiofonico in corso...</p>
            </div>

            <!-- Player per lo streaming o la traccia caricata -->
            <audio controls id="radio-player">
                <source src="" type="audio/mpeg">
                Il tuo browser non supporta l'elemento audio.
            </audio>
            
            <p><button class="btn" onclick="generaNuovoContenuto()">Forza Aggiornamento AI</button></p>
        </div>

        <script>
            function generaNuovoContenuto() {
                document.getElementById('ai-script').innerText = 'L\'IA sta elaborando il prossimo blocco radiofonico...';
                fetch('/api/genera-palinsesto')
                    .then(response => response.json())
                    .then(data => {
                        document.getElementById('ai-script').innerText = data.testo || 'Contenuto aggiornato!';
                        if(data.audio_url) {
                            var player = document.getElementById('radio-player');
                            player.src = data.audio_url;
                            player.play();
                        }
                    })
                    .catch(err => {
                        document.getElementById('ai-script').innerText = 'Errore durante la richiesta all\'IA.';
                    });
            }
        </script>
    </body>
    </html>
    '''
    return render_template_string(html)

@app.route('/api/genera-palinsesto', methods=['GET'])
def genera_palinsesto():
    try:
        # 1. Chiamata all'IA per generare il testo del break radiofonico
        completion = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Sei il conduttore radiofonico di Radio Fuori Onda Faenza. Annuncia la musica in modo energico e locale."},
                {"role": "user", "content": "Genera una breve introduzione di 30 secondi per il prossimo blocco musicale."}
            ]
        ]
        testo_radio = completion.choices[0].message.content

        # NOTA: Qui si può integrare la chiamata Text-to-Speech (TTS) e il successivo upload su Dropbox.
        # Al momento restituiamo il testo generato per confermare che l'infrastruttura risponde.
        return jsonify({
            "status": "success",
            "testo": testo_radio,
            "audio_url": "" # Inserire qui il link diretto della traccia audio finale se salvata
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    # Usiamo la porta dinamica assegnata da Render o la 10000 di default
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
