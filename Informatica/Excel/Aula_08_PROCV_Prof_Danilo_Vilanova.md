# EXCEL PARA CONCURSOS - Aula 08: PROCV
**Professor:** Danilo Vilanova (Canal: Informática Concursos)  
**Link da Aula:** [Assistir no YouTube](https://www.youtube.com/watch?v=2tCnNcz5fqw&list=PLnmFkFtxOflLLmJaSKJZDwwfe94kDVKDE)  
**Duração:** 59 minutos  
**Categoria do Excel:** Pesquisa e Referência (Guia Fórmulas)

---

## 1. Resumo Estruturado e Conceitos-Chave

### A. O que é a Função PROCV?
- **Finalidade:** Realiza uma **procura vertical** (nas colunas) de um determinado dado em uma tabela e retorna uma informação correspondente localizada na mesma linha.
- **Equivalente em inglês:** `VLOOKUP` (*Vertical Lookup*).
- **Função correlata:** `PROCH` (`HLOOKUP`) realiza a procura na **horizontal** (nas linhas).
- **Novas alternativas mencionadas:** `PROCX` (busca bidirecional em qualquer posição) e a combinação `ÍNDICE + CORRESP`.
- **Categoria no Excel / Calc:** Fórmulas > **Pesquisa e Referência**.

---

### B. A Sintaxe Sagrada do PROCV (4 Argumentos)

```excel
=PROCV(valor_procurado; matriz_tabela; núm_índice_coluna; [procurar_intervalo])
```

| Argumento | Ordem | O que significa na prática | Exemplo prático |
| :--- | :---: | :--- | :--- |
| **1º Valor Procurado** | 1 | O que você quer pesquisar (célula, número, texto entre aspas ou função aninhada). | `"RJ"`, `D2`, `MAIOR(A1:A5; 1)` |
| **2º Matriz / Tabela** | 2 | Intervalo completo dos dados onde será feita a busca. **Regra de ouro:** o valor procurado deve estar sempre na **primeira coluna** desse intervalo. | `A2:B7`, `A1:C12` |
| **3º Índice da Coluna** | 3 | O **número ordinal** da coluna (1, 2, 3...) dentro da matriz onde está a resposta desejada. **Atenção:** é sempre um número, nunca a letra da coluna. | `2` (segunda coluna), `3` (terceira) |
| **4º Tipo de Correspondência** | 4 | Define se a busca é exata ou aproximada:<br>• `0` ou `FALSO`: busca **EXATA**.<br>• `1` ou `VERDADEIRO` (ou omitido): busca **APROXIMADA**. | `0`, `FALSO` |

---

### C. O Erro `#N/D` (Não Disponível)
Quando o 4º argumento for `0` ou `FALSO` (busca exata) e o valor procurado **não existir** na primeira coluna da matriz, o Excel retornará o erro **`#N/D`** (*Não Disponível* / *Nada Disponível*).

---

## 2. Pontos Críticos de Banca & Pegadinhas (Onde 95% dos Candidatos Erram)

1. **Inversão da Ordem dos Argumentos (Clássica Cebraspe):**
   - *Pegadinha:* Afirmar que "o primeiro argumento da função PROCV é o índice da coluna".
   - *Verdade:* O 1º argumento é sempre o **valor procurado**. O índice da coluna é o **3º argumento**.

2. **Letra da Coluna no 3º Argumento:**
   - *Pegadinha:* A questão coloca `=PROCV("SP"; A1:C10; B; 0)`.
   - *Verdade:* Isso gera **erro de sintaxe** no Excel. O 3º argumento exige obrigatoriamente um número inteiro (`2`), jamais a letra (`B`).

3. **Inversão entre Exato e Aproximado:**
   - *Pegadinha:* Afirmar que `1` (ou `VERDADEIRO`) faz busca exata e `0` faz busca aproximada.
   - *Verdade:* `0` = `FALSO` = **Exato**; `1` = `VERDADEIRO` = **Aproximado**.

4. **"Busca em qualquer posição":**
   - *Pegadinha:* A banca afirma que "o PROCV permite localizar itens em qualquer posição da tabela por coluna".
   - *Verdade:* **Errado**. O PROCV busca apenas na **primeira coluna à esquerda** da matriz e retorna dados à sua direita. Para qualquer posição, usa-se `PROCX` ou `ÍNDICE + CORRESP`.

5. **Função Aninhada no 1º Argumento (Nível Superior / FGV / FCC):**
   - *Pegadinha:* Inserir outra função no 1º argumento:
     `=PROCV(MAIOR(A1:A5; 1); A1:B5; 2; FALSO)`
   - *Como resolver:* Resolva de dentro para fora. Primeiro calcule `MAIOR(A1:A5; 1) = 8`. Depois faça `=PROCV(8; A1:B5; 2; FALSO)`.

---

## 3. Esquematização para Revisão Ativa

### A. Tabela Comparativa: PROCV vs. PROCH vs. PROCX

| Função | Direção da Busca | 3º Argumento | Flexibilidade |
| :--- | :--- | :--- | :--- |
| **PROCV** | Vertical (coluna) | Número da **Coluna** (`núm_índice_coluna`) | Busca somente na 1ª coluna à esquerda |
| **PROCH** | Horizontal (linha) | Número da **Linha** (`núm_índice_lin`) | Busca somente na 1ª linha superior |
| **PROCX** | Qualquer direção | Matriz de retorno | Bidirecional (pesquisa antes, depois, cima ou baixo) |

---

### B. Mnemônico para Memorizar a Sintaxe

> **"Você Me Indica a Coisa"**
> - **V** $\rightarrow$ **V**alor procurado (1º)
> - **M** $\rightarrow$ **M**atriz / Tabela (2º)
> - **I** $\rightarrow$ **Í**ndice da coluna/linha (3º)
> - **C** $\rightarrow$ **C**orrespondência (4º: 0 = Falso / 1 = Verdadeiro)

---

## 4. Mini-Simulado de Fixação (Comentado)

### Questão 1 (Estilo Cebraspe / Certo ou Errado)
> **(Banca CESPE / Adaptada)** Na função `=PROCV` do Microsoft Excel, o primeiro argumento define o número de índice da coluna que contém a resposta desejada, enquanto o segundo define a matriz da tabela.  
> *( ) CERTO      ( ) ERRADO*  
>  
> **Gabarito: ERRADO.**  
> **Comentário:** O primeiro argumento é o valor procurado. O índice da coluna é o terceiro argumento.

---

### Questão 2 (Estilo FGV / Múltipla Escolha)
> **(FGV / Adaptada)** Em uma planilha do Excel, um assistente precisa localizar o salário de um servidor a partir de sua matrícula (coluna A, dados de A2 a D100). A função adequada e sua categoria são:  
> A) SOMASE, Matemática.  
> B) PROCV, Pesquisa e Referência.  
> C) PROCH, Estatística.  
> D) ÍNDICE, Lógica.  
> E) PROCV, Banco de Dados.  
>  
> **Gabarito: B.**  
> **Comentário:** Busca em colunas = PROCV. Categoria = Pesquisa e Referência.

---

### Questão 3 (Estilo FCC / Prática de Tabela)
> **(FCC / Adaptada)** Tabela:
> - A2=101, B2=Teclado, C2=80
> - A3=102, B3=Mouse, C3=45
> - A4=103, B4=Monitor, C4=750
> - A5=104, B5=Cadeira, C5=520
>  
> Fórmula na célula E1: `=PROCV(103; A1:C5; 3; 0)`. O retorno será:  
> A) Mouse  
> B) Monitor  
> C) 45  
> D) 750  
> E) #N/D  
>  
> **Gabarito: D (750).**  
> **Comentário:** Localiza 103 na coluna A (linha 4), vai até a 3ª coluna (coluna C) com correspondência exata (0) $\rightarrow$ 750.

---

### Questão 4 (Estilo Vunesp / Aninhada Avançada)
> **(Vunesp / Adaptada)** Considerando a mesma tabela da Questão 3, qual o resultado de:  
> `=PROCV(MÍNIMO(A2:A5); A2:C5; 2; FALSO)`  
> A) Teclado  
> B) Mouse  
> C) 101  
> D) 80  
> E) Cadeira  
>  
> **Gabarito: A (Teclado).**  
> **Comentário:** `MÍNIMO(A2:A5)` resulta em `101`. `=PROCV(101; A2:C5; 2; FALSO)` busca 101 e retorna o conteúdo da coluna 2 $\rightarrow$ Teclado.
