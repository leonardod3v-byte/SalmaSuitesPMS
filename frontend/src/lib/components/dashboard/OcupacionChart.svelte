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

    onMount(() => {
        if (!data?.dias?.length) return;
        crearGrafico();

        return () => {
            if (chart) chart.destroy();
        };
    });

    function crearGrafico() {
        if (!canvas || !data) return;
        if (chart) chart.destroy();

        const labels = data.dias.map(d => d.dia.substring(0, 3).toUpperCase());
        const valores = data.dias.map(d => d.porcentaje);

        chart = new Chart(canvas, {
            type: 'bar',
            data: {
                labels,
                datasets: [{
                    label: 'Ocupación',
                    data: valores,
                    backgroundColor: 'rgba(179, 142, 93, 0.7)',
                    borderColor: '#b38e5d',
                    borderWidth: 1.5,
                    borderRadius: 6,
                    hoverBackgroundColor: '#d9c5a3',
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        backgroundColor: '#2d1b14',
                        titleColor: '#f2efe9',
                        bodyColor: '#f2efe9',
                        borderColor: '#b38e5d',
                        borderWidth: 1,
                        callbacks: {
                            label: (ctx) => `${ctx.parsed.y}% de ocupación`
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
                        },
                        grid: {
                            color: 'rgba(74, 53, 44, 0.3)',
                        }
                    },
                    x: {
                        ticks: {
                            color: '#827066',
                            font: { weight: 'bold', size: 10 }
                        },
                        grid: { display: false }
                    }
                }
            }
        });
    }

    $effect(() => {
        if (data?.dias?.length && canvas) {
            crearGrafico();
        }
    });
</script>

<section class="lg:col-span-2 bg-hotel-surface rounded-2xl p-6 border border-hotel-border shadow-hotel-sm flex flex-col h-[400px]">
    <div class="flex justify-between items-center mb-4 shrink-0">
        <h3 class="font-display text-xl text-hotel-text-primary italic">Ocupación Semanal</h3>
        {#if data}
            <span class="text-xs text-hotel-text-tertiary">Promedio: {data.promedio}%</span>
        {/if}
    </div>
    <div class="flex-1 min-h-0">
        <canvas bind:this={canvas}></canvas>
    </div>
</section>