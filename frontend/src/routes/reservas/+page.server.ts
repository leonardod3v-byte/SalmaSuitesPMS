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
        // Ajustar al lunes (0=dom, 1=lun, ...)
        semanaInicio.setDate(semanaInicio.getDate() - (dia === 0 ? 6 : dia - 1));
    }

    const semanaFin = new Date(semanaInicio);
    semanaFin.setDate(semanaFin.getDate() + 6);
    const fmtISO = (d: Date) => d.toISOString().split('T')[0];

    const params = new URLSearchParams();
    // Traer reservas que se solapen con la semana actual
    params.set('fecha_desde', fmtISO(semanaInicio));
    params.set('fecha_hasta',  fmtISO(semanaFin));

    const safeJson = async (r: PromiseSettledResult<Response>, fallback: unknown) => {
        if (r.status === 'rejected' || !r.value.ok) return fallback;
        try { return await r.value.json(); } catch { return fallback; }
    };

    const [reservasRes, habitacionesRes] = await Promise.allSettled([
        fetch(`${API_BASE}/reservaciones/?${params}`, { headers }),
        fetch(`${API_BASE}/habitaciones/`, { headers }),
    ]);

    return {
        user:          locals.user,
        reservas:      await safeJson(reservasRes, []),
        habitaciones:  await safeJson(habitacionesRes, []),
        semanaInicio:  fmtISO(semanaInicio),
        semanaFin:     fmtISO(semanaFin),
    };
};