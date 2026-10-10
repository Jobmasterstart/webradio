import os
import json
from datetime import datetime
from flask import Flask, render_template_string, jsonify
from openai import OpenAI
import dropbox
from tinytag import TinyTag
import io

app = Flask(__name__)

# Configurazione client con gestione errori aziendale
try:
    openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    dbx = dropbox.Dropbox(
        app_key=os.environ.get("DROPBOX_APP_KEY"),
        app_secret=os.environ.get("DROPBOX_APP_SECRET"),
        oauth2_refresh_token=os.environ.get("DROPBOX_REFRESH_TOKEN")
    )
except Exception as e:
    print(f"⚠️ Errore critico di configurazione: {e}")

def ottieni_fascia_oraria_intelligente():
    """Rileva l'ora del server e restituisce la linea guida del palinsesto"""
    ora = datetime.now().hour
    if 6 <= ora < 10:
        return "MATTINO (6-10): Risveglio felice. Pop/Rock Anni 80/90 ritmato, sia italiano che straniero."
    elif 10 <= ora < 14:
        return "MEZZOGIORNO (10-14): Grandi classici radiofonici. Alternanza equilibrata Italia/Estero Anni 70/80."
    elif 14 <= ora < 18:
        return "POMERIGGIO (14-18): Ritmo e grinta. Rock Anni 80, Eurodance Anni 90 e canzoni energiche."
    elif 18 <= ora < 22:
        return "SERA/APERITIVO (18-22): Musica di classe. Cantautorato italiano, grandi icone pop Anni 70/80/90."
    else:
        return "NOTTURNA (22-6): Sound intimo e rilassante. Canzoni lente, romantiche e grandi successi nostalgici."

def analizza_brano_ibrido(entry):
    """Metodo Ibrido: Tenta la lettura dei tag ID3; in caso di fallimento, interviene l'IA sul nome del file"""
    titolo = None
    artista = None
    genere = None
    anno = None

    # TENTATIVO 1: Lettura dei metadati ID3 interni (TinyTag)
    try:
        # Chiediamo a Dropbox solo i primi 300KB del file (sufficienti per leggere i tag ID3) senza sovraccaricare Render
        _, res = dbx.files_download_zip(entry.path_lower, range="bytes=0-300000")
        audio_buffer = io.BytesIO(res.content)
        tag = TinyTag.get(audio_buffer, image=False)
        
        titolo = tag.title
        artista = tag.artist
        genere = tag.genre
        anno = tag.year
    except Exception:
        pass # Se fallisce la lettura interna, passiamo serenamente al metodo 2

    # TENTATIVO 2: Se i dati fondamentali mancano, interviene l'IA analizzando il nome del file
    if not titolo or not artista:
        try:
            prompt_analisi = (
                f"Analizza il seguente nome di file musicale: '{entry.name}'.\n"
                "Estrai o deduci intelligentemente: titolo, artista, decennio/anno e se è musica Italiana o Straniera.\n"
                "Rispondi ESCLUSIVAMENTE con un oggetto JSON avente le chiavi: 'titolo', 'artista', 'genere', 'anno'."
            )
            completion = openai_client.chat.completions.create(
                model="gpt-4o-mini",
                response_format={"type": "json_object"},
                messages=[{"role": "user", "content": prompt_analisi}]
            )
            dati_ia = json.loads(completion.choices.message.content)
            
            titolo = titolo or dati_ia.get("titolo") or entry.name.replace(".mp3", "")
            artista = artista or dati_ia.get("artista") or "Artista Sconosciuto"
            genere = genere or dati_ia.get("genere") or "Genere Misto"
            anno = anno or dati_ia.get("anno") or "Anni 80"
        except Exception:
            titolo = entry.name.replace(".mp3", "")
            artista = "Regia Automatica"
            genere = "Anni 70-80-90"
            anno = "Vari"

    return {
        "file_name": entry.name,
        "path": entry.path_lower,
        "titolo": titolo,
        "artista": artista,
        "genere": genere,
        "anno": anno
    }

def scansiona_catalogo_dropbox():
    """Esplora la cartella Dropbox e mappa tutti i brani presenti usando la logica ibrida"""
    try:
        # NOTA: Assicurati che la cartella si chiami esattamente così o adatta la stringa (es: '/musica')
        risultato = dbx.files_list_folder('/musicaradio')
        catalogo = []
        for entry in risultato.entries:
            if entry.name.lower().endswith('.mp3'):
                info_brano = analizza_brano_ibrido(entry)
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
        <title>Radio Fuori Onda Faenza - Regia Ibrida AI</title>
        <style>
            body { background: #0b0b0e; color: #e5e5e7; font-family: 'Segoe UI', system-ui, sans-serif; text-align: center; padding-top: 50px; }
            .radio-box { background: #14141a; padding: 40px; display: inline-block; border-radius: 24px; border: 1px solid #23232f; box-shadow: 0 12px 40px rgba(0,0,0,0.6); max-width: 520px; width: 90%; }
            h1 { color: #25d366; margin: 0 0 5px 0; font-size: 2.2em; font-weight: 800; letter-spacing: -0.5px; }
            .badge { background: rgba(37, 211, 102, 0.15); color: #25d366; padding: 4px 12px; border-radius: 12px; font-size: 0.8em; font-weight: bold; display: inline-block; margin-bottom: 25px; }
            .schedule { background: #1c1c24; padding: 15px; border-radius: 12px; text-align: left; font-size: 0.9em; border-left: 4px solid #00bcd4; margin-bottom: 25px; }
            .player-container { background: #09090c; padding: 25px; border-radius: 16px; border: 1px solid #1c1c24; margin: 20px 0; }
            .track { font-size: 1.5em; font-weight: bold; color: #ffffff; line-height: 1.2; }
            .meta { font-size: 0.95em; color: #8a8a9e; margin-top: 6px; }
            .ai-logic { font-style: italic; color: #b3b3c6; font-size: 0.9em; background: #181822; padding: 14px; border-radius: 8px; text-align: left; line-height: 1.5; margin-top: 20px; }
            audio { width: 100%; margin-top: 20px; }
        </style>
    </head>
    <body>
        <div class="radio-box">
            <h1>Fuori Onda Faenza</h1>
            <div class="badge">📡 REGIA IBRIDA AI ATTIVA</div>
            
            <div class="schedule">
                <strong>📅 Palinsesto Fascia Oraria:</strong><br>
                <span id="palinsesto-info">Analisi dell'orario in corso...</span>
            </div>

            <div class="player-container">
                <div style="font-size: 0.75em; color: #8a8a9e; text-transform: uppercase; font-weight: 700; margin-bottom: 10px; letter-spacing: 1px;">In Onda Ora:</div>
                <div class="track" id="track-title">Sintonizzazione regia...</div>
                <div class="meta" id="track-details">-</div>
                
                <audio controls autoplay id="radio-core-player">
                    <source src="" type="audio/mpeg">
                </audio>
            </div>

            <div class="ai-logic" id="ai-reasoning">
                <strong>🧠 Scelta del Direttore Artistico AI:</strong> L'algoritmo sta integrando i metadati ID3 e l'analisi testuale per scegliere il pezzo migliore.
            </div>
        </div>

        <script>
            const audioPlayer = document.getElementById('radio-core-player');

            function caricaProssimaCanzone() {
                fetch('/api/regia-ibrida-prossimo')
                    .then(res => res.json())
                    .then(data => {
                        if(data.status === "success") {
                            document.getElementById('palinsesto-info').innerText = data.fascia;
                            document.getElementById('track-title').innerText = data.scelta.titolo;
                            document.getElementById('track-details').innerText = data.scelta.artista + " (" + data.scelta.anno + ") - " + data.scelta.genere;
                            document.getElementById('ai-reasoning').innerHTML = '<strong>🧠 Criterio di Selezione:</strong> ' + data.motivazione;
                            
                            audioPlayer.src = data.url_streaming;
                            audioPlayer.play().catch(() => console.log("In attesa di interazione dell'utente per l'audio."));
                        } else {
                            document.getElementById('track-title').innerText = "Nessun brano utilizzabile su Dropbox.";
                        }
                    })
                    .catch(() => {
                        document.getElementById('track-title').innerText = "Errore di sincronizzazione con la regia.";
                    });
            }

            // Transizione fluida e infinita: appena finisce un brano, parte il successivo scelto dall'IA
            audioPlayer.onended = caricaProssimaCanzone;
            window.onload = caricaProssimaCanzone;
        </script>
    </body>
    </html>
    '''
    return render_template_string(html)

@app.route('/api/regia-ibrida-prossimo')
def regia_ibrida_prossimo():
    try:
        fascia = ottieni_fascia_oraria_intelligente()
        catalogo = scansiona_catalogo_dropbox()

        if not catalogo:
            return jsonify({"status": "error", "message": "Nessun file musicale trovato"}), 404

        # Inviamo l'intero catalogo mappato (con tag interni o dedotti da IA) a GPT per la programmazione
        prompt_regia = (
            "Sei il Direttore di Programmazione Radiofonica di Radio Fuori Onda Faenza. "
            "Devi selezionare la traccia ideale anni 70/80/90, italiana o straniera, basandoti sulla fascia oraria corrente.\n\n"
            f"FASCIA ATTUALE: {fascia}\n\n"
            f"CATALOGO BRANI DISPONIBILI (COMPRESO DI METADATI ID3/ANALIZZATI):\n{json.dumps(catalogo, indent=2)}\n\n"
            "Scegli un brano. Rispondi RIGIDAMENTE con un oggetto JSON contenente il 'file_name' esatto scelto e una 'motivazione' artistica.\n"
