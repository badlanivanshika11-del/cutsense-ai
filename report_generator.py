import io
import csv
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable

def generate_csv_report(metadata: dict, report) -> str:
    """Generates a CSV string containing the analysis report."""
    output = io.StringIO()
    writer = csv.writer(output)
    
    writer.writerow(["Video Title", metadata.get("title", "")])
    writer.writerow(["Uploader", metadata.get("uploader", "")])
    writer.writerow(["Overall Pacing", report.pacing_rating])
    writer.writerow(["Estimated Cuts / Min", report.estimated_cuts_per_minute])
    writer.writerow(["Script Hook Evaluation", report.script_hook_evaluation])
    writer.writerow(["Thumbnail Analysis", report.thumbnail_analysis])
    writer.writerow([])
    
    writer.writerow(["Timestamp Start", "Timestamp End", "Edit Type", "Description", "Engagement Impact"])
    for item in report.timeline:
        writer.writerow([
            item.timestamp_start,
            item.timestamp_end,
            item.editing_type,
            item.description,
            item.engagement_impact
        ])
        
    return output.getvalue()

def generate_pdf_report(metadata: dict, report) -> bytes:
    """Generates a styled PDF report as bytes."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    story = []
    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#6366f1'),
        spaceAfter=6
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#64748b'),
        spaceAfter=12
    )
    
    h2_style = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontSize=13,
        leading=16,
        textColor=colors.HexColor('#1e293b'),
        spaceBefore=10,
        spaceAfter=6
    )
    
    body_style = ParagraphStyle(
        'BodyTextCustom',
        parent=styles['Normal'],
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#334155')
    )

    # Document Header
    story.append(Paragraph("🎬 CutSense AI - Video Editing & Retention Report", title_style))
    story.append(Paragraph(f"Video: {metadata.get('title', 'N/A')} | Creator: {metadata.get('uploader', 'N/A')}", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#e2e8f0'), spaceAfter=10))

    # Metrics Summary
    story.append(Paragraph("📊 Pacing & Metrics Summary", h2_style))
    summary_data = [
        [Paragraph(f"<b>Overall Pacing:</b> {report.pacing_rating}", body_style),
         Paragraph(f"<b>Est. Cuts / Min:</b> {report.estimated_cuts_per_minute}", body_style)]
    ]
    summary_table = Table(summary_data, colWidths=[270, 270])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
        ('PADDING', (0,0), (-1,-1), 8),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('LINEBELOW', (0,0), (-1,-1), 1, colors.HexColor('#cbd5e1')),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 10))

    # Retention Hook & Thumbnail
    story.append(Paragraph("🪝 First 15-Second Retention Hook", h2_style))
    story.append(Paragraph(report.script_hook_evaluation, body_style))
    story.append(Spacer(1, 8))

    story.append(Paragraph("🖼️ Thumbnail & Visual Clickability", h2_style))
    story.append(Paragraph(report.thumbnail_analysis, body_style))
    story.append(Spacer(1, 10))

    # Timestamped Timeline Table
    story.append(Paragraph("⏱️ Timestamped Editing & Transition Timeline", h2_style))
    
    table_data = [
        [Paragraph("<b>Time</b>", body_style),
         Paragraph("<b>Edit Type</b>", body_style),
         Paragraph("<b>Technique Description</b>", body_style),
         Paragraph("<b>Retention Impact</b>", body_style)]
    ]

    for item in report.timeline:
        table_data.append([
            Paragraph(f"{item.timestamp_start} - {item.timestamp_end}", body_style),
            Paragraph(f"<b>{item.editing_type}</b>", body_style),
            Paragraph(item.description, body_style),
            Paragraph(item.engagement_impact, body_style)
        ])

    timeline_table = Table(table_data, colWidths=[70, 85, 195, 190])
    timeline_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#eeefec')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor('#0f172a')),
        ('PADDING', (0,0), (-1,-1), 6),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(timeline_table)

    doc.build(story)
    return buffer.getvalue()
