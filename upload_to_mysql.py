import mysql.connector as mysql
import json
from datetime import datetime

def upload_to_mysql(uex_service_data, mySqlConfig, table_name):
    mydb = mysql.connect(
        host=mySqlConfig['MYSQL_SERVER']['HOST'],
        user=mySqlConfig['MYSQL_USER']['USERNAME'],
        password=mySqlConfig['MYSQL_USER']['PASSWORD']
    )

    # Extrahiere die Daten aus dem 'data' Feld
    data = uex_service_data.get('data', [])
    
    # Falls data eine Liste ist, verarbeite jeden Eintrag
    if isinstance(data, list):
        process_data_list(data, mydb, mySqlConfig, table_name, True)
    else:
        # Falls data ein einzelnes Objekt ist
        process_single_data(data, mydb, mySqlConfig, table_name, True)
    
    mydb.close()

def upload_route_data(uex_route_data, mySqlConfig, table_name, firstRun):
    mydb = mysql.connect(
        host=mySqlConfig['MYSQL_SERVER']['HOST'],
        user=mySqlConfig['MYSQL_USER']['USERNAME'],
        password=mySqlConfig['MYSQL_USER']['PASSWORD']
    )

    data = uex_route_data.get('data', [])

    if firstRun:
        fullTableName = f"{mySqlConfig['MYSQL_SERVER']['DATABASE']}.{table_name}"
        clear_table_data(mydb, fullTableName)

    if isinstance(data, list):
        process_data_list(data, mydb, mySqlConfig, table_name, False)
    else:
        process_single_data(data, mydb, mySqlConfig, table_name, False)
    
def process_data_list(data_list, mydb, mySqlConfig, table_name, clearTable):
    """Verarbeitet eine Liste von Datenobjekten"""
    database = mySqlConfig['MYSQL_SERVER']['DATABASE']
    service_name = table_name
    full_table_name = f"{database}.{table_name}"
    
    mycursor = mydb.cursor()
    
    # Erstelle Tabelle mit id als Primärschlüssel
    mycursor.execute(f"CREATE TABLE IF NOT EXISTS {full_table_name} (id INT AUTO_INCREMENT PRIMARY KEY)")
    
    # Hole alle vorhandenen Spalten der Tabelle
    mycursor.execute(f"SHOW COLUMNS FROM {full_table_name}")
    existing_columns = [column[0] for column in mycursor.fetchall()]
    
    # Leere die Tabelle vor dem Einfügen neuer Daten (Überschreiben)
    if clearTable:
        clear_table_data(mydb, full_table_name)
    
    # Sammle alle möglichen Spalten aus allen Datenobjekten
    all_columns = set()
    for item in data_list:
        if isinstance(item, dict):
            all_columns.update(item.keys())
    
    # Erstelle dynamisch Felder basierend auf allen Daten
    for column_name in all_columns:
        if column_name not in existing_columns:
            # Bestimme den MySQL-Datentyp basierend auf dem ersten Wert
            column_type = determine_column_type(data_list, column_name)
            
            try:
                mycursor.execute(f"ALTER TABLE {full_table_name} ADD COLUMN {column_name} {column_type}")
                print(f"Spalte '{column_name}' ({column_type}) zur Tabelle '{service_name}' hinzugefügt")
            except mysql.Error as e:
                print(f"Fehler beim Hinzufügen der Spalte '{column_name}': {e}")
    
    # Füge alle Daten ein
    inserted_count = 0
    for item in data_list:
        if isinstance(item, dict):
            try:
                # Erstelle INSERT-Statement dynamisch
                columns = list(item.keys())
                placeholders = ', '.join(['%s'] * len(columns))
                column_names = ', '.join(columns)
                
                # Bereite Werte vor
                values = prepare_values(item, columns)
                
                # Führe INSERT aus
                insert_query = f"INSERT INTO {full_table_name} ({column_names}) VALUES ({placeholders})"
                mycursor.execute(insert_query, values)
                inserted_count += 1
                
            except mysql.Error as e:
                print(f"Fehler beim Einfügen von Daten: {e}")
    
    mydb.commit()
    mycursor.close()
    
    print(f"{inserted_count} Datensätze erfolgreich in Tabelle '{service_name}' eingefügt (Daten überschrieben)")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def process_single_data(data, mydb, mySqlConfig, table_name):
    """Verarbeitet ein einzelnes Datenobjekt"""
    database = mySqlConfig['MYSQL_SERVER']['DATABASE']
    service_name = table_name
    full_table_name = f"{database}.{table_name}"
    
    mycursor = mydb.cursor()
    
    # Erstelle Tabelle mit id als Primärschlüssel
    mycursor.execute(f"CREATE TABLE IF NOT EXISTS {full_table_name} (id INT AUTO_INCREMENT PRIMARY KEY)")
    
    # Hole alle vorhandenen Spalten der Tabelle
    mycursor.execute(f"SHOW COLUMNS FROM {full_table_name}")
    existing_columns = [column[0] for column in mycursor.fetchall()]
    
    # Leere die Tabelle vor dem Einfügen neuer Daten (Überschreiben)
    clear_table_data(mydb, full_table_name)
    
    if isinstance(data, dict):
        # Erstelle dynamisch Felder basierend auf den Daten
        for key, value in data.items():
            if key not in existing_columns:
                column_type = determine_single_column_type(value)
                
                try:
                    mycursor.execute(f"ALTER TABLE {full_table_name} ADD COLUMN {key} {column_type}")
                    print(f"Spalte '{key}' ({column_type}) zur Tabelle '{service_name}' hinzugefügt")
                except mysql.Error as e:
                    print(f"Fehler beim Hinzufügen der Spalte '{key}': {e}")
        
        # Erstelle INSERT-Statement dynamisch
        columns = list(data.keys())
        placeholders = ', '.join(['%s'] * len(columns))
        column_names = ', '.join(columns)
        
        # Bereite Werte vor
        values = prepare_values(data, columns)
        
        # Führe INSERT aus
        insert_query = f"INSERT INTO {full_table_name} ({column_names}) VALUES ({placeholders})"
        mycursor.execute(insert_query, values)
        
        mydb.commit()
        mycursor.close()
        
        print(f"Daten erfolgreich in Tabelle '{service_name}' eingefügt (Daten überschrieben)")

def clear_table_data(mydb, table_name):
    """Leert eine Tabelle ohne die Verbindung zu schließen"""
    cursor = mydb.cursor()
    
    try:
        # Zähle Zeilen vor dem Löschen
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        row_count = cursor.fetchone()[0]
        
        if row_count > 0:
            # Verwende TRUNCATE für bessere Performance (setzt AUTO_INCREMENT zurück)
            cursor.execute(f"TRUNCATE TABLE {table_name}")
            mydb.commit()
            print(f"Tabelle '{table_name}' geleert. {row_count} Zeilen gelöscht.")
        else:
            print(f"Tabelle '{table_name}' war bereits leer.")
            
    except mysql.Error as e:
        # Falls TRUNCATE fehlschlägt (z.B. wegen FOREIGN KEY Constraints), verwende DELETE
        try:
            cursor.execute(f"DELETE FROM {table_name}")
            mydb.commit()
            print(f"Tabelle '{table_name}' geleert. {row_count} Zeilen gelöscht (mit DELETE).")
        except mysql.Error as e2:
            print(f"Fehler beim Leeren der Tabelle: {e2}")
    
    cursor.close()

def determine_column_type(data_list, column_name):
    """Bestimmt den MySQL-Datentyp basierend auf allen Werten einer Spalte"""
    types_found = set()
    
    for item in data_list:
        if isinstance(item, dict) and column_name in item:
            value = item[column_name]
            if isinstance(value, int):
                types_found.add('int')
            elif isinstance(value, float):
                types_found.add('float')
            elif isinstance(value, bool):
                types_found.add('bool')
            elif isinstance(value, (dict, list)):
                types_found.add('json')
            else:
                types_found.add('text')
    
    # Priorisiere Datentypen
    if 'json' in types_found:
        return "JSON"
    elif 'float' in types_found:
        return "DECIMAL(15,2)"
    elif 'int' in types_found:
        return "INT"
    elif 'bool' in types_found:
        return "BOOLEAN"
    else:
        return "TEXT"

def determine_single_column_type(value):
    """Bestimmt den MySQL-Datentyp für einen einzelnen Wert"""
    if isinstance(value, int):
        return "INT"
    elif isinstance(value, float):
        return "DECIMAL(15,2)"
    elif isinstance(value, bool):
        return "BOOLEAN"
    elif isinstance(value, (dict, list)):
        return "JSON"
    else:
        return "TEXT"

def prepare_values(data_dict, columns):
    """Bereitet Werte für INSERT vor"""
    values = []
    for key in columns:
        value = data_dict.get(key)
        if isinstance(value, (dict, list)):
            values.append(json.dumps(value))
        else:
            values.append(value)
    return values