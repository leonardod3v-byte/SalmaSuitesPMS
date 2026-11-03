<script lang="ts">
    import { onMount, onDestroy } from 'svelte';
    import { goto } from '$app/navigation';
    import { apiFetch } from '$lib/services/api';
    import WelcomeBanner from '$components/dashboard/WelcomeBanner.svelte';
    import KPICard from '$components/dashboard/KPICard.svelte';
    import OcupacionChart from '$components/dashboard/OcupacionChart.svelte';
    import ActividadesLog from '$components/dashboard/ActividadesLog.svelte';
    import RoomMap from '$components/dashboard/RoomMap.svelte';
    import Loading from '$components/ui/Loading.svelte';
    import PageHeader from '$components/ui/PageHeader.svelte';
    import Button from '$components/ui/Button.svelte';
    import Icon from '$components/ui/Icons.svelte';
    import { auth } from '$stores/auth.svelte';

    let kpis = $state<any>(null);
    let ocupacionSemanal = $state<any>(null);
    let actividades = $state<any[]>([]);
    let habitaciones = $state<any[]>([]);
    let proximosCheckouts = $state<any>(null);
    let habitacionesSucias = $state<number>(0);
    let cargando = $state(true);
    let error = $state('');
    let pollingInterval: ReturnType<typeof setInterval>;

    async function cargarDatos() {
        try {
            const [k, o, a, h, p] = await Promise.all([
                apiFetch<any>('/dashboard/kpis/'),
                apiFetch<any>('/dashboard/ocupacion-semanal/'),
                apiFetch<any[]>('/bitacora/actividades/?limit=20'),
                apiFetch<any[]>('/habitaciones/'),
                apiFetch<any>('/dashboard/proximos-checkouts/'),
            ]);
            kpis = k;
            ocupacionSemanal = o;
            actividades = a;
            habitaciones = h;
            proximosCheckouts = p;
            habitacionesSucias = h.filter((hab: any) => hab.estado === 'Sucia').length;
        } catch (e: any) {
            error = e.message || 'Error al cargar el panel';
        } finally {
            cargando = false;
        }
    }

    onMount(() => {
        cargarDatos();
        pollingInterval = setInterval(async () => {
            try {
                const a = await apiFetch<any[]>('/bitacora/actividades/?limit=20');
                actividades = a;
            } catch { }
        }, 60_000);
    });

    onDestroy(() => {
        if (pollingInterval) clearInterval(pollingInterval);
    });
</script>

<svelte:head>
    <title>Panel de Control | SalmaSuitesPMS</title>
</svelte:head>

{#if cargando}
    <Loading type="dashboard" message="Cargando panel de control..." skeletonCount={4} />
{:else if error}
    <div class="flex items-center justify-center h-[60vh]">
        <div class="text-center p-8 bg-hotel-error/5 border border-hotel-error/20 rounded-2xl">
            <p class="text-hotel-error-light font-bold uppercase tracking-widest text-xs mb-4">{error}</p>
            <Button variant="gold" size="sm" onclick={() => window.location.reload()}>Reintentar</Button>
        </div>
    </div>
{:else}
    <div class="space-y-8">
        <!-- HERO: Bienvenida + Fecha -->
        <WelcomeBanner stats={{ checkIns: kpis?.checkins_hoy ?? 0, checkOuts: proximosCheckouts?.total ?? 0 }} />

        <!-- SECCIÓN 1: KPIs Principales -->
        <section>
            <div class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
                <a href="/habitaciones?estado=Ocupada" class="block">
                    <KPICard
                        title="Ocupación Real"
                        value="{kpis?.ocupacion?.porcentaje ?? 0}%"
                        subtitle="{kpis?.ocupacion?.ocupadas ?? 0} de {kpis?.ocupacion?.disponibles ?? 0} habs."
                        iconName="hotel"
                        color="gold"
                    />
                </a>
                <a href="/reservaciones?estado=EnCurso" class="block">
                    <KPICard
                        title="Check-In Hoy"
                        value={kpis?.checkins_hoy ?? 0}
                        subtitle="{proximosCheckouts?.total ?? 0} check-outs pendientes"
                        iconName="calendar"
                        color="success"
                    />
                </a>
                <a href="/reportes/cierre-caja" class="block">
                    <KPICard
                        title="Ingresos Hoy"
                        value="${kpis?.flujo_caja?.total ?? '0.00'}"
                        subtitle="E: ${kpis?.flujo_caja?.efectivo ?? '0'} · T: ${kpis?.flujo_caja?.tarjeta ?? '0'} · M: ${kpis?.flujo_caja?.pago_movil ?? '0'}"
                        iconName="dinero"
                        color="gold"
                    />
                </a>
                <a href="/huespedes?categoria=VIP&solo_alojados=1" class="block">
                    <KPICard
                        title="Clientes VIP"
                        value={kpis?.vip_alojados ?? 0}
                        subtitle="{kpis?.productos_bajos ?? 0} productos bajos"
                        iconName="corona"
                        color="vip"
                    />
                </a>
            </div>
        </section>

        <!-- SECCIÓN 3: Análisis (Gráfico + Actividad) -->
        <section>
            <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 items-start">
                <div class="lg:col-span-2 h-100 min-w-0">
                    <OcupacionChart data={ocupacionSemanal} />
                </div>
                <div class="h-100 min-w-0">
                    <ActividadesLog actividades={actividades} />
                </div>
            </div>
        </section>

        <!-- SECCIÓN 4: Mapa de Habitaciones -->
        <section>
            <RoomMap habitaciones={habitaciones} />
        </section>
    </div>
{/if}
