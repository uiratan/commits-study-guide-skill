import subprocess
import html
import sys
import os
import json

# Parâmetros de entrada
COMMIT_INICIAL = os.getenv("COMMIT_INICIAL", "")
COMMIT_FINAL = os.getenv("COMMIT_FINAL", "HEAD")
OUTPUT_FILE = os.getenv("OUTPUT_FILE", "git_study_guide.html")
ANALYSIS_PAYLOAD = os.getenv("ANALYSIS_PAYLOAD", "{}")

# Localização do template
ASSETS_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_PATH = os.path.join(ASSETS_DIR, "template.html")

def run_cmd(cmd):
    try:
        return subprocess.check_output(cmd, shell=True, text=True, encoding='utf-8', errors='replace').strip()
    except subprocess.CalledProcessError:
        return ""

if not COMMIT_INICIAL:
    print("Erro: COMMIT_INICIAL é obrigatório.")
    sys.exit(1)

# Carregar Análise
try:
    analyses = json.loads(ANALYSIS_PAYLOAD)
except Exception as e:
    print(f"Aviso: Erro ao ler payload JSON: {e}")
    analyses = {}

# Obter histórico (mais novos primeiro)
git_log_out = run_cmd(f"git log {COMMIT_INICIAL}^..{COMMIT_FINAL} --format='%H|%s'")
commit_data = [line.split('|', 1) for line in git_log_out.split('\n') if '|' in line]

# Hierarquia e Metadados
branch_atual = run_cmd("git rev-parse --abbrev-ref HEAD")
def get_date(sha): return run_cmd(f"git log -1 --format=%cd --date=format:'%d/%m/%Y' {sha}")
main_branch = next((b for b in ["main", "master", "origin/main", "origin/master"] if run_cmd(f"git rev-parse --verify {b} 2>/dev/null")), "")
hierarquia = branch_atual
if main_branch and main_branch != branch_atual:
    mbase = run_cmd(f"git merge-base HEAD {main_branch}")
    if mbase: hierarquia = f"{main_branch.replace('origin/', '')} --({get_date(mbase)})--> {branch_atual}"
remote = run_cmd(f"git config --get branch.{branch_atual}.remote") or "origin"

# Fragmentos HTML
nav_html = ""
content_html = ""
for i, (sha, msg) in enumerate(commit_data):
    nav_html += f'<a href="#aula-{sha}"><span class="nav-sha">{sha[:7]}</span> {i+1}. {html.escape(msg)}</a>\n'
    
    # Extrair Diff
    diff_raw = run_cmd(f"git show {sha} --format=''")
    formatted_diff = ""
    for line in diff_raw.split('\n'):
        s = html.escape(line)
        if line.startswith('diff --git'): formatted_diff += f'<div class="diff-line file-header">{s}</div>'
        elif line.startswith('+') and not line.startswith('+++'): formatted_diff += f'<div class="diff-line add">{s}</div>'
        elif line.startswith('-') and not line.startswith('---'): formatted_diff += f'<div class="diff-line del">{s}</div>'
        elif any(line.startswith(p) for p in ['diff ', 'index ', '---', '+++', '@@ ']): formatted_diff += f'<div class="diff-line info">{s}</div>'
        else: formatted_diff += f'<div class="diff-line">{s}</div>'

    # Análise injetada com robustez (completo, 8 chars, 7 chars)
    data = analyses.get(sha, analyses.get(sha[:8], analyses.get(sha[:7], {
        "m": "Motivação não analisada pelo agente.",
        "i": "Implementação padrão.",
        "c": "<ul><li>Sem conceitos.</li></ul>",
        "a": "<ul><li>Sem alternativas.</li></ul>",
        "conclusao": "Evolução."
    })))

    # Fallback para chaves por extenso
    m = data.get('m', data.get('motivacao', 'Não detalhado.'))
    i = data.get('i', data.get('implementacao', 'Padrão.'))
    c = data.get('c', data.get('conceitos', '<ul><li>Sem conceitos.</li></ul>'))
    a = data.get('a', data.get('alternativas', '<ul><li>Sem alternativas.</li></ul>'))
    concl = data.get('conclusao', 'Evolução.')

    content_html += f'''
    <div class="commit-section" id="aula-{sha}">
        <div class="commit-header"><div class="sha">{sha[:8]}</div><h1>{html.escape(msg)}</h1></div>
        <div class="commit-body">
            <div class="topic"><strong>Motivação</strong><p>{m}</p></div>
            <div class="topic"><strong>Implementação</strong><p>{i}</p></div>
            <div class="topic"><strong>Conceitos e Documentação</strong>{c}</div>
            <div class="topic"><strong>Alternativas e Refatoração</strong>{a}</div>
            <div class="conclusion"><p>💡 {concl}</p></div>
            <h3>Código da Aula</h3><pre class="code-diff">{formatted_diff}</pre>
        </div>
    </div>'''

# Montagem final
with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
    final_html = f.read().replace("{{HIERARQUIA}}", hierarquia).replace("{{REMOTO}}", remote).replace("{{NAV_LINKS}}", nav_html).replace("{{CONTENT}}", content_html)

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write(final_html)

print(f"Relatório '{OUTPUT_FILE}' gerado com sucesso!")
