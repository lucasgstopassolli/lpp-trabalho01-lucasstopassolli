# Etapa Prévia: Setup do Repositório e Especificação da Vinícola

## Contexto para o Agente CLI
Este é o passo inicial obrigatório antes de escrever código. A regra da disciplina exige que `docs/especificacao.md` seja preenchido e commitado ANTES do código das etapas, sem citar tecnologias (Python, Socket.IO, Vue, Phaser) dentro da especificação.
- **Aluno:** Lucas Gabriel Stopassolli (`@lucasgstopassolli`)
- **Tema Sorteado (#22):** Vinícola (Recurso primário: `uvas` -> Recurso refinado: `vinho` | Construções: `parreiral`, `lagar`, `adega` | Trabalhadores: `vindimadores` | O que expira: `uva passa do ponto`).

## 1. Garantir `.gitignore` e `requirements.txt`
Verifique se o `.gitignore` na raiz ignora ambientes virtuais e arquivos temporários:
```gitignore
.venv/
venv/
__pycache__/
*.pyc
.DS_Store
.antigravity/
prompts/
```

Verifique se `requirements.txt` contém:
```txt
python-socketio
uvicorn
```

## 2. Preencher `docs/especificacao.md`
Substitua integralmente o conteúdo de `docs/especificacao.md` por:

```markdown
# Especificação — Vila em Tempo Real (Vinícola)

**Integrante(s):** Lucas Gabriel Stopassolli (@lucasgstopassolli)
**Tipo de vila (sorteio):** #22 — Vinícola (uvas → vinho | parreiral, lagar, adega | vindimadores | uva passa do ponto)

> Especificação comportamental na linguagem do domínio da Vinícola.

## 1. Regras da vila

- **Recurso primário e recurso refinado:** O recurso primário é **Uvas** (inicia em `150`). O recurso refinado é **Vinho** (inicia em `0`).
- **Custo de uma construção:** Cada nova estrutura da vinícola (Parreiral, Lagar ou Adega) custa **`50` uvas**.
- **Tempo da obra:** Cada obra leva **`8` segundos** para ser concluída.
- **Limite de trabalhadores:** A vinícola possui no máximo **`2` vindimadores** trabalhando simultaneamente em obras (`0/2` inicialmente).
- **Intervalo e quantidade da produção automática:** A cada **`5` segundos**, os parreirais produzem automaticamente **`10` uvas** (valor inicial).
- **O que muda quando uma obra termina:** O vindimador ocupado fica livre (`-1` ocupado), a obra passa para concluída (`+1` construção entre Parreiral, Lagar e Adega), a colheita automática de uvas aumenta em **`+5` uvas** por ciclo, e cada construção concluída passa a refinar **`2` uvas em `1` vinho** a cada ciclo de produção (caso haja uvas suficientes).
- **Regra de expiração (Uva passa do ponto):** As uvas são perecíveis. Um verificador de safra roda a cada **`15` segundos**; se o estoque acumulado ultrapassar **`180` uvas** sem que os jogadores construam ou refinem, **`20` uvas passam do ponto** (são perdidas do estoque).

## 2. Eventos

| Evento | Emite | Recebe | O que muda no estado |
|---|---|---|---|
| `estado.sincronizado` | Servidor | Só quem conectou | Entrega a fotografia atual da vinícola (fase, uvas, vinho, vindimadores e obras) ao recém-chegado. |
| `vila.abertura_solicitada` | Mestre | Servidor | (é um pedido para iniciar a safra; nada muda até validação) |
| `vila.iniciada` | Servidor | Todos | A fase da temporada muda de `aguardando` para `aberta` e iniciam-se os ciclos de tempo da safra. |
| `construcao.solicitada` | Jogador | Servidor | (é um pedido para erguer Parreiral/Lagar/Adega; nada muda até validação) |
| `construcao.iniciada` | Servidor | Todos | Debita `50` uvas do estoque, ocupa `1` vindimador e incrementa `1` obra em andamento. |
| `operacao.recusada` | Servidor | Só quem pediu | Nenhuma alteração no estado; informa o motivo da recusa (safra fechada, uvas insuficientes ou sem vindimador livre). |
| `recurso.produzido` | Servidor | Todos | Incrementa o estoque de uvas conforme a taxa de produção atual da vinícola. |
| `vinho.produzido` | Servidor | Todos | Quando há construções concluídas e uvas disponíveis, consome `2` uvas por construção concluída e gera `1` vinho por construção concluída. |
| `uva.expirada` | Servidor | Todos | Quando o estoque excede `180` uvas no ciclo de verificação, reduz `20` uvas que passaram do ponto. |
| `construcao.concluida` | Servidor | Todos | Libera `1` vindimador, reduz `1` obra em andamento, soma `1` construção concluída e aumenta a produção de uvas em `+5`. |
| `vila.encerramento_solicitado` | Mestre | Servidor | (é um pedido para encerrar a safra; nada muda até validação) |
| `vila.encerrada` | Servidor | Todos | A fase da temporada muda para `encerrada`, interrompendo a produção e bloqueando novas construções. |

## 3. Cenários de teste (Dado / Quando / Então, escritos com eventos)

### Recusa
**Dado** que a vinícola está na fase `aberta`, mas todos os `2` de `2` vindimadores já estão ocupados erguendo estruturas (ou o estoque de uvas é menor que `50`), **quando** um jogador emite `construcao.solicitada`, **então** o estado da vinícola não se altera e o servidor emite `operacao.recusada` exclusivamente para o jogador que fez o pedido informando o motivo.

### Passagem do tempo
**Dado** que o Mestre emitiu `vila.abertura_solicitada` e o servidor confirmou `vila.iniciada`, e um jogador iniciou uma obra (`construcao.iniciada`), **quando** os ciclos de tempo avançam sem novos cliques, **então** o servidor emite periodicamente `recurso.produzido` (e `vinho.produzido` após haver estruturas prontas) para todos, emite `construcao.concluida` após `8` segundos liberando o vindimador, e emite `uva.expirada` caso o estoque acumulado ultrapasse `180` uvas no ciclo de perecibilidade.

### Disputa entre dois jogadores
**Dado** que a temporada está `aberta` e há `1` de `2` vindimadores ocupados (restando apenas `1` vindimador livre) ou restam apenas `50` uvas no estoque, **quando** os jogadores A e B emitem `construcao.solicitada` simultaneamente, **então** o servidor avalia um pedido por vez de forma atômica, emitindo `construcao.iniciada` para todos em nome do primeiro jogador e emitindo `operacao.recusada` apenas para o segundo jogador.
```

## 3. Comandos Git Obrigatórios desta Etapa
Execute no terminal:
```bash
git add docs/especificacao.md .gitignore
git commit -m "docs: especificação da vila"
```