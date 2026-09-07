import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { realtimeService } from './eventsService';

// Mock do ambiente do SvelteKit
vi.mock('$app/environment', () => ({
  browser: true
}));

// Mock do window.location
global.window = {
  location: {
    protocol: 'http:',
    host: 'localhost:5173'
  }
};

// Mock global do WebSocket
class MockWebSocket {
  static CONNECTING = 0;
  static OPEN = 1;
  static CLOSING = 2;
  static CLOSED = 3;

  /** @type {(() => void) | null} */
  onopen = null;

  /** @param {string} url */
  constructor(url) {
    this.url = url;
    this.readyState = 0; // CONNECTING
    this.send = vi.fn();

    // Simular a abertura assíncrona
    setTimeout(() => {
      this.readyState = 1; // OPEN
      if (this.onopen) this.onopen();
    }, 10);
  }
}

global.WebSocket = MockWebSocket;

describe('eventsService - WebSockets', () => {
  beforeEach(() => {
    vi.useFakeTimers();
    realtimeService.ws = null;
    realtimeService.isConnected = false;
    realtimeService.listeners.clear();
    if (realtimeService.reconnectTimer) {
      clearTimeout(realtimeService.reconnectTimer);
      realtimeService.reconnectTimer = null;
    }
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it('deve conectar ao WebSocket e emitir evento connected', async () => {
    const connectSpy = vi.fn();
    realtimeService.subscribe('connected', connectSpy);
    
    // Avança o timer para simular a abertura
    vi.advanceTimersByTime(20);
    
    expect(realtimeService.ws).not.toBeNull();
    expect(realtimeService.isConnected).toBe(true);

    const ws = realtimeService.ws;
    if (!ws) throw new Error('WebSocket não conectado');
    expect(ws.url).toBe('ws://localhost:5173/api/v1/events');

    // Simula o servidor enviando mensagem de connected
    (/** @type {(ev: any) => void} */ (ws.onmessage))({
        data: JSON.stringify({ event: 'connected', data: { status: 'online' } })
    });

    expect(connectSpy).toHaveBeenCalledWith({ status: 'online' });
  });

  it('deve emitir eventos arbitrários recebidos', async () => {
    const relintSpy = vi.fn();
    realtimeService.subscribe('relint_created', relintSpy);

    vi.advanceTimersByTime(20);

    const ws = realtimeService.ws;
    if (!ws) throw new Error('WebSocket não conectado');
    (/** @type {(ev: any) => void} */ (ws.onmessage))({
        data: JSON.stringify({ event: 'relint_created', data: { id: 1 } })
    });

    expect(relintSpy).toHaveBeenCalledWith({ id: 1 });
  });

  it('deve tentar reconectar após falha de conexão (onclose)', async () => {
    realtimeService.connect();
    vi.advanceTimersByTime(20);

    expect(realtimeService.isConnected).toBe(true);

    const ws = realtimeService.ws;
    if (!ws) throw new Error('WebSocket não conectado');

    // Força fechamento
    (/** @type {() => void} */ (ws.onclose))();
    expect(realtimeService.isConnected).toBe(false);
    expect(realtimeService.ws).toBeNull();

    // Aguarda o timer de 3000ms
    vi.advanceTimersByTime(3000);
    expect(realtimeService.ws).not.toBeNull();
  });

  it('deve enviar mensagens para o servidor (bidirecional)', async () => {
    realtimeService.connect();
    vi.advanceTimersByTime(20);

    expect(realtimeService.isConnected).toBe(true);

    realtimeService.send('client_ping', { foo: 'bar' });

    const ws = realtimeService.ws;
    if (!ws) throw new Error('WebSocket não conectado');
    expect(ws.send).toHaveBeenCalledWith(JSON.stringify({
        event: 'client_ping',
        data: { foo: 'bar' }
    }));
  });
});
