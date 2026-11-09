<script lang="ts">
    import { onMount } from 'svelte';
    import { Chart, registerables } from 'chart.js';

    Chart.register(...registerables);

    interface Props {
        data: {
            semana: string;
            dias: { dia: string; fecha: string; ocupadas: number; disponibles: number; porcentaje: number }[];
            promedio: number;
        } | null;
    }

    let { data }: Props = $props();
    let canvas: HTMLCanvasElement;
    let chart: Chart | null = null;

    const hoyISO = new Date().toISOString().split('T')[0];

    onMount(() => {
        if (!data?.dias?.length) return;
        crearGrafico();
        return () => { if (chart) chart.destroy(); };
    });

    function crearGrafico() {
        if (!canvas || !data) return;
        if (chart) chart.destroy();

        const labels = data.dias.map(d => d.dia.substring(0, 3));
        const valores = data.dias.map(d => d.porcentaje);
        const indiceHoy = data.dias.findIndex(d => d.fecha === hoyISO);

        chart = new Chart(canvas, {
            type: 'bar',
            data: {
                labels,
                datasets: [{
                    label: 'Ocupación',
                    data: valores,
                    backgroundColor: data.dias.map((_, i) =>
                        i === indiceHoy
                            ? 'rgba(179, 142, 93, 0.95)'
                            : 'rgba(179, 142, 93, 0.25)'
                    ),
                    hoverBackgroundColor: 'rgba(179, 142, 93, 0.75)',
                    borderRadius: 6,
                    borderSkipped: false,
                    barPercentage: 0.55,
                    categoryPercentage: 0.8,
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        backgroundColor: '#1a120d',
                        titleColor: '#d4af37',
                        titleFont: { size: 11, weight: 'bold' },
                        bodyColor: '#f2efe9',
                        bodyFont: { size: 11 },
                        borderColor: '#4a352c',
                        borderWidth: 1,
                        padding: 10,
                        cornerRadius: 6,
                        displayColors: false,
                        callbacks: {
                            title: (ctx) => {
                                const dia = data.dias[ctx[0].dataIndex];
                                return dia.dia.toUpperCase();
                            },
                            label: (ctx) => {
                                const dia = data.dias[ctx.dataIndex];
                                return `${dia.porcentaje}% · ${dia.ocupadas}/${dia.disponibles} habs.`;
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        ticks: {
                            callback: (v) => `${v}%`,
                            color: '#827066',
                            font: { size: 10 },
                            stepSize: 25,
                            padding: 8,
                        },
                        grid: {
                            color: 'rgba(74, 53, 44, 0.1)',
                            drawTicks: false,
                        },
                        border: { display: false },
                    },
                    x: {
                        ticks: {
                            color: '#827066',
                            font: { size: 10, weight: '600' },
                            padding: 6,
                        },
                        grid: { display: false },
                        border: { display: false },
                    }
                },
                animation: { duration: 500, easing: 'easeOutQuart' },
                layout: { padding: { top: 8, bottom: 4 } }
            }
        });
    }

    $effect(() => {
        if (data?.dias?.length && canvas) crearGrafico();
    });
</script>

<section class="lg:col-span-2 bg-hotel-surface rounded-2xl p-6 border border-hotel-border h-100 flex flex-col">
    <div class="flex justify-between items-start mb-6 shrink-0">
        <div>
            <h3 class="font-display text-xl text-hotel-text-primary italic flex items-center gap-2">Ocupación Semanal</h3>
            <p class="text-[10px] uppercase tracking-[0.2em] text-hotel-text-tertiary mt-0.5">
                {new Date(data.semana + 'T12:00:00').toLocaleDateString('es-VE', { day: '2-digit', month: 'short' })} —
                {new Date(new Date(data.semana + 'T12:00:00').getTime() + 6 * 86400000).toLocaleDateString('es-VE', { day: '2-digit', month: 'short' })}
            </p>
        </div>
        {#if data}
            <div class="flex items-baseline gap-1.5 px-2.5 py-1 rounded-md bg-hotel-gold/5 border border-hotel-gold/20">
                <span class="text-[9px] uppercase tracking-widest text-hotel-gold/70 font-bold">Prom.</span>
                <span class="font-display text-base font-bold text-hotel-gold tabular-nums">{data.promedio}%</span>
            </div>
        {/if}
    </div>
    <div class="flex-1 min-h-0">
        {#if data?.dias?.length}
            <canvas bind:this={canvas}></canvas>
        {:else}
            <div class="flex items-center justify-center h-full text-hotel-text-tertiary text-xs">Sin datos disponibles</div>
        {/if}
    </div>
</section>
