from datetime import datetime

class ICSExporter:
    def export(self, schedule, output_file):
        try:
            ics_data = "BEGIN:VCALENDAR\nVERSION:2.0\nPRODID:-//NikoIT//NONSGML v1.0//EN\n"
            
            dtstamp = datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')

            for entry in schedule:
                date_str = entry['date'].strftime('%Y%m%d')
                primary = entry['primary']
                secondary = entry['secondary']

                event = f"BEGIN:VEVENT\n"
                event += f"SUMMARY:{primary}\n"
                event += f"DTSTART;VALUE=DATE:{date_str}\n"
                event += f"DTSTAMP:{dtstamp}\n"
                event += f"END:VEVENT\n"
                
                ics_data += event

                if secondary != ' - ':
                    event_secondary = f"BEGIN:VEVENT\n"
                    event_secondary += f"SUMMARY:VERTR.: {secondary}\n"
                    event_secondary += f"DTSTART;VALUE=DATE:{date_str}\n"
                    event_secondary += f"DTSTAMP:{dtstamp}\n"
                    event_secondary += f"END:VEVENT\n"

                    ics_data += event_secondary

                event += f"\n"

            ics_data += "END:VCALENDAR"

            with open(output_file, 'w', encoding='utf-8-sig') as f:
                f.write(ics_data)
            print(f"ICS gespeichert in {output_file}")

        except Exception as e:
            raise ValueError(f"Fehler beim speicher zu ICS: {e}")
