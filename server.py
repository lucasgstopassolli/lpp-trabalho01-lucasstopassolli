import socketio

# Instancia o servidor Socket.IO assíncrono (ASGI) permitindo conexões locais
sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")

# Serve o front-end (index.html) e os assets do mapa/sprites do Phaser
app = socketio.ASGIApp(sio, static_files={
    "/": "client/index.html",
    "/assets": "client/assets",
})

# A partir da Etapa 1, adicione o seu código ABAIXO desta linha.
