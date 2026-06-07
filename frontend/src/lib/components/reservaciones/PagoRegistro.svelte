<script lang="ts">
  import { pagosApi } from '$lib/services/pagos';
  import { toast } from '$lib/stores/toast';
  import Button from '$lib/components/Button.svelte';
  import Icon from '$lib/components/Icons.svelte';

  const METODOS = [
    { value: 'efectivo', label: 'Efectivo', icon: 'efectivo' },
    { value: 'tarjeta', label: 'Tarjeta', icon: 'credit-card' },
    { value: 'pago_movil', label: 'Pago Móvil', icon: 'pago_movil' },
  ];

  let { reservaId, totalPendiente, onpago } = $props();
  // svelte-ignore state_referenced_locally
  let monto = $state(totalPendiente);
  let metodo = $state('efectivo');
  let referencia = $state('');
  let guardando = $state(false);

  async function registrar() {
    if (monto <= 0) return toast.send('Monto inválido', 'error');
    guardando = true;
    try {
      await pagosApi.registrar({ reserva: reservaId, monto, metodo, referencia });
      toast.send('Pago registrado', 'success');
      onpago();
    } catch { toast.send('Error', 'error'); }
    finally { guardando = false; }
  }
</script>

<div class="space-y-6">
  <div class="bg-hotel-surface/40 rounded-2xl p-6">
    <h3 class="text-sm font-bold uppercase mb-4">Registrar Abono</h3>
    <div class="space-y-4">
      <div>
        <!-- svelte-ignore a11y_label_has_associated_control -->
        <label class="text-[10px] font-black uppercase">Monto a pagar ($)</label>
        <input type="number" bind:value={monto} class="input-hotel mt-1" />
      </div>
      <div>
        <!-- svelte-ignore a11y_label_has_associated_control -->
        <label class="text-[10px] font-black uppercase">Método de pago</label>
        <div class="grid grid-cols-3 gap-2 mt-2">
          {#each METODOS as m}
            <button onclick={() => metodo = m.value} class="flex flex-col items-center p-3 rounded-xl border {metodo === m.value ? 'border-hotel-gold bg-hotel-gold/10' : 'border-hotel-border'}">
              <Icon name='efectivo' class="w-5 h-5" />
              <span class="text-[9px] font-bold mt-1">{m.label}</span>
            </button>
          {/each}
        </div>
      </div>
      <div>
        <!-- svelte-ignore a11y_label_has_associated_control -->
        <label class="text-[10px] font-black uppercase">Referencia</label>
        <input type="text" bind:value={referencia} placeholder="Nº de operación" class="input-hotel mt-1" />
      </div>
    </div>
  </div>
  <div class="flex justify-end gap-3">
    <Button variant="ghost" onclick={onpago}>Cancelar</Button>
    <Button variant="gold" onclick={registrar} disabled={guardando}>{guardando ? 'Procesando...' : 'Confirmar Pago'}</Button>
  </div>
</div>