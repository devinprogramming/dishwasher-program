import csv

class CSVExporter:
    def export(self, schedule, output_file):
        try:
            with open(output_file, 'w', newline='', encoding='utf-8-sig') as file:
                writer = csv.DictWriter(file, fieldnames=['datum', 'dienst', 'vertretung'], delimiter=';')
                writer.writeheader()
                for entry in schedule:
                    writer.writerow({
                        'datum': entry['date'].strftime('%d.%m.%Y'),
                        'dienst': entry['primary'] or '',
                        'vertretung': entry['secondary'] or ''
                    })
        except Exception as e:
            raise ValueError(f"Fehler beim speichern zu CSV: {e}")
