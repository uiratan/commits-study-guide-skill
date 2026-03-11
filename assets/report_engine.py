import subprocess
import html
import sys
import os

# Parâmetros Passados pelo Gemini
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

mbase_10_master = run_cmd("git merge-base origin/10.0.x origin/master")
date_10_master = get_date(mbase_10_master) if mbase_10_master else "????"
mbase_atual_10 = run_cmd("git merge-base HEAD origin/10.0.x")
date_atual_10 = get_date(mbase_atual_10) if mbase_atual_10 else "????"

hierarquia = f"master --({date_10_master})--> 10.0.x --({date_atual_10})--> {branch}"
remote = run_cmd(f"git config --get branch.{branch}.remote")
if not remote: remote = "origin"

def generate_analysis(msg):
    return "{{MOTIVACAO}}", "{{IMPLEMENTACAO}}", "{{CONCEITOS}}", "{{ALTERNATIVAS}}", "{{CONCLUSAO}}"

html_out = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Relatório de Estudo de Commits - Evolução Arquitetural</title>
<style>
    :root {{
        --bg-color: #ffffff;
        --sidebar-bg: #000000;
        --sidebar-text: #ffffff;
        --text-color: #353740;
        --text-strong: #000000;
        --code-bg: #0d1117;
        --border-color: #e5e5e5;
        --card-bg: #ffffff;
        --header-bg: #f7f7f8;
        --topic-bg: #ffffff;
        --conclusion-bg: #f7f7f8;
        --diff-add: rgba(16, 163, 127, 0.15);
        --diff-del: rgba(248, 81, 73, 0.15);
        --diff-add-text: #10a37f;
        --diff-del-text: #ff7b72;
        --accent: #10a37f;
    }}
    
    .dark-mode {{
        --bg-color: #050505;
        --text-color: #c5c5d2;
        --text-strong: #ffffff;
        --border-color: #2d2d2d;
        --card-bg: #000000;
        --header-bg: #0d0d0d;
        --topic-bg: #000000;
        --conclusion-bg: #0d0d0d;
        --accent: #10a37f;
    }}

    body {{
        margin: 0;
        font-family: 'Inter', -apple-system, system-ui, sans-serif;
        display: flex;
        height: 100vh;
        overflow: hidden;
        background-color: var(--bg-color);
        color: var(--text-color);
        line-height: 1.6;
        transition: background-color 0.2s;
    }}
    
    .sidebar {{
        width: 320px;
        min-width: 150px;
        max-width: 500px;
        background-color: var(--sidebar-bg);
        color: var(--sidebar-text);
        display: flex;
        flex-direction: column;
        overflow: hidden;
        position: relative;
        z-index: 10;
        flex-shrink: 0;
        border-right: 1px solid var(--border-color);
    }}
    
    .resizer {{
        width: 2px;
        cursor: col-resize;
        background-color: var(--border-color);
        transition: background-color 0.2s;
        flex-shrink: 0;
        z-index: 20;
    }}
    .resizer:hover, .resizer.dragging {{
        background-color: var(--accent);
        width: 4px;
    }}
    
    .sidebar-header {{
        padding: 32px 24px;
        background-color: var(--sidebar-bg);
    }}
    .sidebar-header h2 {{ 
        margin: 0 0 16px 0; 
        font-size: 1.1rem; 
        font-weight: 600; 
        letter-spacing: -0.02em;
        text-transform: uppercase;
        color: var(--accent);
    }}
    .sidebar-header p {{ 
        margin: 8px 0 0 0; 
        font-size: 0.75rem; 
        color: #8e8ea0;
        font-family: 'Courier New', monospace;
    }}
    
    .nav-links {{
        flex: 1;
        overflow-y: auto;
        padding: 0 12px 32px 12px;
    }}
    .nav-links a {{
        display: block;
        padding: 10px 16px;
        color: #acacbe;
        text-decoration: none;
        font-size: 0.85rem;
        border-radius: 6px;
        margin-bottom: 2px;
        white-space: normal;
        word-wrap: break-word;
        line-height: 1.4;
        transition: all 0.15s ease;
    }}
    .nav-links a:hover {{
        background-color: #202123;
        color: #fff;
    }}
    
    .content {{
        flex: 1;
        overflow-y: auto;
        padding: 64px 80px;
        scroll-behavior: smooth;
    }}
    .commit-section {{
        background: var(--card-bg);
        margin-bottom: 100px;
        max-width: 900px;
    }}
    .commit-header {{
        margin-bottom: 40px;
        padding-bottom: 24px;
        border-bottom: 1px solid var(--border-color);
    }}
    .commit-header h1 {{ 
        color: var(--text-strong); 
        font-size: 2.2rem; 
        margin: 0 0 16px 0; 
        line-height: 1.1;
        letter-spacing: -0.03em;
        font-weight: 700;
    }}
    .tech-summary {{
        font-size: 1.1rem;
        color: var(--accent);
        margin: 0;
        font-weight: 500;
    }}
    
    .commit-body {{ padding: 0; }}
    
    h3 {{ 
        color: var(--text-strong); 
        margin-top: 48px; 
        margin-bottom: 24px;
        font-size: 1.4rem;
        font-weight: 600;
        letter-spacing: -0.02em;
    }}
    
    .topic {{ 
        margin-bottom: 32px; 
        padding: 0;
    }}
    .topic strong {{ 
        color: var(--text-strong); 
        display: block; 
        margin-bottom: 12px; 
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #8e8ea0;
    }}
    .topic p {{ margin: 0; font-size: 1.05rem; }}
    
    .conclusion {{
        background-color: var(--conclusion-bg);
        border: 1px solid var(--border-color);
        padding: 24px;
        border-radius: 8px;
        margin: 48px 0;
    }}
    .conclusion p {{ margin: 0; font-size: 1rem; color: var(--text-strong); }}
    .conclusion strong {{ color: var(--accent); margin-right: 8px; }}

    .theme-toggle {{
        background: #202123;
        border: 1px solid #444654;
        color: #fff;
        padding: 10px 16px;
        border-radius: 6px;
        cursor: pointer;
        font-size: 0.75rem;
        margin-top: 24px;
        display: flex;
        align-items: center;
        gap: 8px;
        width: 100%;
        justify-content: center;
        transition: all 0.2s;
    }}
    .theme-toggle:hover {{ background: #444654; }}
    
    /* Code Diff Styles */
    pre.code-diff {{
        background-color: var(--code-bg);
        color: #e6edf3;
        padding: 24px;
        border-radius: 12px;
        overflow-x: auto;
        font-family: 'Fira Code', 'Menlo', monospace;
        font-size: 0.85rem;
        line-height: 1.6;
        margin: 0;
        border: 1px solid var(--border-color);
    }}
    .diff-line {{ display: flex; }}
    .diff-line .text {{ padding-left: 5px; white-space: pre; }}
    .diff-line.add {{ background-color: var(--diff-add); display: block; }}
    .diff-line.add .text {{ color: var(--diff-add-text); }}
    .diff-line.del {{ background-color: var(--diff-del); display: block; }}
    .diff-line.del .text {{ color: var(--diff-del-text); }}
    .diff-line.info {{ color: #565869; font-style: italic; border-top: 1px solid #2d2d2d; margin-top: 16px; padding-top: 16px; display: block; }}
    
    .diff-line.file-header {{
        background-color: rgba(16, 163, 127, 0.1);
        color: var(--accent);
        font-weight: 600;
        border: 1px solid var(--accent);
        border-radius: 4px;
        margin-top: 32px;
        padding: 8px 12px;
        display: block;
        font-size: 0.85rem;
    }}
    .diff-line.file-header:first-child {{ margin-top: 0; }}
</style>
</head>
<body>

<div class="sidebar">
    <div class="sidebar-header">
        <h2>Aulas de Arquitetura</h2>
        <p><strong>Hierarquia:</strong> {hierarquia}</p>
        <p><strong>Remoto:</strong> {remote}</p>
        <button class="theme-toggle" id="themeToggle">
            <span id="themeIcon">🌙</span> <span id="themeText">Modo Escuro</span>
        </button>
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
        if line.startswith('diff --git'):
            formatted_diff += f'<div class="diff-line file-header">{safe_line}</div>'
        elif line.startswith('+') and not line.startswith('+++'):
            formatted_diff += f'<div class="diff-line add"><span class="text">{safe_line}</span></div>'
        elif line.startswith('-') and not line.startswith('---'):
            formatted_diff += f'<div class="diff-line del"><span class="text">{safe_line}</span></div>'
        elif line.startswith('diff ') or line.startswith('index ') or line.startswith('---') or line.startswith('+++') or line.startswith('@@ '):
            formatted_diff += f'<div class="diff-line info">{safe_line}</div>'
        else:
            formatted_diff += f'<div class="diff-line"><span class="text">{safe_line}</span></div>'

    m, i, c, a, c_aula = generate_analysis(msg)

    html_out += f'''
    <div class="commit-section" id="aula-{sha}">
        <div class="commit-header">
            <h1>{html.escape(msg)}</h1>
            <p class="tech-summary">{sha[:8]}</p>
        </div>
        
        <div class="commit-body">
            <div class="topic"><strong>Motivação</strong><p>{m}</p></div>
            <div class="topic"><strong>Implementação</strong><p>{i}</p></div>
            <div class="topic"><strong>Conceitos e Documentação</strong><p>{c}</p></div>
            <div class="topic"><strong>Alternativas e Refatoração</strong><p>{a}</p></div>
            <div class="conclusion"><p><strong>Conclusão da Aula</strong> {c_aula}</p></div>
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
        if (newWidth > 150 && newWidth < 600) { sidebar.style.width = `${newWidth}px`; }
    };

    const mouseUpHandler = function () {
        document.removeEventListener('mousemove', mouseMoveHandler);
        document.removeEventListener('mouseup', mouseUpHandler);
        resizer.classList.remove('dragging');
        document.body.style.cursor = 'default';
        document.body.style.userSelect = 'auto';
    };

    resizer.addEventListener('mousedown', mouseDownHandler);

    // Theme Toggle Logic
    const themeToggle = document.getElementById('themeToggle');
    const themeIcon = document.getElementById('themeIcon');
    const themeText = document.getElementById('themeText');
    const body = document.body;

    themeToggle.addEventListener('click', () => {
        body.classList.toggle('dark-mode');
        const isDark = body.classList.contains('dark-mode');
        themeIcon.innerText = isDark ? '☀️' : '🌙';
        themeText.innerText = isDark ? 'Modo Claro' : 'Modo Escuro';
        localStorage.setItem('theme', isDark ? 'dark' : 'light');
    });

    if (localStorage.getItem('theme') === 'dark') {
        body.classList.add('dark-mode');
        themeIcon.innerText = '☀️';
        themeText.innerText = 'Modo Claro';
    }
</script>
</body>
</html>
"""

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write(html_out)

print(f"Relatório '{OUTPUT_FILE}' gerado com sucesso!")
