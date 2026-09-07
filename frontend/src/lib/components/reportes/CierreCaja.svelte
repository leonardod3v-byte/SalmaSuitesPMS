<script lang="ts">
    import { onMount } from 'svelte';
    import { auth } from '$lib/stores/auth.svelte';
    import { toast } from '$lib/stores/toast';
    import DatePicker from '$components/ui/DatePicker.svelte';
    import Button from '$components/ui/Button.svelte';
    import Loading from '$components/ui/Loading.svelte';
    import { fetchDiario, confirmarCierre } from '$lib/services/reportes';
    import type { ResumenDiario } from '$lib/types/reporte';

    let fecha = $state(new Date().toISOString().split('T')[0]);
    let datos = $state<ResumenDiario | null>(null);
    let cargando = $state(false);
    let error = $state('');
    let cerrando = $state(false);

    async function cargar() {
        cargando = true;
        error = '';
        try {
            datos = await fetchDiario(fecha);
        } catch (e: any) {
            error = e.message;
        } finally {
            cargando = false;
        }
    }

    async function cerrarCaja() {
        if (!confirm('¿Confirmar el cierre de caja para esta fecha? Una vez cerrado no se podrán registrar más pagos.')) return;
        cerrando = true;
        try {
            await confirmarCierre(fecha);
            toast.success('Cierre de caja realizado.');
            await cargar();
        } catch (e: any) {
            toast.error(e.message);
        } finally {
            cerrando = false;
        }
    }

    function imprimir() {
        window.print();
    }

    function exportarCSV() {
        if (!datos?.detalle.length) return;
        const headers = ['Hora', 'Reserva', 'Huésped', 'Método', 'Referencia', 'Monto'];
        const rows = datos.detalle.map(d => [d.hora, `#${d.reserva_id}`, d.huesped, d.metodo_pago, d.numero_referencia || '—', d.monto]);
        const csv = [headers, ...rows].map(r => r.map(c => `"${c}"`).join(',')).join('\n');
        const blob = new Blob(['\uFEFF' + csv], { type: 'text/csv;charset=utf-8;' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `cierre_caja_${fecha}.csv`;
        a.click();
        URL.revokeObjectURL(url);
    }

    onMount(() => cargar());

    function formatNumber(val: string): string {
        return parseFloat(val).toFixed(2);
    }
</script>

<div class="space-y-6">
    <!-- Selector de fecha -->
    <div class="flex flex-wrap items-center gap-3 p-3 rounded-2xl bg-hotel-surface/40 border border-hotel-border">
        <DatePicker bind:value={fecha} />
        <div class="w-px h-8 bg-hotel-border hidden sm:block"></div>
        <div class="flex gap-2">
            <button
                onclick={() => { 
                    fecha = new Date().toISOString().split('T')[0]; 
                    cargar(); 
                }}
                class="px-3 py-1.5 rounded-lg text-[10px] font-bold uppercase tracking-wider border {fecha === new Date().toISOString().split('T')[0] ? 'border-hotel-gold bg-hotel-gold/5 text-hotel-gold' : 'border-hotel-border text-hotel-text-tertiary hover:border-hotel-gold/50 hover:text-hotel-gold'} transition-all"
            >
                Hoy
            </button>
            <button
                onclick={() => { 
                    const ayer = new Date(Date.now() - 86400000).toISOString().split('T')[0];
                    fecha = ayer;
                    cargar(); 
                }}
                class="px-3 py-1.5 rounded-lg text-[10px] font-bold uppercase tracking-wider border border-hotel-border text-hotel-text-tertiary hover:border-hotel-gold/50 hover:text-hotel-gold transition-all"
            >
                Ayer
            </button>
        </div>
        <Button variant="gold" size="md" onclick={cargar}>
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/></svg>
        </Button>
        <div class="w-px h-8 bg-hotel-border hidden sm:block"></div>
        {#if datos}
            <Button variant="secondary" size="md" onclick={exportarCSV}>CSV</Button>
            <a href="{import.meta.env.VITE_API_URL ?? 'http://localhost:8000/api'}/reportes/cierre-caja-pdf/?fecha={fecha}" target="_blank" class="no-underline">
                <Button variant="secondary" size="md">
                    Imprimir
                </Button>
            </a>
            {#if auth.isAdmin && !datos.cerrado}
                <Button variant="danger" size="md" onclick={cerrarCaja} loading={cerrando}>Cerrar Caja</Button>
            {/if}
        {/if}
    </div>

    {#if cargando}
        <Loading type="dashboard" message="Cargando cierre..." />
    {:else if error}
        <div class="text-center p-8 bg-hotel-error/5 border border-hotel-error/20 rounded-2xl">
            <p class="text-hotel-error-light font-bold uppercase tracking-widest text-xs mb-4">{error}</p>
            <Button variant="gold" size="md" onclick={cargar}>Reintentar</Button>
        </div>
    {:else if datos}
        <!-- Resumen -->
        <div class="grid grid-cols-2 sm:grid-cols-5 gap-4">
            <div class="p-4 rounded-2xl bg-hotel-surface border border-hotel-border text-center">
                <p class="text-[10px] uppercase tracking-wider text-hotel-text-tertiary mb-1">Total</p>
                <p class="text-xl font-bold text-hotel-gold">${formatNumber(datos.total_general)}</p>
            </div>
            <div class="p-4 rounded-2xl bg-hotel-surface border border-hotel-border text-center">
                <p class="text-[10px] uppercase tracking-wider text-hotel-text-tertiary mb-1">Efectivo</p>
                <p class="text-xl font-bold text-hotel-text-primary">${formatNumber(datos.total_efectivo)}</p>
            </div>
            <div class="p-4 rounded-2xl bg-hotel-surface border border-hotel-border text-center">
                <p class="text-[10px] uppercase tracking-wider text-hotel-text-tertiary mb-1">Tarjeta</p>
                <p class="text-xl font-bold text-hotel-text-primary">${formatNumber(datos.total_tarjeta)}</p>
            </div>
            <div class="p-4 rounded-2xl bg-hotel-surface border border-hotel-border text-center">
                <p class="text-[10px] uppercase tracking-wider text-hotel-text-tertiary mb-1">Pago Móvil</p>
                <p class="text-xl font-bold text-hotel-text-primary">${formatNumber(datos.total_pago_movil)}</p>
            </div>
            <div class="p-4 rounded-2xl bg-hotel-surface border border-hotel-border text-center">
                <p class="text-[10px] uppercase tracking-wider text-hotel-text-tertiary mb-1">Transacciones</p>
                <p class="text-xl font-bold text-hotel-text-primary">{datos.cantidad_transacciones}</p>
            </div>
        </div>

        {#if datos.cerrado}
            <div class="flex items-center gap-2 p-3 rounded-xl bg-hotel-success/10 border border-hotel-success/20 text-hotel-success-light text-sm">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/></svg>
                Caja cerrada — No se pueden registrar más pagos en esta fecha.
            </div>
        {/if}

        <!-- Tabla detalle -->
        <div class="bg-hotel-surface rounded-2xl border border-hotel-border shadow-hotel-sm overflow-hidden">
            <div class="overflow-x-auto">
                <table class="w-full text-sm">
                    <thead>
                        <tr class="border-b border-hotel-border text-[10px] uppercase tracking-widest text-hotel-text-tertiary text-left">
                            <th class="p-3 font-bold">Hora</th>
                            <th class="p-3 font-bold">Reserva</th>
                            <th class="p-3 font-bold hidden md:table-cell">Huésped</th>
                            <th class="p-3 font-bold">Método</th>
                            <th class="p-3 font-bold hidden sm:table-cell">Referencia</th>
                            <th class="p-3 font-bold text-right">Monto</th>
                        </tr>
                    </thead>
                    <tbody>
                        {#each datos.detalle as d}
                            <tr class="border-b border-hotel-border/30">
                                <td class="p-3 text-hotel-text-secondary">{d.hora?.substring(0, 5)}</td>
                                <td class="p-3">
                                    <a href="/reservaciones/{d.reserva_id}" class="text-hotel-gold hover:underline font-bold">#{d.reserva_id}</a>
                                </td>
                                <td class="p-3 text-hotel-text-primary hidden md:table-cell">{d.huesped}</td>
                                <td class="p-3 text-hotel-text-secondary">{d.metodo_pago}</td>
                                <td class="p-3 text-hotel-text-secondary hidden sm:table-cell">{d.numero_referencia || '—'}</td>
                                <td class="p-3 text-right font-bold text-hotel-gold">${formatNumber(d.monto)}</td>
                            </tr>
                        {:else}
                            <tr>
                                <td colspan="6" class="p-10 text-center text-hotel-text-tertiary uppercase tracking-widest text-xs">Sin transacciones en esta fecha</td>
                            </tr>
                        {/each}
                    </tbody>
                </table>
            </div>
        </div>
    {/if}
</div>