from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.units import mm
from reportlab.platypus import TableStyle
import os
import tempfile
import time
from typing import List

class PDFService:
    def __init__(self):
        pass

    def create_pdf(self, goal: str, strategy_points: List[str], micro_habits: List[str]) -> str:
        """Create a PDF document with the goal, strategy points, and micro-habits."""
        # Create a unique filename
        filename = f"goal_plan_{int(time.time())}.pdf"
        filepath = os.path.join(tempfile.gettempdir(), filename)
        
        # Create the PDF document
        doc = SimpleDocTemplate(
            filepath,
            pagesize=letter,
            rightMargin=50,
            leftMargin=50,
            topMargin=50,
            bottomMargin=50
        )
        
        # Define styles
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Title'],
            fontSize=24,
            spaceAfter=30,
            textColor=colors.HexColor('#FF4B4B'),
            alignment=1  # Center alignment
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=20,
            spaceBefore=20,
            textColor=colors.HexColor('#FF4B4B')
        )
        
        subheading_style = ParagraphStyle(
            'CustomSubheading',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            textColor=colors.HexColor('#FF4B4B'),
            fontWeight='bold'
        )
        
        body_style = ParagraphStyle(
            'CustomBody',
            parent=styles['Normal'],
            fontSize=11,
            spaceAfter=15,
            leading=16
        )
        
        # Create the content
        content = []
        
        # Add title and goal
        content.append(Paragraph("Strategic Action Plan", title_style))
        content.append(Spacer(1, 20))
        content.append(Paragraph("Goal", heading_style))
        content.append(Paragraph(goal, body_style))
        content.append(Spacer(1, 20))
        
        # Add Strategic Initiatives
        content.append(Paragraph("Strategic Initiatives", heading_style))
        content.append(Spacer(1, 10))
        
        # Create a table for initiatives
        initiative_data = []
        for i, point in enumerate(strategy_points, 1):
            # Split initiative into title and description
            parts = point.split(':', 1)
            if len(parts) == 2:
                title, description = parts
                # Add initiative to table
                initiative_data.append([
                    f"{i}",
                    Paragraph(f"<b>{title}</b>", body_style),
                    Paragraph(description, body_style)
                ])
            else:
                # Fallback for initiatives without title
                initiative_data.append([
                    f"{i}",
                    Paragraph(point, body_style),
                    ""
                ])
        
        if initiative_data:
            # Create and style the table
            initiative_table = Table(
                initiative_data,
                colWidths=[30, 150, 300],
                style=TableStyle([
                    ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#FF4B4B')),
                    ('TEXTCOLOR', (0, 0), (0, -1), colors.white),
                    ('ALIGN', (0, 0), (0, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 11),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                    ('TOPPADDING', (0, 0), (-1, -1), 12),
                    ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ])
            )
            content.append(initiative_table)
        
        content.append(Spacer(1, 30))
        
        # Add Micro-habits
        content.append(Paragraph("Daily Micro-habits", heading_style))
        content.append(Spacer(1, 10))
        
        # Create a table for habits
        habit_data = []
        for i, habit in enumerate(micro_habits, 1):
            habit_data.append([f"{i}", Paragraph(habit, body_style)])
        
        if habit_data:
            # Create and style the habits table
            habit_table = Table(
                habit_data,
                colWidths=[30, 450],
                style=TableStyle([
                    ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#FF4B4B')),
                    ('TEXTCOLOR', (0, 0), (0, -1), colors.white),
                    ('ALIGN', (0, 0), (0, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 11),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                    ('TOPPADDING', (0, 0), (-1, -1), 12),
                    ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ])
            )
            content.append(habit_table)
        
        # Add footer with timestamp
        content.append(Spacer(1, 30))
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.grey,
            alignment=1
        )
        content.append(Paragraph(
            f"Generated on {time.strftime('%B %d, %Y at %I:%M %p')}",
            footer_style
        ))
        
        # Build the PDF
        doc.build(content)
        
        return filepath
