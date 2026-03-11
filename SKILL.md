---
name: commits-study-guide
description: "Gera um relatório HTML interativo estruturado como um curso de arquitetura, detalhando a evolução do código commit a commit. Use quando o usuário solicitar um relatório de commits, histórico de estudo ou guia de migração desde um commit específico."
license: CC-BY-4.0
metadata:
  author: Gemini CLI
  version: 1.0.0
---

# Generate Git Study Guide

Esta skill gera um guia de estudo profundo a partir do histórico de commits do Git. Ela transforma alterações de código em "aulas" com explicações detalhadas sobre motivação, implementação, conceitos técnicos e alternativas.

## Instruções

### Passo 1: Preparação dos Parâmetros
Identifique os seguintes parâmetros com o usuário:
- **Commit Inicial:** O SHA ou referência onde o estudo deve começar (Obrigatório).
- **Commit Final:** O SHA ou referência final (Padrão: `HEAD`).
- **Arquivo de Saída:** O nome do arquivo `.html` (Padrão: `relatorio_estudo_commits.html`).

### Passo 2: Execução do Motor de Geração
O agente deve ler o script `assets/report_engine.py` e adaptá-lo para os commits solicitados. O script deve:
1. Extrair os commits no range `[Commit Inicial]^..[Commit Final]`.
2. Identificar a hierarquia de branches (`master -> intermediaria -> atual`) e as datas de nascimento (commit de divergência) formatadas como `dd/mm/yyyy`.

### Passo 3: Enriquecimento das Aulas
Para cada commit identificado, o agente deve analisar a mensagem do commit e o diff para gerar:
- **Motivação:** Por que essa mudança foi feita?
- **Implementação:** Como a alteração foi executada?
- **Conceitos e Documentação:** Detalhamento técnico (ex: tags Maven, especificações Jakarta EE).
- **Alternativas e Refatoração:** Outras formas de resolver e prós/contras.

### Visual e Estética
O relatório gerado deve obrigatoriamente seguir o padrão:
- Sidebar redimensionável à esquerda com títulos completos (quebra de linha).
- Hierarquia de branches com datas no formato `dd/mm/yyyy`.
- Realce de sintaxe simulado para código Java e XML.
- Estrutura de tópicos: Motivação, Implementação, Conceitos, Alternativas e Conclusão.

## Exemplo de Uso
Usuário diz: "Gere um relatório de estudo do commit a1b2c3d até agora"

Ações:
1. Localiza o script nos assets da skill.
2. Calcula a hierarquia de branches e datas.
3. Analisa as mudanças entre `a1b2c3d` e `HEAD`.
4. Gera o arquivo HTML com o visual padrão (sidebar redimensionável, CSS moderno).
