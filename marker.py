import os
import re
from bs4 import BeautifulSoup

SUBMISSIONS_DIR = "Submissions"

# Define required HTML and CSS elements
required_html_elements = ["h1", "h2", "p", "nav", "img"]
required_css_properties = [
    "font-family", "background-color", "background-image", "padding", "margin",
    "display", "align-items", "color", "justify-content"
]
required_form_elements = ["input",  "button", "label"]

def check_html(file_path):
    """Checks for required HTML elements and forms in a given HTML file."""
    with open(file_path, "r", encoding="utf-8") as file:
        soup = BeautifulSoup(file, "html.parser")

    present_elements = {tag: bool(soup.find(tag)) for tag in required_html_elements}
    missing_elements = [tag for tag, exists in present_elements.items() if not exists]

    form_found = bool(soup.find("form"))
    form_elements_found = {tag: bool(soup.find(tag)) for tag in required_form_elements} if form_found else {}
    missing_form_elements = [tag for tag, exists in form_elements_found.items() if not exists] if form_found else []

    return present_elements, missing_elements, form_found, form_elements_found, missing_form_elements

def check_css(file_path):
    """Checks for required CSS properties in a given CSS file."""
    with open(file_path, "r", encoding="utf-8") as file:
        css_content = file.read()
    
    present_css = {prop: bool(re.search(rf"{prop}\s*:", css_content)) for prop in required_css_properties}
    missing_css = [prop for prop, exists in present_css.items() if not exists]

    return present_css, missing_css

def check_student_submission(student_folder):
    """Checks all student files and generates a structured progress report."""
    css_file = os.path.join(student_folder, "style.css")
    present_html_elements = {}
    missing_html_elements = set(required_html_elements)
    form_found = False
    form_elements_found = {}
    missing_form_elements = set(required_form_elements)

    # Check all HTML files
    for file in os.listdir(student_folder):
        if file.endswith(".html"):
            present, missing, has_form, form_found_elements, missing_form = check_html(os.path.join(student_folder, file))
            
            # Update main records
            present_html_elements.update({k: v for k, v in present.items() if v})
            missing_html_elements -= set(present_html_elements.keys())

            if has_form:
                form_found = True
                form_elements_found.update({k: v for k, v in form_found_elements.items() if v})
                missing_form_elements -= set(form_elements_found.keys())

    # Check CSS file
    present_css = {}
    missing_css = required_css_properties  # Assume missing unless checked
    if os.path.exists(css_file):
        present_css, missing_css = check_css(css_file)

    # Generate feedback
    feedback = {
        "Positive": [],
        "Improvement Needed": []
    }

    # HTML feedback
    if present_html_elements:
        feedback["Positive"].append(f"Understands basic HTML structure, using: {', '.join(present_html_elements.keys())}.")
    if missing_html_elements:
        feedback["Improvement Needed"].append(f"Needs to include missing HTML elements: {', '.join(missing_html_elements)}.")

    # Form feedback
    if form_found:
        if form_elements_found:
            feedback["Positive"].append(f"Has learned how to create a form with elements: {', '.join(form_elements_found.keys())}.")
        if missing_form_elements:
            feedback["Improvement Needed"].append(f"Form is missing elements: {', '.join(missing_form_elements)}.")
    else:
        feedback["Improvement Needed"].append("Has not yet added a form to their project.")

    # CSS feedback
    if present_css:
        applied_css = [prop for prop, exists in present_css.items() if exists]
        if applied_css:
            feedback["Positive"].append(f"Applied CSS styles correctly, including: {', '.join(applied_css)}.")
    if missing_css:
        feedback["Improvement Needed"].append(f"Needs to apply missing CSS properties: {', '.join(missing_css)}.")

    # Calculate score
    score = 100 - (len(missing_html_elements) * 5) - (len(missing_css) * 5) - (len(missing_form_elements) * 3)
    score = max(0, score)  # Ensure the score doesn't go below 0

    return score, feedback

def generate_report():
    """Processes all student submissions and generates a progress report."""
    results = {}
    for student in os.listdir(SUBMISSIONS_DIR):
        student_path = os.path.join(SUBMISSIONS_DIR, student)
        if os.path.isdir(student_path):
            score, feedback = check_student_submission(student_path)
            results[student] = {"Score": score, "Feedback": feedback}

    # Format report
    report_text = ""
    for student, result in results.items():
        report_text += f"Student: {student}\n"
        report_text += f"Score: {result['Score']}/100\n\n"
        
        report_text += "✅ **What the student has learned and done well:**\n"
        for item in result["Feedback"]["Positive"]:
            report_text += f" - {item}\n"

        report_text += "\n❌ **Areas for improvement:**\n"
        for item in result["Feedback"]["Improvement Needed"]:
            report_text += f" - {item}\n"

        report_text += "\n" + "="*50 + "\n\n"

    with open("Student_Progress_Report.txt", "w", encoding="utf-8") as file:
        file.write(report_text)

    print("Progress report generated: Student_Progress_Report.txt")

# Run script
if __name__ == "__main__":
    generate_report()
