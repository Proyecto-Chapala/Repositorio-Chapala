import os
import re
import subprocess

def markdown_to_html(md_text):
    lines = md_text.split('\n')
    html_parts = []
    
    in_code_block = False
    code_block_lang = ''
    code_buffer = []
    
    in_table = False
    table_buffer = []
    
    in_list = False
    list_type = None # 'ul' or 'ol'
    
    in_blockquote = False
    blockquote_buffer = []
    
    def flush_list():
        nonlocal in_list, list_type
        if in_list:
            html_parts.append(f"</{list_type}>")
            in_list = False
            list_type = None

    def flush_table():
        nonlocal in_table, table_buffer
        if in_table and table_buffer:
            header_row = table_buffer[0]
            # row 1 is delimiter (|---|---|)
            body_rows = table_buffer[2:] if len(table_buffer) > 2 else []
            
            table_html = ['<div class="table-wrap"><table><thead><tr>']
            th_cells = [c.strip() for c in header_row.strip().strip('|').split('|')]
            for th in th_cells:
                table_html.append(f'<th>{inline_formatting(th)}</th>')
            table_html.append('</tr></thead><tbody>')
            
            for row in body_rows:
                if not row.strip() or not '|' in row:
                    continue
                td_cells = [c.strip() for c in row.strip().strip('|').split('|')]
                table_html.append('<tr>')
                for td in td_cells:
                    table_html.append(f'<td>{inline_formatting(td)}</td>')
                table_html.append('</tr>')
            table_html.append('</tbody></table></div>')
            html_parts.append('\n'.join(table_html))
            table_buffer = []
            in_table = False

    def flush_blockquote():
        nonlocal in_blockquote, blockquote_buffer
        if in_blockquote and blockquote_buffer:
            content = '\n'.join(blockquote_buffer)
            alert_type = 'note'
            alert_title = 'Nota'
            
            if '[!NOTE]' in content:
                alert_type = 'note'
                alert_title = 'Nota'
                content = content.replace('[!NOTE]', '').strip()
            elif '[!IMPORTANT]' in content:
                alert_type = 'important'
                alert_title = 'Importante'
                content = content.replace('[!IMPORTANT]', '').strip()
            elif '[!WARNING]' in content:
                alert_type = 'warning'
                alert_title = 'Advertencia'
                content = content.replace('[!WARNING]', '').strip()
            elif '[!CAUTION]' in content:
                alert_type = 'caution'
                alert_title = 'Precaución'
                content = content.replace('[!CAUTION]', '').strip()
            elif '[!TIP]' in content:
                alert_type = 'tip'
                alert_title = 'Consejo'
                content = content.replace('[!TIP]', '').strip()
                
            formatted = inline_formatting(content).replace('\n', '<br>')
            html_parts.append(f'<div class="callout callout-{alert_type}"><div class="callout-title">{alert_title}</div><div class="callout-body">{formatted}</div></div>')
            blockquote_buffer = []
            in_blockquote = False

    for line in lines:
        stripped = line.strip()
        
        # Code blocks
        if stripped.startswith('```'):
            if in_code_block:
                code_content = '\n'.join(code_buffer)
                code_content = code_content.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                html_parts.append(f'<pre><code class="lang-{code_block_lang}">{code_content}</code></pre>')
                code_buffer = []
                in_code_block = False
            else:
                flush_list()
                flush_table()
                flush_blockquote()
                in_code_block = True
                code_block_lang = stripped[3:].strip()
            continue
            
        if in_code_block:
            code_buffer.append(line)
            continue
            
        # Table lines
        if stripped.startswith('|') and stripped.endswith('|'):
            flush_list()
            flush_blockquote()
            in_table = True
            table_buffer.append(stripped)
            continue
        elif in_table:
            flush_table()

        # Blockquote lines
        if stripped.startswith('>'):
            flush_list()
            in_blockquote = True
            bq_text = stripped[1:].strip()
            blockquote_buffer.append(bq_text)
            continue
        elif in_blockquote:
            flush_blockquote()

        # Blank line
        if not stripped:
            flush_list()
            flush_table()
            flush_blockquote()
            continue

        # Horizontal rule
        if stripped in ['---', '***', '___']:
            flush_list()
            html_parts.append('<hr>')
            continue

        # Headings
        if stripped.startswith('# '):
            flush_list()
            title = stripped[2:].strip()
            html_parts.append(f'<h1 class="chapter-title">{inline_formatting(title)}</h1>')
            continue
        elif stripped.startswith('## '):
            flush_list()
            title = stripped[3:].strip()
            html_parts.append(f'<h2 class="section-title">{inline_formatting(title)}</h2>')
            continue
        elif stripped.startswith('### '):
            flush_list()
            title = stripped[4:].strip()
            html_parts.append(f'<h3 class="subsection-title">{inline_formatting(title)}</h3>')
            continue
        elif stripped.startswith('#### '):
            flush_list()
            title = stripped[5:].strip()
            html_parts.append(f'<h4>{inline_formatting(title)}</h4>')
            continue

        # Unordered list
        if stripped.startswith('* ') or stripped.startswith('- '):
            item_text = stripped[2:].strip()
            if not in_list or list_type != 'ul':
                flush_list()
                html_parts.append('<ul>')
                in_list = True
                list_type = 'ul'
            html_parts.append(f'<li>{inline_formatting(item_text)}</li>')
            continue

        # Ordered list
        m_ol = re.match(r'^(\d+)\.\s+(.*)$', stripped)
        if m_ol:
            item_text = m_ol.group(2).strip()
            if not in_list or list_type != 'ol':
                flush_list()
                html_parts.append('<ol>')
                in_list = True
                list_type = 'ol'
            html_parts.append(f'<li>{inline_formatting(item_text)}</li>')
            continue

        # Regular paragraph
        flush_list()
        html_parts.append(f'<p>{inline_formatting(stripped)}</p>')

    flush_list()
    flush_table()
    flush_blockquote()
    return '\n'.join(html_parts)

def inline_formatting(text):
    # LaTeX display math: $$...$$
    def repl_display_math(m):
        raw = m.group(1).strip()
        raw = raw.replace('\\text{', '').replace('}', '').replace('\\times', '×').replace('\\frac', '').replace('\\theta_', 'θ_')
        return f'<div class="math-block">{raw}</div>'
    text = re.sub(r'\$\$(.*?)\$\$', repl_display_math, text)
    
    # Inline math: $...$
    def repl_inline_math(m):
        raw = m.group(1).strip()
        raw = raw.replace('\\text{', '').replace('}', '').replace('\\times', '×').replace('\\frac', '').replace('\\theta_', 'θ_')
        return f'<span class="math-inline"><i>{raw}</i></span>'
    text = re.sub(r'\$(.*?)\$', repl_inline_math, text)

    # Bold italic
    text = re.sub(r'\*\*\*(.*?)\*\*\*', r'<strong><em>\1</em></strong>', text)
    # Bold
    text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
    # Italic
    text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', text)
    # Inline code
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
    # Links
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', text)
    
    return text

def build_full_html():
    with open('docs/MANUAL_USUARIO.md', 'r', encoding='utf-8') as f:
        md_text = f.read()
        
    body_html = markdown_to_html(md_text)
    
    html_template = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>Manual de Usuario Maestro — Sistema CHAPALA</title>
<style>
  @page {{
    size: letter portrait;
    margin: 20mm 15mm 20mm 15mm;
    @bottom-left {{
      content: "All Oil Services, C.A. • Sistema CHAPALA";
      font-size: 8.5pt;
      font-family: 'Segoe UI', Arial, sans-serif;
      color: #64748b;
    }}
    @bottom-right {{
      content: "Página " counter(page);
      font-size: 8.5pt;
      font-family: 'Segoe UI', Arial, sans-serif;
      color: #64748b;
      font-weight: 600;
    }}
  }}

  * {{
    box-sizing: border-box;
  }}

  body {{
    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, Helvetica, Arial, sans-serif;
    color: #1e293b;
    line-height: 1.55;
    font-size: 10pt;
    margin: 0;
    padding: 0;
  }}

  /* Portada Ejecutiva */
  .cover-page {{
    page-break-after: always;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    height: 90vh;
    padding: 30px 20px;
    border: 3px solid #14283b;
    background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
    position: relative;
  }}

  .cover-header {{
    border-bottom: 3px solid #d97706;
    padding-bottom: 20px;
  }}

  .cover-brand {{
    font-size: 24pt;
    font-weight: 900;
    color: #14283b;
    letter-spacing: .05em;
    display: flex;
    align-items: center;
    gap: 12px;
  }}

  .cover-brand span {{
    color: #d97706;
  }}

  .cover-company {{
    font-size: 12pt;
    font-weight: 600;
    color: #475569;
    margin-top: 5px;
    text-transform: uppercase;
    letter-spacing: .08em;
  }}

  .cover-body {{
    margin: auto 0;
  }}

  .cover-title {{
    font-size: 28pt;
    font-weight: 900;
    color: #0f172a;
    line-height: 1.15;
    margin-bottom: 15px;
  }}

  .cover-subtitle {{
    font-size: 14pt;
    font-weight: 500;
    color: #334155;
    line-height: 1.4;
    border-left: 4px solid #d97706;
    padding-left: 15px;
    margin-bottom: 25px;
  }}

  .cover-badge {{
    display: inline-block;
    background: #14283b;
    color: #ffffff;
    font-size: 10pt;
    font-weight: 700;
    padding: 6px 16px;
    border-radius: 4px;
    text-transform: uppercase;
    letter-spacing: .06em;
  }}

  .cover-footer {{
    border-top: 1px solid #cbd5e1;
    padding-top: 20px;
    display: flex;
    justify-content: space-between;
    font-size: 9.5pt;
    color: #475569;
  }}

  .cover-footer strong {{
    color: #0f172a;
  }}

  /* Encabezados y Secciones */
  h1.chapter-title {{
    color: #14283b;
    font-size: 18pt;
    font-weight: 800;
    border-bottom: 2px solid #14283b;
    padding-bottom: 8px;
    margin-top: 30px;
    margin-bottom: 14px;
    page-break-before: always;
  }}

  h2.section-title {{
    color: #1e3a5f;
    font-size: 13pt;
    font-weight: 800;
    margin-top: 22px;
    margin-bottom: 10px;
    border-left: 4px solid #d97706;
    padding-left: 10px;
  }}

  h3.subsection-title {{
    color: #334155;
    font-size: 11pt;
    font-weight: 700;
    margin-top: 16px;
    margin-bottom: 6px;
  }}

  h4 {{
    font-size: 10pt;
    font-weight: 700;
    color: #475569;
    margin-top: 12px;
    margin-bottom: 4px;
  }}

  p {{
    margin-top: 0;
    margin-bottom: 10px;
    text-align: justify;
  }}

  ul, ol {{
    margin-top: 4px;
    margin-bottom: 12px;
    padding-left: 24px;
  }}

  li {{
    margin-bottom: 4px;
  }}

  /* Tablas Ejecutivas */
  .table-wrap {{
    margin: 12px 0 16px 0;
    width: 100%;
    page-break-inside: avoid;
  }}

  table {{
    width: 100%;
    border-collapse: collapse;
    font-size: 9pt;
    background: #ffffff;
  }}

  th {{
    background: #14283b;
    color: #ffffff;
    font-weight: 700;
    text-align: left;
    padding: 7px 10px;
    border: 1px solid #14283b;
    font-size: 9pt;
  }}

  td {{
    padding: 6px 10px;
    border: 1px solid #cbd5e1;
    vertical-align: top;
  }}

  tr:nth-child(even) td {{
    background: #f8fafc;
  }}

  /* Callouts & Alertas */
  .callout {{
    margin: 12px 0 16px 0;
    padding: 10px 14px;
    border-radius: 6px;
    page-break-inside: avoid;
    font-size: 9.5pt;
  }}

  .callout-title {{
    font-weight: 800;
    margin-bottom: 4px;
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 9.5pt;
    text-transform: uppercase;
    letter-spacing: .03em;
  }}

  .callout-note {{
    background: #eff6ff;
    border-left: 4px solid #3b82f6;
    color: #1e3a8a;
  }}
  .callout-note .callout-title {{ color: #1d4ed8; }}

  .callout-important {{
    background: #fffbeb;
    border-left: 4px solid #f59e0b;
    color: #78350f;
  }}
  .callout-important .callout-title {{ color: #b45309; }}

  .callout-warning {{
    background: #fef2f2;
    border-left: 4px solid #ef4444;
    color: #7f1d1d;
  }}
  .callout-warning .callout-title {{ color: #b91c1c; }}

  .callout-caution {{
    background: #fdf2f8;
    border-left: 4px solid #ec4899;
    color: #831843;
  }}
  .callout-caution .callout-title {{ color: #be185d; }}

  .callout-tip {{
    background: #f0fdf4;
    border-left: 4px solid #10b981;
    color: #064e3b;
  }}
  .callout-tip .callout-title {{ color: #047857; }}

  /* Código y Cajas Técnicas */
  pre {{
    background: #0f172a;
    color: #e2e8f0;
    padding: 10px 14px;
    border-radius: 6px;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 8.5pt;
    line-height: 1.4;
    overflow-x: auto;
    margin: 12px 0;
    page-break-inside: avoid;
  }}

  code {{
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 8.8pt;
    background: #f1f5f9;
    color: #b45309;
    padding: 2px 5px;
    border-radius: 4px;
    border: 1px solid #e2e8f0;
  }}

  pre code {{
    background: transparent;
    border: none;
    color: inherit;
    padding: 0;
  }}

  /* Matemáticas y Fórmulas */
  .math-block {{
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-left: 3px solid #d97706;
    padding: 8px 12px;
    margin: 8px 0;
    font-family: 'Cambria Math', 'Georgia', serif;
    font-size: 10pt;
    color: #0f172a;
    text-align: center;
    page-break-inside: avoid;
  }}

  .math-inline {{
    font-family: 'Cambria Math', 'Georgia', serif;
    color: #1e3a5f;
    font-weight: 600;
  }}

  hr {{
    border: none;
    border-top: 1px solid #e2e8f0;
    margin: 20px 0;
  }}
</style>
</head>
<body>

<!-- PORTADA -->
<div class="cover-page">
  <div class="cover-header">
    <div class="cover-brand">CHAPALA <span>OPERACIONES</span></div>
    <div class="cover-company">All Oil Services, C.A. &bull; División Técnica y de Ingeniería</div>
  </div>

  <div class="cover-body">
    <div class="cover-title">MANUAL DE USUARIO MAESTRO</div>
    <div class="cover-subtitle">
      Plataforma Integral de Ingeniería, Inventario y Reportes Diarios de Fluidos de Perforación (Arquitectura ONE-TRAX)
    </div>
    <div class="cover-badge">Versión 2.0 &bull; Refactorización y Producción</div>
  </div>

  <div class="cover-footer">
    <div><strong>Proyecto:</strong> Sistema CHAPALA</div>
    <div><strong>Fecha de Emisión:</strong> Septiembre 2026</div>
    <div><strong>Entorno:</strong> Web Multi-Usuario (Django &bull; PostgreSQL)</div>
  </div>
</div>

<!-- CONTENIDO PRINCIPAL -->
<div class="content-body">
{body_html}
</div>

</body>
</html>"""
    
    with open('docs/MANUAL_USUARIO.html', 'w', encoding='utf-8') as f:
        f.write(html_template)
    print("Generated docs/MANUAL_USUARIO.html successfully!")

if __name__ == '__main__':
    build_full_html()
