import os
from flask import Flask, render_template_string

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">

    <title>Radio Fuori Onda Faenza</title>

    <style>
        * {
            box-sizing: border-box;
        }

        body {
            margin: 0;
            min-height: 100vh;
            background: #101114;
            color: #ffffff;
            font-family: Arial, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 24px;
        }

        .card {
            width: 100%;
            max-width: 560px;
            background: #1b1c21;
            border: 1px solid #34363e;
            border-radius: 20px;
            padding: 32px;
            box-shadow: 0 10px 35px rgba(0, 0, 0, 0.35);
        }

        .logo {
            font-size: 42px;
            margin-bottom: 10px;
        }

        h1 {
            margin: 0;
            color: #25d366;
            font-size: 28px;
        }

        .subtitle {
            color: #b8bac4;
            margin-top: 10px;
            line-height: 1.5;
        }

        .status {
            display: inline-block;
            margin: 20px 0;
            padding: 8px 12px;
            border-radius: 20px;
            background: #292c32;
            color: #f0c674;
            font-size: 13px;
        }

        .section {
            margin-top: 24px;
            padding: 18px;
            background: #24262c;
            border-radius: 12px;
            text-align: left;
        }

        .section h2 {
            font-size: 16px;
            margin: 0 0 12px;
        }

        audio {
            width: 100%;
        }

        .note {
            color: #a9abb5;
            font-size: 13px;
            line-height: 1.6;
        }

        footer {
            margin-top: 28px;
            color: #777b86;
            font-size: 12px;
        }
    </style>
</head>

<body>
    <main class="card">

        <div class="logo">🎙️</div>

        <h1>Radio Fuori Onda Faenza</h1>

        <p class="subtitle">
            La tua radio, la tua musica, la tua città.
        </p>

        <div class="status">
            ● Sito online — streaming da configurare
        </div>

        <section class="section">
            <h2>🎵 Ascolta la radio</h2>

            <p class="note">
                Il collegamento al flusso radio verrà configurato
                quando sarà pronto il server audio.
            </p>

            <audio controls preload="none">
                <source id="radio-source" src="" type="audio/mpeg">
                Il tuo browser non supporta il lettore audio.
            </audio>
        </section>

        <section class="section">
            <h2>📢 Spot pubblicitari</h2>

            <p class="note">
                Gli spot verranno gestiti dalla regia automatica
                e inseriti secondo il palinsesto.
            </p>
        </section>

        <section class="section">
            <h2>🤖 Regia intelligente</h2>

            <p class="note">
                Obiettivo del sistema: selezione musicale automatica,
                organizzazione del palinsesto e gestione degli
                inserimenti pubblicitari.
            </p>

            <p class="note">
                La regia automatica è in fase di configurazione.
            </p>
        </section>

        <footer>
            Radio Fuori Onda Faenza
        </footer>

    </main>
</body>
</html>
"""


@app.route("/")
def home():
    return render_template_string(HTML)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
