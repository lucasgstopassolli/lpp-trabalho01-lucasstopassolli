# Especificação — Vila em Tempo Real (Vinícola)

**Integrante(s):** Lucas Gabriel Stopassolli (@lucasgstopassolli)
**Tipo de vila (sorteio):** #22 — Vinícola (uvas → vinho | parreiral, lagar, adega/vinícola | vindimadores | uva passa do ponto)

> Especificação comportamental na linguagem do domínio da Vinícola.

## 1. Regras da vila

- **Recurso primário e recurso refinado:** O recurso primário é **Uvas** (inicia em `150`, colhidas do parreiral e prensadas no lagar). O recurso refinado é **Vinho** (inicia em `0`, produzido nas vinícolas/adegas concluídas).
- **Custo de uma construção:** Cada nova estrutura de **Vinícola** custa **`50` uvas**.
- **Tempo da obra:** Cada obra leva **`8` segundos** para ser concluída.
- **Limite de trabalhadores:** A vila possui no máximo **`2` vindimadores** trabalhando simultaneamente em obras (`0/2` inicialmente).
- **Intervalo e quantidade da produção automática:** A cada **`5` segundos**, o parreiral produz automaticamente **`10` uvas** (valor inicial).
- **O que muda quando uma obra termina:** O vindimador ocupado fica livre (`-1` ocupado), a obra passa para concluída (`+1` Vinícola pronta), a colheita automática de uvas aumenta em **`+5` uvas** por ciclo, e cada Vinícola concluída passa a refinar **`2` uvas em `1` vinho** a cada ciclo de produção (caso haja uvas suficientes no estoque).
- **Regra de expiração (Uva passa do ponto):** As uvas são perecíveis. Um verificador de safra atua a cada **`15` segundos**; se o estoque acumulado ultrapassar **`180` uvas** sem que os jogadores construam ou refinem o suficiente, **`20` uvas passam do ponto** (são perdidas do estoque).

## 2. Eventos

| Evento | Emite | Recebe | O que muda no estado |
|---|---|---|---|
| `estado.sincronizado` | Servidor | Só quem conectou | Entrega a fotografia atual da vinícola (fase, uvas, vinho, vindimadores e obras) ao recém-chegado. |
| `vila.abertura_solicitada` | Mestre | Servidor | (é um pedido para iniciar a safra; nada muda até validação) |
| `vila.iniciada` | Servidor | Todos | A fase da temporada muda de `aguardando` para `aberta` e iniciam-se os ciclos de colheita, refino e perecibilidade. |
| `construcao.solicitada` | Jogador | Servidor | (é um pedido para erguer uma Vinícola; nada muda até validação) |
| `construcao.iniciada` | Servidor | Todos | Debita `50` uvas do estoque, ocupa `1` vindimador e incrementa `1` obra de Vinícola em andamento. |
| `operacao.recusada` | Servidor | Só quem pediu | Nenhuma alteração no estado; informa o motivo da recusa (temporada não está aberta, uvas insuficientes ou sem vindimador livre). |
| `recurso.produzido` | Servidor | Todos | Incrementa o estoque de uvas conforme a taxa de produção atual da vinícola. |
| `vinho.produzido` | Servidor | Todos | Quando há Vinícolas concluídas e uvas disponíveis, consome `2` uvas por Vinícola pronta e gera `1` vinho por Vinícola pronta. |
| `uva.expirada` | Servidor | Todos | Quando o estoque excede `180` uvas no ciclo de verificação (a cada `15` segundos), reduz `20` uvas que passaram do ponto. |
| `construcao.concluida` | Servidor | Todos | Libera `1` vindimador, reduz `1` obra em andamento, soma `1` Vinícola concluída e aumenta a produção de uvas em `+5`. |
| `vila.encerramento_solicitado` | Mestre | Servidor | (é um pedido para encerrar a safra; nada muda até validação) |
| `vila.encerrada` | Servidor | Todos | A fase da temporada muda para `encerrada`, interrompendo a produção e bloqueando novas construções. |

## 3. Cenários de teste (Dado / Quando / Então, escritos com eventos)

### Recusa
**Dado** que a vinícola está na fase `aberta`, mas todos os `2` de `2` vindimadores já estão ocupados erguendo Vinícolas (ou o estoque de uvas é menor que `50`, ou a temporada ainda está `aguardando`), **quando** um jogador emite `construcao.solicitada`, **então** o estado da vinícola não se altera e o servidor emite `operacao.recusada` exclusivamente para o jogador que fez o pedido informando o motivo.

### Passagem do tempo
**Dado** que o Mestre emitiu `vila.abertura_solicitada` e o servidor confirmou `vila.iniciada`, e um jogador iniciou uma obra (`construcao.iniciada`), **quando** os ciclos de tempo avançam sem novos cliques, **então** o servidor emite periodicamente `recurso.produzido` a cada `5` segundos para todos, emite `construcao.concluida` após `8` segundos liberando o vindimador e passando a emitir `vinho.produzido` nos ciclos seguintes, e emite `uva.expirada` a cada `15` segundos caso o estoque acumulado ultrapasse `180` uvas.

### Disputa entre dois jogadores
**Dado** que a temporada está `aberta` e há `1` de `2` vindimadores ocupados (restando apenas `1` vindimador livre) ou restam apenas `50` uvas no estoque, **quando** os jogadores A e B emitem `construcao.solicitada` simultaneamente, **então** o servidor avalia um pedido por vez de forma atômica, emitindo `construcao.iniciada` para todos em nome do primeiro jogador e emitindo `operacao.recusada` apenas para o segundo jogador.
