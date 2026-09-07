<script>
  import Input from '$lib/components/ui/Input.svelte';
  import Badge from '$lib/components/ui/Badge.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import { 
    MapPin, 
    ArrowSquareOut, 
    Compass, 
    Buildings, 
    Shield, 
    CheckCircle, 
    Info, 
    WarningCircle,
    Globe
  } from 'phosphor-svelte';

  /** @type {{ relint: any, disabled?: boolean, onUpdate?: (relint: any) => void }} */
  let { relint, disabled = false, onUpdate } = $props();

  /** @typedef {{ level: string, label: string, variant: 'amber'|'success'|'warning'|'error'|'info'|'neutral', icon: any }} GeoPrecisionInfo */

  // Cálculo reativo do nível de confiabilidade
  /** @type {GeoPrecisionInfo} */
  let geoPrecision = $derived.by(() => {
    const p = (relint.geo_precision || relint.precisao_geo || relint.precision_level || '').toLowerCase();
    
    if (p === 'alta' || p === 'exact_coords') {
      return {
        level: 'alta',
        label: 'Alta Confiabilidade (Coordenadas no Documento)',
        variant: 'success',
        icon: CheckCircle
      };
    }
    
    if (p === 'media' || p === 'direct_link') {
      return {
        level: 'media',
        label: 'Média Confiabilidade (Link Maps no Documento)',
        variant: 'info',
        icon: Info
      };
    }

    if (p === 'baixa' || p === 'address_inferred' || p === 'low_precision') {
      return {
        level: 'baixa',
        label: 'Baixa Confiabilidade (Somente Endereço)',
        variant: 'amber',
        icon: WarningCircle
      };
    }

    // Heurística de fallback refinada:
    // 1. Se tem coordenadas literais não aproximadas -> Alta
    if (relint.coordinates && relint.coordinates.trim().length > 5 && !relint.coordinates.includes('Aproximado')) {
      return {
        level: 'alta',
        label: 'Alta Confiabilidade (Coordenadas no Documento)',
        variant: 'success',
        icon: CheckCircle
      };
    }

    // 2. Se o link é um link explícito encurtado ou de local específico citado no PDF -> Média
    if (relint.map_url && (relint.map_url.includes('maps.app.goo.gl') || relint.map_url.includes('goo.gl/maps') || relint.map_url.includes('google.com/maps/place'))) {
      return {
        level: 'media',
        label: 'Média Confiabilidade (Link Maps no Documento)',
        variant: 'info',
        icon: Info
      };
    }

    // 3. Se for link de busca gerado (/maps/search) ou apenas endereço -> Baixa
    return {
      level: 'baixa',
      label: 'Baixa Confiabilidade (Somente Endereço)',
      variant: 'amber',
      icon: WarningCircle
    };
  });

  // URL para abrir no Google Maps (Prioridade: 1. Coordenadas explícitas, 2. Link do Documento, 3. Endereço completo)
  let googleMapsUrl = $derived.by(() => {
    if (relint.coordinates && relint.coordinates.trim().length > 5 && !relint.coordinates.includes('Aproximado')) {
      const cleanCoords = relint.coordinates.replace(/\s+/g, '');
      return `https://www.google.com/maps?q=${cleanCoords}`;
    }
    if (relint.map_url && relint.map_url.trim()) {
      return relint.map_url;
    }
    if (relint.address && relint.address.trim()) {
      let q = relint.address.trim();
      if (relint.municipality && !q.toLowerCase().includes(relint.municipality.toLowerCase())) {
        q = `${q}, ${relint.municipality} - RS`;
      }
      return `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(q)}`;
    }
    return '';
  });

  // URL do Iframe para o mapa incorporado (Prioridade: 1. Coords reais com pin, 2. Rua com busca, 3. Cidade inteira sem balão)
  let mapEmbedUrl = $derived.by(() => {
    // 1. Prioridade para coordenadas GPS válidas (com pin no ponto exato)
    if (relint.coordinates && relint.coordinates.trim().length > 5 && !relint.coordinates.includes('Aproximado')) {
      const parts = relint.coordinates.split(',').map((/** @type {string} */ s) => s.trim());
      if (parts.length === 2) {
        const lat = parseFloat(parts[0]);
        const lon = parseFloat(parts[1]);
        if (!isNaN(lat) && !isNaN(lon)) {
          const delta = 0.008;
          const bbox = `${lon - delta},${lat - delta},${lon + delta},${lat + delta}`;
          return `https://www.openstreetmap.org/export/embed.html?bbox=${bbox}&layer=mapnik&marker=${lat},${lon}`;
        }
      }
    }

    // 2. Se temos rua/endereço específico, busca detalhada no mapa
    const cleanAddr = (relint.address || '').replace(/sem informação|não informado/gi, '').trim();
    if (cleanAddr && cleanAddr !== '-' && cleanAddr.length > 3) {
      let q = cleanAddr;
      if (relint.municipality && !q.toLowerCase().includes(relint.municipality.toLowerCase())) {
        q = `${q}, ${relint.municipality} - RS`;
      }
      return `https://maps.google.com/maps?q=${encodeURIComponent(q)}&t=&z=15&ie=UTF8&iwloc=&output=embed`;
    }

    // 3. Se temos SOMENTE a cidade/município: enquadra a CIDADE INTEIRA (zoom 12, sem balão/iwloc)
    if (relint.municipality && relint.municipality.trim()) {
      const cityQuery = `${relint.municipality.trim()}, Rio Grande do Sul, Brasil`;
      return `https://maps.google.com/maps?q=${encodeURIComponent(cityQuery)}&t=&z=12&ie=UTF8&iwloc=&output=embed`;
    }

    return '';
  });

  function openGoogleMaps() {
    if (googleMapsUrl) {
      window.open(googleMapsUrl, '_blank', 'noopener,noreferrer');
    }
  }
</script>

<div class="tab-location">
  <!-- Cabeçalho de Precisão & Ações Rápidas -->
  <div class="location-header">
    <div class="geo-badge-box">
      <MapPin size={20} weight="fill" color="var(--color-amber-primary)" />
      <span class="geo-label">Nível de Precisão Geográfica:</span>
      <Badge variant={geoPrecision.variant} size="sm">
        {#snippet icon()}
          <svelte:component this={geoPrecision.icon} size={13} weight="bold" />
        {/snippet}
        {geoPrecision.label}
      </Badge>
    </div>

    {#if googleMapsUrl}
      <Button variant="outline" size="sm" onclick={openGoogleMaps}>
        {#snippet icon()}
          <ArrowSquareOut size={15} weight="bold" />
        {/snippet}
        Abrir no Google Maps
      </Button>
    {/if}
  </div>

  <!-- Grid de Campos Estruturados -->
  <div class="form-grid">
    <div class="form-group full-width">
      <Input 
        label="ENDEREÇO COMPLETO DO FATO (PADRÃO GOOGLE)" 
        bind:value={relint.address} 
        placeholder="ex: Rua Cento e Vinte e Sete, s/nº - Bairro São Cristóvão, Frederico Westphalen - RS"
        {disabled}
      />
    </div>

    <div class="form-group">
      <Input 
        label="BAIRRO / LOCALIDADE" 
        bind:value={relint.neighborhood} 
        placeholder="ex: Centro / Linha Santa Ana"
        {disabled}
      />
    </div>

    <div class="form-group">
      <Input 
        label="MUNICÍPIO / CIDADE" 
        bind:value={relint.municipality} 
        placeholder="ex: Palmeira das Missões"
        {disabled}
      />
    </div>

    <div class="form-group">
      <Input 
        label="UNIDADE POLICIAL (BPM / FRAÇÃO)" 
        bind:value={relint.police_unit} 
        placeholder="ex: 39º BPM / 1ª Cia"
        {disabled}
      />
    </div>

    <div class="form-group">
      <Input 
        label="COORDENADAS GPS (LATITUDE, LONGITUDE)" 
        bind:value={relint.coordinates} 
        placeholder="ex: -28.26123, -53.49123"
        {disabled}
      />
    </div>

    <div class="form-group full-width">
      <Input 
        label="URL DO GOOGLE MAPS" 
        bind:value={relint.map_url} 
        placeholder="ex: https://maps.app.goo.gl/xxx"
        {disabled}
      />
    </div>
  </div>

  <!-- Box de Visualização do Mapa -->
  <div class="map-container-card">
    <div class="map-card-header">
      <div class="map-title-box">
        <Globe size={18} weight="bold" color="var(--color-amber-primary)" />
        <span class="map-title">Visualização Geográfica da Ocorrência</span>
      </div>
      {#if relint.coordinates}
        <span class="map-coords-badge">{relint.coordinates}</span>
      {/if}
    </div>

    <div class="map-frame-wrapper">
      {#if mapEmbedUrl}
        <iframe 
          title="Mapa da Localização do Fato"
          src={mapEmbedUrl} 
          class="map-iframe"
          loading="lazy"
        ></iframe>
      {:else}
        <div class="map-empty-state">
          <MapPin size={36} weight="duotone" color="var(--color-text-muted)" />
          <p class="map-empty-text">Informe o endereço ou coordenadas para visualizar o mapa interativo.</p>
        </div>
      {/if}
    </div>
  </div>
</div>

<style>
  .tab-location {
    display: flex;
    flex-direction: column;
    gap: var(--space-4);
    padding: var(--space-2) 0;
  }

  .location-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    background-color: var(--color-bg-surface-card);
    padding: var(--space-3) var(--space-4);
    border-radius: var(--radius-sm);
    border: 1px solid var(--color-border-subtle);
    gap: var(--space-3);
    flex-wrap: wrap;
  }

  .geo-badge-box {
    display: flex;
    align-items: center;
    gap: var(--space-3);
    flex-wrap: wrap;
  }

  .geo-label {
    font-size: var(--font-size-ui);
    color: var(--color-text-muted);
    font-weight: var(--font-weight-medium);
  }

  .form-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: var(--space-4);
  }

  .full-width {
    grid-column: span 2;
  }

  /* Box de Mapa Interativo */
  .map-container-card {
    background-color: var(--color-bg-surface-card);
    border-radius: var(--radius-default);
    border: 1px solid var(--color-border-subtle);
    overflow: hidden;
    margin-top: var(--space-2);
  }

  .map-card-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: var(--space-3) var(--space-4);
    background-color: rgba(255, 255, 255, 0.02);
    border-bottom: 1px solid var(--color-border-subtle);
  }

  .map-title-box {
    display: flex;
    align-items: center;
    gap: var(--space-2);
  }

  .map-title {
    font-size: var(--font-size-ui);
    font-weight: var(--font-weight-semibold);
    color: var(--color-text-main);
    letter-spacing: var(--letter-spacing-wide);
    text-transform: uppercase;
  }

  .map-coords-badge {
    font-family: var(--font-family-mono);
    font-size: var(--font-size-xs);
    color: var(--color-amber-primary);
    background: rgba(224, 159, 62, 0.1);
    padding: 2px 8px;
    border-radius: var(--radius-xs);
    border: 1px solid rgba(224, 159, 62, 0.25);
  }

  .map-frame-wrapper {
    height: 320px;
    width: 100%;
    position: relative;
    background-color: #121212;
  }

  .map-iframe {
    width: 100%;
    height: 100%;
    border: none;
    filter: invert(90%) hue-rotate(180deg) brightness(95%) contrast(90%); /* Dark theme overlay para o mapa */
  }

  .map-empty-state {
    height: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: var(--space-2);
    padding: var(--space-6);
  }

  .map-empty-text {
    font-size: var(--font-size-ui);
    color: var(--color-text-muted);
    text-align: center;
    margin: 0;
  }
</style>
