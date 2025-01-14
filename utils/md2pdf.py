import pdfkit
from markdown import markdown
import mdformat
from pathlib import Path
import tempfile
import os

def markdown_to_pdf(input_path: str, output_path: str = None, style: str = "professional") -> str:
    """Convert a markdown file to PDF using pdfkit (wkhtmltopdf).
    
    Args:
        input_path: Path to the markdown file
        output_path: Optional path for the output PDF file
        style: Style preset ("professional", "compact", "modern")
    
    Returns:
        str: Path to the generated PDF file
    """
    config = pdfkit.configuration(wkhtmltopdf=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe')
    
    # Configurable parameters with smaller fonts
    STYLES = {
        "professional": {
            "font_size_base": "10.5pt",
            "font_size_h1": "15pt",
            "font_size_h2": "12pt",
            "font_size_h3": "11pt",
            "line_height": "1.4",
            "margins": "18mm",
            "max_width": "21cm",
        },
        "compact": {
            "font_size_base": "9.5pt",
            "font_size_h1": "13pt",
            "font_size_h2": "11pt",
            "font_size_h3": "10pt",
            "line_height": "1.35",
            "margins": "15mm",
            "max_width": "21cm",
        },
        "modern": {
            "font_size_base": "12pt",
            "font_size_h1": "18pt",
            "font_size_h2": "14pt",
            "font_size_h3": "13pt",
            "line_height": "1.6",
            "margins": "20mm",
            "max_width": "21cm",
        }
    }
    
    # Get style parameters
    style_params = STYLES.get(style, STYLES["professional"])
    
    # Read and format markdown content
    with open(input_path, 'r', encoding='utf-8') as f:
        md_content = f.read()
         
    # Format markdown for consistency
    formatted_md = mdformat.text(
        md_content,
        options={
            "wrap": "no",
            "number": False,
        }
    )
    
    # Convert markdown to HTML with extra features
    html_content = markdown(
        formatted_md,
        extensions=[
            'extra',
            'codehilite',
            'fenced_code',
            'toc',
            'attr_list',
            'meta',
            'nl2br'
        ]
    )
    html_content = html_content.replace('\\', '')
    
    # CSS with configurable parameters
    css = f"""
        body {{ 
            font-family: 'Segoe UI', 'Calibri', 'Open Sans', sans-serif;
            line-height: {style_params['line_height']}; 
            margin: 0 auto;
            max-width: {style_params['max_width']};
            font-size: {style_params['font_size_base']};
            color: #2d2d2d;
            letter-spacing: 0.01em;
            text-align: justify;
            text-justify: inter-word;
        }}
        
        /* Section breaks control */
        h2 {{ 
            page-break-after: avoid;    /* Keep headers with their content */
        }}
        
        /* Keep sections together */
        h2, h2 + ul, h2 + p, h2 + .section-content {{
            page-break-inside: avoid;   /* Prevent splitting sections */
            display: block;             /* Back to block display */
            width: 100%;               /* Full width */
            overflow: visible;         /* Ensure text flows properly */
        }}
        
        /* Keep experience entries together */
        .experience-entry {{
            page-break-inside: avoid;
            margin: 0.6em 0;
            display: block;
            width: 100%;
        }}
        
        /* Keep lists together */
        ul {{
            page-break-inside: avoid;
            margin: 0.25em 0;
            padding-left: 1.3em;
            text-align: justify;
            display: block;
        }}
        
        /* Ensure proper text wrapping */
        p, li {{
            word-wrap: break-word;      /* Allow words to break */
            overflow-wrap: break-word;  /* Modern version of word-wrap */
            white-space: normal;        /* Normal text wrapping */
        }}
        
        /* Keep contact info together */
        .contact-info {{
            page-break-inside: avoid;   /* Prevent splitting contact info */
            margin: 0.4em 0;
            font-size: {style_params['font_size_base']};
            line-height: 1.4;
        }}
        
        /* Headers - keep left-aligned */
        h1 {{ 
            font-family: 'Segoe UI Light', 'Calibri Light', sans-serif;
            font-size: {style_params['font_size_h1']}; 
            margin-bottom: 0.3em;
            margin-top: 0.4em;
            color: #1a1a1a;
            font-weight: 400;
            text-align: left;
        }}
        h2 {{ 
            font-family: 'Segoe UI Semibold', 'Calibri', sans-serif;
            font-size: {style_params['font_size_h2']}; 
            margin-top: 0.7em;
            margin-bottom: 0.2em;
            color: #2d2d2d;
            border-bottom: 1px solid #ddd;
            padding-bottom: 2px;
            font-weight: 500;
            text-align: left;
        }}
        h3 {{ 
            font-family: 'Segoe UI', 'Calibri', sans-serif;
            font-size: {style_params['font_size_h3']}; 
            margin-top: 0.5em;
            margin-bottom: 0.15em;
            color: #404040;
            font-weight: 500;
            text-align: left;
        }}
        
        /* Paragraphs - ensure justification */
        p {{
            margin-top: 0.15em;
            margin-bottom: 0.3em;
            text-align: justify;
            text-justify: inter-word;
            hyphens: auto;
        }}
        
        /* Lists - keep left-aligned */
        li {{ 
            margin: 0.15em 0;
            line-height: 1.35;
            padding-bottom: 0.1em;
            text-align: justify;
            text-justify: inter-word;
        }}
        
        /* Links */
        a {{ 
            color: #2d5a9b;
            text-decoration: none;
            font-weight: 400;
        }}
        
        /* Emphasis and strong */
        em {{ font-style: italic; }}
        strong {{ 
            font-family: 'Segoe UI Semibold', 'Calibri', sans-serif;
            font-weight: 500;
            color: #2d2d2d;
        }}
    """
    
    # PDF generation options
    options = {
        # Page setup
        'page-size': 'A4',
        'margin-top': style_params['margins'],
        'margin-right': style_params['margins'],
        'margin-bottom': style_params['margins'],
        'margin-left': style_params['margins'],
        
        # Content rendering
        'encoding': 'UTF-8',
        'no-outline': None,
        'enable-local-file-access': None,
        
        # Print options
        'print-media-type': None,
        'enable-smart-shrinking': True,
        
        # Quality settings
        'image-quality': '100',
        'image-dpi': '300',
        
        # Text rendering
        'minimum-font-size': '8',
        
        # Links
        'enable-external-links': True,
        'enable-internal-links': True,
    }
    
    # Create complete HTML document
    full_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>{css}</style>
    </head>
    <body>
        {html_content}
    </body>
    </html>
    """
    
    # Create temporary HTML file
    with tempfile.NamedTemporaryFile(suffix='.html', mode='w', encoding='utf-8', delete=False) as temp:
        temp.write(full_html)
        temp_path = temp.name
    
    try:
        # Convert HTML to PDF using pdfkit
        pdfkit.from_file(temp_path, output_path, options=options, configuration=config)
    finally:
        # Clean up temporary file
        Path(temp_path).unlink()
    
    return output_path

if __name__ == "__main__":
    # Example usage with different styles
    markdown_to_pdf("cv_diane.md", "resume_professional_diane.pdf", "professional")



