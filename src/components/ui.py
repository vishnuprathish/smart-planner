import base64

def get_pdf_download_link(pdf_path: str, link_text: str) -> str:
    """Generate a styled download link for the PDF."""
    with open(pdf_path, "rb") as f:
        pdf_data = f.read()
    b64_pdf = base64.b64encode(pdf_data).decode('utf-8')
    
    return f'''
        <a href="data:application/pdf;base64,{b64_pdf}" 
           download="strategic_plan.pdf" 
           class="download-button">
            {link_text}
        </a>
    '''
