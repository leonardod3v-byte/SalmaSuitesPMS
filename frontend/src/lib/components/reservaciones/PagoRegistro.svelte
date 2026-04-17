<script lang="ts">
  import { reservacionesApi } from '$lib/services/reservaciones';
  import { toast } from '$lib/stores/toast';

  let { reservaId, totalPendiente, onpago }: {
    reservaId: number;
    totalPendiente: number;
    onpago: () => void;
  } = $props();

  let monto = $state(totalPendiente);
  let metodo = $state('transferencia');
  let referencia = $state('');
  let guardando = $state(false);

  async function registrarPago() {
    if (monto <= 0) return;
    guardando = true;
    
    try {
      // Esto crea un registro en una tabla de 'pagos', no modifica la 'reserva'
      await reservacionesApi.registrarPago(reservaId, {
        monto,
        metodo,
        referencia,
        fecha: new Date().toISOString()
      });
      
      toast.send('Pago procesado y balance actualizado', 'success');
      onpago();
    } catch {
      toast.send('Error al registrar el movimiento financiero', 'error');
    } finally {
      guardando = false;
    }
  }
</script>

<div class="bg-hotel-surface p-6 rounded-2rem border border-hotel-border shadow-xl">
  <div class="flex items-center gap-4 mb-6">
    <div class="w-12 h-12 rounded-xl bg-hotel-gold/10 flex items-center justify-center text-hotel-gold">
      <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
      </svg>
    </div>
    <div>
      <h3 class="font-display text-lg italic font-black text-hotel-text-primary">Registrar Abono</h3>
      <p class="text-[10px] uppercase tracking-widest text-hotel-text-tertiary">Balance pendiente: ${totalPendiente.toFixed(2)}</p>
    </div>
  </div>

  <div class="space-y-4">
    <div class="space-y-1">
      <label class="text-[9px] font-black uppercase tracking-widest text-hotel-text-secondary ml-2">Monto a Recibir</label>
      <input 
        type="number" 
        bind:value={monto}
        class="w-full bg-hotel-bg border-2 border-hotel-border rounded-xl px-4 py-3 text-sm font-mono text-hotel-gold focus:border-hotel-gold outline-none transition-all"
      />
    </div>

    <div class="grid grid-cols-2 gap-2">
      {#each ['efectivo', 'transferencia', 'punto', 'zelle'] as m}
        <button 
          onclick={() => metodo = m}
          class="py-2 rounded-lg border-2 text-[10px] font-bold uppercase tracking-tighter transition-all
          {metodo === m ? 'border-hotel-gold bg-hotel-gold/5 text-hotel-gold' : 'border-hotel-border text-hotel-text-tertiary'}">
          {m}
        </button>
      {/each}
    </div>

    <input 
      type="text" 
      bind:value={referencia}
      placeholder="Número de referencia / comprobante"
      class="w-full bg-hotel-bg border-2 border-hotel-border rounded-xl px-4 py-2 text-xs text-hotel-text-primary outline-none focus:border-hotel-gold"
    />

    <button 
      onclick={registrarPago}
      disabled={guardando || monto <= 0}
      class="w-full btn-gold py-4 text-[11px] font-black uppercase tracking-[0.2em] mt-2"
    >
      {guardando ? 'Comunicando con Banco...' : 'Confirmar Transacción'}
    </button>
  </div>
</div>