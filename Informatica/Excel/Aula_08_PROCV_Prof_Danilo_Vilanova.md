# INFORMATICA - EXCEL PARA CONCURSOS - Aula 08: PROCV
**Professor:** Danilo Vilanova (Canal: Informática Concursos)  
**Link da Aula:** [Assistir no YouTube](https://www.youtube.com/watch?v=2tCnNcz5fqw)  
**Duração:** 50 minutos  
**Categoria:** Edital de Concursos Públicos  

---

## 1. Resumo Estruturado e Conceitos-Chave

### A. Função PROCV: Sintaxe e Argumentos
- **CONCEITO:** Função de busca vertical em tabelas do Excel/Calc:
  `=PROCV(valor_procurado; matriz_tabela; núm_índice_coluna; [procurar_intervalo])`
- **EXPLICAÇÃO DOS 4 ARGUMENTOS:**
  1. `valor_procurado`: O que você busca na 1ª coluna da matriz.
  2. `matriz_tabela`: O intervalo completo onde estão os dados.
  3. `núm_índice_coluna`: O número sequencial da coluna que contém a resposta (1, 2, 3...).
  4. `procurar_intervalo`: `0` ou `FALSO` (busca exata); `1` ou `VERDADEIRO` (busca aproximada).
- **EXEMPLO PRÁTICO:**
  `=PROCV("Maria"; A2:C50; 3; 0)` -> Busca "Maria" na coluna A e retorna o valor correspondente na coluna C (3ª coluna).
- **CUIDADO / EXCEÇÃO (Regra da Direita):** O PROCV pesquisa OBRIGATORIAMENTE na PRIMEIRA coluna da matriz e só consegue retornar valores à DIREITA. Ele NUNCA busca valores à esquerda!
- **COMO PODE SER COBRADO:** A banca colocará a letra da coluna no 3º argumento (ex: `"C"` ao invés de `3`) gerando `#VALOR!`.

---

### B. O 4º Argumento e o Erro #N/D
- **CONCEITO:**
  - `0` ou `FALSO`: Exige correspondência exata. Se não encontrar, retorna `#N/D` (Não Disponível).
  - `1` ou `VERDADEIRO` (ou omitido): Busca aproximada. EXIGE que a 1ª coluna esteja em **ordem crescente**!
- **CUIDADO / PEGADINHA CLÁSSICA:** Se você omitir o 4º argumento, o Excel assume `1` (aproximada). Se a tabela não estiver ordenada, retornará valores errôneos!
- **COMO PODE SER COBRADO:** "A função `=PROCV(A1; B1:D10; 2)` realiza busca com correspondência estritamente exata por padrão." Item ERRADO (omissão = aproximada).

---

## 2. Raio-X de Banca & Pegadinhas Mais Frequentes (Cebraspe / FGV)

### 🚨 Pegadinha 1: Letra de Coluna no 3º Argumento
- **O que a banca afirma para induzir ao erro:** "A fórmula `=PROCV(B2; A1:D10; "D"; 0)` localiza o código contido em B2 e retorna corretamente o preço localizado na coluna D."
- **Pegadinha desmascarada (Onde está o erro):** O 3º argumento do PROCV é estritamente um NÚMERO ÍNDICE (1, 2, 3, 4...). Passar a letra da coluna entre aspas causa erro de digitação de sintaxe (`#VALOR!`).
- **💡 Regra de Ouro / Mnemônico:** "3º Argumento do PROCV é NÚMERO, nunca letra! Coluna D = número 4."

### 🚨 Pegadinha 2: Omissão do Quarto Argumento
- **O que a banca afirma para induzir ao erro:** "Ao utilizar `=PROCV(A1; Tabela; 2)`, o Excel buscará apenas a correspondência exata do valor A1."
- **Pegadinha desmascarada (Onde está o erro):** Se o 4º argumento for omitido, o Excel adota o valor padrão `VERDADEIRO` (busca aproximada). Para busca exata, é obrigatório digitar `0` ou `FALSO`.
- **💡 Regra de Ouro / Mnemônico:** "Zero = Zero dúvidas (Exata); Omitiu = Caiu no aproximado!"

### 🚨 Pegadinha 3: Busca para a Esquerda
- **O que a banca afirma para induzir ao erro:** "A função PROCV pode ser utilizada para pesquisar um CPF na coluna B e retornar o nome do funcionário localizado na coluna A."
- **Pegadinha desmascarada (Onde está o erro):** O PROCV só busca da esquerda para a direita. O valor procurado DEVE estar na primeira coluna da matriz. Para buscar à esquerda, utiliza-se `=PROCX()` ou a combinação `=ÍNDICE(..., CORRESP(...))`.
- **💡 Regra de Ouro / Mnemônico:** "PROCV é míope da esquerda: quem procura com PROCV só olha para a DIREITA!"
