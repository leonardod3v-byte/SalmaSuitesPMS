<script lang="ts">
  import { reservacionesApi, type ReservaListItem } from '$lib/services/reservaciones';
  import { toast } from '$lib/stores/toast';
  import ModalShell from '$lib/components/ModalShell.svelte';

  let { reserva, onclose, onregistrado }: {
    reserva:       ReservaListItem;
    onclose:       () => void;
    onregistrado:  () => void;
  } = $props();

  let motivo    = $state('');
  let guardando = $state(false);
  let error     = $state('');

  const hoy = new Date().toLocaleDateString('es-VE', {
    day: '2-digit', month: 'long', year: 'numeric'
  });

  async function registrar() {
    if (motivo.trim().length < 10) {
      error = 'Se requiere una justificación detallada (mín. 10 caracteres).';
      return;
    }
    guardando = true;
    error = '';
    try {
      await reservacionesApi.registrarNoShow(reserva.id, motivo);
      toast.send('Acta de No-Show archivada correctamente', 'success');
      onregistrado();
      onclose();
    } catch {
      error = 'Fallo en la comunicación con el servidor.';
      toast.send('Error al registrar No-Show', 'error');
    } finally {
      guardando = false;
    }
  }
</script>

<ModalShell
  title="Acta de No-Show"
  subtitle="Procedimiento de Anulación Irreversible"
  maxWidth="max-w-lg"
  {onclose}
>
  <div class="space-y-8">
    <div class="relative bg-hotel-bg p-6 rounded-3xl border border-hotel-border/60 shadow-inner group">
      <div class="absolute top-0 right-8 w-12 h-4 bg-hotel-surface border border-hotel-border border-t-0 rounded-b-xl opacity-20 group-hover:opacity-40 transition-opacity"></div>
      
      <header class="mb-4 flex justify-between items-start">
        <span class="text-[8px] font-black uppercase tracking-[0.4em] text-hotel-text-tertiary">Documento Digital</span>
        <span class="text-[10px] font-mono text-hotel-gold">ID-{reserva.id}</span>
      </header>

      <div class="space-y-3 font-mono text-[10px] leading-relaxed">
        <div class="flex justify-between border-b border-hotel-border/30 pb-1">
          <span class="text-hotel-text-tertiary uppercase">Hotel</span>
          <span class="text-hotel-text-primary font-bold">SALMA SUITE VIP</span>
        </div>
        <div class="flex justify-between border-b border-hotel-border/30 pb-1">
          <span class="text-hotel-text-tertiary uppercase">Fecha Emisión</span>
          <span class="text-hotel-text-primary uppercase">{hoy}</span>
        </div>
        <div class="flex justify-between border-b border-hotel-border/30 pb-1">
          <span class="text-hotel-text-tertiary uppercase">Huésped Titular</span>
          <span class="text-hotel-text-primary font-bold">{reserva.huesped_nombre}</span>
        </div>
        <div class="flex justify-between border-b border-hotel-border/30 pb-1">
          <span class="text-hotel-text-tertiary uppercase">Unidad Asignada</span>
          <span class="text-hotel-text-primary">HABITACIÓN #{reserva.habitacion_numero}</span>
        </div>
        
        <div class="mt-4 pt-2">
          <p class="text-hotel-text-tertiary uppercase mb-2">Declaratoria de Motivo:</p>
          <p class="text-hotel-text-primary italic whitespace-pre-wrap min-h-40px border-l-2 border-hotel-gold/30 pl-3">
            {motivo || 'Esperando entrada de datos...'}
          </p>
        </div>
      </div>
    </div>

    <div class="space-y-3">
      <label for="motivo" class="text-[10px] font-black uppercase tracking-[0.2em] text-hotel-text-secondary">Justificación del Incumplimiento</label>
      <textarea
        id="motivo"
        bind:value={motivo}
        rows="3"
        placeholder="Ej: El huésped no respondió a las llamadas de confirmación tras 4 horas de retraso..."
        class="w-full rounded-2xl px-5 py-4 text-xs bg-hotel-bg text-hotel-text-primary border-2 transition-all outline-none resize-none placeholder:text-hotel-text-tertiary/50
               {error ? 'border-hotel-error focus:ring-4 focus:ring-hotel-error/10' 
                      : 'border-hotel-border focus:border-hotel-gold/50 focus:ring-4 focus:ring-hotel-gold/5'}"
      ></textarea>
      {#if error}
        <p class="text-[9px] font-bold text-hotel-error-light uppercase tracking-widest animate-pulse">{error}</p>
      {/if}
    </div>

    <div class="flex gap-4">
      <button onclick={onclose} class="flex-1 py-4 text-[10px] font-black uppercase tracking-[0.2em] text-hotel-text-tertiary hover:text-hotel-text-primary transition-all">
        Abortar
      </button>
      <button
        onclick={registrar}
        disabled={guardando}
        class="flex-2 btn-error shadow-hotel-error/20"
      >
        {#if guardando}
          <svg class="w-4 h-4 animate-spin mr-2 inline" viewBox="0 0 24 24" fill="none">
            <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="3" stroke-dasharray="31.4" stroke-dashoffset="10"/>
          </svg>
          Archivando...
        {:else}
          Registrar Incumplimiento
        {/if}
      </button>
    </div>
  </div>
</ModalShell>