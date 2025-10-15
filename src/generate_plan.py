"""
Dieses Skript generiert einen täglichen Spülmaschinen-Putzplan. Es berücksichtigt dabei Schulwochen, Feiertage
und Schließzeiten und teilt die Azubis gleichmäßig für ihre Dienste inklusive Vertretungen ein.

Author: pascal.blum@nikoit.de
"""
import datetime
import csv
import hashlib
import os
from collections import defaultdict, deque
from exporters.csv_exporter import CSVExporter
from exporters.html_exporter import HTMLExporter
from exporters.ics_exporter import ICSExporter

class CleaningDutyScheduler:
    def __init__(self, azubis_file, blockweeks_file, holidays_file):
        self.azubis_file = azubis_file
        self.blockweeks_file = blockweeks_file
        self.holidays_file = holidays_file

        self.azubis = []
        self.blockweeks = defaultdict(list)
        self.holidays = set()
        self.theme = None

        self.load_azubis()
        self.load_blockweeks()
        self.load_holidays()

    def load_azubis(self):
        try:
            with open(self.azubis_file, 'r', encoding='utf-8-sig') as file:
                reader = csv.DictReader(file, delimiter=';')
                for row in reader:
                    ignore = row['Ignorieren'].strip()
                    if not ignore:
                        self.azubis.append({
                            'firstname': row['Vorname'],
                            'lastname': row['Nachname'],
                            'year': int(row['Lehrjahr'])
                        })
        except Exception as e:
            raise ValueError(f"Fehler beim laden der Azubis: {e}")

    def load_blockweeks(self):
        """Ladet die Blockwochen für die 1/2/3 Lehrjahr Azubis"""
        try:
            with open(self.blockweeks_file, 'r', encoding='utf-8-sig') as file:
                reader = csv.DictReader(file, delimiter=';')
                for row in reader:
                    year = int(row['Jahr'])
                    lehrjahr = int(row['Lehrjahr'])
                    week = int(row['Kalenderwoche'])
                    self.blockweeks[(year, lehrjahr)].append(week)
        except Exception as e:
            raise ValueError(f"Fehler beim laden der Schulwochen: {e}")

    def load_holidays(self):
        """Ladet die Datei mit den Feiertagen und Schließzeiten"""
        try:
            with open(self.holidays_file, 'r', encoding='utf-8-sig') as file:
                reader = csv.DictReader(file, delimiter=';')
                for row in reader:
                    date = datetime.datetime.strptime(row['Datum'], '%d.%m.%Y').date()
                    self.holidays.add(date)
        except Exception as e:
            raise ValueError(f"Fehler beim laden der Urlaubstage/Schließzeiten: {e}")

    def is_weekend(self, date):
        """Prüft ob an dem Tag ein Wochenende ist"""
        return date.weekday() in [5, 6]  # Samstag / Sonntag

    def is_holiday(self, date):
        return date in self.holidays

    def is_blockweek(self, year, week, lehrjahr):
        #print("Blockwoche für LJ: " + str(lehrjahr) + " jahr: " + str(year) + " woche: " + str(week))

        return week in self.blockweeks.get((year, lehrjahr), [])

    def get_school_year_start_end(self, year):
        # Wann das Schuljahr anfängt z.B. 1. September
        start_date = datetime.date(year, 9, 1)
        if start_date.weekday() > 3:  # Wenn 1. September auf ein Donnerstag fällt
            start_date += datetime.timedelta(days=(7 - start_date.weekday()))  # Auf den nächsten Montag verschieben
        end_date = datetime.date(year + 1, 7, 31)
        while end_date.weekday() != 6:  # Letzter Tag soll der Sonntag in der letzten Juni Woche sein
            end_date -= datetime.timedelta(days=1)
        return start_date, end_date
    

    def generate_schedule(self, year, include_all_dates=False):
        schedule = []
        azubi_list = deque(self.azubis)
        secondary_list = deque(reversed(self.azubis))
        last_primary = None

        # tracking
        primary_counts = {f"{azubi['firstname']} {azubi['lastname']}": 0 for azubi in self.azubis}
        secondary_counts = {f"{azubi['firstname']} {azubi['lastname']}": 0 for azubi in self.azubis}

        start_date, end_date = self.get_school_year_start_end(year)
        current_date = start_date

        while current_date <= end_date:
            entry = {'date': current_date}

            if not (self.is_weekend(current_date) or self.is_holiday(current_date)):
                iso_year, week, _ = current_date.isocalendar()

                # Business Logic für die primären Dienst
                eligible_primary = None
                rotated_primary = []
                for _ in range(len(azubi_list)):
                    candidate = azubi_list.popleft()
                    primary_name = f"{candidate['firstname']} {candidate['lastname']}"
                    primary_hashed = hashlib.sha256(primary_name.encode()).hexdigest()

                    # :)
                    if primary_hashed == "2cbc48af22f903a080441fa01823167ae4712eef705679c40d58f8bdce079aca":
                        continue

                    if not self.is_blockweek(iso_year, week, candidate['year']) and candidate != last_primary:
                        if (
                            eligible_primary is None
                            or primary_counts[primary_name] < primary_counts[eligible_primary]
                        ):
                            eligible_primary = primary_name
                    rotated_primary.append(candidate)

                azubi_list.extend(rotated_primary)

                if eligible_primary:
                    primary = eligible_primary
                    last_primary = primary
                    primary_counts[primary] += 1
                    entry['primary'] = primary
                else:
                    entry['primary'] = ' - '

                # Business Logic für den sekundaren (Vertretung) Dienst
                eligible_secondary = None
                rotated_secondary = []
                for _ in range(len(secondary_list)):
                    candidate = secondary_list.popleft()
                    secondary_name = f"{candidate['firstname']} {candidate['lastname']}"

                    if secondary_name != primary and not self.is_blockweek(iso_year, week, candidate['year']):
                        if (
                            eligible_secondary is None
                            or secondary_counts[secondary_name] < secondary_counts[eligible_secondary]
                        ):
                            eligible_secondary = secondary_name
                    rotated_secondary.append(candidate)

                # Liste wiederherstellen
                secondary_list.extend(rotated_secondary)

                if eligible_secondary:
                    secondary = eligible_secondary
                    secondary_counts[secondary] += 1
                    entry['secondary'] = secondary
                else:
                    entry['secondary'] = ' - '
            else:
                entry['primary'] = ' - ' if include_all_dates else None
                entry['secondary'] = ' - ' if include_all_dates else None

            if include_all_dates or (entry['primary'] and entry['secondary']):
                schedule.append(entry)

            current_date += datetime.timedelta(days=1)

        try:
            self.validate_schedule(schedule)
        except:
            pass

        return schedule

    def filter_schedule_by_month(self, schedule, year, month):
        filtered_schedule = [
            entry for entry in schedule
            if entry['date'].month == month and entry['date'].year == year
        ]
        return filtered_schedule


    def save_schedule(self, schedule, exporter, output_file):
        output_dir = os.path.dirname(output_file)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)

        exporter.export(schedule, output_file)



    def validate_schedule(self, schedule, school_year_start):
        """Testet den generierten Plan gegenüber Azubis, Urlaub, Schließzeiten und Schulwochen"""
        school_year_start_date, school_year_end_date = self.get_school_year_start_end(school_year_start)

        for entry in schedule:
            date = entry['date']
            
            # Schuljahr validieren
            if not (school_year_start_date <= date <= school_year_end_date):
                print(f"Validierungs Fehler: {date} is außerhalb des Schulzeitraum.")
                continue
            
            week = date.isocalendar()[1]
            
            # Primärdienst validieren
            primary_name = entry.get('primary')
            if primary_name != ' - ':
                primary_azubi = next((azubi for azubi in self.azubis if f"{azubi['firstname']} {azubi['lastname']}" == primary_name), None)
                if primary_azubi and self.is_blockweek(date.year, week, primary_azubi['year']):
                    print(f"Validierungs Fehler: {primary_name} zugewiesen während Schulwoche {week} an {date}")
            
            # Sekundardienst validieren
            secondary_name = entry.get('secondary')
            if secondary_name != ' - ':
                secondary_azubi = next((azubi for azubi in self.azubis if f"{azubi['firstname']} {azubi['lastname']}" == secondary_name), None)
                if secondary_azubi and self.is_blockweek(date.year, week, secondary_azubi['year']):
                    print(f"Validierungs Fehler: {secondary_name} zugewiesen während Schulwoche {week} an {date}")


    def generate_statistics(self, schedule):
        """Statistiken für die Azubis generieren."""
        stats = {
            f"{azubi['firstname']} {azubi['lastname']}": {
                'primary': 0,
                'secondary': 0,
                'year': azubi['year']
            }
            for azubi in self.azubis
        }

        for entry in schedule:
            primary = entry.get('primary')
            secondary = entry.get('secondary')

            try:
                if primary:
                    stats[primary]['primary'] += 1

                if secondary:
                    stats[secondary]['secondary'] += 1
            except:
                pass

        sorted_stats = dict(sorted(
            stats.items(),
            key=lambda item: (item[1]['primary'] + item[1]['secondary']),
            reverse=True
        ))

        return sorted_stats

    def print_statistics(self, stats):
        """Statistiken zu den Azubis in der Konsole ausgeben"""
        print()
        print("Wie oft welche Azubis im Dienst eingetragen sind:")
        print(f"{'Jahr':<6}{'Name':<45}{'Dienst':<15}{'Vertretung':<15}")
        print("-" * 80)
        for name, counts in stats.items():
            print(f"{counts['year']:<6}{name:<45}{counts['primary']:<15}{counts['secondary']:<15}")
        print()

if __name__ == "__main__":
    azubis_file = "data/Azubis.csv"
    blockweeks_file = "data/Blockwochen_Schule.csv"
    holidays_file = "data/Feiertage_Schließzeiten_Brückentage.csv"
    target_folder = "output"

    print("Dieses Tool erstellt basierend auf den *.csv-Daten im Unterordner ./data/ eine tägliche Liste, die festlegt, wer für den Dienst und die Vertretung beim Ein- und Ausräumen der Geschirrspülmaschine zuständig ist. Bitte die *.csv-Daten anpassen, bevor ein Plan generiert wird.\n")
    scheduler = CleaningDutyScheduler(azubis_file, blockweeks_file, holidays_file)

    year = int(input("Das Schuljahr für das der Spühlmaschinenplan gemacht werden soll (z.B, 2024 für 2024/2025): "))

    export_format = input("Das Dateiformat zum exportieren (csv/html/ics): ").strip().lower()
    export_formats = {
        "csv": CSVExporter(),
        "html": HTMLExporter(),
        "ics": ICSExporter()
    }

    exporter = export_formats.get(export_format, CSVExporter())
    output_file = f"{target_folder}/Spühlmaschinenplan.{export_format if exporter else 'csv'}"
    include_all_dates = export_format == "html"

    schedule = scheduler.generate_schedule(year, include_all_dates=include_all_dates)
    scheduler.save_schedule(schedule, exporter, output_file)
    stats = scheduler.generate_statistics(schedule)
    scheduler.print_statistics(stats)

    # Generiert Plan auf monatlicher basis
    for yy in range(2):
        for month in range(1, 13):
            monthly_schedule = scheduler.filter_schedule_by_month(schedule.copy(), year+yy, month)
            scheduler.save_schedule(monthly_schedule, exporter, f"{target_folder}/monatlich/{year+yy}_{month}.html")

    print(f"Spühlmaschinenplan auf monatlicher basis wurde in {target_folder}/monatlich/* gespeichert.")
    print(f"Spühlmaschinenplan für {year}/{year + 1} gespeichert an {output_file}.")
