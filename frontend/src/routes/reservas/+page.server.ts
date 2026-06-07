import { redirect } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';

const API_BASE    = process.env.VITE_API_URL ?? 'http://localhost:8000/api';
const COOKIE_NAME = 'auth_token';

export const load: PageServerLoad = async ({ locals, cookies, url }) => {
    if (!locals.user) throw redirect(303, '/login');

    const token   = cookies.get(COOKIE_NAME);
    const headers = { Cookie: `${COOKIE_NAME}=${token}` };

    // Semana a mostrar (por defecto: lunes de la semana actual)
    const semanaParam = url.searchParams.get('semana');
    let semanaInicio: Date;
    if (semanaParam) {
        semanaInicio = new Date(semanaParam + 'T00:00:00');
    } else {
        semanaInicio = new Date();
        const dia = semanaInicio.getDay();
        semanaInicio.setDate(semanaInicio.getDate() - (dia === 0 ? 6 : dia - 1));
    }

    const semanaFin = new Date(semanaInicio);
    semanaFin.setDate(semanaFin.getDate() + 6);
    const fmtISO = (d: Date) => d.toISOString().split('T')[0];

    // Parámetros base para el calendario (rango de fechas)
    const params = new URLSearchParams();
    params.set('fecha_desde', fmtISO(semanaInicio));
    params.set('fecha_hasta',  fmtISO(semanaFin));

    // 🔹 FILTRO DE HISTORIAL: obtener de la URL qué mostrar (activas o finalizadas)
    const tipoVista = url.searchParams.get('tipo') ?? 'activas';
    let estadosFiltro: string[] = [];
    if (tipoVista === 'activas') {
        estadosFiltro = ['sin_pagar', 'confirmada', 'pagada', 'check_in'];
    } else {
        estadosFiltro = ['check_out', 'cancelada', 'no_show'];
    }
    if (estadosFiltro.length) {
        params.set('estados', estadosFiltro.join(','));
    }

    const safeJsonPaginated = async (r: PromiseSettledResult<Response>, fallback: unknown[]) => {
        if (r.status === 'rejected' || !r.value.ok) return fallback;
        try {
            const data = await r.value.json();
            if (data && typeof data === 'object' && Array.isArray(data.results)) {
                return data.results;
            }
            if (Array.isArray(data)) return data;
            return fallback;
        } catch {
            return fallback;
        }
    };

    const [reservasRes, habitacionesRes] = await Promise.allSettled([
        fetch(`${API_BASE}/reservaciones/?${params}`, { headers }),
        fetch(`${API_BASE}/habitaciones/`, { headers }),
    ]);

    return {
        user:          locals.user,
        reservas:      await safeJsonPaginated(reservasRes, []),
        habitaciones:  await safeJsonPaginated(habitacionesRes, []),
        semanaInicio:  fmtISO(semanaInicio),
        semanaFin:     fmtISO(semanaFin),
        tipoVista,
    };
};