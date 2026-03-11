---
name: commits-study-guide
description: "Gera um relatório HTML premium (Feed Greyscale) detalhando a evolução do código commit a commit com análise técnica profunda. Use para guias de estudo, relatórios de arquitetura ou análise de mudanças desde um SHA específico."
license: CC-BY-4.0
metadata:
  author: Gemini CLI
  version: 7.0.0
---

# Commits Study Guide (v7 - Arquitetura Premium Limpa)

Esta skill transforma o histórico do Git em um curso de arquitetura visualmente rico e tecnicamente denso.

## 🚀 Fluxo de Execução (OBRIGATÓRIO)

Você é um Arquiteto de Software sênior. O sucesso deste relatório depende da sua capacidade de explicar o "porquê" de cada mudança.

### Passo 1: Análise Técnica Profunda
Para **CADA** commit no intervalo solicitado:
1.  Execute `git show SHA` para analisar as mudanças reais de código.
2.  Redija uma análise técnica contendo:
    *   **Motivação**: Por que essa mudança foi feita? (Seja específico sobre o problema resolvido).
    *   **Implementação**: Como foi feito tecnicamente? Quais classes/arquivos foram o foco?
    *   **Conceitos**: Explique as tecnologias envolvidas e inclua **links obrigatórios** 🔗 para a documentação oficial.
    *   **Alternativas**: O que mais poderia ter sido feito e quais os prós/contras?
    *   **Conclusão**: O aprendizado chave deste commit.

### Passo 2: Geração do Payload
Prepare um objeto JSON contendo todas as análises. Use o SHA completo como chave.

### Passo 3: Geração do Relatório
Injete o payload via variável de ambiente `ANALYSIS_PAYLOAD` e execute o motor:

```bash
export COMMIT_INICIAL="SHA"
export ANALYSIS_PAYLOAD='SEU_JSON_AQUI'
export OUTPUT_FILE="NOME.html"
python3 /home/uira/.gemini/skills/commits-study-guide/assets/report_engine.py
```

## 🎨 Visual e Comportamental
- **Estética**: Premium Greyscale (TechLeads Club Style).
- **Dark Mode**: 100% funcional via JavaScript local (persiste no navegador).
- **Código**: Dinâmico GitHub Light/Dark acompanhando o tema da página.
- **Hierarquia**: Automática `main/master -> atual`.
- **Zero Lixo**: Sem arquivos temporários no projeto.
