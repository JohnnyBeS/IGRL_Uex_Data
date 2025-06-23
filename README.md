# IGRL_Uex_Data

Ein Python-Tool zum automatischen Download und Speicherung von UEX (Universal Exchange) API-Daten in einer MySQL-Datenbank.

## 📋 Übersicht

Dieses Projekt lädt automatisch Daten von verschiedenen UEX-API-Endpunkten herunter und speichert sie in einer MySQL-Datenbank. Es unterstützt dynamische Tabellenerstellung, Routenberechnungen und umfassende Datenbankverwaltung.

## 🚀 Features

- **Automatischer API-Download**: Lädt Daten von mehreren UEX-Services
- **Dynamische Tabellenerstellung**: Erstellt MySQL-Tabellen automatisch basierend auf API-Daten
- **Routenberechnung**: Berechnet Handelsrouten für alle Commodities
- **Datenbankverwaltung**: Umfassende Tools zur Datenbankverwaltung und -analyse
- **Konfigurierbar**: Alle Einstellungen über INI-Dateien
- **Fehlerbehandlung**: Robuste Fehlerbehandlung und Logging

## 📁 Projektstruktur

```
IGRL_Uex_Data/
├── Config/
│   ├── config.ini              # API-Konfiguration
│   ├── mySql.ini               # MySQL-Verbindungsdaten
│   ├── tradeRoutes.ini         # Routenberechnung-Konfiguration
│   ├── status_buy.csv          # Kaufstatus-Definitionen
│   └── status_sell.csv         # Verkaufsstatus-Definitionen
├── main.py                     # Hauptprogramm
├── get_uex_data.py            # API-Download-Funktionen
├── upload_to_mysql.py         # MySQL-Upload-Funktionen
├── db_access.py               # Datenbankverwaltungstool
├── requirements.txt           # Python-Abhängigkeiten
└── README.md                  # Diese Datei
```

## ⚙️ Installation

### 1. Repository klonen
```bash
git clone <repository-url>
cd IGRL_Uex_Data
```

### 2. Virtuelle Umgebung erstellen
```bash
python -m venv venv
```

### 3. Virtuelle Umgebung aktivieren
```bash
# Windows
.\venv\Scripts\Activate.ps1

# Linux/Mac
source venv/bin/activate
```

### 4. Abhängigkeiten installieren
```bash
pip install -r requirements.txt
```

## 🔧 Konfiguration

### API-Konfiguration (`Config/config.ini`)
```ini
[api]
base_url = https://api.uexcorp.space/2.0/
services = commodities,space_stations,terminals,commodities_prices_all,vehicles,vehicles_prices,vehicles_purchases_prices,vehicles_rentals_prices
token = YOUR_API_TOKEN

[google_sheets]
api_key = YOUR_GOOGLE_SHEETS_API_KEY
sheetId = YOUR_SHEET_ID

[output]
resource_path = Resources
```

### MySQL-Konfiguration (`Config/mySql.ini`)
```ini
[MYSQL_SERVER]
HOST = localhost
PORT = 3306
DATABASE = your_database_name

[MYSQL_USER]
USERNAME = your_username
PASSWORD = your_password
```

### Routenberechnung (`Config/tradeRoutes.ini`)
```ini
[API]
SERVICE_TRIGGER = commodities
ENDPOINT = trade_routes

[PARAMETERS]
INVESTMENT = 1000000
```

## 🎯 Verwendung

### Hauptprogramm ausführen
```bash
python main.py
```

Das Hauptprogramm:
1. Lädt Daten von allen konfigurierten API-Services
2. Erstellt/aktualisiert MySQL-Tabellen dynamisch
3. Berechnet Handelsrouten für alle Commodities
4. Zeigt Ausführungszeit und Statistiken

### Datenbankverwaltung

#### Interaktiver Modus
```bash
python db_access.py interactive
```

#### Verfügbare Befehle:
```bash
# Tabellen anzeigen
python db_access.py tables

# Statistiken aller Tabellen
python db_access.py stats

# Datenbankübersicht
python db_access.py database

# Detaillierte Tabellenstatistiken
python db_access.py detailed <table_name>

# Tabellenstruktur anzeigen
python db_access.py structure <table_name>

# CREATE TABLE Statement anzeigen
python db_access.py create <table_name>

# Daten anzeigen
python db_access.py data <table_name> [limit]

# Tabelle leeren
python db_access.py clear <table_name>

# Alle Tabellen leeren
python db_access.py clear all

# Spalte hinzufügen
python db_access.py add <table> <column> <definition>

# Spalte ändern
python db_access.py modify <table> <column> <new_definition>

# Spalte entfernen
python db_access.py drop <table> <column>

# Spalte umbenennen
python db_access.py rename <table> <old_name> <new_name>

# Benutzerdefinierte SQL-Abfrage
python db_access.py query "SELECT * FROM table_name"
```

## 📊 Datenbankstatistiken

### Übersicht aller Tabellen
```bash
python db_access.py stats
```

**Beispiel-Ausgabe:**
```
Tabelle                    Datensätze   Größe (MB)   Index (MB)   Gesamt (MB)
-------------------------------------------------------------------------
commodities               150          2.45         0.12         2.57
vehicles                  89           1.23         0.08         1.31
space_stations            45           0.67         0.05         0.72
-------------------------------------------------------------------------
GESAMT                    284          4.35         0.25         4.60
```

### Detaillierte Tabellenstatistiken
```bash
python db_access.py detailed commodities
```

Zeigt umfassende Informationen über:
- Datensatzanzahl
- Tabellengröße (Daten + Index)
- Durchschnittliche Zeilengröße
- Erstellungs- und Update-Zeit
- AUTO_INCREMENT Werte
- Spaltenstruktur

## 🔄 Datenverarbeitung

### Dynamische Tabellenerstellung
Das System erstellt MySQL-Tabellen automatisch basierend auf den API-Daten:

- **Intelligente Datentypen**: INT, DECIMAL, BOOLEAN, JSON, TEXT
- **Automatische Spaltenerkennung**: Neue Felder werden automatisch hinzugefügt
- **Überschreiben**: Tabellen werden vor jedem Import geleert

### Unterstützte Datentypen
- `int` → `INT`
- `float` → `DECIMAL(15,2)`
- `bool` → `BOOLEAN`
- `dict/list` → `JSON`
- `string` → `TEXT`

## 🛠️ Entwicklung

### Projektstruktur erweitern
1. Neue API-Services in `config.ini` hinzufügen
2. Spezielle Verarbeitungslogik in `upload_to_mysql.py` implementieren
3. Neue Datenbankfunktionen in `db_access.py` hinzufügen

### Fehlerbehandlung
- Alle API-Aufrufe haben Try-Catch-Blöcke
- MySQL-Fehler werden abgefangen und protokolliert
- Verbindungsprobleme werden behandelt

## 📈 Performance

### Optimierungen
- **TRUNCATE** statt DELETE für bessere Performance
- **Batch-Inserts** für große Datenmengen
- **Dynamische Spaltenerkennung** für effiziente Speicherung
- **Einzelne Datenbankverbindungen** pro Operation

### Monitoring
- Ausführungszeit-Tracking
- Datensatzanzahl-Statistiken
- Tabellengröße-Monitoring
- Timestamp-Logging

## 🔒 Sicherheit

### Best Practices
- **Konfigurationsdateien** im `.gitignore`
- **Virtuelle Umgebung** für Isolation
- **Fehlerbehandlung** ohne sensible Daten
- **Bestätigung** für kritische Operationen

### Konfigurationsdateien
```
Config/*
```

## 📝 Logging

Das System protokolliert:
- API-Download-Versuche
- Datenbankoperationen
- Fehler und Ausnahmen
- Ausführungszeiten
- Datensatzanzahlen

## 🤝 Beitragen

1. Fork das Repository
2. Erstelle einen Feature-Branch
3. Implementiere deine Änderungen
4. Teste gründlich
5. Erstelle einen Pull Request

## 📄 Lizenz

Dieses Projekt ist für den privaten Gebrauch bestimmt.

## 🆘 Support

Bei Problemen oder Fragen:
1. Überprüfe die Konfigurationsdateien
2. Teste die Datenbankverbindung
3. Überprüfe die API-Token
4. Konsultiere die Logs

## 🔄 Updates

### Regelmäßige Updates
- API-Daten werden bei jedem Lauf aktualisiert
- Tabellenstrukturen werden automatisch angepasst
- Neue Felder werden dynamisch hinzugefügt

### Manuelle Updates
```bash
# Datenbankstatistiken aktualisieren
python db_access.py stats

# Spezifische Tabelle aktualisieren
python db_access.py clear <table_name>
python main.py
```