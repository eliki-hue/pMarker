import os
from reportlab.lib.pagesizes import A4, portrait
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import mm, inch
import re
from datetime import datetime

def parse_student_data(text_content):
    """Parse the text content and extract student data"""
    student_blocks = re.split(r'={50,}', text_content)
    students = []
    
    for block in student_blocks:
        if not block.strip():
            continue
            
        student = {}
        lines = block.strip().split('\n')
        
        # Extract name and score
        name_line = lines[0]
        student['name'] = re.search(r'Student:\s*(.+)', name_line).group(1).strip()
        
        score_line = lines[1]
        student['score'] = re.search(r'Score:\s*(.+)', score_line).group(1).strip()
        
        # Initialize sections
        student['learned'] = []
        student['improvement'] = []
        
        # Process learned and improvement sections
        current_section = None
        for line in lines[2:]:
            if '✅' in line:
                current_section = 'learned'
                continue
            elif '❌' in line:
                current_section = 'improvement'
                continue
                
            if current_section and line.strip().startswith('-'):
                student[current_section].append(line.strip()[2:])
                
        students.append(student)
    
    return students

def create_coding_report(student, filename, report_meta):
    """
    Create a coding progress report PDF matching the music report format
    """
    # Set page size to A4 portrait
    doc = SimpleDocTemplate(filename, pagesize=portrait(A4),
                          leftMargin=20*mm, rightMargin=20*mm,
                          topMargin=15*mm, bottomMargin=15*mm)
    story = []
    
    # Define styles
    styles = getSampleStyleSheet()
    
    # Title style
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Heading1'],
        fontSize=16,
        alignment=1,
        spaceAfter=12,
        textColor=colors.HexColor('#2c3e50'),
        fontName='Helvetica-Bold'
    )
    
    # Student info style
    student_style = ParagraphStyle(
        'StudentInfo',
        parent=styles['Normal'],
        fontSize=12,
        alignment=0,
        spaceAfter=6,
        textColor=colors.HexColor('#34495e'),
        fontName='Helvetica'
    )
    
    # Table header style
    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.black,
        fontName='Helvetica-Bold'
    )
    
    # Table content style
    table_content_style = ParagraphStyle(
        'TableContent',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.black,
        fontName='Helvetica'
    )
    
    # Section style
    section_style = ParagraphStyle(
        'Section',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.black,
        fontName='Helvetica-Bold',
        spaceBefore=12,
        spaceAfter=6
    )
    
    # Bullet style
    bullet_style = ParagraphStyle(
        'Bullet',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.black,
        fontName='Helvetica',
        leftIndent=12,
        bulletIndent=6,
        spaceAfter=4
    )
    
    # ======================
    # HEADER SECTION
    # ======================
    story.append(Paragraph("CODING PROGRESS REPORT FOR TERM ONE 2025", title_style))
    
    # ======================
    # STUDENT INFORMATION
    # ======================
    student_info = [
        [Paragraph("<b>NAME:</b>", student_style), Paragraph(student['name'], student_style)],
        [Paragraph("<b>CLASS:</b>", student_style), Paragraph(report_meta.get('class', 'Grade 5'), student_style)],
        [Paragraph("<b>SCORE:</b>", student_style), Paragraph(student['score'], student_style)],
        [Paragraph("<b>REPORT DATE:</b>", student_style), Paragraph(datetime.now().strftime("%B %d, %Y"), student_style)]
    ]
    
    student_table = Table(student_info, colWidths=[1.5*inch, 4*inch])
    student_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    
    story.append(student_table)
    story.append(Spacer(1, 0.3*inch))
    
    # ======================
    # RUBRIC TABLE
    # ======================
    # Create table header
    rubric_header = [
        Paragraph("<b>CATEGORY</b>", table_header_style),
        Paragraph("<b>RATING</b>", table_header_style),
        Paragraph("<b>COMMENTS</b>", table_header_style)
    ]
    
    # Create table data - we'll convert learned/improvement to rubric format
    rubric_data = [rubric_header]
    
    # Add learned items as positive achievements
    for item in student['learned']:
        rubric_data.append([
            Paragraph("Achievement", table_content_style),
            Paragraph("✓", table_content_style),
            Paragraph(item, table_content_style)
        ])
    
    # Add improvement items as areas to work on
    for item in student['improvement']:
        rubric_data.append([
            Paragraph("Area for Improvement", table_content_style),
            Paragraph("✗", table_content_style),
            Paragraph(item, table_content_style)
        ])
    
    # Create and style table
    rubric_table = Table(rubric_data, colWidths=[1.5*inch, 0.8*inch, 3.5*inch])
    rubric_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f2f2f2')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    
    story.append(rubric_table)
    story.append(Spacer(1, 0.3*inch))
    
    # ======================
    # CONCEPTS COVERED
    # ======================
    story.append(Paragraph("<b>CONCEPTS COVERED THIS TERM:</b>", section_style))
    
    # This would be customized based on your curriculum
    concepts = [
        "Basic Python syntax",
        "Variables and data types",
        "Conditional statements",
        "Loops",
        "Functions",
        "Basic data structures"
    ]
    
    for concept in concepts:
        story.append(Paragraph(f"• {concept}", bullet_style))
    
    story.append(Spacer(1, 0.5*inch))
    
    # ======================
    # TEACHER SIGNATURE
    # ======================
    teacher_info = [
        [Paragraph("<b>TEACHER:</b> [Teacher Name]", student_style), ""],
        ["", Paragraph("<b>SIGNATURE:</b> _________________________", student_style)]
    ]
    
    teacher_table = Table(teacher_info, colWidths=[3*inch, 3*inch])
    teacher_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (1, 1), (1, 1), 'RIGHT'),
    ]))
    
    story.append(teacher_table)
    
    doc.build(story)

def generate_coding_reports(text_file_path, report_meta=None):
    """
    Generate coding progress PDF reports for all students
    """
    if report_meta is None:
        report_meta = {
            'term': '1',
            'year': '2025',
            'class': 'Grade 5'
        }
    
    # Create gen_reports directory if it doesn't exist
    output_folder = "gen_reports"
    os.makedirs(output_folder, exist_ok=True)
    
    try:
        with open(text_file_path, 'r', encoding='utf-8') as file:
            content = file.read()
    except UnicodeDecodeError:
        with open(text_file_path, 'r', encoding='latin-1') as file:
            content = file.read()
    
    students = parse_student_data(content)
    
    for student in students:
        # Create a valid filename with proper .pdf extension
        filename = f"Coding Progress Report - {student['name']} {report_meta['class']}.pdf"  # Added . before pdf
        filename = re.sub(r'[^\w\s-]', '', filename).strip()
        full_path = os.path.join(output_folder, filename)
        
        print(f"Generating report for {student['name']}...")
        create_coding_report(student, full_path, report_meta)
        
        # Verify PDF was created
        if os.path.exists(full_path):
            print(f"Successfully created: {full_path}")
        else:
            print(f"Failed to create: {full_path}")
    
    print(f"\nGenerated {len(students)} reports in '{output_folder}' folder.")

if __name__ == "__main__":
    # Configuration
    config = {
        'text_file_path': "Student_Progress_Report.txt",  # Your input file
        'report_meta': {
            'term': '2',
            'year': '2025',
            'class': 'Year 8 Coding'
        }
    }
    
    generate_coding_reports(
        text_file_path=config['text_file_path'],
        report_meta=config['report_meta']
    )