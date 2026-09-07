<script lang="ts">
    import { onMount } from 'svelte';
    import { Chart, registerables } from 'chart.js';
    import DatePicker from '$components/ui/DatePicker.svelte';
    import Select from '$components/ui/Select.svelte';
    import Button from '$components/ui/Button.svelte';
    import { fetchIngresos } from '$lib/services/reportes';
    import type { IngresoPeriodo } from '$lib/types/reporte';

    Chart.register(...registerables);

    let inicio = $state(new Date(new Date().getFullYear(), new Date().getMonth(), 1).toISOString().split('T')[0]);
    let fin = $state(new Date().toISOString().split('T')[0]);
    let metodo = $state('');
    let datos = $state<IngresoPeriodo[]>([]);
    let cargando = $state(false);
    // svelte-ignore non_reactive_update
    let canvas: HTMLCanvasElement;
    let chart: Chart | null = null;

    const metodos = [
        { value: '', label: 'Todos los métodos' },
        { value: 'Efectivo', label: 'Efectivo' },
        { value: 'Tarjeta', label: 'Tarjeta' },
        { value: 'PagoMovil', label: 'Pago Móvil' },
    ];

    async function cargar() {
        cargando = true;
        try {
            datos = await fetchIngresos(inicio, fin, metodo || undefined);
            crearGrafico();
        } catch { } finally {
            cargando = false;
        }
    }

    function crearGrafico() {
        if (!canvas || !datos.length) return;
        if (chart) chart.destroy();

        const labels = datos.map(d => {
            const fecha = new Date(d.fecha + 'T12:00:00');
            return fecha.toLocaleDateString('es-VE', { day: '2-digit', month: 'short' });
        });

        chart = new Chart(canvas, {
            type: 'bar',
            data: {
                labels,
                datasets: [
                    {
                        label: 'Efectivo',
                        data: datos.map(d => parseFloat(d.efectivo)),
                        backgroundColor: 'rgba(45, 106, 79, 0.6)',
                        borderColor: '#2d6a4f',
                        borderWidth: 1,
                        borderRadius: 4,
                    },
                    {
                        label: 'Tarjeta',
                        data: datos.map(d => parseFloat(d.tarjeta)),
                        backgroundColor: 'rgba(179, 142, 93, 0.6)',
                        borderColor: '#b38e5d',
                        borderWidth: 1,
                        borderRadius: 4,
                    },
                    {
                        label: 'Pago Móvil',
                        data: datos.map(d => parseFloat(d.pago_movil)),
                        backgroundColor: 'rgba(30, 58, 95, 0.6)',
                        borderColor: '#1e3a5f',
                        borderWidth: 1,
                        borderRadius: 4,
                    },
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        labels: { color: '#bdb2a7', font: { size: 10 }, usePointStyle: true }
                    },
                    tooltip: {
                        backgroundColor: '#2d1b14',
                        titleColor: '#f2efe9',
                        bodyColor: '#f2efe9',
                        borderColor: '#b38e5d',
                        borderWidth: 1,
                        callbacks: {
                            label: (ctx) => `${ctx.dataset.label}: $${ctx.parsed.y.toFixed(2)}`
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: { color: '#827066', callback: (v) => `$${v}` },
                        grid: { color: 'rgba(74, 53, 44, 0.3)' }
                    },
                    x: {
                        ticks: { color: '#827066', font: { size: 9 } },
                        grid: { display: false }
                    }
                }
            }
        });
    }

    onMount(() => cargar());
</script>

<div class="space-y-6">
    <!-- Filtros -->
    <div class="flex flex-wrap items-center gap-3 p-3 rounded-2xl bg-hotel-surface/40 border border-hotel-border">
        <div class="flex items-center gap-2">
            <DatePicker bind:value={inicio} />
            <span class="text-hotel-text-tertiary text-xs">—</span>
            <DatePicker bind:value={fin} />
        </div>
        <div class="w-px h-8 bg-hotel-border hidden sm:block"></div>
        <div class="w-45">
            <Select options={metodos} bind:value={metodo} />
        </div>
        <Button variant="gold" size="md" onclick={cargar} loading={cargando}>
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/></svg>
        </Button>

        <div class="flex gap-2">
            {#each [
                { label: 'Hoy', inicio: new Date().toISOString().split('T')[0], fin: new Date().toISOString().split('T')[0] },
                { label: '7 días', inicio: new Date(Date.now() - 6*86400000).toISOString().split('T')[0], fin: new Date().toISOString().split('T')[0] },
                { label: '30 días', inicio: new Date(Date.now() - 29*86400000).toISOString().split('T')[0], fin: new Date().toISOString().split('T')[0] },
                { label: 'Este mes', inicio: new Date(new Date().getFullYear(), new Date().getMonth(), 1).toISOString().split('T')[0], fin: new Date().toISOString().split('T')[0] },
            ] as rango}
                <button
                    onclick={() => { inicio = rango.inicio; fin = rango.fin; cargar(); }}
                    class="px-3 py-1.5 rounded-lg text-[10px] font-bold uppercase tracking-wider border border-hotel-border text-hotel-text-tertiary hover:border-hotel-gold/50 hover:text-hotel-gold transition-all"
                >
                    {rango.label}
                </button>
            {/each}
        </div>
    </div>

    <!-- Gráfico -->
    <div class="bg-hotel-surface rounded-2xl border border-hotel-border shadow-hotel-sm p-6">
        <h3 class="font-display text-xl text-hotel-text-primary italic mb-6">Ingresos por Período</h3>
        {#if datos.length > 0}
            <div class="h-80">
                <canvas bind:this={canvas}></canvas>
            </div>
        {:else}
            <p class="text-center text-hotel-text-tertiary py-12 uppercase tracking-widest text-xs">Sin datos para este período</p>
        {/if}
    </div>
</div>