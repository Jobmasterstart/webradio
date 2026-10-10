import os
import json
from datetime import datetime
from flask import Flask, render_template_string, jsonify
from openai import OpenAI
import dropbox

app = Flask(__name__)

# Configurazione sicura dei client esterni
try:
    openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    dbx = dropbox.Dropbox(
        app_key=os.environ.get("DROPBOX_APP_KEY"),
        app_secret=os.environ.get("DROPBOX_APP_SECRET"),
        oauth2_refresh_token=os.environ.get("DROPBOX_REFRESH_TOKEN")
    )
except Exception as e:
    print(f"⚠️ Errore di configurazione: {e}")

def ottieni_fascia_oraria_intelligente():
    """Rileva l'ora attuale del server e definisce lo stile musicale adatto"""
    ora = datetime.now().hour
    if 6 <= ora < 10:
        return "MATTINO (6-10): Risveglio ed energia. Pop/Rock Anni 80/90 sia italiano che straniero per iniziare la giornata."
    elif 10 <= ora < 14:
        return "MEZZOGIORNO (10-14): Grandi classici radiofonici. Alternanza Italia/Estero Anni 70/80."
    elif 14 <= ora < 18:
        return "POMERIGGIO (14-18): Ritmo e grinta. Spazio al rock Anni 80, dance Anni 90 e hit cariche."
    elif 18 <= ora < 22:
        return "SERA/APERITIVO (18-22): Musica di classe. Cantautorato italiano e grandi icone pop Anni 70/80/90."
    else:
        return "NOTTURNA (22-6): Sound intimo e rilassante. Canzoni prevalentemente lente, ballate e successi nostalgici."

def analizza_brano_con_ia(nome_file, path_file):
    """L'IA analizza il nome del file e riconosce artista, titolo, anno e genere in automatico"""
    try:
        prompt_analisi = (
            f"Analizza il seguente nome di file musicale proveniente da una radio: '{nome_file}'.\n"
            "Riconosci e separa intelligentemente: titolo, artista, decennio/anno di uscita e genere musicale.\n"
            "Rispondi ESCLUSIVAMENTE con un oggetto JSON valido avente le chiavi: 'titolo', 'artista', 'genere', 'anno'."
        )
        completion = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            response_format={"type": "json_object"},
            messages=[{"role": "user", "content": prompt_analisi}]
        )
        dati_ia = json.loads(completion.choices.message.content)
        
        return {
            "file_name": nome_file,
            "path": path_file,
            "titolo": dati_ia.get("titolo") or nome_file.replace(".mp3", ""),
            "artista": dati_ia.get("artista") or "Artista Sconosciuto",
            "genere": dati_ia.get("genere") or "Anni 70-80-90",
            "anno": dati_ia.get("anno") or "Vari"
        }
    except Exception:
        # Salvataggio di emergenza se l'API fallisce
        return {
            "file_name": nome_file,
            "path": path_file,
            "titolo": nome_file.replace(".mp3", ""),
            "artista": "Regia Automatica",
            "genere": "Musica d'archivio",
            "anno": "Vari"
        }

def scansiona_catalogo_dropbox():
    """Esplora la cartella principale di Dropbox e indicizza tutti i brani MP3"""
    try:
        risultato = dbx.files_list_folder('/musicaradio')
        catalogo = []
        for entry in risultato.entries:
            if entry.name.lower().endswith('.mp3'):
                info_brano = analizza_brano_con_ia(entry.name, entry.path_lower)
                catalogo.append(info_brano)
        return catalogo
    except Exception as e:
        print(f"Errore scansione Dropbox: {e}")
        return []

@app.route('/')
def home():
    html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Radio Fuori Onda Faenza - Regia AI</title>
        <style>
            body { background: #0b0b0e; color: #e5e5e7; font-family: 'Segoe UI', sans-serif; text-align: center; padding-top: 50px; }
            .radio-box { background: #14141a; padding: 40px; display: inline-block; border-radius: 24px; border: 1px solid #23232f; box-shadow: 0 12px 40px rgba(0,0,0,0.6); max-width: 520px; width: 90%; }
            h1 { color: #25d366; margin: 0 0 5px 0; font-size: 2.2em; font-weight: 800; }
            .badge { background: rgba(37, 211, 102, 0.15); color: #25d366; padding: 4px 12px; border-radius: 12px; font-size: 0.8em; font-weight: bold; display: inline-block; margin-bottom: 25px; }
            .schedule { background: #1c1c24; padding: 15px; border-radius: 12px; text-align: left; font-size: 0.9em; border-left: 4px solid #00bcd4; margin-bottom: 25px; }
            .player-container { background: #09090c; padding: 25px; border-radius: 16px; border: 1px solid #1c1c24; margin: 20px 0; }
            .track { font-size: 1.5em; font-weight: bold; color: #ffffff; }
            .meta { font-size: 0.95em; color: #8a8a9e; margin-top: 6px; }
            .ai-logic { font-style: italic; color: #b3b3c6; font-size: 0.9em; background: #181822; padding: 14px; border-radius: 8px; text-align: left; line-height: 1.5; margin-top: 20px; }
            audio { width: 100%; margin-top: 20px; }
        </style>
    </head>
    <body>
        <div class="radio-box">
            <h1>Fuori Onda Faenza</h1>
            <div class="badge">📡 REGIA AUTOMATICA AI ATTIVA</div>
            
            <div class="schedule">
                <strong>📅 Palinsesto Fascia Oraria:</strong><br>
                <span id="palinsesto-info">Analizzazione dell'orario in corso...</span>
            </div>

            <div class="player-container">
                <div style="font-size: 0.75em; color: #8a8a9e; text-transform: uppercase; font-weight: 700; margin-bottom: 10px;">In Onda Ora:</div>
                <div class="track" id="track-title">Sintonizzazione regia...</div>
                <div class="meta" id="track-details">-</div>
                
                <audio controls autoplay id="radio-core-player">
                    <source src="" type="audio/mpeg">
                </audio>
            </div>

            <div class="ai-logic" id="ai-reasoning">
                <strong>🧠 Scelta dell'IA:</strong> L'algoritmo sta scansionando i brani musicali per comporre la sequenza ideale.
            </div>
        </div>

        <script>
            const audioPlayer = document.getElementById('radio-core-player');

            function caricaProssimaCanzone() {
                fetch('/api/regia-prossimo')
                    .then(res => res.json())
                    .then(data => {
                        if(data.status === "success") {
                            document.getElementById('palinsesto-info').innerText = data.fascia;
                            document.getElementById('track-title').innerText = data.scelta.titolo;
                            document.getElementById('track-details').innerText = data.scelta.artista + " (" + data.scelta.anno + ") - " + data.scelta.genere;
                            document.getElementById('ai-reasoning').innerHTML = '<strong>🧠 Criterio di Selezione:</strong> ' + data.motivazione;
                            
                            audioPlayer.src = data.url_streaming;
                            audioPlayer.play().catch(() => console.log("In attesa di interazione con la pagina."));
                        } else {
                            document.getElementById('track-title').innerText = "Nessun brano trovato su Dropbox.";
                        }
                    })
                    .catch(() => {
                        document.getElementById('track-title').innerText = "Errore di connessione con il server.";
                    });
            }

            audioPlayer.onended = caricaProssimaCanzone;
            window.onload = caricaProssimaCanzone;
        </script>
    </body>
    </html>
    '''
    return render_template_string(html)

@app.route('/api/regia-prossimo')
def regia_prossimo():
    try:
        fascia = ottieni_fascia_oraria_intelligente()
        catalogo = scansiona_catalogo_dropbox()

        if not catalogo:
            return jsonify({"status": "error", "message": "Nessun file musicale trovato"}), 404

        prompt_regia = (
            "Sei il Direttore Artistico di Radio Fuori Onda Faenza. "
            "Il tuo compito è selezionare il brano ideale anni 70/80/90, italiano o straniero, basandoti sulla fascia oraria corrente.\n\n"
            f"FASCIA ATTUALE: {fascia}\n\n"
            f"CATALOGO BRANI RICONOSCIUTI:\n{json.dumps(catalogo, indent=2)}\n\n"
            "Scegli un brano. Rispondi esclusivamente con un oggetto JSON contenente il 'file_name' esatto scelto e una 'motivazione' artistica.\n"
            "Esempio:\n{\"file_name\": \"musica1.mp3\", \"motivazione\": \"Brano perfetto per questa ora del giorno, mantiene alto il morale degli ascoltatori con del sano pop anni 80.\"}"
        )

        completion = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            response_format={"type": "json_object"},
            messages=[{"role": "system", "content": prompt_regia}]
        )

        risposta = json.loads(completion.choices.message.content)
        file_selezionato = risposta.get("file_name")
        motivazione = risposta.get("motivazione", "Selezione automatica oraria.")

        canzone_scelta = next((c for c in catalogo if c["file_name"] == file_selezionato), catalogo[0])
        media_info = dbx.files_get_temporary_link(canzone_scelta["path"])

        return jsonify({
            "status": "success",
            "fascia": fascia,
            "scelta": canzone_scelta,
            "url_streaming": media_info.link,
            "motivazione": motivazione
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
