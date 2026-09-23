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

## 2. Raio-X de Banca & Pegadinhas Mais Frequentes

### 🚨 Pegadinha 1: O Valor da Coluna Errada
- **O que a banca afirma para induzir ao erro:** "A função `PROCV` retorna o valor da coluna especificada no argumento de índice, mesmo que esse valor não esteja presente na tabela."
- **Pegadinha desmascarada (Onde está o erro):** O `PROCV` só retorna um valor se o valor procurado estiver na primeira coluna da matriz. Se o valor não estiver presente, retornará `#N/D`, não o valor da coluna especificada.
- **💡 Regra de Ouro / Mnemônico:** "Primeiro, procura; depois, retorna!"

### 🚨 Pegadinha 2: Confusão entre Exato e Aproximado
- **O que a banca afirma para induzir ao erro:** "O argumento `1` no `PROCV` realiza uma busca exata, enquanto `0` realiza uma busca aproximada."
- **Pegadinha desmascarada (Onde está o erro):** O `0` ou `FALSO` realiza a busca exata, enquanto `1` ou `VERDADEIRO` faz a busca aproximada. Isso é frequentemente confundido por candidatos.
- **💡 Regra de Ouro / Mnemônico:** "Zero é certeiro; um é um palpite."

### 🚨 Pegadinha 3: Letra em vez de Número
- **O que a banca afirma para induzir ao erro:** "A fórmula `=PROCV('RJ'; A1:C10; B; 0)` está correta e retorna o valor."
- **Pegadinha desmascarada (Onde está o erro):** O terceiro argumento deve ser um número inteiro, representando a coluna, e não uma letra. Portanto, `B` gerará um erro de sintaxe.
- **💡 Regra de Ouro / Mnemônico:** "Número é o que conta, letra não vale!"

### 🚨 Pegadinha 4: Busca na Posição Errada
- **O que a banca afirma para induzir ao erro:** "A função `PROCV` pode buscar valores em qualquer coluna da tabela."
- **Pegadinha desmascarada (Onde está o erro):** O `PROCV` só busca na primeira coluna da matriz especificada para encontrar o valor. Para busca em qualquer coluna, deve-se usar `PROCX`.
- **💡 Regra de Ouro / Mnemônico:** "Primeiro à esquerda, depois à direita."

### 🚨 Pegadinha 5: Uso Incorreto de Funções Aninhadas
- **O que a banca afirma para induzir ao erro:** "A fórmula `=PROCV(MAIOR(A1:A5; 1); A1:B5; 2; FALSO)` não precisa de cálculos adicionais."
- **Pegadinha desmascarada (Onde está o erro):** A função interna `MAIOR(A1:A5; 1)` deve ser avaliada primeiro, resultando em um valor que será então usado no `PROCV`. Ignorar isso pode levar a erros de interpretação.
- **💡 Regra de Ouro / Mnemônico:** "Resolva de dentro para fora, como uma cebola!" 

### 🚨 Pegadinha 6: Erro de Referência Inválida
- **O que a banca afirma para induzir ao erro:** "Se o índice da coluna no `PROCV` for maior que o número de colunas da matriz, o Excel retornará um valor vazio."
- **Pegadinha desmascarada (Onde está o erro):** O Excel retornará um erro `#REF!` se o índice da coluna especificado for maior que o número de colunas na matriz, e não um valor vazio.
- **💡 Regra de Ouro / Mnemônico:** "Cuidado com o índice, o limite é real!"

### 🚨 Função PROCV e a Primeira Coluna
1. **O conhecimento correto:** O `PROCV` realiza a busca vertical na primeira coluna da matriz especificada e retorna um valor correspondente da coluna definida pelo índice.
2. **O erro ou confusão provável:** Candidatos podem acreditar que o `PROCV` pode buscar em qualquer coluna da matriz, resultando em uma interpretação errada da função.
3. **Como uma questão poderia explorar essa confusão:** "A função `PROCV` pode localizar o valor procurado em qualquer coluna da tabela. Assinale V para verdadeiro e F para falso."
4. **Como o aluno deve evitar o erro:** Lembrar que a busca é sempre na **primeira coluna** da matriz. O mnemônico "Primeiro à esquerda" pode ajudar a fixar essa ideia.

### 🚨 Diferença entre Busca Exata e Aproximada
1. **O conhecimento correto:** O argumento `0` ou `FALSO` no `PROCV` indica que a busca deve ser exata, enquanto `1` ou `VERDADEIRO` (ou omitido) realiza uma busca aproximada.
2. **O erro ou confusão provável:** Candidatos confundem os argumentos e acreditam que `1` realiza a busca exata e `0` a aproximada.
3. **Como uma questão poderia explorar essa confusão:** "No `PROCV`, o argumento `1` realiza uma busca exata. Essa afirmação é: ( ) CERTO ( ) ERRADO."
4. **Como o aluno deve evitar o erro:** Utilizar a frase "Zero é certeiro; um é um palpite" como mnemônico para lembrar a função dos argumentos.

### 🚨 Erro de Sintaxe com Índice da Coluna
1. **O conhecimento correto:** O terceiro argumento do `PROCV` deve ser um número inteiro que representa a coluna da qual o valor deve ser retornado.
2. **O erro ou confusão provável:** Candidatos podem tentar usar letras (como `B`) em vez de números, resultando em erro de sintaxe.
3. **Como uma questão poderia explorar essa confusão:** "A fórmula `=PROCV('RJ'; A1:C10; B; 0)` está correta e retornará um valor. Assinale V ou F."
4. **Como o aluno deve evitar o erro:** Lembrar que números são obrigatórios para o índice da coluna, usando o mnemônico "Número é o que conta, letra não vale!".

### 🚨 Compreensão do Erro `#N/D`
1. **O conhecimento correto:** O erro `#N/D` é retornado quando uma busca exata (`0` ou `FALSO`) não encontra o valor procurado na matriz.
2. **O erro ou confusão provável:** Candidatos podem não associar corretamente o erro à ausência do valor na primeira coluna.
3. **Como uma questão poderia explorar essa confusão:** "Se o `PROCV` não encontra o valor procurado, ele retorna `0`. Essa afirmação é: ( ) CERTO ( ) ERRADO."
4. **Como o aluno deve evitar o erro:** Compreender que `#N/D` é o resultado da ausência do valor procurado e não um valor nulo. A frase "Nada disponível, não achou" pode ajudar a fixar essa ideia.

### 🚨 Limitações do Índice da Coluna
1. **O conhecimento correto:** O índice da coluna no `PROCV` não pode ser maior que o número total de colunas na matriz; caso contrário, o Excel retornará o erro `#REF!`.
2. **O erro ou confusão provável:** Candidatos podem achar que o `PROCV` simplesmente retornará um valor vazio se o índice for inválido.
3. **Como uma questão poderia explorar essa confusão:** "Se o índice da coluna em `PROCV` for maior que o número de colunas da matriz, o Excel retornará um valor vazio. Essa afirmação é: ( ) CERTO ( ) ERRADO."
4. **Como o aluno deve evitar o erro:** Lembrar que um índice inválido resulta em `#REF!`. A frase "Cuidado com o índice, o limite é real!" pode ser usada como lembrete.


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
