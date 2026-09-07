"""
Testes unitários e de integração para o endpoint de eventos WebSockets em tempo real (/api/v1/events).
"""
import pytest
from fastapi.testclient import TestClient
from backend.api.app import app
from backend.api.routers.events import broadcaster

def test_websocket_connection_and_broadcast():
    client = TestClient(app)
    # Tenta conectar via websocket e realizar as asserções dentro do contexto
    with client.websocket_connect("/api/v1/events") as websocket:
        # 1. Verifica se a mensagem inicial de conexão é enviada corretamente
        data = websocket.receive_json()
        assert data["event"] == "connected"
        assert data["data"]["status"] == "online"
        
        # 2. Verifica se a inscrição no broadcaster ocorreu com sucesso
        # Como _listeners contém o próprio objeto websocket interno do starlette/fastapi,
        # apenas verificamos se há ouvintes.
        assert len(broadcaster._listeners) > 0
        
        # 3. Testa o método de broadcast bidirecional
        # Força o envio de uma mensagem pelo broadcaster
        broadcaster.broadcast("test_event", {"message": "hello"})
        
        # O cliente websocket deve receber exatamente o que o broadcaster emitiu
        event_data = websocket.receive_json()
        assert event_data["event"] == "test_event"
        assert event_data["data"]["message"] == "hello"

        # 4. Testa a via reversa: Envio de mensagem pelo cliente em direção ao servidor
        # A implementação atual no servidor apenas processa silenciosamente (ou printa)
        websocket.send_json({"event": "client_ping", "data": {}})
        # Se nenhuma exceção WebSocketDisconnect ou parse error for disparada, o teste de ping/bidirecional passa.

    # 5. Após o `with` acabar (desconexão forçada pelo cliente), o servidor
    # dispara a exceção WebSocketDisconnect e invoca broadcaster.unsubscribe(websocket).
    # Aqui não podemos testar o _listeners de forma determinística porque a desconexão é assíncrona,
    # mas o fato de a conexão abrir e fechar limpo cumpre o fluxo de reatividade.
