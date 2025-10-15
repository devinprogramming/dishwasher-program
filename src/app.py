"""
Flask-Webanwendung zur Verwaltung und Generierung von Reinigungsplänen sowie zur Bearbeitung von den beiliegenden CSV-Daten.

Dieses Skript stellt eine Admin-Oberfläche bereit, über die CSV-Dateien verwaltet werden können.
Es integriert eine automatische Reinigungsplan-Generierung unter Berücksichtigung von Feiertagen und Schulzeiten.

Hierfür müssen am Anfang von jedem Schuljahr die CSV-Dateien im /data/ Order über Excel oder der Web-Oberfläche ergänzt werden.

Hauptfunktionen:
- Generierung von Reinigungsplänen als HTML
- Verwaltung von CSV-Dateien
- Backup- und Wiederherstellungsmechanismen für CSV-Daten
- Bereitstellung eines Admin-Dashboards zur Steuerung

Autor: pascal.blum@nikoit.de
"""
from flask import Flask, render_template, request, jsonify, send_from_directory, redirect, url_for
import os
import pandas as pd
import shutil
from datetime import datetime
import json
import time
from generate_plan import CleaningDutyScheduler, HTMLExporter

app = Flask(__name__)
DATA_DIR = './data/'
BACKUP_DIR = './data/backups/'

if not os.path.exists(BACKUP_DIR):
    os.makedirs(BACKUP_DIR)

@app.route('/')
def index():
    """
    Stellt die Startseite mit dem Spühlmaschinenplan bereit.
    """
    return send_from_directory('static', 'Spühlmaschinenplan.html')

# Admin Dashboard
PAGES = {
    "plan_management": "Übersicht",
    "csv_management": "Management"
}

@app.route("/admin/")
def dashboard():
    """
    Lädt das Admin-Dashboard mit einer Auswahl an Verwaltungsseiten.
    """
    return render_template("dashboard.html", pages=PAGES, default_page='plan_management')

@app.route("/admin/page/<page>")
def page_content(page):
    """
    Lädt den Inhalt einer spezifischen Admin-Seite.
    """
    if page in PAGES:
        return render_template(f"{page}.html")
    return "Seite nicht gefunden", 404

@app.route('/admin/generate-plan', methods=['GET'])
def generate_plan():
    """
    Erstellt einen neuen Reinigungsplan für das aktuelle Schuljahr und speichert ihn als HTML.
    """
    azubis_file = "data/Azubis.csv"
    blockweeks_file = "data/Blockwochen_Schule.csv"
    holidays_file = "data/Feiertage_Schließzeiten_Brückentage.csv"
    
    scheduler = CleaningDutyScheduler(azubis_file, blockweeks_file, holidays_file)
    

    current_date = datetime.now().date()
    
    # Hier muss das Schuljahr rein z.B. 01.01.2025 -> 2024 | 10.10.2024 -> 2024 | 01.09.2024 -> 2025
    # get_school_year_start_end() gibt ein valides anfang und enddatum für das schuljahr zurück
    school_start, school_end = scheduler.get_school_year_start_end(current_date.year)
    if school_start <= current_date <= school_end:
        school_year = current_date.year
    else:
        school_year = current_date.year - 1

    current_year = school_year
    

    exporter = HTMLExporter()
    output_file = f"static/Spühlmaschinenplan.html"
    
    include_all_dates = True
    schedule = scheduler.generate_schedule(current_year, include_all_dates=include_all_dates)
    
    scheduler.save_schedule(schedule, exporter, output_file)
    
    stats = scheduler.generate_statistics(schedule)
    stats_file = f"static/statistics.json"
    
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    stats_with_timestamp = {
        "timestamp": timestamp,
        "data": stats
    }

    with open(stats_file, 'w') as f:
        json.dump(stats_with_timestamp, f, indent=4)
    
    return jsonify({
        "message": f"Plan für {current_year} generiert und als HTML gespeichert.",
        "statistics": stats
    })

@app.route('/admin/get-statistics', methods=['GET'])
def get_statistics():
    """
    Gibt die zuletzt berechneten Statistiken zum Reinigungsplan zurück.
    """
    stats_file = f"static/statistics.json"
    
    if os.path.exists(stats_file):
        with open(stats_file, 'r') as f:
            stats = json.load(f)
        return jsonify(stats)
    
    return jsonify({"error": "Statistiken nicht gefunden"}), 404


# Admin API
@app.route('/api/csv', methods=['GET'])
def list_csv_files():
    """
    Listet alle vorhandenen CSV-Dateien im Datenverzeichnis auf.
    """
    csv_files = [f for f in os.listdir(DATA_DIR) if f.endswith('.csv')]
    return jsonify(csv_files)

@app.route('/api/csv/<filename>', methods=['GET'])
def get_csv(filename):
    """
    Listet alle Zeilen in einer CSV-Datei auf.
    """
    filepath = os.path.join(DATA_DIR, filename)
    if os.path.exists(filepath):
        df = pd.read_csv(filepath, sep=';', dtype=str).fillna('')
        return jsonify({"columns": df.columns.tolist(), "data": df.to_dict(orient='records')})
    return jsonify({"error": "Datei nicht gefunden"}), 404

@app.route('/api/csv/<filename>/meta', methods=['GET'])
def get_csv_metadata(filename):
    """
    Liest die Metadaten für eine CSV-Datei aus.
    """
    meta_filepath = os.path.join(DATA_DIR, f"{filename}.json")
    if os.path.exists(meta_filepath):
        with open(meta_filepath, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        return jsonify(metadata)
    return jsonify({"error": "Metadaten nicht gefunden"}), 404

@app.route('/api/csv/<filename>/update', methods=['POST'])
def update_csv(filename):
    """
    Bearbeitet eine Zeile aus einer CSV-Datei.
    """
    data = request.json
    df = pd.read_csv(os.path.join(DATA_DIR, filename), sep=';', dtype=str)
    df.iloc[data['index'], df.columns.get_loc(data['column'])] = data['value']
    df.to_csv(os.path.join(DATA_DIR, filename), sep=';', index=False)
    return jsonify({"success": True})

@app.route('/api/csv/<filename>/delete', methods=['POST'])
def delete_row(filename):
    """
    Löscht eine Zeile aus einer CSV-Datei.
    """
    data = request.json
    df = pd.read_csv(os.path.join(DATA_DIR, filename), sep=';', dtype=str)
    df = df.drop(index=data['index']).reset_index(drop=True)
    df.to_csv(os.path.join(DATA_DIR, filename), sep=';', index=False)
    return jsonify({"success": True})

@app.route('/api/csv/<filename>/reorder', methods=['POST'])
def reorder_csv(filename):
    """
    Ändert die Reihenfolge einer Zeile einer CSV-Datei.
    """
    order = request.json['order']
    df = pd.read_csv(os.path.join(DATA_DIR, filename), sep=';', dtype=str)
    df = df.reindex(order).reset_index(drop=True)
    df.to_csv(os.path.join(DATA_DIR, filename), sep=';', index=False)
    return jsonify({"success": True})

@app.route('/api/csv/<filename>/add', methods=['POST'])
def add_row(filename):
    """
    Fügt eine Zeile in einer CSV-Datei hinzu.
    """
    df = pd.read_csv(os.path.join(DATA_DIR, filename), sep=';', dtype=str)
    new_row = {col: "" for col in df.columns}
    new_df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    new_df.to_csv(os.path.join(DATA_DIR, filename), sep=';', index=False)
    return jsonify({"success": True})


@app.route('/api/backups', methods=['GET'])
def list_backups():
    """
    Listet alle Backups auf.
    """
    backups = [f for f in os.listdir(BACKUP_DIR) if f.endswith('.csv')]
    backups.sort(reverse = True)
    return jsonify(backups)

@app.route('/api/backups/create', methods=['POST'])
def create_backup():
    """
    Erstellt vom jetzigen Stand ein Backup.
    """
    for filename in os.listdir(DATA_DIR):
        if filename.endswith('.csv'):
            timestamp = datetime.now().strftime('%Y.%m.%d_%H-%M-%S')
            backup_name = f"{timestamp}___{filename}"
            shutil.copy(os.path.join(DATA_DIR, filename), os.path.join(BACKUP_DIR, backup_name))
    prune_backups()
    return jsonify({"success": True})

@app.route('/api/backups/restore', methods=['POST'])
def restore_backup():
    """
    Stellt ein Backup wieder her.
    """
    data = request.get_json()
    backup_name = data.get('backup')
    original_name = '___'.join(backup_name.split('___')[1:])
    shutil.copy(os.path.join(BACKUP_DIR, backup_name), os.path.join(DATA_DIR, original_name))
    return jsonify({"success": True})

def prune_backups(days=30):
    """
    Löscht Backups, die älter als die angegebene Anzahl von Tagen sind.
    """
    print(f"Folgende alte backups wurden nach {days} Tagen gelöscht." )
    cutoff_time = time.time() - (days * 86400)
    for filename in os.listdir(BACKUP_DIR):
        if filename.endswith('.csv'):
            file_path = os.path.join(BACKUP_DIR, filename)
            if os.path.isfile(file_path) and os.stat(file_path).st_mtime < cutoff_time:
                os.remove(file_path)
                print(f"  {file_path} gelöscht")

if __name__ == '__main__':
    app.run(debug=True)
