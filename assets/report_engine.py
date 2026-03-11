import subprocess
import html
import sys
import os

# Parâmetros Passados pelo Gemini (ou defaults)
COMMIT_INICIAL = os.getenv("COMMIT_INICIAL", "f6ae3c0a1301e28720dd0ca884a963b1635b95cf")
COMMIT_FINAL = os.getenv("COMMIT_FINAL", "HEAD")
OUTPUT_FILE = os.getenv("OUTPUT_FILE", "relatorio_estudo_commits.html")

def run_cmd(cmd):
    try:
        return subprocess.check_output(cmd, shell=True, text=True, encoding='utf-8', errors='replace').strip()
    except subprocess.CalledProcessError:
        return ""

git_log_out = run_cmd(f"git log {COMMIT_INICIAL}^..{COMMIT_FINAL} --format='%H|%s'")
lines = git_log_out.split('\n')
lines.reverse()

commit_data = []
for line in lines:
    if not line.strip(): continue
    parts = line.split('|', 1)
    if len(parts) == 2:
        commit_data.append((parts[0], parts[1]))

branch = run_cmd("git rev-parse --abbrev-ref HEAD")
if not branch: branch = "Desconhecida"

# Cálculo da Hierarquia Dinâmica com Datas
def get_date(commit_sha):
    return run_cmd(f"git log -1 --format=%cd --date=format:'%d/%m/%Y' {commit_sha}")

# Identificar o ponto entre Master e Intermediária (tentativa baseada em nomes comuns)
mbase_10_master = run_cmd("git merge-base origin/10.0.x origin/master")
if not mbase_10_master: mbase_10_master = run_cmd("git merge-base HEAD origin/master")

date_10_master = get_date(mbase_10_master) if mbase_10_master else "????"

# Identificar o ponto entre Intermediária e a Branch Atual
mbase_atual_10 = run_cmd(f"git merge-base HEAD origin/10.0.x")
if not mbase_atual_10: mbase_atual_10 = mbase_10_master

date_atual_10 = get_date(mbase_atual_10) if mbase_atual_10 else "????"

# Hierarquia visual
hierarquia = f"master --({date_10_master})--> 10.0.x --({date_atual_10})--> {branch}"

remote = run_cmd(f"git config --get branch.{branch}.remote")
if not remote: remote = "origin"

def generate_analysis(msg):
    # Esta função será preenchida pelo Gemini CLI com base no commit específico
    # Por padrão, ela retorna placeholders para serem sobrescritos
    return "{{MOTIVACAO}}", "{{IMPLEMENTACAO}}", "{{CONCEITOS}}", "{{ALTERNATIVAS}}", "{{CONCLUSAO}}"

html_out = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Relatório de Estudo de Commits - Evolução Arquitetural</title>
<style>
    :root {{
        --bg-color: #f4f6f8;
        --sidebar-bg: #1e293b;
        --sidebar-text: #f8fafc;
        --text-color: #334155;
        --text-strong: #0f172a;
        --code-bg: #0d1117;
        --border-color: #cbd5e1;
        --diff-add: rgba(46, 160, 67, 0.15);
        --diff-del: rgba(248, 81, 73, 0.15);
        --diff-add-text: #3fb950;
        --diff-del-text: #ff7b72;
        --accent: #2563eb;
    }}
    body {{
        margin: 0;
        font-family: 'Inter', 'Segoe UI', sans-serif;
        display: flex;
        height: 100vh;
        overflow: hidden;
        background-color: var(--bg-color);
        color: var(--text-color);
        line-height: 1.6;
    }}
    
    .sidebar {{
        width: 350px;
        min-width: 150px;
        max-width: 600px;
        background-color: var(--sidebar-bg);
        color: var(--sidebar-text);
        display: flex;
        flex-direction: column;
        overflow: hidden;
        position: relative;
        box-shadow: 2px 0 10px rgba(0,0,0,0.1);
        z-index: 10;
        flex-shrink: 0;
    }}
    
    .resizer {{
        width: 6px;
        cursor: col-resize;
        background-color: transparent;
        transition: background-color 0.2s;
        flex-shrink: 0;
        z-index: 20;
    }}
    .resizer:hover, .resizer.dragging {{
        background-color: var(--accent);
    }}
    
    .sidebar-header {{
        padding: 20px;
        border-bottom: 1px solid rgba(255,255,255,0.1);
        background-color: #0f172a;
    }}
    .sidebar-header h2 {{ margin: 0 0 10px 0; font-size: 1.25rem; font-weight: 600; color: #fff; }}
    .sidebar-header p {{ margin: 5px 0 0 0; font-size: 0.85rem; color: #94a3b8; }}
    
    .nav-links {{
        flex: 1;
        overflow-y: auto;
        padding: 10px 0;
    }}
    .nav-links a {{
        display: block;
        padding: 12px 20px;
        color: #cbd5e1;
        text-decoration: none;
        font-size: 0.85rem;
        border-left: 4px solid transparent;
        white-space: normal;
        word-wrap: break-word;
        line-height: 1.4;
        transition: all 0.2s ease;
    }}
    .nav-links a:hover, .nav-links a:active {{
        background-color: rgba(255,255,255,0.05);
        border-left-color: var(--accent);
        color: #fff;
    }}
    
    .content {{
        flex: 1;
        overflow-y: auto;
        padding: 40px;
        scroll-behavior: smooth;
    }}
    .commit-section {{
        background: white;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05), 0 2px 4px -1px rgba(0,0,0,0.03);
        margin-bottom: 50px;
        border: 1px solid var(--border-color);
        overflow: hidden;
    }}
    .commit-header {{
        background-color: #f1f5f9;
        padding: 20px 30px;
        border-bottom: 1px solid var(--border-color);
    }}
    .commit-header h1 {{ 
        color: var(--text-strong); 
        font-size: 1.5rem; 
        margin: 0 0 10px 0; 
        line-height: 1.3;
    }}
    
    .commit-body {{ padding: 30px; }}
    
    h3 {{ 
        color: var(--accent); 
        margin-top: 0; 
        margin-bottom: 20px;
        font-size: 1.2rem;
        border-bottom: 2px solid #e2e8f0;
        padding-bottom: 8px;
    }}
    
    .topic {{ 
        margin-bottom: 20px; 
        background-color: #f8fafc;
        padding: 15px 20px;
        border-radius: 8px;
        border-left: 4px solid #cbd5e1;
    }}
    .topic strong {{ 
        color: var(--text-strong); 
        display: block; 
        margin-bottom: 8px; 
        font-size: 1.05rem;
    }}
    
    .conclusion {{
        background-color: #eff6ff;
        border-left: 4px solid var(--accent);
        padding: 15px 20px;
        border-radius: 8px;
        margin-bottom: 30px;
        margin-top: 30px;
    }}
    .conclusion strong {{ color: var(--accent); }}
    
    pre.code-diff {{
        background-color: var(--code-bg);
        color: #e6edf3;
        padding: 20px;
        border-radius: 8px;
        overflow-x: auto;
        font-family: 'Fira Code', 'Courier New', Courier, monospace;
        font-size: 0.85rem;
        line-height: 1.5;
        margin: 0;
        box-shadow: inset 0 2px 4px rgba(0,0,0,0.5);
    }}
    .diff-line {{ display: flex; }}
    .diff-line .text {{ padding-left: 5px; white-space: pre; }}
    .diff-line.add {{ background-color: var(--diff-add); display: block; }}
    .diff-line.add .text {{ color: var(--diff-add-text); }}
    .diff-line.del {{ background-color: var(--diff-del); display: block; }}
    .diff-line.del .text {{ color: var(--diff-del-text); }}
    .diff-line.info {{ color: #8b949e; font-style: italic; border-top: 1px dashed #30363d; margin-top: 10px; padding-top: 10px; display: block; }}
</style>
</head>
<body>

<div class="sidebar">
    <div class="sidebar-header">
        <h2>Aulas de Arquitetura</h2>
        <p><strong>Hierarquia:</strong> {hierarquia}</p>
        <p><strong>Remoto:</strong> {remote}</p>
    </div>
    <div class="nav-links">
"""

for i, (sha, msg) in enumerate(commit_data):
    html_out += f'        <a href="#aula-{sha}" title="{msg}">{i+1}. {html.escape(msg)}</a>\n'

html_out += """
    </div>
</div>
<div class="resizer" id="dragMe"></div>
<div class="content">
"""

for sha, msg in commit_data:
    try:
        diff_out = subprocess.check_output(f"git show {sha} --format=''", shell=True, text=True, encoding='utf-8', errors='replace')
    except subprocess.CalledProcessError:
        diff_out = "Não foi possível carregar o diff."

    diff_lines = diff_out.split('\n')
    
    formatted_diff = ""
    for line in diff_lines:
        safe_line = html.escape(line)
        if line.startswith('+') and not line.startswith('+++'):
            formatted_diff += f'<div class="diff-line add"><span class="text">{safe_line}</span></div>'
        elif line.startswith('-') and not line.startswith('---'):
            formatted_diff += f'<div class="diff-line del"><span class="text">{safe_line}</span></div>'
        elif line.startswith('diff ') or line.startswith('index ') or line.startswith('---') or line.startswith('+++') or line.startswith('@@ '):
            formatted_diff += f'<div class="diff-line info">{safe_line}</div>'
        else:
            formatted_diff += f'<div class="diff-line"><span class="text">{safe_line}</span></div>'

    # Gemini preencherá estes campos dinamicamente durante a execução da skill
    m, i, c, a, c_aula = generate_analysis(msg)

    html_out += f'''
    <div class="commit-section" id="aula-{sha}">
        <div class="commit-header">
            <h1>[{sha[:8]}] - {html.escape(msg)}</h1>
        </div>
        
        <div class="commit-body">
            <h3>Explicação Detalhada</h3>
            
            <div class="topic"><strong>Motivação:</strong><p>{m}</p></div>
            <div class="topic"><strong>Implementação:</strong><p>{i}</p></div>
            <div class="topic"><strong>Conceitos e Documentação:</strong><p>{c}</p></div>
            <div class="topic"><strong>Alternativas e Refatoração:</strong><p>{a}</p></div>
            
            <div class="conclusion">
                <p><strong>Conclusão da Aula:</strong> {c_aula}</p>
            </div>
            
            <h3>Código da Aula (Diff)</h3>
            <pre class="code-diff">{formatted_diff}</pre>
        </div>
    </div>
'''

html_out += """
</div>

<script>
    const resizer = document.getElementById('dragMe');
    const sidebar = resizer.previousElementSibling;
    let x = 0, w = 0;

    const mouseDownHandler = function (e) {
        x = e.clientX;
        w = parseInt(window.getComputedStyle(sidebar).width, 10);
        document.addEventListener('mousemove', mouseMoveHandler);
        document.addEventListener('mouseup', mouseUpHandler);
        resizer.classList.add('dragging');
        document.body.style.cursor = 'col-resize';
        document.body.style.userSelect = 'none';
    };

    const mouseMoveHandler = function (e) {
        const dx = e.clientX - x;
        const newWidth = w + dx;
        if (newWidth > 150 && newWidth < 600) {
            sidebar.style.width = `${newWidth}px`;
        }
    };

    const mouseUpHandler = function () {
        document.removeEventListener('mousemove', mouseMoveHandler);
        document.removeEventListener('mouseup', mouseUpHandler);
        resizer.classList.remove('dragging');
        document.body.style.cursor = 'default';
        document.body.style.userSelect = 'auto';
    };

    resizer.addEventListener('mousedown', mouseDownHandler);
</script>
</body>
</html>
"""

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write(html_out)

print(f"Relatório '{OUTPUT_FILE}' gerado com sucesso!")
