import mysql.connector as mysql
from configparser import ConfigParser
import json

def load_mysql_config():
    mysql_config = ConfigParser()
    mysql_config.read('Config/mySql.ini')
    return mysql_config

def connect_to_db():
    """Verbindung zur Datenbank herstellen"""
    mysql_config = load_mysql_config()
    
    mydb = mysql.connect(
        host=mysql_config['MYSQL_SERVER']['HOST'],
        port=int(mysql_config['MYSQL_SERVER']['PORT']),
        user=mysql_config['MYSQL_USER']['USERNAME'],
        password=mysql_config['MYSQL_USER']['PASSWORD'],
        database=mysql_config['MYSQL_SERVER']['DATABASE']
    )
    return mydb

def show_tables():
    """Alle Tabellen anzeigen"""
    mydb = connect_to_db()
    cursor = mydb.cursor()
    
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()
    
    print("Verfügbare Tabellen:")
    for table in tables:
        print(f"- {table[0]}")
    
    cursor.close()
    mydb.close()

def show_table_stats():
    """Zeigt Statistiken für alle Tabellen an (Anzahl Datensätze und Größe)"""
    mydb = connect_to_db()
    cursor = mydb.cursor()
    
    try:
        # Hole alle Tabellen
        cursor.execute("SHOW TABLES")
        tables = [table[0] for table in cursor.fetchall()]
        
        if not tables:
            print("Keine Tabellen gefunden.")
            return
        
        print(f"\n{'Tabelle':<25} {'Datensätze':<12} {'Größe (MB)':<12} {'Index (MB)':<12} {'Gesamt (MB)':<12}")
        print("-" * 85)
        
        total_rows = 0
        total_data_size = 0
        total_index_size = 0
        
        for table in tables:
            # Hole Tabellenstatistiken
            cursor.execute(f"""
                SELECT 
                    TABLE_ROWS,
                    ROUND(((DATA_LENGTH + INDEX_LENGTH) / 1024 / 1024), 2) AS 'Total_MB',
                    ROUND((DATA_LENGTH / 1024 / 1024), 2) AS 'Data_MB',
                    ROUND((INDEX_LENGTH / 1024 / 1024), 2) AS 'Index_MB'
                FROM information_schema.TABLES 
                WHERE TABLE_SCHEMA = DATABASE() 
                AND TABLE_NAME = '{table}'
            """)
            
            result = cursor.fetchone()
            if result:
                rows, total_mb, data_mb, index_mb = result
                
                # Falls TABLE_ROWS NULL ist, zähle manuell
                if rows is None:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    rows = cursor.fetchone()[0]
                
                print(f"{table:<25} {rows:<12} {data_mb:<12} {index_mb:<12} {total_mb:<12}")
                
                total_rows += rows if rows else 0
                total_data_size += data_mb if data_mb else 0
                total_index_size += index_mb if index_mb else 0
        
        print("-" * 85)
        print(f"{'GESAMT':<25} {total_rows:<12} {total_data_size:<12} {total_index_size:<12} {total_data_size + total_index_size:<12}")
        
    except mysql.Error as e:
        print(f"Fehler beim Abrufen der Tabellenstatistiken: {e}")
    
    cursor.close()
    mydb.close()

def show_detailed_table_stats(table_name):
    """Zeigt detaillierte Statistiken für eine spezifische Tabelle"""
    mydb = connect_to_db()
    cursor = mydb.cursor()
    
    try:
        # Prüfe ob Tabelle existiert
        cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
        if not cursor.fetchone():
            print(f"Tabelle '{table_name}' nicht gefunden.")
            return
        
        # Hole detaillierte Tabellenstatistiken
        cursor.execute(f"""
            SELECT 
                TABLE_NAME,
                TABLE_ROWS,
                ROUND(((DATA_LENGTH + INDEX_LENGTH) / 1024 / 1024), 2) AS 'Total_MB',
                ROUND((DATA_LENGTH / 1024 / 1024), 2) AS 'Data_MB',
                ROUND((INDEX_LENGTH / 1024 / 1024), 2) AS 'Index_MB',
                ROUND((DATA_LENGTH / 1024), 2) AS 'Data_KB',
                ROUND((INDEX_LENGTH / 1024), 2) AS 'Index_KB',
                AVG_ROW_LENGTH,
                MAX_DATA_LENGTH,
                AUTO_INCREMENT,
                CREATE_TIME,
                UPDATE_TIME,
                TABLE_COMMENT
            FROM information_schema.TABLES 
            WHERE TABLE_SCHEMA = DATABASE() 
            AND TABLE_NAME = '{table_name}'
        """)
        
        result = cursor.fetchone()
        if result:
            (table_name, table_rows, total_mb, data_mb, index_mb, 
             data_kb, index_kb, avg_row_length, max_data_length, 
             auto_increment, create_time, update_time, table_comment) = result
            
            # Falls TABLE_ROWS NULL ist, zähle manuell
            if table_rows is None:
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                table_rows = cursor.fetchone()[0]
            
            print(f"\nDetaillierte Statistiken für Tabelle '{table_name}':")
            print("=" * 60)
            print(f"Datensätze:           {table_rows:,}")
            print(f"Gesamtgröße:          {total_mb} MB ({total_mb * 1024:.0f} KB)")
            print(f"Daten:                {data_mb} MB ({data_kb} KB)")
            print(f"Index:                {index_mb} MB ({index_kb} KB)")
            print(f"Durchschnittl. Zeile: {avg_row_length} Bytes")
            if max_data_length:
                print(f"Max. Datenlänge:      {max_data_length:,} Bytes")
            if auto_increment:
                print(f"AUTO_INCREMENT:       {auto_increment:,}")
            if create_time:
                print(f"Erstellt:             {create_time}")
            if update_time:
                print(f"Zuletzt aktualisiert: {update_time}")
            if table_comment:
                print(f"Kommentar:            {table_comment}")
            
            # Hole Spaltenstatistiken
            cursor.execute(f"SHOW COLUMNS FROM {table_name}")
            columns = cursor.fetchall()
            
            print(f"\nSpalten ({len(columns)}):")
            print("-" * 60)
            print(f"{'Spalte':<20} {'Typ':<20} {'Null':<8} {'Key':<8} {'Default':<15}")
            print("-" * 60)
            for column in columns:
                col_name, col_type, nullable, key, default, extra = column
                default_str = str(default) if default is not None else "NULL"
                print(f"{col_name:<20} {col_type:<20} {nullable:<8} {key:<8} {default_str:<15}")
        
    except mysql.Error as e:
        print(f"Fehler beim Abrufen der Tabellenstatistiken: {e}")

    cursor.close()
    mydb.close()

def show_database_stats():
    """Zeigt allgemeine Datenbankstatistiken"""
    mydb = connect_to_db()
    cursor = mydb.cursor()
    
    try:
        # Hole Datenbankstatistiken
        cursor.execute("""
            SELECT 
                SCHEMA_NAME,
                ROUND(SUM(((DATA_LENGTH + INDEX_LENGTH) / 1024 / 1024)), 2) AS 'Total_MB',
                ROUND(SUM((DATA_LENGTH / 1024 / 1024)), 2) AS 'Data_MB',
                ROUND(SUM((INDEX_LENGTH / 1024 / 1024)), 2) AS 'Index_MB',
                COUNT(TABLE_NAME) AS 'Table_Count'
            FROM information_schema.TABLES 
            WHERE TABLE_SCHEMA = DATABASE()
            GROUP BY SCHEMA_NAME
        """)
        
        result = cursor.fetchone()
        if result:
            schema_name, total_mb, data_mb, index_mb, table_count = result
            
            print(f"\nDatenbankstatistiken für '{schema_name}':")
            print("=" * 50)
            print(f"Anzahl Tabellen:      {table_count}")
            print(f"Gesamtgröße:          {total_mb} MB")
            print(f"Daten:                {data_mb} MB")
            print(f"Index:                {index_mb} MB")
            
            # Hole Zeilenanzahl für alle Tabellen
            cursor.execute("SHOW TABLES")
            tables = [table[0] for table in cursor.fetchall()]
            
            total_rows = 0
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                rows = cursor.fetchone()[0]
                total_rows += rows
            
            print(f"Gesamte Datensätze:   {total_rows:,}")
            
    except mysql.Error as e:
        print(f"Fehler beim Abrufen der Datenbankstatistiken: {e}")
    
    cursor.close()
    mydb.close()

def show_table_structure(table_name):
    """Struktur einer Tabelle anzeigen"""
    mydb = connect_to_db()
    cursor = mydb.cursor()
    
    cursor.execute(f"DESCRIBE {table_name}")
    columns = cursor.fetchall()
    
    print(f"\nStruktur der Tabelle '{table_name}':")
    print("Spalte\t\tTyp\t\tNull\tKey\tDefault")
    print("-" * 60)
    for column in columns:
        print(f"{column[0]}\t\t{column[1]}\t\t{column[2]}\t{column[3]}\t{column[4]}")
    
    cursor.close()
    mydb.close()

def show_create_table(table_name):
    """CREATE TABLE Statement einer Tabelle anzeigen"""
    mydb = connect_to_db()
    cursor = mydb.cursor()
    
    cursor.execute(f"SHOW CREATE TABLE {table_name}")
    result = cursor.fetchone()
    
    print(f"\nCREATE TABLE Statement für '{table_name}':")
    print("-" * 80)
    print(result[1])
    
    cursor.close()
    mydb.close()

def modify_table_column(table_name, column_name, new_definition):
    """Spalte einer Tabelle ändern"""
    mydb = connect_to_db()
    cursor = mydb.cursor()
    
    try:
        query = f"ALTER TABLE {table_name} MODIFY COLUMN {column_name} {new_definition}"
        cursor.execute(query)
        mydb.commit()
        print(f"Spalte '{column_name}' in Tabelle '{table_name}' erfolgreich geändert.")
        print(f"Neue Definition: {new_definition}")
    except mysql.Error as e:
        print(f"Fehler beim Ändern der Spalte: {e}")
    
    cursor.close()
    mydb.close()

def add_table_column(table_name, column_name, column_definition):
    """Neue Spalte zu einer Tabelle hinzufügen"""
    mydb = connect_to_db()
    cursor = mydb.cursor()
    
    try:
        query = f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_definition}"
        cursor.execute(query)
        mydb.commit()
        print(f"Spalte '{column_name}' erfolgreich zur Tabelle '{table_name}' hinzugefügt.")
    except mysql.Error as e:
        print(f"Fehler beim Hinzufügen der Spalte: {e}")
    
    cursor.close()
    mydb.close()

def drop_table_column(table_name, column_name):
    """Spalte aus einer Tabelle entfernen"""
    mydb = connect_to_db()
    cursor = mydb.cursor()
    
    try:
        query = f"ALTER TABLE {table_name} DROP COLUMN {column_name}"
        cursor.execute(query)
        mydb.commit()
        print(f"Spalte '{column_name}' erfolgreich aus Tabelle '{table_name}' entfernt.")
    except mysql.Error as e:
        print(f"Fehler beim Entfernen der Spalte: {e}")
    
    cursor.close()
    mydb.close()

def rename_table_column(table_name, old_column_name, new_column_name):
    """Spalte umbenennen"""
    mydb = connect_to_db()
    cursor = mydb.cursor()
    
    try:
        # Hole die aktuelle Definition der Spalte
        cursor.execute(f"SHOW COLUMNS FROM {table_name} LIKE '{old_column_name}'")
        column_info = cursor.fetchone()
        
        if column_info:
            column_type = column_info[1]
            is_nullable = "NULL" if column_info[2] == "YES" else "NOT NULL"
            default_value = f"DEFAULT {column_info[4]}" if column_info[4] else ""
            
            query = f"ALTER TABLE {table_name} CHANGE COLUMN {old_column_name} {new_column_name} {column_type} {is_nullable} {default_value}"
            cursor.execute(query)
            mydb.commit()
            print(f"Spalte '{old_column_name}' erfolgreich zu '{new_column_name}' umbenannt.")
        else:
            print(f"Spalte '{old_column_name}' nicht gefunden.")
    except mysql.Error as e:
        print(f"Fehler beim Umbenennen der Spalte: {e}")
    
    cursor.close()
    mydb.close()

def show_table_data(table_name, limit=10):
    """Daten einer Tabelle anzeigen"""
    mydb = connect_to_db()
    cursor = mydb.cursor()
    
    cursor.execute(f"SELECT * FROM {table_name} LIMIT {limit}")
    rows = cursor.fetchall()
    
    if rows:
        # Spaltennamen holen
        cursor.execute(f"SHOW COLUMNS FROM {table_name}")
        columns = [column[0] for column in cursor.fetchall()]
        
        print(f"\nDaten aus Tabelle '{table_name}' (max. {limit} Zeilen):")
        print(" | ".join(columns))
        print("-" * (len(" | ".join(columns))))
        
        for row in rows:
            formatted_row = []
            for value in row:
                if isinstance(value, str) and len(value) > 50:
                    formatted_row.append(value[:47] + "...")
                else:
                    formatted_row.append(str(value))
            print(" | ".join(formatted_row))
    else:
        print(f"Tabelle '{table_name}' ist leer.")
    
    cursor.close()
    mydb.close()

def clear_table(table_name):
    """Alle Daten aus einer Tabelle löschen"""
    mydb = connect_to_db()
    cursor = mydb.cursor()
    
    try:
        # Zähle Zeilen vor dem Löschen
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        row_count = cursor.fetchone()[0]
        
        cursor.execute(f"DELETE FROM {table_name}")
        mydb.commit()
        
        print(f"Tabelle '{table_name}' geleert. {row_count} Zeilen gelöscht.")
    except mysql.Error as e:
        print(f"Fehler beim Leeren der Tabelle: {e}")
    
    cursor.close()
    mydb.close()

def clear_all_tables():
    """Alle Daten aus allen Tabellen löschen"""
    mydb = connect_to_db()
    cursor = mydb.cursor()
    
    try:
        # Hole alle Tabellen
        cursor.execute("SHOW TABLES")
        tables = [table[0] for table in cursor.fetchall()]
        
        if not tables:
            print("Keine Tabellen gefunden.")
            return
        
        print(f"Warnung: Dies wird alle Daten aus {len(tables)} Tabellen löschen!")
        confirm = input("Sind Sie sicher? (yes/no): ")
        
        if confirm.lower() == 'yes':
            total_deleted = 0
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                row_count = cursor.fetchone()[0]
                cursor.execute(f"DELETE FROM {table}")
                total_deleted += row_count
                print(f"Tabelle '{table}': {row_count} Zeilen gelöscht")
            
            mydb.commit()
            print(f"\nAlle Tabellen geleert. Insgesamt {total_deleted} Zeilen gelöscht.")
        else:
            print("Vorgang abgebrochen.")
    except mysql.Error as e:
        print(f"Fehler beim Leeren der Tabellen: {e}")
    
    cursor.close()
    mydb.close()

def execute_custom_query(query):
    """Benutzerdefinierte SQL-Abfrage ausführen"""
    mydb = connect_to_db()
    cursor = mydb.cursor()
    
    try:
        cursor.execute(query)
        
        if query.strip().upper().startswith('SELECT'):
            rows = cursor.fetchall()
            if rows:
                # Spaltennamen holen
                columns = [desc[0] for desc in cursor.description]
                print(f"\nErgebnis ({len(rows)} Zeilen):")
                print(" | ".join(columns))
                print("-" * (len(" | ".join(columns))))
                
                for row in rows:
                    formatted_row = []
                    for value in row:
                        if isinstance(value, str) and len(value) > 50:
                            formatted_row.append(value[:47] + "...")
                        else:
                            formatted_row.append(str(value))
                    print(" | ".join(formatted_row))
            else:
                print("Keine Daten gefunden.")
        else:
            mydb.commit()
            print(f"Abfrage erfolgreich ausgeführt. {cursor.rowcount} Zeilen betroffen.")
            
    except mysql.Error as e:
        print(f"Fehler bei der Abfrage: {e}")
    
    cursor.close()
    mydb.close()

def interactive_mode():
    """Interaktiver Modus für SQL-Abfragen"""
    print("Interaktiver MySQL-Zugriff")
    print("Geben Sie 'quit' ein, um zu beenden")
    print("Geben Sie 'help' ein, für verfügbare Befehle")
    
    while True:
        try:
            command = input("\nmysql> ").strip()
            
            if command.lower() == 'quit':
                break
            elif command.lower() == 'help':
                print("Verfügbare Befehle:")
                print("- show tables")
                print("- show stats")
                print("- show database")
                print("- show detailed <table_name>")
                print("- describe <table_name>")
                print("- show create <table_name>")
                print("- select * from <table_name> limit 10")
                print("- clear table <table_name>")
                print("- clear all tables")
                print("- modify column <table> <column> <new_definition>")
                print("- add column <table> <column> <definition>")
                print("- drop column <table> <column>")
                print("- rename column <table> <old_name> <new_name>")
                print("- <beliebige SQL-Abfrage>")
                print("- quit")
            elif command.lower() == 'show tables':
                show_tables()
            elif command.lower() == 'show stats':
                show_table_stats()
            elif command.lower() == 'show database':
                show_database_stats()
            elif command.lower().startswith('show detailed '):
                table_name = command.split(' ', 2)[2]
                show_detailed_table_stats(table_name)
            elif command.lower().startswith('describe '):
                table_name = command.split(' ', 1)[1]
                show_table_structure(table_name)
            elif command.lower().startswith('show create '):
                table_name = command.split(' ', 2)[2]
                show_create_table(table_name)
            elif command.lower().startswith('clear table '):
                table_name = command.split(' ', 2)[2]
                clear_table(table_name)
            elif command.lower() == 'clear all tables':
                clear_all_tables()
            elif command.lower().startswith('modify column '):
                parts = command.split(' ', 3)
                if len(parts) >= 4:
                    modify_table_column(parts[2], parts[3], parts[4])
                else:
                    print("Verwendung: modify column <table> <column> <new_definition>")
            elif command.lower().startswith('add column '):
                parts = command.split(' ', 3)
                if len(parts) >= 4:
                    add_table_column(parts[2], parts[3], parts[4])
                else:
                    print("Verwendung: add column <table> <column> <definition>")
            elif command.lower().startswith('drop column '):
                parts = command.split(' ', 3)
                if len(parts) >= 3:
                    drop_table_column(parts[2], parts[3])
                else:
                    print("Verwendung: drop column <table> <column>")
            elif command.lower().startswith('rename column '):
                parts = command.split(' ', 4)
                if len(parts) >= 4:
                    rename_table_column(parts[2], parts[3], parts[4])
                else:
                    print("Verwendung: rename column <table> <old_name> <new_name>")
            elif command.lower().startswith('select ') and 'from ' in command.lower():
                execute_custom_query(command)
            elif command:
                execute_custom_query(command)
                
        except KeyboardInterrupt:
            print("\nBeendet.")
            break
        except Exception as e:
            print(f"Fehler: {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "tables":
            show_tables()
        elif command == "stats":
            show_table_stats()
        elif command == "database":
            show_database_stats()
        elif command == "detailed" and len(sys.argv) > 2:
            show_detailed_table_stats(sys.argv[2])
        elif command == "structure" and len(sys.argv) > 2:
            show_table_structure(sys.argv[2])
        elif command == "create" and len(sys.argv) > 2:
            show_create_table(sys.argv[2])
        elif command == "data" and len(sys.argv) > 2:
            limit = int(sys.argv[3]) if len(sys.argv) > 3 else 10
            show_table_data(sys.argv[2], limit)
        elif command == "clear" and len(sys.argv) > 2:
            if sys.argv[2] == "all":
                clear_all_tables()
            else:
                clear_table(sys.argv[2])
        elif command == "modify" and len(sys.argv) > 4:
            modify_table_column(sys.argv[2], sys.argv[3], sys.argv[4])
        elif command == "add" and len(sys.argv) > 4:
            add_table_column(sys.argv[2], sys.argv[3], sys.argv[4])
        elif command == "drop" and len(sys.argv) > 3:
            drop_table_column(sys.argv[2], sys.argv[3])
        elif command == "rename" and len(sys.argv) > 4:
            rename_table_column(sys.argv[2], sys.argv[3], sys.argv[4])
        elif command == "query" and len(sys.argv) > 2:
            execute_custom_query(sys.argv[2])
        elif command == "interactive":
            interactive_mode()
        else:
            print("Verwendung:")
            print("python db_access.py tables")
            print("python db_access.py stats")
            print("python db_access.py database")
            print("python db_access.py detailed <table_name>")
            print("python db_access.py structure <table_name>")
            print("python db_access.py create <table_name>")
            print("python db_access.py data <table_name> [limit]")
            print("python db_access.py clear <table_name>")
            print("python db_access.py clear all")
            print("python db_access.py modify <table> <column> <new_definition>")
            print("python db_access.py add <table> <column> <definition>")
            print("python db_access.py drop <table> <column>")
            print("python db_access.py rename <table> <old_name> <new_name>")
            print("python db_access.py query \"SELECT * FROM table_name\"")
            print("python db_access.py interactive")
    else:
        interactive_mode() 