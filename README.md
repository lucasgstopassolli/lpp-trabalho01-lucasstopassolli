# Vila em Tempo Real — Vinícola (#22)

Aplicação web cooperativa em tempo real desenvolvida para a disciplina de **Linguagem de Programação e Paradigmas (2026/2)** do curso de Sistemas de Informação — **UNIDAVI** (Prof. Esp. Ademar Perfoll Junior).

- **Tema sorteado (#22):** Vinícola (`uvas` → `vinho` | construções: `parreiral`, `lagar`, `adega/vinícola` | trabalhadores: `vindimadores` | expiração: `uva passa do ponto`).

## Integrantes
- Lucas Gabriel Stopassolli — [@lucasgstopassolli](https://github.com/lucasgstopassolli)

## Tecnologias Utilizadas
- **Servidor (Back-end):** Python 3, `python-socketio` (ASGI) e `uvicorn`.
- **Comunicação em Tempo Real:** Socket.IO.
- **Interface e Painel de Eventos (Front-end):** Vue 3 (via CDN) + Phaser 3 (via CDN, Tilemap 2D e animações de partículas/curvas de Bézier).

## Como instalar e executar

1. Clone o repositório e acesse a pasta do projeto:
   ```bash
   git clone https://github.com/lucasgstopassolli/lpp-trabalho01-lucasstopassolli.git
   cd lpp-trabalho01-lucasstopassolli
   ```
2. Crie e ative um ambiente virtual Python:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate        # Linux / macOS
   # .venv\Scripts\activate         # Windows
   ```
3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
4. Inicie o servidor com `uvicorn`:
   ```bash
   uvicorn server:app --reload
   ```
5. Abra o navegador em **`http://localhost:8000`** (não abra o arquivo `index.html` diretamente via `file://`).

## Como testar com duas ou três abas

1. **Conexão e Sincronização (`estado.sincronizado`):**
   - Abra duas abas lado a lado em `http://localhost:8000`.
   - Na Aba 1, digite seu nome e clique em **👑 Entrar como Mestre**.
   - Na Aba 2, digite outro nome e clique em **👨🌾 Entrar como Jogador**.
   - Ambas exibirão imediatamente `150 uvas`, `0 vinho`, `0/2 vindimadores` e o evento `⬇ on estado.sincronizado (causa: conexao)` no Painel de Eventos.
2. **Teste de Recusa antes da Abertura (`operacao.recusada`):**
   - Na Aba 2 (Jogador), clique em **🔨 Construir Vinícola** antes de o Mestre abrir a temporada.
   - Apenas a Aba 2 tremerá e receberá `⬇ on operacao.recusada` com o motivo `"A temporada não está aberta"`.
3. **Abertura e Passagem do Tempo (`vila.iniciada`, `recurso.produzido`, `vinho.produzido`, `uva.expirada`):**
   - Na Aba 1 (Mestre), clique em **☀️ Abrir temporada**. Ambas as abas recebem `vila.iniciada` e inicia-se a animação visual das uvas saindo do Parreiral até o Lagar.
   - A cada `5s`, o servidor emite `recurso.produzido` somando uvas automaticamente.
   - Na Aba 2 (Jogador), clique em **🔨 Construir Vinícola**. O estoque cai em `50 uvas`, ocupa `1/2 vindimadores` e inicia um canteiro de obras. Após `8s`, o servidor emite `construcao.concluida`, libera o vindimador, aumenta a colheita em `+5 uvas` e passa a emitir `vinho.produzido` a cada ciclo (convertendo `2 uvas` em `1 vinho` por Vinícola pronta, com animação do mosto indo do Lagar até a Vinícola).
   - Se o estoque ultrapassar `180 uvas`, a cada `15s` o servidor emite `uva.expirada` descontando `20 uvas` que passaram do ponto.
4. **Teste de Disputa Simultânea:**
   - Abra uma Aba 3 como **Jogador B**. Com `1/2 vindimadores` ocupados, clique em **🔨 Construir Vinícola** quase simultaneamente no Jogador A e no Jogador B.
   - O servidor processa um evento por vez sem `await` intermediário na validação: o primeiro recebe `construcao.iniciada` (indo para `2/2`) e o segundo recebe `operacao.recusada` (`"Sem vindimador livre no momento"`).
5. **Encerramento (`vila.encerrada`):**
   - Na Aba 1 (Mestre), clique em **🌙 Encerrar temporada**. Todos recebem `vila.encerrada`, a vinícola escurece e os temporizadores param.

## Perguntas

### 1. Quais eventos o seu sistema emite e escuta?
- **Pedidos emitidos pelo Cliente e escutados pelo Servidor (`pedir` / `emit` no cliente -> `@sio.on` no servidor):**
  - `vila.abertura_solicitada` (Mestre pede para abrir a temporada de vindima).
  - `construcao.solicitada` (Jogador pede para erguer uma nova Vinícola).
  - `vila.encerramento_solicitado` (Mestre pede para encerrar a temporada).
- **Fatos e recusas emitidos pelo Servidor e escutados pelos Clientes (`sio.emit` no servidor -> `ouvir` / `on` no cliente):**
  - `estado.sincronizado` (enviado em unicast `to=sid` ao conectar, entregando o estado inicial).
  - `operacao.recusada` (enviado em unicast `to=sid` apenas ao autor de um pedido recusado).
  - `vila.iniciada` (broadcast para todos ao iniciar a safra).
  - `construcao.iniciada` (broadcast ao aceitar uma obra de Vinícola, debitar 50 uvas e ocupar 1 vindimador).
  - `recurso.produzido` (broadcast disparado pelo temporizador a cada 5s colhendo uvas).
  - `vinho.produzido` (broadcast disparado pelo temporizador refinando 2 uvas em 1 vinho por Vinícola concluída).
  - `uva.expirada` (broadcast disparado pelo temporizador de perecibilidade a cada 15s quando o estoque passa de 180 uvas, perdendo 20 uvas).
  - `construcao.concluida` (broadcast disparado pelo temporizador após 8s de obra, liberando o vindimador e aumentando a produção em +5).
  - `vila.encerrada` (broadcast ao encerrar a temporada).

### 2. Como o sistema sabe quando deve atualizar os outros jogadores?
O sistema não utiliza *polling* (o cliente nunca pergunta ao servidor se algo mudou) e o cliente jamais altera o próprio estado local diretamente ao clicar em um botão. Toda mudança nasce no servidor a partir de duas fontes de eventos: (1) um pedido válido enviado por um cliente (`vila.abertura_solicitada`, `construcao.solicitada`, `vila.encerramento_solicitado`) ou (2) um temporizador assíncrono em segundo plano (`producao`, `expiracao`, `obra`). Sempre que o servidor altera o dicionário `estado`, ele emite imediatamente um evento de fato (`await sio.emit("nome.do.evento", fato(...))`) em *broadcast* para todos os clientes conectados. Cada cliente escuta esse evento via `ouvir(...)`, atualiza seu estado reativo com `atualizar(d)` e o Vue/Phaser redesenham a interface automaticamente. Apenas na conexão inicial (`estado.sincronizado`) e nas recusas (`operacao.recusada`) o servidor utiliza `to=sid` para responder individualmente.

### 3. Que parte do código mostra claramente o uso do paradigma orientado a eventos?
- **No Servidor (`server.py`):** Os decoradores `@sio.on("vila.abertura_solicitada")`, `@sio.on("construcao.solicitada")` e `@sio.on("vila.encerramento_solicitado")` funcionam como *event handlers* que escutam pedidos dos clientes, validam regras atomicamente e emitem fatos com `await sio.emit(...)` empacotando a causa geradora via `fato(causa, **extras)`. Além disso, as corrotinas `producao()`, `expiracao()` e `obra()` iniciadas com `sio.start_background_task(...)` demonstram o tempo como fonte geradora de eventos.
- **No Cliente (`client/index.html`):** As regiões `PEDIDOS` (funções que invocam `pedir(...)` encapsulando `socket.emit`) e `ESCUTAS` (chamadas `ouvir(evento, reacao, callback)` dentro de `entrar()` encapsulando `socket.on`), onde o cliente registra o encadeamento causal no Painel de Eventos e aciona a reação visual correspondente no Vue e nos métodos da `VilaScene` do Phaser.

## Uso de IA
Utilizei o assistente Gemini e o Antigravity CLI aplicando práticas de SDD (*Spec-Driven Development*) para planejar as etapas do projeto, revisar a consistência da especificação do tema sorteado (#22 Vinícola), estilizar a interface em tema Dark Arcade e implementar as animações visuais do fluxo produtivo no Phaser. Todo o código, regras de eventos e testes em múltiplas abas foram revisados, validados e testados por mim.

## Extras Implementados e Créditos Visuais
- **Cadeia produtiva completa de refino (`vinho.produzido`):** Conversão automática de uvas em vinho a cada ciclo proporcional ao número de Vinícolas concluídas.
- **Sistema de perecibilidade (`uva.expirada`):** Evento próprio disparado por temporizador quando o estoque acumula mais de 180 uvas sem uso, fazendo 20 uvas passarem do ponto.
- **Animação visual do fluxo produtivo no Phaser:** Transporte animado em curvas de Bézier das uvas saindo do Parreiral até o Lagar (`client/assets/lagar.png`) com efeito de prensa/partículas e envio do mosto até as Vinícolas construídas.
- **Interface Widescreen Dark Mode Arcade & Painel Minimizável:** HUD em cards, estética arcade retrô e Painel de Eventos retrátil com chips contadores de eventos em tempo real (Etapa 7).
- **Créditos de Assets:** Mapa e sprites base fornecidos no Kit Inicial da disciplina, com personalizações visuais de sprites (`sprites-vila.png`, `tileset-vila.png` e `lagar.png`) adaptadas pelo próprio autor para o tema Vinícola.
