<script lang="ts">
    import { onMount, onDestroy } from 'svelte';
    import DatePicker from '$components/ui/DatePicker.svelte';
    import Select from '$components/ui/Select.svelte';
    import Button from '$components/ui/Button.svelte';
    import Icon from '$components/ui/Icons.svelte';
    import { fetchIngresos } from '$lib/services/reportes';
    import type { IngresoPeriodo } from '$lib/types/reporte';

    let inicio = $state(new Date(new Date().getFullYear(), new Date().getMonth(), 1).toISOString().split('T')[0]);
    let fin = $state(new Date().toISOString().split('T')[0]);
    let metodo = $state('');
    let datos = $state<IngresoPeriodo[]>([]);
    let cargando = $state(false);
    let canvas: HTMLCanvasElement;
    let chart: any = null;

    const metodos = [
        { value: '', label: 'Todos los métodos' },
        { value: 'Efectivo', label: 'Efectivo' },
        { value: 'Tarjeta', label: 'Tarjeta' },
        { value: 'PagoMovil', label: 'Pago Móvil' },
    ];

    let totalPeriodo = $derived(datos.reduce((sum, d) => sum + parseFloat(d.total), 0));
    let totalEfectivo = $derived(datos.reduce((sum, d) => sum + parseFloat(d.efectivo), 0));
    let totalTarjeta = $derived(datos.reduce((sum, d) => sum + parseFloat(d.tarjeta), 0));
    let totalPagoMovil = $derived(datos.reduce((sum, d) => sum + parseFloat(d.pago_movil), 0));

    async function cargar() {
        cargando = true;
        try {
            datos = await fetchIngresos(inicio, fin, metodo || undefined);
            // Pequeño delay para asegurar que el canvas esté montado antes de dibujar
            setTimeout(() => crearGrafico(), 30);
        } catch { } finally {
            cargando = false;
        }
    }

    async function crearGrafico() {
        if (!canvas || datos.length === 0) return;

        // Importación dinámica: solo carga Chart.js cuando se necesita
        const { Chart, registerables } = await import('chart.js');
        Chart.register(...registerables);

        if (chart) {
            chart.destroy();
            chart = null;
        }

        const labels = datos.map(d => {
            const fecha = new Date(d.fecha + 'T12:00:00');
            return fecha.toLocaleDateString('es-VE', { day: '2-digit', month: 'short' });
        });

        // Configurar devicePixelRatio bajo para mejor rendimiento
        const dpr = Math.min(window.devicePixelRatio, 1.5);

        chart = new Chart(canvas, {
            type: 'bar',
            data: {
                labels,
                datasets: [
                    {
                        label: 'Efectivo',
                        data: datos.map(d => parseFloat(d.efectivo)),
                        backgroundColor: 'rgba(45, 106, 79, 0.8)',
                        borderColor: '#2d6a4f',
                        borderWidth: 1,
                        borderRadius: 4,
                    },
                    {
                        label: 'Tarjeta',
                        data: datos.map(d => parseFloat(d.tarjeta)),
                        backgroundColor: 'rgba(179, 142, 93, 0.8)',
                        borderColor: '#b38e5d',
                        borderWidth: 1,
                        borderRadius: 4,
                    },
                    {
                        label: 'Pago Móvil',
                        data: datos.map(d => parseFloat(d.pago_movil)),
                        backgroundColor: 'rgba(30, 58, 95, 0.8)',
                        borderColor: '#1e3a5f',
                        borderWidth: 1,
                        borderRadius: 4,
                    },
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                devicePixelRatio: dpr,
                animation: {
                    duration: 400, // Animación más rápida (antes era por defecto 1000ms)
                },
                plugins: {
                    legend: {
                        labels: { color: '#bdb2a7', font: { size: 11 }, usePointStyle: true, padding: 20 }
                    },
                    tooltip: {
                        backgroundColor: '#2d1b14',
                        titleColor: '#f2efe9',
                        bodyColor: '#f2efe9',
                        borderColor: '#b38e5d',
                        borderWidth: 1,
                        padding: 10,
                        callbacks: {
                            label: (ctx) => ` ${ctx.dataset.label}: $${ctx.parsed.y.toFixed(2)}`
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: { color: '#827066', callback: (v) => `$${v}`, font: { size: 10 } },
                        grid: { color: 'rgba(74, 53, 44, 0.2)' }
                    },
                    x: {
                        ticks: { color: '#827066', font: { size: 10 } },
                        grid: { display: false }
                    }
                }
            }
        });
    }

    function aplicarRango(inicioR: string, finR: string) {
        inicio = inicioR;
        fin = finR;
        cargar();
    }

    onMount(() => cargar());

    onDestroy(() => {
        if (chart) {
            chart.destroy();
        }
    });
</script>

<div class="space-y-6">
    <!-- Barra de Filtros -->
    <div class="flex flex-col xl:flex-row gap-4 p-4 rounded-2xl bg-hotel-surface/40 border border-hotel-border">
        <div class="flex flex-wrap items-end gap-3 flex-1">
            <div class="w-full sm:w-auto">
                <DatePicker label="Desde" bind:value={inicio} />
            </div>
            <div class="w-full sm:w-auto">
                <DatePicker label="Hasta" bind:value={fin} />
            </div>
            <div class="w-full sm:w-48">
                <Select label="Método de Pago" options={metodos} bind:value={metodo} />
            </div>
            <Button variant="gold" size="md" onclick={cargar} loading={cargando}>
                <Icon name="search" class="w-4 h-4" />
            </Button>
        </div>

        <div class="flex flex-wrap items-center gap-2 border-t xl:border-t-0 xl:border-l border-hotel-border/50 pt-4 xl:pt-0 xl:pl-4">
            <span class="text-[9px] uppercase tracking-wider text-hotel-text-tertiary font-bold w-full xl:w-auto mb-1 xl:mb-0">Rangos rápidos:</span>
            <button
                onclick={() => aplicarRango(new Date().toISOString().split('T')[0], new Date().toISOString().split('T')[0])}
                class="px-3 py-1.5 rounded-lg text-[10px] font-bold uppercase tracking-wider border border-hotel-border text-hotel-text-tertiary hover:border-hotel-gold/50 hover:text-hotel-gold transition-all"
            >
                Hoy
            </button>
            <button
                onclick={() => aplicarRango(new Date(Date.now() - 6*86400000).toISOString().split('T')[0], new Date().toISOString().split('T')[0])}
                class="px-3 py-1.5 rounded-lg text-[10px] font-bold uppercase tracking-wider border border-hotel-border text-hotel-text-tertiary hover:border-hotel-gold/50 hover:text-hotel-gold transition-all"
            >
                7 días
            </button>
            <button
                onclick={() => aplicarRango(new Date(Date.now() - 29*86400000).toISOString().split('T')[0], new Date().toISOString().split('T')[0])}
                class="px-3 py-1.5 rounded-lg text-[10px] font-bold uppercase tracking-wider border border-hotel-border text-hotel-text-tertiary hover:border-hotel-gold/50 hover:text-hotel-gold transition-all"
            >
                30 días
            </button>
            <button
                onclick={() => aplicarRango(new Date(new Date().getFullYear(), new Date().getMonth(), 1).toISOString().split('T')[0], new Date().toISOString().split('T')[0])}
                class="px-3 py-1.5 rounded-lg text-[10px] font-bold uppercase tracking-wider border border-hotel-border text-hotel-text-tertiary hover:border-hotel-gold/50 hover:text-hotel-gold transition-all"
            >
                Este mes
            </button>
        </div>
    </div>

    <!-- Tarjetas de Resumen -->
    {#if datos.length > 0}
        <div class="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <div class="p-4 rounded-2xl bg-hotel-surface border border-hotel-border shadow-sm text-center">
                <p class="text-[10px] uppercase tracking-wider text-hotel-text-tertiary mb-1">Total Período</p>
                <p class="text-xl font-bold text-hotel-gold">${totalPeriodo.toFixed(2)}</p>
            </div>
            <div class="p-4 rounded-2xl bg-hotel-surface border border-hotel-border shadow-sm text-center">
                <p class="text-[10px] uppercase tracking-wider text-hotel-text-tertiary mb-1">Efectivo</p>
                <p class="text-xl font-bold text-hotel-text-primary">${totalEfectivo.toFixed(2)}</p>
            </div>
            <div class="p-4 rounded-2xl bg-hotel-surface border border-hotel-border shadow-sm text-center">
                <p class="text-[10px] uppercase tracking-wider text-hotel-text-tertiary mb-1">Tarjeta</p>
                <p class="text-xl font-bold text-hotel-text-primary">${totalTarjeta.toFixed(2)}</p>
            </div>
            <div class="p-4 rounded-2xl bg-hotel-surface border border-hotel-border shadow-sm text-center">
                <p class="text-[10px] uppercase tracking-wider text-hotel-text-tertiary mb-1">Pago Móvil</p>
                <p class="text-xl font-bold text-hotel-text-primary">${totalPagoMovil.toFixed(2)}</p>
            </div>
        </div>
    {/if}

    <!-- Gráfico -->
    <div class="bg-hotel-surface rounded-2xl border border-hotel-border shadow-hotel-sm p-6">
        <h3 class="font-display text-xl text-hotel-text-primary italic mb-6 flex items-center gap-2">
            <Icon name="grafico" class="w-5 h-5 text-hotel-gold" />
            Ingresos por Período
        </h3>
        {#if datos.length > 0}
            <div class="h-96">
                <canvas bind:this={canvas}></canvas>
            </div>
        {:else if cargando}
            <div class="h-96 flex items-center justify-center">
                <span class="text-hotel-text-tertiary uppercase tracking-widest text-xs animate-pulse">Cargando datos...</span>
            </div>
        {:else}
            <div class="h-96 flex items-center justify-center">
                <p class="text-hotel-text-tertiary uppercase tracking-widest text-xs">Sin datos para este período</p>
            </div>
        {/if}
    </div>
</div>
