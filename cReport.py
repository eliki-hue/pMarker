import os
from reportlab.lib.pagesizes import letter, A4, landscape, portrait
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch, mm
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

def create_student_report(student, filename, logo_path, report_meta):
    """
    Create a PDF report for a single student with professional header
    report_meta should contain: {'page_size': 'A4', 'orientation': 'portrait', 
                                'term': '1', 'year': '2023', 'class': 'Grade 5'}
    """
    # Set page size and orientation
    page_size = {
        'letter': letter,
        'A4': A4
    }.get(report_meta.get('page_size', 'A4'), letter)
    
    orientation = report_meta.get('orientation', 'portrait')
    if orientation == 'landscape':
        page_size = landscape(page_size)
    else:
        page_size = portrait(page_size)
    
    doc = SimpleDocTemplate(filename, pagesize=page_size,
                          leftMargin=20*mm, rightMargin=20*mm,
                          topMargin=15*mm, bottomMargin=15*mm)
    story = []
    
    # Define styles
    styles = getSampleStyleSheet()
    
    # School header style
    school_style = ParagraphStyle(
        'SchoolHeader',
        parent=styles['Heading1'],
        fontSize=14,
        alignment=1,
        spaceAfter=6,
        textColor=colors.HexColor('#2c3e50'),
        fontName='Helvetica-Bold'
    )
    
    # Report title style
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
    
    # Section header style
    section_style = ParagraphStyle(
        'Section',
        parent=styles['Heading2'],
        fontSize=12,
        spaceBefore=12,
        spaceAfter=6,
        textColor=colors.HexColor('#16a085'),
        fontName='Helvetica-Bold'
    )
    
    # Bullet point style
    bullet_style = ParagraphStyle(
        'Bullet',
        parent=styles['Normal'],
        fontSize=10,
        leftIndent=12,
        spaceAfter=4,
        bulletIndent=6,
        textColor=colors.HexColor('#34495e'),
        fontName='Helvetica'
    )
    
    # Footer style
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        alignment=2,
        textColor=colors.HexColor('#7f8c8d'),
        fontName='Helvetica-Oblique'
    )
    
    # ======================
    # HEADER SECTION
    # ======================
    
    # Create header table with logo and school info
   # Corrected header section code:
header_table_data = []

# Add logo if exists
if os.path.exists(logo_path):
    logo = Image(logo_path, width=1.5*inch, height=1.5*inch)
    logo.hAlign = 'LEFT'
    header_table_data.append([logo, ""])
else:
    header_table_data.append(["", ""])

# Create school information Paragraph objects first
school_name = Paragraph("<b>SCHOOL NAME</b>", school_style)
school_address = Paragraph("123 Education Street, Learning City", school_style)
term_year = Paragraph(f"Term: {report_meta.get('term', '1')} | Year: {report_meta.get('year', str(datetime.now().year))}", school_style)
class_info = Paragraph(f"Class: {report_meta.get('class', 'Grade')}", school_style)
report_title = Paragraph("STUDENT PROGRESS REPORT", title_style)

# Combine all elements with line breaks
school_info_combined = [school_name, school_address, term_year, class_info, report_title]
school_info_paragraph = Paragraph("<br/>".join([p.text for p in school_info_combined]), school_style)

header_table_data.append(["", school_info_paragraph, ""])

header_table = Table(header_table_data, colWidths=[1.5*inch, None, 1.5*inch])
header_table.setStyle(TableStyle([
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
]))

story.append(header_table)
story.append(Spacer(1, 0.2*inch))
    
    # ======================
    # STUDENT INFORMATION
    # ======================
    
student_info_table = Table([
    [Paragraph("<b>Student Name:</b>", student_style), Paragraph(student['name'], student_style)],
    [Paragraph("<b>Report Date:</b>", student_style), Paragraph(datetime.now().strftime("%B %d, %Y"), student_style)],
    [Paragraph("<b>Score:</b>", student_style), Paragraph(student['score'], student_style)]
], colWidths=[2*inch, 4*inch])

student_info_table.setStyle(TableStyle([
    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
]))

story.append(student_info_table)
story.append(Spacer(1, 0.3*inch))

# ======================
# REPORT CONTENT
# ======================

# What student learned
story.append(Paragraph("✅ <b>What the student has learned and done well:</b>", section_style))
if student['learned']:
    for item in student['learned']:
        story.append(Paragraph(f"• {item}", bullet_style))
else:
    story.append(Paragraph("No specific achievements noted yet.", bullet_style))

story.append(Spacer(1, 0.2*inch))

# Areas for improvement
story.append(Paragraph("❌ <b>Areas for improvement:</b>", section_style))
if student['improvement']:
    for item in student['improvement']:
        story.append(Paragraph(f"• {item}", bullet_style))
else:
    story.append(Paragraph("No specific improvement areas noted.", bullet_style))

# ======================
# FOOTER
# ======================

story.append(Spacer(1, 0.5*inch))
footer_text = f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')} by Academic Progress System"
story.append(Paragraph(footer_text, footer_style))

doc.build(story)

def generate_all_reports(text_file_path, logo_path, report_meta=None):
    """
    Generate PDF reports for all students in gen_reports folder
    report_meta should contain: page_size, orientation, term, year, class
    """
    if report_meta is None:
        report_meta = {
            'page_size': 'A4',
            'orientation': 'portrait',
            'term': '1',
            'year': str(datetime.now().year),
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
        # Create a valid filename
        filename = re.sub(r'[^\w\s-]', '', student['name']).strip().lower()
        filename = re.sub(r'[-\s]+', '_', filename) + '_progress_report.pdf'
        full_path = os.path.join(output_folder, filename)
        
        print(f"Generating report for {student['name']}...")
        create_student_report(student, full_path, logo_path, report_meta)
        
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
        'logo_path': "logo.png",  # Path to your logo image
        'report_meta': {
            'page_size': 'A5',  # 'letter' or 'A4'
            'orientation': 'portrait',  # 'portrait' or 'landscape'
            'term': '2',
            'year': '2025',
            'class': 'Year 8'
        }
    }
    
    generate_all_reports(
        text_file_path=config['text_file_path'],
        logo_path=config['logo_path'],
        
        report_meta=config['report_meta']
    )