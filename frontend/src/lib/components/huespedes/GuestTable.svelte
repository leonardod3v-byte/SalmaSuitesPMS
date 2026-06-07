<script lang="ts">
  import { type HuespedListItem } from '$lib/services/huespedes';
  import VIPToggle from './VIPToggle.svelte';
  import Button from '$lib/components/Button.svelte';
  import Icon from '$lib/components/Icons.svelte';

  let { huespedes, onVipToggled, onVerDetalle }: {
    huespedes: HuespedListItem[];
    onVipToggled: (id: number, nuevoEstado: boolean) => void;
    onVerDetalle: (h: HuespedListItem) => void;
  } = $props();

  const df = new Intl.DateTimeFormat('es-VE', { day: '2-digit', month: 'short', year: 'numeric' });
</script>

{#snippet Identity(h: HuespedListItem)}
  <div class="flex items-center gap-3">
    <div class="w-8 h-8 rounded-full bg-hotel-gold/10 border border-hotel-gold/20 flex items-center justify-center shrink-0">
      <span class="text-[11px] font-black text-hotel-gold uppercase">
        {h.nombre_completo.charAt(0)}
      </span>
    </div>
    <div class="flex flex-col">
      <span class="font-semibold text-hotel-text-primary leading-tight">{h.nombre_completo}</span>
      <span class="md:hidden font-mono text-[10px] text-hotel-text-tertiary mt-0.5">{h.documento_formateado}</span>
    </div>
  </div>
{/snippet}

{#snippet Document(doc: string)}
  <span class="font-mono text-[10px] tracking-tighter bg-hotel-bg px-2 py-1 rounded border border-hotel-border text-hotel-text-secondary uppercase">
    {doc}
  </span>
{/snippet}

{#if huespedes.length === 0}
  <div class="py-24 text-center border border-dashed border-hotel-border rounded-2xl bg-hotel-surface/30">
    <Icon name="user" class="w-12 h-12 mx-auto mb-4 text-hotel-text-tertiary/50" />
    <p class="text-sm font-display italic text-hotel-text-tertiary">No hay huéspedes registrados en esta categoría</p>
  </div>
{:else}
  <div class="hidden md:block overflow-hidden rounded-xl border border-hotel-border bg-hotel-surface/20">
    <table class="w-full text-left border-collapse">
      <thead>
        <tr class="bg-hotel-bg/80 border-b border-hotel-border">
          {#each ['Huésped', 'Documento', 'Contacto', 'Estatus', 'Registro', ''] as label}
            <th class="px-5 py-4 text-[10px] font-black uppercase tracking-[0.15em] text-hotel-text-tertiary">{label}</th>
          {/each}
        </tr>
      </thead>
      <tbody class="divide-y divide-hotel-border/30">
        {#each huespedes as h (h.id)}
          <tr class="group hover:bg-hotel-gold/0.02 transition-colors">
            <td class="px-5 py-4">{@render Identity(h)}</td>
            <td class="px-5 py-4">{@render Document(h.documento_formateado)}</td>
            <td class="px-5 py-4">
              <div class="text-[11px] leading-relaxed">
                <p class="text-hotel-text-secondary font-medium">{h.telefono || '—'}</p>
                <p class="text-hotel-text-tertiary truncate max-w-[150px]">{h.email || ''}</p>
              </div>
            </td>
            <td class="px-5 py-4">
              <VIPToggle id={h.id} esVip={h.es_vip} onToggled={(v) => onVipToggled(h.id, v)} />
            </td>
            <td class="px-5 py-4 text-[11px] text-hotel-text-tertiary font-medium">
              {df.format(new Date(h.created_at))}
            </td>
            <td class="px-5 py-4 text-right">
              <Button variant="ghost" size="sm" onclick={() => onVerDetalle(h)}>
                Detalles
              </Button>
            </td>
          </tr>
        {/each}
      </tbody>
    </table>
  </div>

  <div class="md:hidden space-y-3">
    {#each huespedes as h (h.id)}
      <div class="bg-hotel-surface border border-hotel-border rounded-xl p-4 active:scale-[0.98] transition-all">
        <div class="flex items-start justify-between">
          <button onclick={() => onVerDetalle(h)} class="flex-1 text-left">
            {@render Identity(h)}
          </button>
          <VIPToggle id={h.id} esVip={h.es_vip} onToggled={(v) => onVipToggled(h.id, v)} />
        </div>
        
        {#if h.telefono || h.email}
          <div class="mt-4 pt-3 border-t border-hotel-border/50 flex flex-wrap gap-x-4 gap-y-1 text-[11px] text-hotel-text-tertiary">
            {#if h.telefono}<span class="flex items-center gap-1 font-medium text-hotel-text-secondary">{h.telefono}</span>{/if}
            {#if h.email}<span class="truncate">{h.email}</span>{/if}
          </div>
        {/if}
      </div>
    {/each}
  </div>
{/if}