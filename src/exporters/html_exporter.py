"""
Expotiert den Geschirrspühlplan-Objekt in eine HTML-Seite.

Author: pascal.blum@nikoit.de
"""
import locale
from datetime import datetime

locale.setlocale(locale.LC_TIME, 'de_DE.UTF-8')

class HTMLExporter:
    
    def get_theme_styles(self):
        return {
            "light": """
                body {
                    font-family: Arial, sans-serif;
                    margin: 20px;
                    line-height: 1.6em;
                    background-color: #f9f9f9;
                    color: #333;
                }
                caption {
                    font-size: 2rem;
                    font-weight: bold;
                    text-align: center;
                    margin: 20px 0px;
                }
                .badge {
                    font-size: x-small;
                    background-color: blue;
                    color: white;
                    padding: 4px 8px;
                    text-align: center;
                    border-radius: 5px;
                    vertical-align: super;
                }
                table {
                    border-collapse: collapse;
                    width: 100%;
                    max-width: 1000px;
                    margin: 0px auto;
                }
                th, td {
                    border: 1px solid #ccc;
                    padding: 7px;
                    text-align: center;
                }
                th {
                    background-color: #2c3e50;
                    color: #ffffff;
                    position: sticky;
                    position: -webkit-sticky;
                    top: 0px;
                    z-index: 2;
                }
                .month-header {
                    background-color: #34495e;
                    color: #ffffff;
                    font-size: 1.2em;
                    font-weight: bold;
                }
                .weekday {
                    background-color: #f4f4f4;
                }
                .weekday-weekend {
                    background-color: #ffe0b2;
                }
                .weekday-weekday {
                    background-color: #ffffff;
                }
                .holiday {
                    background-color: #e8e8e8;
                    color: #7a7a7a;
                }
                .highlight {
                    border: 14px solid orange;
                    position: relative;
                    box-sizing: border-box;
                    border-collapse: separate;
                }
                .highlight td {
                    border: none;
                }
                @media (max-width: 768px) {
                    table {
                        font-size: 0.9em;
                    }
                    th, td {
                        padding: 8px;
                    }
                }
                .bold {
                    font-weight: bold;
                }
                .table-container {
                    overflow-x: auto;
                    -webkit-overflow-scrolling: touch;
                }
                @media print {
                    .print-hidden {
                        display: none !important;
                    }
                }
            """,
            "dark": """
                body {
                    font-family: Arial, sans-serif;
                    margin: 20px;
                    line-height: 1.6em;
                    background-color: #121212;
                    color: #e0e0e0;
                }
                caption {
                    font-size: 2rem;
                    font-weight: bold;
                    text-align: center;
                    margin: 20px 0px;
                }
                .badge {
                    font-size: x-small;
                    background-color: blue;
                    color: white;
                    padding: 4px 8px;
                    text-align: center;
                    border-radius: 5px;
                    vertical-align: super;
                }
                table {
                    border-collapse: collapse;
                    width: 100%;
                    max-width: 1000px;
                    margin: 0px auto;
                }
                th, td {
                    border: 1px solid #444;
                    padding: 10px;
                    text-align: center;
                }
                th {
                    background-color: #333333;
                    color: orange;
                    position: sticky;
                    position: -webkit-sticky;
                    top: 0px;
                    z-index: 2;
                }
                .month-header {
                    background-color: #444444;
                    color: #e0e0e0;
                    font-size: 1.2em;
                    font-weight: bold;
                }
                .weekday {
                    background-color: #1e1e1e;
                }
                .weekday-weekend {
                    background-color: #2a2a2a;
                }
                .weekday-weekday {
                    background-color: #242424;
                }
                .holiday {
                    background-color: #3a3a3a;
                    color: #b0b0b0;
                }
                .highlight {
                    border: 14px solid orange;
                    position: relative;
                    box-sizing: border-box;
                    border-collapse: separate;
                }
                .highlight td {
                    border: none;
                }
                @media (max-width: 768px) {
                    table {
                        font-size: 0.9em;
                    }
                    th, td {
                        padding: 8px;
                    }
                }
                .bold {
                    font-weight: bold;
                }
                @media print {
                    .print-hidden {
                        display: none !important;
                    }
                }
            """,
            "print": """
                body {
                    font-family: Arial, sans-serif;
                    margin: 20px;
                }
                table {
                    border-collapse: collapse;
                    width: 100%;
                }
                caption {
                    font-size: 2rem;
                    font-weight: bold;
                    text-align: center;
                    margin: 20px 0px;
                }
                .badge {
                    font-size: x-small;
                    padding: 4px 8px;
                    text-align: center;
                    vertical-align: super;
                }
                th, td {
                    border: 1px solid #ccc;
                    text-align: center;
                }
                tr:nth-child(odd):not(:nth-child(-n+2)) {
                    background-color: #f1f1f1;
                }
                .month-header {
                    font-size: 1.2em;
                    font-weight: bold;
                }
                .wrapper {
                    overflow-x: auto;
                }
                .bold {
                    font-weight: bold;
                }
                @media print {
                    .print-hidden {
                        display: none !important;
                    }
                }
            """
        }
    
    def format_name(self, name):
        parts = name.split()
        return f"{parts[0]} {parts[-1][0]}." if len(parts) > 1 else name if parts else ""

    def export(self, schedule, output_file):
        try:
            today = datetime.now().strftime('%d.%m.%y')
            styles = self.get_theme_styles()
            
            with open(output_file, 'w', encoding='utf-8-sig') as file:
                file.write(f"""
                <!DOCTYPE html>
                <html lang="de">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>Spühlmaschinen-Plan - aktualisiert am {today}</title>
                    <style id="theme-style">{styles['light']}</style>
                    <script>
                        function scrollToTodayRow() {{
                            const highlightedRow = document.querySelector('.highlight');
                            if (highlightedRow) {{
                                requestAnimationFrame(() => {{
                                    highlightedRow.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
                                }});
                            }}
                        }}

                        function setTheme(theme) {{
                            document.getElementById('theme-style').innerHTML = {{
                                'light': `{styles['light']}`,
                                'dark': `{styles['dark']}`,
                                'print': `{styles['print']}`
                            }}[theme] || `{styles['light']}`;
                            localStorage.setItem('theme', theme);
                        }}

                        function highlightTodayRows() {{
                            const currentDate = new Intl.DateTimeFormat('de-DE', {{
                                    day: '2-digit',
                                    month: '2-digit',
                                    year: '2-digit'
                                    }}).format(new Date());
                                    
                            const tbodyRows = document.querySelector('table tbody').querySelectorAll('tr');
                            
                            tbodyRows.forEach(row => {{
                                const dateCell = row.querySelector('td:nth-child(2)');
                                if (dateCell) {{
                                    const rowDate = dateCell.textContent.trim();
                                    if (rowDate === currentDate) {{
                                        row.classList.add('highlight');
                                    }}
                                }}
                            }});
                        }}

                        function populateFilterDropdown() {{
                            const dropdown = document.getElementById('row-filter');
                            const monthHeaders = document.querySelectorAll('.month-header');
                            const tbodyRows = document.querySelectorAll('table tbody tr');
                            let months = [];

                            // Add a custom row count option
                            const rowCountOption = document.createElement('option');
                            rowCountOption.value = '10';
                            rowCountOption.textContent = '10 Zeilen';
                            dropdown.appendChild(rowCountOption);

                            // Add an option to show all rows
                            const allRowsOption = document.createElement('option');
                            allRowsOption.value = 'all';
                            allRowsOption.textContent = 'Alle';
                            dropdown.appendChild(allRowsOption);



                            // Collect unique months from the table
                            monthHeaders.forEach(header => {{
                                const monthText = header.querySelector('td').textContent.trim();
                                if (months.indexOf(monthText) === -1) {{
                                    months.push(monthText);
                                }}
                            }});

                            // Populate the dropdown with months and row options
                            months.forEach(month => {{
                                const option = document.createElement('option');
                                option.value = month;
                                option.textContent = month;
                                dropdown.appendChild(option);
                            }});
                        }}

                        function filterRows() {{
                            const dropdown = document.getElementById('row-filter');
                            const selectedValue = dropdown.value;
                            const tbodyRows = document.querySelectorAll('table tbody tr');
                            let todayIndex = -1; // Use this to find the target row index if needed
                            let monthRows = [];
                            let currentMonth = null; // Variable to track the current month

                            if (selectedValue === '10') {{
                                    const highlightedRow = document.querySelector('.highlight');
                                    if (!highlightedRow) return;

                                    const tbodyRows = document.querySelectorAll('table tbody tr');
                                    const todayIndex = [...tbodyRows].indexOf(highlightedRow);

                                    tbodyRows.forEach((row, index) => {{
                                        if (index >= todayIndex - 5 && index <= todayIndex + 5) {{
                                            row.style.display = ''; // Show row within the buffer
                                        }} else {{
                                            row.style.display = 'none'; // Hide row outside the buffer
                                        }}
                                    }});

                                    scrollToTodayRow();
                                    return; // Exit early from the rest of the filtering logic
                                }}

                            tbodyRows.forEach((row, index) => {{
                                const isMonthHeader = row.classList.contains('month-header');
                                const isDateRow = row.classList.contains('weekday-weekday') || row.classList.contains('weekday-weekend');
                                const rowDateText = row.querySelector('td') ? row.querySelector('td').textContent.trim() : '';

                                // Handling the month selection
                                if (selectedValue !== 'all' && selectedValue !== '10') {{
                                    if (isMonthHeader) {{
                                        // If the row is a month header, check if it matches the selected month
                                        currentMonth = rowDateText; // Set the current month
                                        if (currentMonth === selectedValue) {{
                                            monthRows.push(index); // Include this month header
                                        }}
                                    }}
                                    // If it's a date row, include it if the currentMonth matches the selected month
                                    if (isDateRow && currentMonth === selectedValue) {{
                                        monthRows.push(index); // Include this date row
                                    }}
                                }}
                            }});

                            // Show or hide rows based on the selected month
                            tbodyRows.forEach((row, index) => {{
                                if (selectedValue === 'all' || monthRows.includes(index)) {{
                                    row.style.display = ''; // Show row if it matches the filter
                                }} else {{
                                    row.style.display = 'none'; // Hide row otherwise
                                }}
                            }});

                            // Optional: Scroll to the highlighted row if needed
                            scrollToTodayRow();
                        }}

                        window.onload = function() {{
                                highlightTodayRows();

                                const savedTheme = localStorage.getItem('theme') || 'light';
                                setTheme(savedTheme);

                                scrollToTodayRow();

                                const themeSelect = document.getElementById('theme-select');
                                if (themeSelect) {{
                                    themeSelect.value = savedTheme;
                                }}

                                filterRows();
                            }}

                        document.addEventListener("DOMContentLoaded", function () {{
                            populateFilterDropdown();
                            //checkbox = document.getElementById('showallCheckbox');
                            //checkbox.addEventListener('change', filterRows);
                            
                        }});
                    </script>
                </head>
                <body>
                    <div class="wrapper">
                        <div class="print-hidden" style="position: fixed; bottom: 5px; right: 10px; display: grid; grid-template-columns: repeat(3, auto); gap: 10px; z-index: 1;">
                            <!-- Admin Redirect Button -->
                            <button onclick="window.location.href='/admin/'" style="font-size: 20px; border: none; background: transparent; cursor: pointer;">
                                ⚙️
                            </button>

                            <!-- Filter Dropdown -->
                            <select id="row-filter" onchange="filterRows()">
                            </select>

                            
                            <!-- Theme Selector -->
                            <select id="theme-select" onchange="setTheme(this.value); scrollToTodayRow();" style="height: 30px; border: 4px solid red;">
                                <option value="light">Light</option>
                                <option value="dark">Dark</option>
                                <option value="print">Print</option>
                            </select>

                        </div>
                        <table>
                            <caption>Spühlmaschinen-Plan <span class="badge">stand {today}</span></caption>
                            <thead>
                                <tr>
                                    <th>KW</th>
                                    <th>Datum</th>
                                    <th>Wochentag</th>
                                    <th>Dienst</th>
                                    <th>Vertretung</th>
                                </tr>
                            </thead>
                            <tbody>
                """)
                
                current_month = None
                weekdays = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]
                months = ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August", "September", "Oktober", "November", "Dezember"]


                for entry in schedule:
                    entry_date = entry['date'].strftime('%d.%m.%y')
                    date_obj = datetime.strptime(entry_date, '%d.%m.%y')
                    calendar_week = entry['date'].isocalendar()[1]
                    weekday_index = entry['date'].weekday()
                    weekday = weekdays[weekday_index]
                    entry_month = entry['date'].strftime('%B %Y')

                    is_holiday = " - " in entry['primary'] or " - " in entry['secondary']
                    is_weekend = weekday_index >= 5
                    holiday_class = "holiday" if is_holiday and not is_weekend else ""

                    if current_month != entry_month:
                        current_month = entry_month
                        file.write(f"""
                        <tr class='month-header'>
                            <td colspan='5'>{months[date_obj.month - 1]} {date_obj.year}</td>
                        </tr>
                        """)

                    # legacy code. highlighting wird vom javascript nun gemacht
                    highlight_class = ""
                    weekday_class = "weekday-weekday" if weekday_index < 5 else "weekday-weekend"
                    row_classes = " ".join(filter(None, [weekday_class, holiday_class, highlight_class]))

                    formatted_primary = self.format_name(entry['primary'])
                    formatted_secondary = self.format_name(entry['secondary'])

                    file.write(f"""
                    <tr class='{row_classes}'>
                        <td>{calendar_week}</td>
                        <td class='bold'>{entry_date}</td>
                        <td>{weekday}</td>
                        <td class='bold'>{formatted_primary}</td>
                        <td>{formatted_secondary}</td>
                    </tr>
                    """)
                
                file.write("""</tbody></table></div></body></html>""")
        except Exception as e:
            raise ValueError(f"Fehler beim speichern zu HTML: {e}")
