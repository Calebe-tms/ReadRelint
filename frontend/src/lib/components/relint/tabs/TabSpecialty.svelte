<script>
  import Input from '$lib/components/ui/Input.svelte';
  import Switch from '$lib/components/ui/Switch.svelte';
  import Badge from '$lib/components/ui/Badge.svelte';
  import { Shield, Info } from 'phosphor-svelte';

  /** @type {{ relint: any, disabled?: boolean, onUpdate?: (relint: any) => void }} */
  let { relint, disabled = false, onUpdate } = $props();

  /**
   * Config declarativa por especialidade: cada campo aponta exatamente para as chaves
   * já expostas pela API em `relint[detailsKey]` (ver backend/api/routers/relints.py).
   * 'Outros' e 'Furto Qualificado' não têm tabela de detalhe própria — ficam de fora.
   * @typedef {{ key: string, label: string, type: 'text'|'select'|'switch', options?: string[] }} SpecialtyField
   * @typedef {{ detailsKey: string, badgeVariant: 'amber'|'success'|'warning'|'error'|'info'|'neutral', fields: SpecialtyField[] }} SpecialtyConfigEntry
   */
  /** @type {Record<string, SpecialtyConfigEntry>} */
  const SPECIALTY_CONFIG = {
    'Homicídio': {
      detailsKey: 'homicide_details',
      badgeVariant: 'error',
      fields: [
        { key: 'fact_type', label: 'TIPO DE FATO', type: 'select', options: ['Tentado', 'Consumado'] },
        { key: 'motivation', label: 'MOTIVAÇÃO', type: 'select', options: ['Feminicídio', 'Envolvimento com o Tráfico', 'Oposição a Ação PM', 'Desavença', 'Latrocídio', 'Desconhecido'] },
      ],
    },
    'Prisão por Tráfico': {
      detailsKey: 'drug_trafficking_details',
      badgeVariant: 'warning',
      fields: [
        { key: 'drug_quantity', label: 'QUANTIDADE APREENDIDA', type: 'text' },
        { key: 'drug_types', label: 'TIPO(S) DE DROGA', type: 'text' },
      ],
    },
    'Roubo a Estabelecimento': {
      detailsKey: 'establishment_robbery_details',
      badgeVariant: 'info',
      fields: [
        { key: 'establishment_type', label: 'TIPO DE ESTABELECIMENTO', type: 'text' },
        { key: 'location_type', label: 'TIPO DE LOCAL', type: 'select', options: ['Urbano', 'Rural'] },
        { key: 'injured_victims', label: 'VÍTIMAS LESIONADAS', type: 'switch' },
        { key: 'hostage_victim', label: 'HOUVE REFÉM', type: 'switch' },
      ],
    },
    'Roubo a Residência': {
      detailsKey: 'residence_robbery_details',
      badgeVariant: 'info',
      fields: [
        { key: 'location_type', label: 'TIPO DE LOCAL', type: 'select', options: ['Urbano', 'Rural'] },
        { key: 'injured_victims', label: 'VÍTIMAS LESIONADAS', type: 'switch' },
        { key: 'hostage_victim', label: 'HOUVE REFÉM', type: 'switch' },
      ],
    },
    'Roubo de Veículo': {
      detailsKey: 'vehicle_robbery_details',
      badgeVariant: 'info',
      fields: [
        { key: 'vehicle_model', label: 'MARCA / MODELO', type: 'text' },
        { key: 'license_plate', label: 'PLACA', type: 'text' },
        { key: 'recovered', label: 'VEÍCULO RECUPERADO', type: 'switch' },
        { key: 'recovery_location', label: 'LOCAL DE RECUPERAÇÃO', type: 'text' },
      ],
    },
    'Roubo a Pedestre': {
      detailsKey: 'pedestrian_robbery_details',
      badgeVariant: 'info',
      fields: [
        { key: 'injured_victims', label: 'VÍTIMA LESIONADA', type: 'switch' },
        { key: 'weapon_used', label: 'ARMA UTILIZADA', type: 'select', options: ['Arma de fogo', 'Arma branca', 'Agressão física'] },
        { key: 'stolen_object', label: 'OBJETO(S) ROUBADO(S)', type: 'text' },
      ],
    },
    'Furto de Veículo': {
      detailsKey: 'vehicle_theft_details',
      badgeVariant: 'info',
      fields: [
        { key: 'vehicle_model', label: 'MARCA / MODELO', type: 'text' },
        { key: 'license_plate', label: 'PLACA', type: 'text' },
        { key: 'recovered', label: 'VEÍCULO RECUPERADO', type: 'switch' },
        { key: 'recovery_location', label: 'LOCAL DE RECUPERAÇÃO', type: 'text' },
      ],
    },
  };

  const specialty = $derived(SPECIALTY_CONFIG[relint.bm_group]);

  // Garante que o objeto de detalhes exista para o binding funcionar mesmo em registros
  // antigos processados antes da tabela de especialidade ser preenchida com dado real.
  // A mutação do prop `relint` precisa acontecer num $effect (nunca dentro de um $derived,
  // que o Svelte 5 proíbe e lança `state_unsafe_mutation`).
  $effect(() => {
    if (specialty && !relint[specialty.detailsKey]) {
      relint[specialty.detailsKey] = {};
    }
  });

  const details = $derived(specialty ? relint[specialty.detailsKey] : null);
</script>

<div class="tab-specialty">
  {#if specialty && details}
    <div class="specialty-header">
      <Shield size={20} weight="fill" color="var(--color-amber-primary)" />
      <span class="specialty-title">Campos Especializados de {relint.bm_group}</span>
      <Badge variant={specialty.badgeVariant} size="sm">{relint.bm_group}</Badge>
    </div>

    <div class="form-grid">
      {#each specialty.fields as field (field.key)}
        <div class="form-group" class:is-switch={field.type === 'switch'}>
          {#if field.type === 'select'}
            <label class="select-label" for="specialty-{field.key}">{field.label}</label>
            <select
              id="specialty-{field.key}"
              class="specialty-select"
              bind:value={details[field.key]}
              {disabled}
            >
              <option value="">—</option>
              {#each field.options as option}
                <option value={option}>{option}</option>
              {/each}
            </select>
          {:else if field.type === 'switch'}
            <Switch label={field.label} bind:checked={details[field.key]} {disabled} />
          {:else}
            <Input label={field.label} bind:value={details[field.key]} {disabled} />
          {/if}
        </div>
      {/each}
    </div>
  {:else}
    <div class="empty-specialty">
      <Info size={24} weight="fill" color="var(--color-text-muted)" />
      <p class="empty-text">Este RELINT possui especialidade padrão (<strong>{relint.bm_group || 'Geral'}</strong>) sem formulários adicionais estendidos.</p>
    </div>
  {/if}
</div>

<style>
  .tab-specialty {
    display: flex;
    flex-direction: column;
    gap: var(--space-4);
    padding: var(--space-4) 0;
  }

  .specialty-header {
    display: flex;
    align-items: center;
    gap: var(--space-3);
    background-color: var(--color-bg-primary);
    padding: var(--space-3) var(--space-4);
    border-radius: var(--radius-sm);
    border: 1px solid var(--color-border-subtle);
  }

  .specialty-title {
    font-size: var(--font-size-ui);
    font-weight: var(--font-weight-medium);
    color: var(--color-text-main);
  }

  .form-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: var(--space-4);
  }

  .form-group.is-switch {
    display: flex;
    align-items: center;
    padding-top: var(--space-4);
  }

  .select-label {
    display: block;
    font-size: var(--font-size-xs);
    font-weight: var(--font-weight-semibold);
    letter-spacing: var(--letter-spacing-wider);
    text-transform: uppercase;
    color: var(--color-text-muted);
    margin-bottom: var(--space-2);
  }

  .specialty-select {
    width: 100%;
    height: 40px;
    padding: 0 var(--space-3);
    background-color: var(--color-bg-tertiary);
    border: 1px solid var(--color-border-medium);
    border-radius: var(--radius-sm);
    color: var(--color-text-main);
    font-family: var(--font-family-main);
    font-size: var(--font-size-base);
    cursor: pointer;
    transition:
      border-color var(--duration-fast) var(--ease-standard),
      background-color var(--duration-fast) var(--ease-standard);
  }

  .specialty-select:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  .specialty-select:focus {
    outline: none;
    border-color: var(--color-border-focus);
    background-color: var(--color-bg-surface-card);
  }

  .empty-specialty {
    display: flex;
    align-items: center;
    gap: var(--space-3);
    padding: var(--space-6);
    background-color: var(--color-bg-primary);
    border: 1px dashed var(--color-border-medium);
    border-radius: var(--radius-default);
  }

  .empty-text {
    font-size: var(--font-size-ui);
    color: var(--color-text-muted);
    margin: 0;
  }
</style>
