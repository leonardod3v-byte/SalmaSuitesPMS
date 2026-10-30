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
        <WelcomeBanner stats={{ checkIns: kpis?.checkins_hoy ?? 0, checkOuts: proximosCheckouts?.total ?? 0 }} />

        <!-- KPIs clicables -->
        <div class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
            <a href="/habitaciones?estado=Ocupada" class="block">
                <KPICard title="Ocupación Real" value="{kpis?.ocupacion?.porcentaje ?? 0}%" subtitle="{kpis?.ocupacion?.ocupadas ?? 0} de {kpis?.ocupacion?.disponibles ?? 0} habs." iconName="hotel" color="gold" />
            </a>
            <a href="/reservaciones?estado=EnCurso" class="block">
                <KPICard title="Check-In Hoy" value={kpis?.checkins_hoy ?? 0} subtitle="{proximosCheckouts?.total ?? 0} check-outs pendientes" iconName="calendar" color="success" />
            </a>
            <a href="/reportes/cierre-caja" class="block">
                <KPICard title="Ingresos" value="${kpis?.flujo_caja?.total ?? '0.00'}" subtitle="E: ${kpis?.flujo_caja?.efectivo ?? '0'} | T: ${kpis?.flujo_caja?.tarjeta ?? '0'} | M: ${kpis?.flujo_caja?.pago_movil ?? '0'}" iconName="dinero" color="gold" />
            </a>
            <a href="/huespedes?categoria=VIP&solo_alojados=1" class="block">
                <KPICard title="Clientes VIP" value={kpis?.vip_alojados ?? 0} subtitle="{kpis?.productos_bajos ?? 0} productos bajos" iconName="corona" color="vip" />
            </a>
        </div>

        <!-- Secciones rápidas: checkouts y limpieza -->
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <a href="/reservaciones?checkout=hoy" class="flex items-center gap-4 bg-hotel-surface rounded-2xl p-5 border border-hotel-border hover:border-hotel-gold/50 transition-all shadow-hotel-sm group">
                <div class="flex h-12 w-12 items-center justify-center rounded-xl bg-hotel-gold/10 border border-hotel-gold/20 text-hotel-gold group-hover:bg-hotel-gold group-hover:text-hotel-bg transition-all">
                    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"/></svg>
                </div>
                <div>
                    <p class="text-sm font-bold text-hotel-text-primary">{proximosCheckouts?.total ?? 0}</p>
                    <p class="text-[10px] uppercase tracking-wider text-hotel-text-tertiary">Check‑outs pendientes hoy</p>
                </div>
            </a>
            <a href="/habitaciones?estado=Sucia" class="flex items-center gap-4 bg-hotel-surface rounded-2xl p-5 border border-hotel-border hover:border-hotel-gold/50 transition-all shadow-hotel-sm group">
                <div class="flex h-12 w-12 items-center justify-center rounded-xl bg-hotel-info/10 border border-hotel-info/20 text-hotel-info-light group-hover:bg-hotel-info group-hover:text-white transition-all">
                    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z"/></svg>
                </div>
                <div>
                    <p class="text-sm font-bold text-hotel-text-primary">{habitacionesSucias}</p>
                    <p class="text-[10px] uppercase tracking-wider text-hotel-text-tertiary">Habitaciones por limpiar</p>
                </div>
            </a>
        </div>

        <!-- Ocupación semanal + Actividades -->
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 items-start">
            <!-- Gráfico de Ocupación (ocupa 2 columnas en pantallas grandes) -->
            <div class="lg:col-span-2 h-100 min-w-0">
                <OcupacionChart data={ocupacionSemanal} />
            </div>

            <!-- Actividades Recientes (ocupa 1 columna y tiene su propio scroll) -->
            <div class="h-100 min-w-0">
                <ActividadesLog actividades={actividades} />
            </div>
        </div>

        <!-- Mapa de habitaciones -->
        <RoomMap habitaciones={habitaciones} />
    </div>
{/if}
