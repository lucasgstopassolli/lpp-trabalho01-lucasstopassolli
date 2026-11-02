# Etapa 0: Servidor no Ar, Tela Aberta e Identidade da Vinícola

## Contexto para o Agente CLI
Na Etapa 0 o servidor sobe e serve os arquivos estáticos, sem emitir eventos de negócio ainda. Já deixaremos o `client/index.html` com os rótulos da **Vinícola** (Uvas, Vinho, Vindimadores, Parreiral/Lagar/Adega) e o rodapé com o nome do autor, mantendo o objeto `estado` e os métodos do Phaser prontos para as próximas etapas.

## 1. Verificar `server.py`
Garanta que `server.py` contenha exatamente o esqueleto inicial com comentários:

```python
import socketio

# Instancia o servidor Socket.IO assíncrono (ASGI) permitindo conexões locais
sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")

# Serve o front-end (index.html) e os assets do mapa/sprites do Phaser
app = socketio.ASGIApp(sio, static_files={
    "/": "client/index.html",
    "/assets": "client/assets",
})
```

## 2. Adaptar `client/index.html` para o tema Vinícola (sem adicionar escutas/pedidos ainda)
Em `client/index.html`, faça as seguintes adaptações mantendo toda a estrutura original do Kit:
1. No `<title>` e nos `<h1>`, use `🍇 Vinícola em Tempo Real` e `🍇 Vinícola`.
2. No `<section class="painel">`, exiba:
   - `🍇 Uvas: <strong>{{ estado.uvas }}</strong> (+{{ porMinuto }}/min) <small>(expira acima de 180)</small>`
   - `🍷 Vinho: <strong>{{ estado.vinho }}</strong> (refinado nas adegas)`
   - `👨‍🌾 Vindimadores: {{ estado.trabalhadores }}/{{ estado.limite }} <progress :value="estado.trabalhadores" :max="estado.limite"></progress>`
   - `🏛️ Construções (Parreiral / Lagar / Adega): {{ estado.concluidas }} concluídas, {{ estado.em_obra }} em obra`
3. No botão de construir do jogador:
   - `<button v-else @click="construir">🔨 Construir Parreiral/Lagar/Adega (custo {{ estado.custo }} uvas)</button>`
4. No `<footer>`:
   - `<footer>Desenvolvido por: Lucas Gabriel Stopassolli (@lucasgstopassolli)</footer>`
5. Nos métodos da `VilaScene` (Phaser), ajuste os emojis dos textos flutuantes para o tema da vinícola:
   - Em `obraIniciada(estado)`: troque `"-" + estado.custo + " 🪵"` por `"-" + estado.custo + " 🍇"`
   - Em `obraConcluida(estado)`: troque `"🏠 Obra concluída!"` por `"🍷 Estrutura pronta!"`
   - Em `recursoProduzido(estado)`: troque `"+" + estado.producao + " 🪵"` por `"+" + estado.producao + " 🍇"`
   - Adicione dois métodos visuais auxiliares na `VilaScene` (e exponha-os no `return` de `criarJogo()`):
     ```javascript
     vinhoProduzido(gerado) {                // vinho.produzido
       this.flutuar("+" + gerado + " 🍷", this.acampamento.x, this.acampamento.y - 12, "#6a1b9a");
     }
     uvaExpirada(perdidas) {                 // uva.expirada
       this.flutuar("-" + perdidas + " 🍇 (passou do ponto)", this.acampamento.x, this.acampamento.y, "#c62828");
     }
     ```
   - E no objeto retornado por `criarJogo()`, adicione:
     ```javascript
     vinhoProduzido: (...a) => chamar("vinhoProduzido", ...a),
     uvaExpirada: (...a) => chamar("uvaExpirada", ...a),
     ```
6. No `setup()` do Vue:
   - Em `estado = reactive({...})`, inclua `uvas: 0, vinho: 0,` (mantendo também `toras: 0` por retrocompatibilidade caso necessário).
   - Em `resumir(d)`, formate o resumo de estado como:
     ```javascript
     if (e) partes.push("uvas " + e.uvas + ", vinho " + e.vinho + ", vindimadores " + e.trabalhadores + "/" + e.limite);
     ```

## 3. Teste e Commit
1. Crie a venv (se ainda não existir) e instale os pacotes:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. Faça o commit da Etapa 0:
   ```bash
   git add server.py client/index.html requirements.txt client/assets/
   git commit -m "feat: kit inicial e esqueleto do servidor"
   ```