# INSTRUÇÕES-MESTRAS DE QUALIDADE • OS 4 PILARES DA PLATAFORMA
## Engenharia Pedagógica de Estudos para Concursos Públicos

Este documento estabelece o padrão oficial e inegociável de qualidade e os guardrails pedagógicos da IA para a produção e extração dos **4 Pilares de Alta Retenção** da plataforma **Projeto Aprovação** (`aprovacao-concursos`).

---

## 🏛️ 1. Arquitetura do Sistema Pedagógico

```text
                    TRANSCRIÇÃO DA VIDEOAULA
                               │
                               ▼
               ┌────────────────────────────────┐
               │    INSTRUÇÃO-MESTRA DE         │
               │         QUALIDADE              │
               │     (MASTER_STUDY_ENGINE)      │
               │                                │
               │ • Fidelidade à videoaula       │
               │ • Profundidade e densidade     │
               │ • Relevância para concurso     │
               │ • Raio-X de bancas             │
               │ • Mnemônicos obrigatórios      │
               │ • Distratores plausíveis       │
               │ • Repetição espaçada (SM-2)    │
               └───────────────┬────────────────┘
                               │
          ┌────────────────────┼────────────────────┐
          ▼                    ▼                    ▼                    ▼
     PILAR 1              PILAR 2              PILAR 3              PILAR 4
Resumo Estruturado &    Raio-X de Bancas &   Flashcards Anki &     Mini-Simulado
  Conceitos-Chave           Pegadinhas          Mnemônicos          de Fixação
(Apostila Condensada)   (Visão de Prova)    (Unidades Atômicas)  (Gabarito Comentado)
```

---

## ⚡ 2. A Camada Permanente: `MASTER_STUDY_ENGINE`

### Regra Fundamental Inegociável
> **"Nunca produzir simplesmente um resumo da transcrição. Transformar a aula em material de estudo de ALTO VALOR AGREGADO para concursos públicos, preservando a fidelidade ao conteúdo original e aumentando sua utilidade pedagógica para um candidato."**

### As 19 Regras Gerais Obrigatórias:
1. **Fonte Principal:** Use a transcrição como fonte principal dos fatos apresentados na aula.
2. **Sem Alucinações:** Não invente informações que não estejam sustentadas pela transcrição.
3. **Limpeza Técnica:** Elimine repetições, vícios de linguagem, conversas paralelas e trechos sem valor didático.
4. **Preservação de Conteúdo:** Preserve conceitos, definições, classificações, exemplos, exceções, comparações, regras, observações do professor e relações entre conceitos.
5. **Filtro de Edital:** Identifique aquilo que tem maior potencial de ser cobrado em prova.
6. **Preferência Qualificada:** Dê preferência a definições, conceitos fundamentais, diferenças entre conceitos, classificações, exceções, regras, causas/consequências, exemplos, contraexemplos, palavras-chave e relações de causa e efeito.
7. **Gatilhos de Bancas:** Quando o professor utilizar termos como *"atenção"*, *"cuidado"*, *"pegadinha"*, *"prova"*, *"banca"*, *"importante"*, *"não confunda"*, *"sempre"*, *"nunca"*, *"exceto"*, trate o trecho como prioridade máxima de revisão.
8. **Diferenciação Epistêmica:** Diferencie claramente o que foi efetivamente apresentado na aula de uma inferência pedagógica ou de uma forma de cobrança em prova.
9. **Fidelidade às Palavras do Professor:** Nunca transforme uma inferência em fato afirmado pelo professor.
10. **Organização Funcional:** O material deve ser organizado para permitir compreensão imediata, memorização duradoura, revisão rápida e identificação de armadilhas.
11. **Anti-Superficialidade:** Evite produzir conteúdo superficial apenas para preencher espaço.
12. **Alta Densidade Informacional:** É preferível produzir menos conteúdo, mas com altíssima densidade informacional, do que textos longos e repetitivos.
13. **Foco no Acerto:** Sempre responda: *"O que um candidato precisa saber deste trecho para acertar uma questão de concurso?"*
14. **Previsão de Banca:** Responda: *"Como uma banca examinadora transformaria este conteúdo em uma questão?"*
15. **Distinção Nítida:** Sempre que houver conceitos semelhantes, crie distinções claras entre eles.
16. **Destaque de Exceções:** Sempre que houver uma regra com exceção, isole e destaque a exceção.
17. **Alerta de Confusão:** Se houver assertiva com risco de induzir o aluno ao erro, destaque o risco de confusão.
18. **Fundamentação Real:** Não invente questões ou pegadinhas sem fundamento no conteúdo estudado.
19. **Tom Profissional:** O resultado final deve parecer produzido por um experiente coordenador pedagógico de cursos preparatórios, nunca por um resumo robótico genérico.

---

## 📘 3. Especializações por Pilar

### 🔹 Pilar 1 — Resumo Estruturado & Conceitos-Chave (Apostila Condensada)
- **Missão Pedagógica:** Permitir que o aluno compreenda o conteúdo com profundidade sem precisar rever a videoaula imediatamente.
- **Sequência Didática Obrigatória:**
  $$\text{CONCEITO} \longrightarrow \text{EXPLICAÇÃO} \longrightarrow \text{EXEMPLO} \longrightarrow \text{CUIDADO/EXCEÇÃO} \longrightarrow \text{COMO PODE SER COBRADO}$$
- **Organização:** Hierárquica em Markdown com subseções (`### A. ...`, `### B. ...`), tabelas comparativas para conceitos confrontados e mnemônicos didáticos destacados.

### 🔹 Pilar 2 — Raio-X das Bancas & Pegadinhas Mais Frequentes
- **Missão Pedagógica:** Transformar o conteúdo puro em visão clínica de prova sob a ótica da banca examinadora (Cebraspe, FGV, FCC, Vunesp).
- **Estrutura Obrigatória de cada Armadilha:**
  1. **O que a banca afirma para induzir ao erro:** Assertiva falaciosa ou inversão sutil.
  2. **Pegadinha desmascarada (Onde está o erro):** Análise técnica precisa do ponto de ruptura.
  3. **💡 Regra de Ouro / Mnemônico de Defesa:** Regra mnemônica para o aluno blindar a questão.

### 🔹 Pilar 3 — Flashcards Anki & Esquematização (Unidades Atômicas + Mnemônicos)
- **Missão Pedagógica:** Alimentar o algoritmo de repetição espaçada SM-2 com perguntas e respostas cirúrgicas.
- **Regra Fundamental de Unidade:** Cada cartão testa **UMA única ideia principal** (pergunta desafiadora no anverso, resposta fundamentada no verso).
- **⭐ DIRETRIZ ESPECIAL OBRIGATÓRIA DE MNEMÔNICOS:**
  > **"Você deverá criar sempre mnemônicos, dadas as importâncias deles para os alunos, em especial em Direito Administrativo, Direito Constitucional, Direito Penal e demais matérias onde os mnemônicos são muito utilizados."**
  - *Exemplos obrigatórios:* LIMPE, COFIFOMOB, RAÇÃO, 3T+H, SO-CI-DI-VA-PLU, etc.
  - Sempre que a matéria comportar listas, requisitos, princípios ou classificações, deve existir um flashcard dedicado exclusivamente ao mnemônico e ao desdobramento de cada elemento.

### 🔹 Pilar 4 — Mini-Simulado de Fixação
- **Missão Pedagógica:** Treinamento real de julgamento com padrão real de bancas.
- **Formato Adaptativo:**
  - **Cebraspe:** Assertivas inéditas de **CERTO / ERRADO**, com penalidade de 1 errada anula 1 certa simulada na plataforma.
  - **FGV / FCC / Vunesp:** Múltipla escolha (A, B, C, D, E).
- **Distratores Inteligentes:** Alternativas incorretas plausíveis, fundamentadas nas pegadinhas clássicas da matéria.
- **Gabarito com Comentário Quádruplo:**
  1. Gabarito oficial.
  2. Comentário da resposta certa.
  3. Justificativa detalhada de por que cada distrator está incorreto.
  4. Ponto de aprendizagem nuclear para reter na memória de longo prazo.
