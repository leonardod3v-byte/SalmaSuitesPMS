<script lang="ts">
    import { onMount } from 'svelte';
    import { auth } from '$lib/stores/auth.svelte';
    import { toast } from '$lib/stores/toast';
    import DatePicker from '$components/ui/DatePicker.svelte';
    import Button from '$components/ui/Button.svelte';
    import Loading from '$components/ui/Loading.svelte';
    import Icon from '$components/ui/Icons.svelte';
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

    async function abrirPDF() {
        try {
            const apiUrl = import.meta.env.VITE_API_URL ?? 'http://localhost:8000/api';
            const token = localStorage.getItem('auth_token');

            const res = await fetch(`${apiUrl}/reportes/cierre-caja-pdf/?fecha=${fecha}`, {
                headers: { 'Authorization': `Token ${token}` }
            });

            if (!res.ok) throw new Error('Error al generar el PDF');

            const blob = await res.blob();
            const url = URL.createObjectURL(blob);
            window.open(url, '_blank');
            setTimeout(() => URL.revokeObjectURL(url), 10000);
        } catch (err: any) {
            toast.error(err.message || 'Error al abrir el PDF');
        }
    }

    onMount(() => cargar());

    function formatNumber(val: string): string {
        return parseFloat(val).toFixed(2);
    }
</script>

<div class="space-y-6">
    <!-- Barra de Filtros y Acciones -->
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 p-4 rounded-2xl bg-hotel-surface/40 border border-hotel-border">
        <div class="flex flex-wrap items-center gap-3">
            <div class="w-full sm:w-auto">
                <DatePicker bind:value={fecha} />
            </div>

            <!-- Botones rápidos: Hoy / Ayer -->
            <div class="flex gap-2 mt-2 md:mt-0">
                <button
                    onclick={() => { fecha = new Date().toISOString().split('T')[0]; cargar(); }}
                    class="px-3 py-1.5 rounded-lg text-[10px] font-bold uppercase tracking-wider border {fecha === new Date().toISOString().split('T')[0] ? 'border-hotel-gold bg-hotel-gold/10 text-hotel-gold' : 'border-hotel-border text-hotel-text-tertiary hover:border-hotel-gold/50 hover:text-hotel-gold'} transition-all"
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
                <Icon name="search" class="w-4 h-4" />
            </Button>
        </div>

        <div class="flex flex-wrap items-center gap-2">
            {#if datos}
                <Button variant="secondary" size="md" onclick={abrirPDF}>
                    <span class="flex items-center gap-1.5">
                        <Icon name="file" class="w-4 h-4" /> PDF
                    </span>
                </Button>
                {#if auth.isAdmin && !datos.cerrado}
                    <Button variant="danger" size="md" onclick={cerrarCaja} loading={cerrando}>
                        <span class="flex items-center gap-1.5">
                            <Icon name="lock" class="w-4 h-4" /> Cerrar Caja
                        </span>
                    </Button>
                {/if}
            {/if}
        </div>
    </div>

    {#if cargando}
        <Loading type="dashboard" message="Cargando cierre de caja..." />
    {:else if error}
        <div class="text-center p-8 bg-hotel-error/5 border border-hotel-error/20 rounded-2xl">
            <p class="text-hotel-error-light font-bold uppercase tracking-widest text-xs mb-4">{error}</p>
            <Button variant="gold" size="md" onclick={cargar}>Reintentar</Button>
        </div>
    {:else if datos}
        <!-- Resumen en Tarjetas -->
        <div class="grid grid-cols-2 sm:grid-cols-5 gap-4">
            <div class="p-4 rounded-2xl bg-hotel-surface border border-hotel-border text-center shadow-sm">
                <div class="flex items-center justify-center mb-2 text-hotel-gold">
                    <Icon name="dinero" class="w-5 h-5" />
                </div>
                <p class="text-[10px] uppercase tracking-wider text-hotel-text-tertiary mb-1">Total</p>
                <p class="text-xl font-bold text-hotel-gold">${formatNumber(datos.total_general)}</p>
            </div>
            <div class="p-4 rounded-2xl bg-hotel-surface border border-hotel-border text-center shadow-sm">
                <div class="flex items-center justify-center mb-2 text-hotel-success-light">
                    <Icon name="dinero" class="w-5 h-5" />
                </div>
                <p class="text-[10px] uppercase tracking-wider text-hotel-text-tertiary mb-1">Efectivo</p>
                <p class="text-xl font-bold text-hotel-text-primary">${formatNumber(datos.total_efectivo)}</p>
            </div>
            <div class="p-4 rounded-2xl bg-hotel-surface border border-hotel-border text-center shadow-sm">
                <div class="flex items-center justify-center mb-2 text-hotel-info-light">
                    <Icon name="dinero" class="w-5 h-5" />
                </div>
                <p class="text-[10px] uppercase tracking-wider text-hotel-text-tertiary mb-1">Tarjeta</p>
                <p class="text-xl font-bold text-hotel-text-primary">${formatNumber(datos.total_tarjeta)}</p>
            </div>
            <div class="p-4 rounded-2xl bg-hotel-surface border border-hotel-border text-center shadow-sm">
                <div class="flex items-center justify-center mb-2 text-hotel-vip-light">
                    <Icon name="dinero" class="w-5 h-5" />
                </div>
                <p class="text-[10px] uppercase tracking-wider text-hotel-text-tertiary mb-1">Pago Móvil</p>
                <p class="text-xl font-bold text-hotel-text-primary">${formatNumber(datos.total_pago_movil)}</p>
            </div>
            <div class="p-4 rounded-2xl bg-hotel-surface border border-hotel-border text-center shadow-sm">
                <div class="flex items-center justify-center mb-2 text-hotel-text-secondary">
                    <Icon name="file" class="w-5 h-5" />
                </div>
                <p class="text-[10px] uppercase tracking-wider text-hotel-text-tertiary mb-1">Transacciones</p>
                <p class="text-xl font-bold text-hotel-text-primary">{datos.cantidad_transacciones}</p>
            </div>
        </div>

        {#if datos.cerrado}
            <div class="flex items-center gap-2 p-4 rounded-xl bg-hotel-success/10 border border-hotel-success/20 text-hotel-success-light text-sm font-bold">
                <Icon name="lock" class="w-5 h-5 shrink-0" />
                Caja cerrada — No se pueden registrar más pagos en esta fecha.
            </div>
        {/if}

        <!-- Tabla de Transacciones -->
        <div class="bg-hotel-surface rounded-2xl border border-hotel-border shadow-hotel-sm overflow-hidden">
            <div class="p-4 border-b border-hotel-border/50 bg-hotel-bg/20 flex justify-between items-center">
                <h3 class="font-display text-lg text-hotel-text-primary italic">Detalle de Transacciones</h3>
                <span class="text-[10px] uppercase font-bold text-hotel-text-tertiary bg-hotel-surface px-2 py-1 rounded-md border border-hotel-border">
                    {datos.cantidad_transacciones} registros
                </span>
            </div>
            <div class="overflow-x-auto">
                <table class="w-full text-sm">
                    <thead>
                        <tr class="border-b border-hotel-border text-[10px] uppercase tracking-widest text-hotel-text-tertiary text-left bg-hotel-bg/10">
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
                            <tr class="border-b border-hotel-border/30 hover:bg-hotel-surface-hover transition-colors">
                                <td class="p-3 text-hotel-text-secondary text-xs">{d.hora?.substring(0, 5)}</td>
                                <td class="p-3">
                                    <a href="/reservaciones/{d.reserva_id}" class="text-hotel-gold hover:underline font-bold">#{d.reserva_id}</a>
                                </td>
                                <td class="p-3 text-hotel-text-primary hidden md:table-cell text-xs">{d.huesped}</td>
                                <td class="p-3">
                                    <span class="px-2 py-0.5 rounded-md bg-hotel-bg border border-hotel-border text-[10px] font-medium text-hotel-text-secondary">
                                        {d.metodo_pago}
                                    </span>
                                </td>
                                <td class="p-3 text-hotel-text-secondary hidden sm:table-cell text-xs">{d.numero_referencia || '—'}</td>
                                <td class="p-3 text-right font-bold text-hotel-gold">${formatNumber(d.monto)}</td>
                            </tr>
                        {:else}
                            <tr>
                                <td colspan="6" class="p-10 text-center text-hotel-text-tertiary uppercase tracking-widest text-xs">
                                    Sin transacciones en esta fecha
                                </td>
                            </tr>
                        {/each}
                    </tbody>
                </table>
            </div>
        </div>
    {/if}
</div>
