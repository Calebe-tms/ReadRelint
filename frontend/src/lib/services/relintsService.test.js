/**
 * ============================================================================
 * Testes Unitários: Relints Service (relintsService.js)
 * ============================================================================
 * Valida a lógica de negócio do frontend:
 *  - Formatação e passagem de query parameters (filtros de busca e especialidade)
 *  - Atribuição de código amigável para RELINTs (ex: remoção de .pdf)
 *  - Cálculo e agregação de métricas estatísticas para o Dashboard
 * ============================================================================
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { getRelints, getRelintById, updateRelint, getDashboardStats } from '$lib/services/relintsService';
import { apiClient } from '$lib/api/client';

vi.mock('$lib/api/client', () => ({
  apiClient: {
    get: vi.fn(),
    put: vi.fn()
  }
}));

describe('Serviço de RELINTs (relintsService.js)', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('deve montar a query string correta ao buscar com filtros', async () => {
    vi.mocked(apiClient.get).mockResolvedValue([
      { id: '1', source_file: 'RELINT-001.pdf', subject: 'Disputa de Facções', bm_group: 'Homicídio' }
    ]);

    const result = await getRelints({ search: 'Disputa', bm_group: 'Homicídio', relint_type: 'Todos' });

    // A URL real também recebe um '_t' de cache-busting no final (Date.now()), por isso
    // o match é por prefixo em vez de string exata.
    expect(apiClient.get).toHaveBeenCalledWith(
      expect.stringContaining('/api/v1/relints?search=Disputa&bm_group=Homic%C3%ADdio'),
      { headers: { 'Cache-Control': 'no-cache' } }
    );
    expect(result[0].code).toBe('RELINT-001');
  });

  it('deve formatar texto bruto e código amigável em getRelintById', async () => {
    vi.mocked(apiClient.get).mockResolvedValue({
      id: '2',
      source_file: 'boletim_alvorada.pdf',
      content: 'Texto bruto narrativo do boletim policial.'
    });

    const result = await getRelintById('2');

    expect(apiClient.get).toHaveBeenCalledWith('/api/v1/relints/2');
    expect(result.code).toBe('boletim_alvorada');
    expect(result.raw_text).toBe('Texto bruto narrativo do boletim policial.');
  });

  it('deve calcular estatísticas de dashboard corretamente a partir da lista', async () => {
    // getDashboardStats() tenta primeiro o endpoint agregado '/relints/stats'; simulamos
    // esse endpoint indisponível para exercitar o cálculo de fallback a partir da lista,
    // que é o que este teste valida.
    vi.mocked(apiClient.get).mockImplementation((/** @type {string} */ url) => {
      if (url.includes('/relints/stats')) {
        return Promise.reject(new Error('Endpoint de stats indisponível neste teste'));
      }
      return Promise.resolve([
        {
          id: '1',
          bm_group: 'Homicídio',
          extraction_method: 'Ollama (Llama 3.2)',
          participants: [{ name: 'A' }, { name: 'B' }]
        },
        {
          id: '2',
          bm_group: 'Tráfico de Drogas',
          extraction_method: 'Regex (Sem IA)',
          participants: [{ name: 'C' }]
        }
      ]);
    });

    const stats = await getDashboardStats();

    expect(stats.totalRelints).toBe(2);
    expect(stats.totalPersons).toBe(3);
    expect(stats.homicideCount).toBe(1);
    expect(stats.llmRate).toBe(50); // 1 de 2 foi lido via LLM
  });
});
