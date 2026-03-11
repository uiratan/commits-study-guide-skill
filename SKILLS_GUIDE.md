# Guia de Uso: Skill `commits-study-guide`

Esta skill foi desenvolvida para transformar o histórico do Git em uma experiência de aprendizado visual e técnica. Ela gera um relatório HTML interativo estruturado como um curso de arquitetura.

## 🚀 Como Executar

Para gerar um relatório, basta dar o comando no chat:

> "Gere um guia de estudo a partir do commit [SHA] até agora usando a skill `commits-study-guide`"

### Parâmetros Suportados:
- **Commit Inicial:** (Obrigatório) O SHA do commit onde o estudo começa.
- **Nome do Arquivo:** (Opcional) Você pode definir o nome do `.html` (ex: `relatorio-v2.html`).
- **Range:** Você pode pedir "do commit X até o commit Y".

## 🛠️ O que o Relatório Entrega

1. **Hierarquia de Branches:** Mostra o caminho desde a `master` até a sua branch atual, incluindo as datas de criação formatadas em `dd/mm/yyyy`.
2. **Explicação Pedagógica:** Cada commit vira uma "Aula" contendo:
    - **Motivação:** O "porquê" da mudança.
    - **Implementação:** O "como" técnico.
    - **Conceitos e Documentação:** Detalhes sobre Maven, Jakarta EE, ORM, etc.
    - **Alternativas:** Análise de outras soluções possíveis.
3. **Interface Interativa:**
    - Sidebar redimensionável para facilitar a leitura de títulos longos.
    - Navegação rápida entre aulas.
    - Diferencial visual (diff) de código com realce de sintaxe.

## 📂 Localização dos Arquivos da Skill
- **Instruções (IA):** `.gemini/skills/commits-study-guide/SKILL.md`
- **Motor de Geração (Python):** `.gemini/skills/commits-study-guide/assets/report_engine.py`

---
*Dica: Para usar esta skill em outros projetos, copie a pasta `commits-study-guide` para a pasta de skills global do seu usuário (~/.gemini/skills/).*
