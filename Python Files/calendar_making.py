from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import inch
from datetime import datetime, timedelta

def draw_simple_calendar(c, year, month, events, page_size=letter):
    # Page margins and dimensions
    grid_x = 0.5 * inch
    grid_y = 1.2 * inch
    grid_width = 7.5 * inch
    grid_height = 9 * inch
    day_width = grid_width / 7
    day_height = grid_height / 6

    # Calendar header
    c.setFont("Helvetica-Bold", 18)
    c.setFillColor(colors.black)
    c.drawCentredString(page_size[0] / 2, page_size[1] - 0.8 * inch, f"{datetime(year, month, 1).strftime('%B %Y')}")

    # Add day headers
    days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(colors.grey)
    for i, day in enumerate(days):
        c.drawCentredString(grid_x + i * day_width + day_width / 2, grid_y + grid_height + 0.2 * inch, day)

    # Get the first day of the month and total days
    first_day = datetime(year, month, 1).weekday()
    total_days = (datetime(year, month + 1, 1) - timedelta(days=1)).day if month < 12 else 31

    # Draw the calendar grid
    day = 1
    c.setStrokeColor(colors.lightgrey)
    c.setLineWidth(0.5)
    for row in range(6):
        for col in range(7):
            cell_x = grid_x + col * day_width
            cell_y = grid_y + grid_height - (row + 1) * day_height

            # Draw the cell
            c.rect(cell_x, cell_y, day_width, day_height)

            # Skip cells before the first day or after the last day
            if row == 0 and col < first_day or day > total_days:
                continue

            # Draw the day number
            c.setFont("Helvetica-Bold", 10)
            c.setFillColor(colors.black)
            c.drawString(cell_x + 4, cell_y + day_height - 14, str(day))

            # Add events
            current_date = datetime(year, month, day).strftime("%Y-%m-%d")
            if current_date in events:
                y_offset = cell_y + day_height - 28
                for event in events[current_date]:
                    c.setFont("Helvetica", 8)
                    c.setFillColor(colors.blue)
                    c.drawString(cell_x + 4, y_offset, f"• {event['event_type']}: {event['description']}")
                    y_offset -= 10
                    if y_offset < cell_y + 4:
                        c.drawString(cell_x + 4, y_offset, "...")  # Indicate overflow
                        break
            day += 1

    # Footer
    c.setFont("Helvetica-Oblique", 9)
    c.setFillColor(colors.grey)
    c.drawCentredString(page_size[0] / 2, 0.5 * inch, "Generated with Python & ReportLab")

def generate_simple_calendar(output_file, year, month, events, page_size=letter):
    c = canvas.Canvas(output_file, pagesize=page_size)
    draw_simple_calendar(c, year, month, events, page_size)
    c.showPage()
    c.save()

# Example usage
events = {
    "2024-12-01": [
        {"event_type": "Exam", "time": "10:00 AM - 12:00 PM", "description": "Math Midterm"},
    ],
    "2024-12-03": [
        {"event_type": "Lab", "time": "1:00 PM - 3:00 PM", "description": "Physics Lab"}
    ],
    "2024-12-15": [
        {"event_type": "Assignment", "time": "TBA", "description": "Final Project Submission"}
    ]
}

generate_simple_calendar(
    "simple_calendar.pdf",
    2024,
    12,
    events
)
