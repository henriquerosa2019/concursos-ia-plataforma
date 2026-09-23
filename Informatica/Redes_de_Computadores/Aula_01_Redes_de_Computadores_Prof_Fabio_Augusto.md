# INFORMÁTICA - REDES DE COMPUTADORES
**Professor:** Prof. Fabio Augusto  
**Link da Aula:** [Assistir no YouTube](https://www.youtube.com/watch?v=FkTh68O86Zw)  
**Duração:** 46 minutos (2788 segundos)  
**Categoria:** Edital de Concursos Públicos (Informática Básica e Avançada)  

---

## 1. Resumo Estruturado & Conceitos-Chave

### 1.1 Conceito Fundamental de Redes
Uma rede de computadores consiste na interconexão de dois ou mais dispositivos autônomos por meio de enlaces de comunicação (com ou sem fio), visando o **compartilhamento de recursos** (impressoras, servidores), **dados/arquivos** e **serviços** (e-mail, bancos de dados, web).

### 1.2 Classificação Geográfica (Escala de Abrangência)
As bancas adoram trocar a ordem ou as siglas dessas redes:
- **PAN (Personal Area Network):** Rede de área pessoal. Alcance limitado a poucos metros (até 10m). Tecnologias comuns: **Bluetooth**, NFC, infravermelho.
- **LAN (Local Area Network):** Rede local. Abrange um cômodo, residência, escritório ou prédio único. Tecnologias comuns: **Ethernet (IEEE 802.3)**, **Wi-Fi (WLAN - IEEE 802.11)**.
- **CAN (Campus Area Network):** Rede que interliga edifícios adjacentes de uma mesma universidade, condomínio ou complexo governamental.
- **MAN (Metropolitan Area Network):** Rede de área metropolitana. Abrange uma cidade ou região metropolitana interligando filiais. Variação sem fio: **WMAN (WiMAX - IEEE 802.16)**.
- **WAN (Wide Area Network):** Rede geograficamente distribuída sem fronteiras físicas (países, continentes). O maior exemplo mundial de WAN é a **Internet**.

### 1.3 Topologias de Rede (Física e Lógica)
- **Topologia em Estrela (Star):** É a topologia mais comum no mundo corporativo. Cada nó liga-se diretamente a um dispositivo concentrador central (**Switch**).
  - *Vantagem:* Se um cabo ou estação de trabalho falhar, apenas aquele dispositivo cai; o resto da rede continua operando perfeitamente.
  - *Desvantagem:* Se o concentrador central pifar, a rede inteira para.
- **Topologia em Barramento (Bus):** Todos os computadores compartilham um único meio de transmissão contínuo (cabo coaxial) com terminadores nas pontas.
  - *Armadilha:* Se o cabo central se romper em qualquer trecho, toda a rede é paralisada.
- **Topologia em Anel (Ring / Token Ring):** Os nós são conectados em circuito fechado. Os dados trafegam sequencialmente em uma direção passando de estação em estação até atingir o destino.
- **Topologia em Malha (Mesh):** Todos os nós conectam-se diretamente entre si (ponto a ponto). Oferece máxima redundância e tolerância a falhas, porém possui altíssimo custo de cabeamento.

### 1.4 Dispositivos de Rede e suas Camadas
1. **Hub (Concentrador):**
   - Opera na **Camada 1 (Física)**.
   - Não possui inteligência: quando recebe um pacote por uma porta, replica-o (**broadcast**) para todas as outras portas.
   - Gera tempestades de broadcast e alto número de colisões. Equipamento obsoleto.
2. **Switch (Comutador):**
   - Opera na **Camada 2 (Enlace)**.
   - É inteligente: lê e armazena os **endereços físicos MAC (Media Access Control)** das placas de rede.
   - Encaminha o frame exclusivamente para a porta do destinatário (**unicast**), eliminando colisões.
3. **Roteador (Router):**
   - Opera na **Camada 3 (Rede)**.
   - Encaminha pacotes entre redes distintas com base nos **endereços lógicos (IP)**.
   - Escolhe a melhor rota (tabela de roteamento) para os pacotes trafegarem.

### 1.5 Arquitetura TCP/IP e Principais Protocolos
A pilha TCP/IP organiza as comunicações em 4 camadas:

| Protocolo | Porta | Camada | Função Principal |
| :--- | :---: | :---: | :--- |
| **HTTP** | 80 | Aplicação | Transferência de páginas hipertexto web (texto puro, inseguro). |
| **HTTPS** | 443 | Aplicação | HTTP sobre camada de segurança criptográfica (SSL/TLS). |
| **FTP** | 20 / 21 | Aplicação | Transferência bidirecional de arquivos (dados na 20, controle na 21). |
| **SMTP** | 25 / 587 | Aplicação | Envio (*Simple Mail Transfer Protocol* - "Sua Mensagem Tá Partindo"). |
| **POP3** | 110 / 995 | Aplicação | Recebimento com download local (apaga do servidor por padrão). |
| **IMAP** | 143 / 993 | Aplicação | Acesso e gerenciamento sincronizado de mensagens no servidor. |
| **DNS** | 53 | Aplicação | Resolução de nomes de domínio em endereços IP e vice-versa. |
| **DHCP** | 67 / 68 | Aplicação | Atribuição dinâmica e automática de endereços IP na rede. |
| **SSH** | 22 | Aplicação | Acesso e administração remota por terminal com criptografia segura. |
| **Telnet** | 23 | Aplicação | Acesso remoto legado sem criptografia (senhas trafegam em texto claro). |
| **TCP** | — | Transporte | Orientado à conexão, confiável, controle de fluxo e retransmissão. |
| **UDP** | — | Transporte | Não orientado à conexão, sem garantia de entrega, foco em velocidade. |

---

## 2. Raio-X de Banca & Pegadinhas

### ⚠️ Armadilhas Clássicas do CEBRASPE:
1. **Afirmar que o Switch é um repetidor simples que envia para todos os computadores:**
   - *Pegadinha:* FALSO! Quem envia para todos é o **Hub**. O Switch envia apenas ao nó de destino com base na tabela MAC.
2. **Afirmar que o protocolo UDP realiza handshake antes de transmitir:**
   - *Pegadinha:* FALSO! Quem realiza o *Three-Way Handshake* (SYN, SYN-ACK, ACK) é o **TCP**. O UDP apenas dispara os datagramas sem confirmação de recebimento.
3. **Confundir POP3 com SMTP:**
   - *Pegadinha:* O Cebraspe adora afirmar que "o SMTP é utilizado pelo usuário para descarregar mensagens da caixa postal para o computador". FALSO! O SMTP **envia**; quem recebe/baixa é o POP3 ou IMAP.

### ⚠️ Armadilhas da FGV / FCC / Vunesp:
1. **Diferença entre Internet, Intranet e Extranet:**
   - **Internet:** Rede pública mundial acessível por qualquer usuário.
   - **Intranet:** Rede corporativa privada com acesso restrito a funcionários/colaboradores, que utiliza as MESMAS tecnologias e protocolos da Internet (TCP/IP, navegadores, servidores web internos).
   - **Extranet:** Extensão controlada da Intranet permitindo acesso externo a parceiros, fornecedores ou clientes autorizados via túnel seguro (VPN).

---

## 3. Esquematização & Mnemônicos

### 🧠 Mnemônico das Escalas Geográficas (Do Menor para o Maior):
$$\mathbf{P} \to \mathbf{L} \to \mathbf{M} \to \mathbf{W}$$
- **P**AN: **P**essoal (Bluetooth, ~1 a 10m).
- **L**AN: **L**ocal (Casa, sala, prédio, ~100m).
- **M**AN: **M**unicípio (Metrópole, cidade, ~10 a 50km).
- **W**AN: **W**orld (Mundo, países, global).

### 🧠 Mnemônico dos Protocolos de E-mail:
- **S**MTP = **S**ua **M**ensagem **T**á **P**artindo (Saída / Envio).
- **P**OP = **P**uxa **O** **P**acote (Baixa para a máquina).
- **I**MAP = **I**gualdade (Sincronizado na nuvem).

---

## 4. Mini-Simulado de Fixação (Estilo Banca)

### Questão 1 (CEBRASPE / Polícia Federal - Adaptada)
**Enunciado:** O switch é um dispositivo de interconexão que opera na camada física do modelo OSI e, por esse motivo, retransmite todo pacote recebido por uma de suas portas para todas as demais portas da rede local.  
A) CERTO  
B) ERRADO  
**Gabarito Oficial:** B (ERRADO)  
**Comentário Fundamentado:** O switch opera na **camada de enlace (camada 2)** e aprende os endereços físicos (MAC) das estações conectadas. Assim, ele direciona os quadros unicast exclusivamente à porta do computador de destino. O dispositivo que opera na camada física e transmite para todas as portas por broadcast é o **hub**.

### Questão 2 (FGV / MPE - Adaptada)
**Enunciado:** Um usuário necessita enviar um e-mail utilizando um cliente de correio eletrônico instalado em seu computador e, simultaneamente, manter as mensagens recebidas sincronizadas entre seu smartphone e seu notebook sem que sejam apagadas do servidor. Os protocolos empregados respectivamente para o envio e para essa sincronização são:  
A) POP3 e SMTP  
B) SMTP e IMAP  
C) IMAP e POP3  
D) HTTP e POP3  
E) SMTP e FTP  
**Gabarito Oficial:** B (SMTP e IMAP)  
**Comentário Fundamentado:** O envio de e-mails entre clientes e servidores de correio é realizado via **SMTP** (porta 587/25). Para manter as pastas sincronizadas em múltiplos dispositivos sem remover as mensagens do servidor, utiliza-se o **IMAP** (porta 143/993). O POP3 descarrega os e-mails localmente e não oferece sincronização entre dispositivos.

### Questão 3 (CEBRASPE / PRF - Adaptada)
**Enunciado:** Em uma topologia física em estrela, a interrupção do funcionamento de uma estação de trabalho isolada acarreta a indisponibilidade total de comunicação entre as demais estações da rede.  
A) CERTO  
B) ERRADO  
**Gabarito Oficial:** B (ERRADO)  
**Comentário Fundamentado:** Na topologia em estrela, cada estação possui um enlace exclusivo até o comutador central (switch). Se um computador ou cabo de ponta falhar, apenas aquele nó fica fora da rede; todas as outras máquinas continuam se comunicando normalmente. A rede só pararia por completo caso o concentrador central sofresse uma pane geral.

### Questão 4 (VUNESP / TJ-SP - Adaptada)
**Enunciado:** Assinale a alternativa que apresenta corretamente uma característica do protocolo de transporte UDP:  
A) Garante a entrega dos pacotes por meio de confirmação (ACK).  
B) Estabelece uma conexão prévia por meio do aperto de mão em três vias (Three-Way Handshake).  
C) É um protocolo não orientado à conexão, indicado para transmissões em tempo real que priorizam baixa latência.  
D) Realiza controle estrito de fluxo e de congestionamento de rede.  
E) Opera exclusivamente na camada de aplicação da arquitetura TCP/IP.  
**Gabarito Oficial:** C  
**Comentário Fundamentado:** O UDP (*User Datagram Protocol*) é um protocolo da camada de transporte que opera no modo sem conexão (*connectionless*). Ele não faz *handshake*, não confirma recebimento e não retransmite pacotes perdidos, o que o torna muito mais veloz para streaming de áudio/vídeo, jogos online e consultas DNS.
