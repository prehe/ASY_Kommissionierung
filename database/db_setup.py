import sqlite3
import os
import random

def connect_db():
    """Stellt eine Verbindung zur SQLite-Datenbank her."""
    conn = sqlite3.connect("database/assystenzsystem.db")
    return conn

def create_db(cursor, conn):
    """Erstellt die Datenbank und die erforderlichen Tabellen, falls sie nicht existieren."""
    # Tabelle "kunde"
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS kunde (
        ID INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        vorname TEXT NOT NULL,
        email TEXT NOT NULL,
        telefon TEXT NOT NULL,
        straße TEXT NOT NULL,
        plz INTEGER NOT NULL,
        wohnort TEXT NOT NULL
        )
    """)

# Tabelle "produkt"
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS produkt (
        ID INTEGER PRIMARY KEY,
        bezeichnung TEXT NOT NULL,
        bild BLOB,
        preis REAL NOT NULL DEFAULT 0,
        abmessung TEXT,
        lagerbestand INTEGER NOT NULL DEFAULT 0)
    """)

# Tabelle "auftrag"
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS auftrag (
        ID INTEGER PRIMARY KEY,
        kunden_ID INTEGER NOT NULL,
        bestelldatum TEXT NOT NULL,
        status INT NOT NULL DEFAULT 0,
        FOREIGN KEY (kunden_ID) REFERENCES kunde(ID)
        )
    """)    # status 0 = offen, 1 = in Bearbeitung, 2 = abgeschlossen

# Tabelle "auftragsposition"
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS auftragsposition (
        ID INTEGER PRIMARY KEY,
        auftrag_ID INTEGER NOT NULL,
        produkt_ID INTEGER NOT NULL,
        menge INTEGER NOT NULL,
        einzelpreis REAL NOT NULL,
        erledigt INTEGER NOT NULL DEFAULT 0,
        FOREIGN KEY (auftrag_ID) REFERENCES auftrag(ID),
        FOREIGN KEY (produkt_ID) REFERENCES produkt(ID)
    )
    """)
    # commit the changes
    conn.commit()

# create_db(cursor)
def close_db(conn):
    """Schließt die Verbindung zur SQLite-Datenbank."""
    conn.close()





# ------ Datenbankbefüllung ------
def insert_default_produkte(cursor, conn):
    # Produkte-Daten (ID 1 bis 9)
    image_folder = "database/images"
    produkte = [
        (12401, 'Miele EPW 280 Generalüberholt', 'Miele_EPW_280_Generalüberholt.webp', 103.00, '20x15x5 cm', 12),
        (12402, 'Miele EW 171 Generalüberholt', 'Miele_EW_171_Generalüberholt.webp', 103.00, '18x14x4 cm', 8),
        (12403, 'Miele ELP 255 Generalüberholt', 'Miele_ELP_255_Generalüberholt.webp', 219.00, '30x20x7 cm', 3),
        (12404, 'Miele ELP 567 Generalüberholt', 'Miele_ELP_567_Generalüberholt.webp', 219.00, '30x20x7 cm', 4),
        (12405, 'Siemens Geschirrspülmaschine Heizpumpe Generalüberholt', 'Siemens_Geschirrspülmaschine_Heizpumpe_Generalüberholt.webp', 149.00, '28x20x8 cm', 5),
        (12406, 'Miele WPS Schlauch Wasserschutzeinrichtung W1 Generalüberholt', 'Miele_WPS_Schlauch_Wasserschutzeinrichtung_W1_Generalüberholt.webp', 89.00, '30x12x6 cm', 7),
        (12407, 'Miele Wasserzulaufventil Generalüberholt', 'Miele_Wasserzulaufventil_Generalüberholt.webp', 49.00, '12x10x6 cm', 9),
        (12408, 'Siemens Waschmaschine Heizung Generalüberholt inkl. NTC', 'Siemens_Waschmaschine_Heizung_Generalüberholt.webp', 69.00, '25x15x5 cm', 6),
        (12409, 'Bosch Logixx8 Waschmaschine Elektronik Reparatur', 'Bosch_Logixx8_Waschmaschine_Elektronik_Reparatur.webp', 119.00, '20x15x4 cm', 4)
    ]
    
    # Produkte einfügen oder updaten
    for produkt in produkte:
        id, bezeichnung, bilddatei, preis, abmessung, lagerbestand = produkt
        image_path = os.path.join(image_folder, bilddatei)
        if os.path.isfile(image_path):
            bild_blob = read_image(image_path)
        else:
            print(f"⚠️ Bild nicht gefunden: {image_path} — speichere NULL als Bild.")
            bild_blob = None

        cursor.execute('''
            INSERT OR REPLACE INTO produkt (ID, bezeichnung, bild, preis, abmessung, lagerbestand)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (id, bezeichnung, bild_blob, preis, abmessung, lagerbestand))

    conn.commit()
    print("✅ Produkte erfolgreich in die Datenbank eingefügt.")
    
def insert_default_kunde(cursor, conn):
    # Kundendaten (13 Datensätze)
    kunden = [
        (1, 'Müller', 'Anna', 'anna.mueller@example.de', '+4915112345678', 'Hauptstraße 12', 10115, 'Berlin'),
        (2, 'Schmidt', 'Peter', 'peter.schmidt@example.de', '+4917611122233', 'Bahnhofstraße 7', 80331, 'München'),
        (3, 'Weber', 'Laura', 'laura.weber@example.de', '+4915789988776', 'Kölner Ring 45', 50667, 'Köln'),
        (4, 'Schneider', 'Julia', 'julia.schneider@example.de', '+4915212345670', 'Lindenweg 3', 4109, 'Leipzig'),
        (5, 'Fischer', 'Thomas', 'thomas.fischer@example.de', '+491701112233', 'Marktplatz 8', 44135, 'Dortmund'),
        (6, 'Becker', 'Sophie', 'sophie.becker@example.de', '+4915198765432', 'Goethestraße 15', 28195, 'Bremen'),
        (7, 'Hoffmann', 'Max', 'max.hoffmann@example.de', '+4917612345678', 'Wilhelmstraße 9', 65185, 'Wiesbaden'),
        (8, 'Klein', 'Lisa', 'lisa.klein@example.de', '+491522223344', 'Schillerstraße 20', 70173, 'Stuttgart'),
        (9, 'Wolf', 'Jan', 'jan.wolf@example.de', '+491577889900', 'Friedrichstraße 12', 20095, 'Hamburg'),
        (10, 'Neumann', 'Laura', 'laura.neumann@example.de', '+491578887766', 'Mozartweg 7', 80331, 'München'),
        (11, 'Richter', 'Paul', 'paul.richter@example.de', '+491751234567', 'Kaiserstraße 30', 90403, 'Nürnberg'),
        (12, 'Schulz', 'Marie', 'marie.schulz@example.de', '+4915211223344', 'Bergstraße 11', 90402, 'Nürnberg'),
        (13, 'Lang', 'Felix', 'felix.lang@example.de', '+491763334455', 'Parkallee 5', 44137, 'Dortmund')
    ]

    for kunde in kunden:
        cursor.execute('''
            INSERT OR REPLACE INTO kunde (ID, name, vorname, email, telefon, straße, plz, wohnort)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', kunde)
        conn.commit()
    print("✅ Kunden erfolgreich in die Datenbank eingefügt.")

def read_image(file_path):
    with open(file_path, 'rb') as file:
        return file.read()

def insert_default_auftrag(cursor, conn):
    # Auftragsdaten
    auftraege = [
        (1, 1, '2025-05-20', 0),
        (2, 2, '2025-05-18', 1),
        (3, 3, '2025-05-19', 0),
        (4, 4, '2025-05-17', 0),
        (5, 5, '2025-05-16', 2),
        (6, 6, '2025-05-15', 0)
    ]

    for auftrag in auftraege:
        cursor.execute('''INSERT OR REPLACE INTO auftrag (ID, kunden_ID, bestelldatum, status) VALUES (?, ?, ?, ?)''', auftrag)
        conn.commit()
    print("✅ Aufträge erfolgreich in die Datenbank eingefügt.")

def insert_default_auftragsposition(cursor, conn):
    cursor.execute('SELECT ID, preis FROM produkt')
    produkte = cursor.fetchall()

    if not produkte:
        print("❌ Keine Produkte gefunden!")
        conn.close()
        return

    # Auftragspositionen generieren
    auftragspositionen = []
    pos_id = 1
    for auftrag_id in range(1, 7):  # 6 Aufträge
        num_products = random.randint(1, 3)
        ausgewählte_produkte = random.sample(produkte, num_products)

        for produkt_id, preis in ausgewählte_produkte:
            auftragspositionen.append((
                pos_id,
                auftrag_id,
                produkt_id,
                1,                # Menge
                preis,            # Einzelpreis aus Produkt
                random.randint(0, 1)  # erledigt: 0 oder 1
            ))
            pos_id += 1

    for position in auftragspositionen:
        cursor.execute('''INSERT OR REPLACE INTO auftragsposition (ID, auftrag_ID, produkt_ID, menge, einzelpreis, erledigt) VALUES (?, ?, ?, ?, ?, ?)''', position)

    conn.commit()
    print("✅ Auftragspositionen erfolgreich in die Datenbank eingefügt.")



# ------ Datenbankabfragen ------
def read_job(cursor, id):
    cursor.execute('''SELECT * FROM auftrag WHERE ID = ?''', (id,))
    return cursor.fetchone()

def read_product(cursor, id):
    cursor.execute('''SELECT * FROM produkt WHERE ID = ?''', (id,))
    return cursor.fetchone()

def read_customer(cursor, id):
    cursor.execute('''SELECT * FROM kunde WHERE ID = ?''', (id,))
    return cursor.fetchone()

def read_auftragsposition(cursor, id):
    cursor.execute('''SELECT * FROM auftragsposition WHERE ID = ?''', (id,))
    return cursor.fetchone()

def get_auftragspositionen_by_auftrag_id(cursor, auftrag_id):
    cursor.execute('''SELECT * FROM auftragsposition WHERE auftrag_ID = ?''', (auftrag_id,))
    return cursor.fetchall()


if __name__ == "__main__":
    conn = connect_db()
    cursor = conn.cursor()
    create_db(cursor, conn)
    
    # --- Produkte ---
    # insert_default_produkte(cursor, conn)
    # produkt = read_product(cursor, 12401)
    # print(produkt)

    # --- Kunden ---
    # insert_default_kunde(cursor, conn)
    # kunde = read_customer(cursor, 1)
    # print(kunde)

    # --- Aufträge ---
    # insert_default_auftrag(cursor, conn)
    # auftrag = read_job(cursor, 1)
    # print(auftrag)
    
    # --- Auftragspositionen ---
    insert_default_auftragsposition(cursor, conn)
    # auftragsposition = read_auftragsposition(cursor, 1)
    # print(auftragsposition)

    # --- Auftragspositionen nach Auftrag ID ---
    auftragspositionen = get_auftragspositionen_by_auftrag_id(cursor, 1)
    for position in auftragspositionen:
        print(position)

    close_db(conn)