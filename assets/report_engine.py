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
<title>Commits Study Guide - Premium Greyscale</title>
<style>
    :root {{
        --bg-color: #fcfcfc;
        --sidebar-bg: #fcfcfc;
        --sidebar-text: #4a4a4a;
        --text-color: #4a4a4a;
        --text-strong: #1a1a1a;
        --border-color: #e0e0e0;
        --card-bg: #ffffff;
        --header-bg: #f5f5f5;
        --topic-bg: #f5f5f5;
        --conclusion-bg: #f0f0f0;
        --accent: #333333;
        
        /* GitHub Light Style Code Colors */
        --code-bg: #f6f8fa;
        --code-text: #24292f;
        --diff-add-bg: #dafbe1;
        --diff-add-text: #1a7f37;
        --diff-del-bg: #ffebe9;
        --diff-del-text: #cf222e;
        --diff-info-bg: #ddf4ff;
        --diff-info-text: #0969da;
        --diff-header-bg: #24292f;
        --diff-header-text: #ffffff;
    }}
    
    .dark-mode {{
        --bg-color: #121212;
        --sidebar-bg: #121212;
        --sidebar-text: #a0a0a0;
        --text-color: #a0a0a0;
        --text-strong: #ffffff;
        --border-color: #2a2a2a;
        --card-bg: #1a1a1a;
        --header-bg: #1a1a1a;
        --topic-bg: #121212;
        --conclusion-bg: #252525;
        --accent: #e0e0e0;
        
        /* GitHub Dark Style Code Colors */
        --code-bg: #0d1117;
        --code-text: #c9d1d9;
        --diff-add-bg: rgba(46, 160, 67, 0.15);
        --diff-add-text: #3fb950;
        --diff-del-bg: rgba(248, 81, 73, 0.15);
        --diff-del-text: #f85149;
        --diff-info-bg: rgba(56, 139, 253, 0.1);
        --diff-info-text: #8b949e;
        --diff-header-bg: #2d2d2d;
        --diff-header-text: #ffffff;
    }}

    body {{
        margin: 0;
        font-family: 'Inter', system-ui, sans-serif;
        display: flex;
        height: 100vh;
        overflow: hidden;
        background-color: var(--bg-color);
        color: var(--text-color);
        line-height: 1.6;
        transition: background-color 0.2s;
    }}
    
    .sidebar {{
        width: 300px;
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
        width: 4px;
        cursor: col-resize;
        background-color: transparent;
        transition: background-color 0.2s;
        flex-shrink: 0;
        z-index: 20;
    }}
    .resizer:hover, .resizer.dragging {{ background-color: var(--accent); }}
    
    .sidebar-header {{
        padding: 24px;
        border-bottom: 1px solid var(--border-color);
        background-color: var(--header-bg);
    }}
    .sidebar-header h2 {{ margin: 0; font-size: 1rem; font-weight: 700; text-transform: uppercase; color: var(--text-strong); }}
    .sidebar-header .meta {{ margin-top: 12px; font-size: 0.7rem; color: var(--text-color); opacity: 0.8; }}
    
    .nav-links {{ flex: 1; overflow-y: auto; padding: 16px 8px; }}
    .nav-links a {{
        display: block;
        padding: 10px 16px;
        color: var(--text-color);
        text-decoration: none;
        font-size: 0.85rem;
        border-radius: 8px;
        margin-bottom: 4px;
        white-space: normal;
        word-wrap: break-word;
        transition: all 0.2s;
        border: 1px solid transparent;
    }}
    .nav-links a:hover {{ background-color: var(--topic-bg); border-color: var(--border-color); color: var(--text-strong); }}
    .nav-links a.active {{ background-color: var(--accent); color: #fff; }}

    .theme-toggle {{
        background: var(--topic-bg); border: 1px solid var(--border-color); color: var(--text-color);
        padding: 8px; border-radius: 8px; cursor: pointer; width: 100%; margin-top: 16px; font-size: 0.8rem;
        display: flex; align-items: center; justify-content: center; gap: 8px;
        transition: all 0.2s;
    }}
    .theme-toggle:hover {{ background: var(--border-color); color: var(--text-strong); }}
    
    .content {{ flex: 1; overflow-y: auto; padding: 40px 60px; scroll-behavior: smooth; }}
    .feed-container {{ width: 90%; margin: 0 auto; }}
    
    .commit-section {{
        background: var(--card-bg);
        margin-bottom: 60px;
        border-radius: 16px;
        border: 1px solid var(--border-color);
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        overflow: hidden;
    }}
    
    .commit-header {{ padding: 32px 40px; border-bottom: 1px solid var(--border-color); }}
    .commit-header .sha {{
        font-family: monospace; font-size: 0.8rem; color: var(--accent); background: var(--conclusion-bg);
        padding: 4px 8px; border-radius: 4px; font-weight: 600; margin-bottom: 12px; display: inline-block;
    }}
    .commit-header h1 {{ color: var(--text-strong); font-size: 1.75rem; margin: 0; font-weight: 800; }}
    
    .commit-body {{ padding: 40px; }}
    
    .topic {{ margin-bottom: 32px; }}
    .topic strong {{ color: var(--accent); display: block; margin-bottom: 12px; font-size: 0.8rem; text-transform: uppercase; font-weight: 700; }}
    
    .topic ul {{ margin: 0; padding-left: 20px; list-style-type: disc; }}
    .topic ul li {{ margin-bottom: 12px; font-size: 1.05rem; color: var(--text-color); line-height: 1.5; }}
    .topic ul li strong {{ display: inline; text-transform: none; font-size: inherit; color: var(--text-strong); letter-spacing: normal; margin-right: 4px; }}
    .topic a {{ color: var(--accent); text-decoration: none; border-bottom: 1px dashed var(--accent); font-weight: 600; padding: 0 4px; border-radius: 4px; background: rgba(0, 0, 0, 0.05); }}
    .topic a:hover {{ background: var(--accent); color: #fff; border-bottom-style: solid; }}
    
    .conclusion {{ background-color: var(--conclusion-bg); padding: 24px; border-radius: 12px; margin: 40px 0; border-left: 4px solid var(--accent); }}
    .conclusion p {{ margin: 0; font-weight: 500; color: var(--text-strong); }}
    
    h3 {{ font-size: 1.1rem; font-weight: 700; margin-bottom: 20px; color: var(--text-strong); border-bottom: 1px solid var(--border-color); padding-bottom: 8px; }}

    /* Code Diff Styles - Dynamic GitHub Style */
    pre.code-diff {{
        background-color: var(--code-bg);
        color: var(--code-text);
        padding: 24px;
        border-radius: 12px;
        overflow-x: auto;
        font-family: 'Fira Code', 'Menlo', monospace;
        font-size: 0.85rem;
        line-height: 1.6;
        margin: 0;
        border: 1px solid var(--border-color);
        transition: all 0.2s;
    }}
    .diff-line {{ display: block; padding: 0 16px; margin: 0 -24px; white-space: pre; background-color: transparent; }}
    .diff-line.add {{ background-color: var(--diff-add-bg); color: var(--diff-add-text); }}
    .diff-line.del {{ background-color: var(--diff-del-bg); color: var(--diff-del-text); }}
    .diff-line.info {{ background-color: var(--diff-info-bg); color: var(--diff-info-text); padding-top: 12px; margin-top: 12px; }}
    
    .diff-line.file-header {{
        background-color: var(--diff-header-bg);
        color: var(--diff-header-text);
        font-weight: 600;
        margin: 24px -24px 0 -24px;
        padding: 8px 24px;
        display: block;
        font-size: 0.8rem;
        border-top: 1px solid var(--border-color);
    }}
    .diff-line.file-header:first-child {{ margin-top: 0; border-top: none; }}
</style>
</head>
<body>

<div class="sidebar">
    <div class="sidebar-header">
        <h2>Study Guide</h2>
        <div class="meta">
            <div>Hierarquia: {hierarquia}</div>
            <div>Remoto: {remote}</div>
        </div>
        <button class="theme-toggle" id="themeToggle">
            <span id="themeIcon">🌙</span> <span id="themeText">Dark Mode</span>
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
    <div class="feed-container">
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
            formatted_diff += f'<div class="diff-line add">{safe_line}</div>'
        elif line.startswith('-') and not line.startswith('---'):
            formatted_diff += f'<div class="diff-line del">{safe_line}</div>'
        elif line.startswith('diff ') or line.startswith('index ') or line.startswith('---') or line.startswith('+++') or line.startswith('@@ '):
            formatted_diff += f'<div class="diff-line info">{safe_line}</div>'
        else:
            formatted_diff += f'<div class="diff-line">{safe_line}</div>'

    m, i, c, a, c_aula = generate_analysis(msg)

    html_out += f'''
    <div class="commit-section" id="aula-{sha}">
        <div class="commit-header">
            <div class="sha">{sha[:8]}</div>
            <h1>{html.escape(msg)}</h1>
        </div>
        
        <div class="commit-body">
            <div class="topic"><strong>Motivação</strong><p>{m}</p></div>
            <div class="topic"><strong>Implementação</strong><p>{i}</p></div>
            <div class="topic"><strong>Conceitos e Documentação</strong>{c}</div>
            <div class="topic"><strong>Alternativas e Refatoração</strong>{a}</div>
            
            <div class="conclusion">
                <p>💡 {c_aula}</p>
            </div>
            
            <h3>Código da Aula</h3>
            <pre class="code-diff">{formatted_diff}</pre>
        </div>
    </div>
'''

html_out += """
    </div>
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
        themeText.innerText = isDark ? 'Light Mode' : 'Dark Mode';
        localStorage.setItem('theme', isDark ? 'dark' : 'light');
    });

    if (localStorage.getItem('theme') === 'dark') {
        body.classList.add('dark-mode');
        themeIcon.innerText = '☀️';
        themeText.innerText = 'Light Mode';
    }
</script>
</body>
</html>
"""

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write(html_out)

print(f"Relatório '{OUTPUT_FILE}' gerado com sucesso!")
