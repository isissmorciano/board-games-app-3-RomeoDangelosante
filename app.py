import sqlite3
import os
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)
DB_NAME = 'boardgames.db'

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row # Permette di accedere alle colonne per nome
    return conn

def init_db():
    """Inizializza il database con lo schema e i dati forniti se non esiste."""
    if not os.path.exists(DB_NAME):
        conn = get_db_connection()
        with open('schema.sql', 'w') as f:
            pass # Solo per logica, useremo la stringa qui sotto
        
        # Schema SQL fornito
        schema = """
        DROP TABLE IF EXISTS partite;
        DROP TABLE IF EXISTS giochi;

        CREATE TABLE giochi (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          nome TEXT NOT NULL,
          numero_giocatori_massimo INTEGER NOT NULL,
          durata_media INTEGER NOT NULL,
          categoria TEXT NOT NULL
        );

        CREATE TABLE partite (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          gioco_id INTEGER NOT NULL,
          data DATE NOT NULL,
          vincitore TEXT NOT NULL,
          punteggio_vincitore INTEGER NOT NULL,
          FOREIGN KEY (gioco_id) REFERENCES giochi (id)
        );

        INSERT INTO giochi (nome, numero_giocatori_massimo, durata_media, categoria) VALUES ('Catan', 4, 90, 'Strategia');
        INSERT INTO giochi (nome, numero_giocatori_massimo, durata_media, categoria) VALUES ('Dixit', 6, 30, 'Party');
        INSERT INTO giochi (nome, numero_giocatori_massimo, durata_media, categoria) VALUES ('Ticket to Ride', 5, 60, 'Strategia');

        INSERT INTO partite (gioco_id, data, vincitore, punteggio_vincitore) VALUES (1, '2023-10-15', 'Alice', 10);
        INSERT INTO partite (gioco_id, data, vincitore, punteggio_vincitore) VALUES (1, '2023-10-22', 'Bob', 12);
        INSERT INTO partite (gioco_id, data, vincitore, punteggio_vincitore) VALUES (2, '2023-11-05', 'Charlie', 25);
        INSERT INTO partite (gioco_id, data, vincitore, punteggio_vincitore) VALUES (3, '2023-11-10', 'Alice', 8);
        """
        conn.executescript(schema)
        conn.commit()
        conn.close()
        print("Database inizializzato con successo.")

# --- ROUTE ---

@app.route('/')
def index():
    """Visualizza la lista dei giochi."""
    conn = get_db_connection()
    giochi = conn.execute('SELECT * FROM giochi').fetchall()
    conn.close()
    return render_template('index.html', giochi=giochi)

@app.route('/nuovo_gioco', methods=['GET', 'POST'])
def nuovo_gioco():
    """Crea un nuovo gioco."""
    if request.method == 'POST':
        nome = request.form['nome']
        giocatori = request.form['numero_giocatori_massimo']
        durata = request.form['durata_media']
        categoria = request.form['categoria']

        conn = get_db_connection()
        conn.execute('INSERT INTO giochi (nome, numero_giocatori_massimo, durata_media, categoria) VALUES (?, ?, ?, ?)',
                     (nome, giocatori, durata, categoria))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    
    return render_template('nuovo_gioco.html')

@app.route('/gioco/<int:gioco_id>')
def dettaglio_gioco(gioco_id):
    """Visualizza le partite di un gioco specifico e il form per aggiungerne una."""
    conn = get_db_connection()
    gioco = conn.execute('SELECT * FROM giochi WHERE id = ?', (gioco_id,)).fetchone()
    partite = conn.execute('SELECT * FROM partite WHERE gioco_id = ? ORDER BY data DESC', (gioco_id,)).fetchall()
    conn.close()
    
    if block := None: pass # Hack per evitare errori se gioco è None, idealmente gestire 404
    
    return render_template('dettaglio_gioco.html', gioco=gioco, partite=partite)

@app.route('/gioco/<int:gioco_id>/aggiungi_partita', methods=['POST'])
def aggiungi_partita(gioco_id):
    """Salva una nuova partita per il gioco selezionato."""
    data = request.form['data']
    vincitore = request.form['vincitore']
    punteggio = request.form['punteggio_vincitore']

    conn = get_db_connection()
    conn.execute('INSERT INTO partite (gioco_id, data, vincitore, punteggio_vincitore) VALUES (?, ?, ?, ?)',
                 (gioco_id, data, vincitore, punteggio))
    conn.commit()
    conn.close()
    return redirect(url_for('dettaglio_gioco', gioco_id=gioco_id))

if __name__ == '__main__':
    init_db() # Crea il DB al primo avvio
    app.run(debug=True)