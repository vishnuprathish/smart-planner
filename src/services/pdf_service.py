from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import inch
import os
import tempfile

class PDFService:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        # Create custom styles
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Title'],
            fontSize=24,
            spaceAfter=30,
            textColor=colors.HexColor('#FF4B4B')
        ))
        self.styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=self.styles['Heading1'],
            fontSize=18,
            spaceAfter=20,
            textColor=colors.HexColor('#FF4B4B')
        ))
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['Normal'],
            fontSize=12,
            spaceAfter=12,
            textColor=colors.black
        ))

    def create_pdf(self, goal, strategy_points, micro_habits):
        """Create a PDF with the goal, strategy points, and micro-habits."""
        # Create a temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        doc = SimpleDocTemplate(
            temp_file.name,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )

        # Build the PDF content
        story = []

        # Add Title
        story.append(Paragraph("Smart Goal Planner", self.styles['CustomTitle']))
        story.append(Spacer(1, 12))

        # Add Goal
        story.append(Paragraph("Your Goal:", self.styles['CustomHeading']))
        story.append(Paragraph(goal, self.styles['CustomBody']))
        story.append(Spacer(1, 20))

        # Add Strategy
        story.append(Paragraph("Success Strategy:", self.styles['CustomHeading']))
        for i, point in enumerate(strategy_points, 1):
            story.append(Paragraph(
                f"{i}. {point}",
                self.styles['CustomBody']
            ))
        story.append(Spacer(1, 20))

        # Add Micro-habits
        story.append(Paragraph("Daily Micro-habits:", self.styles['CustomHeading']))
        for i, habit in enumerate(micro_habits, 1):
            story.append(Paragraph(
                f"{i}. {habit}",
                self.styles['CustomBody']
            ))

        # Build the PDF
        doc.build(story)
        return temp_file.name
