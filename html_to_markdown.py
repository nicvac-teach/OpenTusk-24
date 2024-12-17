from bs4 import BeautifulSoup
import re

def convert_strong(tag):
    return f'**{tag.get_text().strip()}**'

def convert_em(tag):
    return f'*{tag.get_text().strip()}*'

def convert_a(tag):
    text = tag.get_text().strip()
    href = tag.get('href', '')
    return f'[{text}]({href})'

def convert_lists(tag):
    items = []
    for li in tag.find_all('li', recursive=False):
        items.append(f"* {li.get_text().strip()}")
    return '\n'.join(items)

def convert_headers(tag):
    level = int(tag.name[1])
    return f"{'#' * level} {tag.get_text().strip()}"

def convert_table(tag):
    rows = []
    # Gestisce l'header della tabella
    header_row = []
    separator_row = []
    
    # Cerca le intestazioni della tabella
    headers = tag.find_all('th')
    if headers:
        for th in headers:
            header_text = th.get_text().strip()
            header_row.append(header_text)
            separator_row.append('-' * max(len(header_text), 3))
        rows.append('| ' + ' | '.join(header_row) + ' |')
        rows.append('| ' + ' | '.join(separator_row) + ' |')
    
    # Gestisce le righe della tabella
    for tr in tag.find_all('tr'):
        cells = tr.find_all(['td'])
        if cells:
            row = []
            for cell in cells:
                row.append(cell.get_text().strip())
            rows.append('| ' + ' | '.join(row) + ' |')
    
    return '\n'.join(rows)

def html_to_markdown(html):
    soup = BeautifulSoup(html, 'html.parser')
    markdown = []
    
    for tag in soup.find_all(True):
        if tag.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            markdown.append(convert_headers(tag))
        elif tag.name == 'p':
            markdown.append(tag.get_text().strip())
        elif tag.name == 'strong' or tag.name == 'b':
            markdown.append(convert_strong(tag))
        elif tag.name == 'em' or tag.name == 'i':
            markdown.append(convert_em(tag))
        elif tag.name == 'a':
            markdown.append(convert_a(tag))
        elif tag.name in ['ul', 'ol']:
            markdown.append(convert_lists(tag))
        elif tag.name == 'table':
            markdown.append(convert_table(tag))
    
    return '\n\n'.join(markdown)

def format_markdown_file(file_path):
    try:
        import mdformat
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        formatted_content = mdformat.text(content)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(formatted_content)
            
    except ImportError:
        print("ATTENZIONE: mdformat non installato. Esegui: pip install mdformat")
        return False
    except Exception as e:
        print(f"Errore durante la formattazione: {str(e)}")
        return False
    return True

def convert_file(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as f:
        html = f.read()
    
    markdown = html_to_markdown(html)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(markdown)
    
    # Applica la formattazione al file markdown
    format_markdown_file(output_file)

if __name__ == '__main__':
    import os
    import sys

    # Constants for input and output directories
    INPUT_DIR = 'html'
    OUTPUT_DIR = 'md'

    opzione = int(input("Vuoi convertire un file singolo o una cartella? (file(1)/cartella(2)): "))
    
    if opzione == 1:
        if len(sys.argv) != 3:
            print("Uso: python html_to_markdown.py input.html output.md")
            sys.exit(1)
        convert_file(sys.argv[1], sys.argv[2])
    
    elif opzione == 2:
        if not os.path.exists(OUTPUT_DIR):
            os.makedirs(OUTPUT_DIR)
            
        for filename in os.listdir(INPUT_DIR):
            if filename.endswith('.html'):
                input_path = os.path.join(INPUT_DIR, filename)
                output_path = os.path.join(OUTPUT_DIR, filename.replace('.html', '.md'))
                convert_file(input_path, output_path)
                print(f"Convertito: {filename}")
    
    else:
        print("Opzione non valida")
        sys.exit(1)
