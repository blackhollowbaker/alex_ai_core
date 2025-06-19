# app/utils/report_generator.py

from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
import os
from datetime import datetime

def generate_pdf_report(data, output_path="summary_report.pdf"):
    env = Environment(loader=FileSystemLoader("app/templates"))
    template = env.get_template("summary_template.html")
    
    html_content = template.render(data=data, date=datetime.now().strftime("%Y-%m-%d"))
    
    HTML(string=html_content).write_pdf(output_path)
    
    return output_path
