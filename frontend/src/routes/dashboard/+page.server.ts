import { redirect } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';

// Usar env variable para la URL base del backend
const API_BASE = process.env.VITE_API_URL ?? 'http://localhost:8000/api';
const COOKIE_NAME = 'auth_token';

export const load: PageServerLoad = async ({ locals, cookies }) => {
    if (!locals.user) {
        throw redirect(303, '/login');
    }

    const token = cookies.get(COOKIE_NAME);
    const headers = { Cookie: `${COOKIE_NAME}=${token}` };

    // Pre-cargar los 4 endpoints del dashboard en paralelo
    const [statsRes, habitacionesRes, actividadesRes, ocupacionRes] = await Promise.allSettled([
        fetch(`${API_BASE}/dashboard/stats/`, { headers }),
        fetch(`${API_BASE}/dashboard/habitaciones-grid/`, { headers }),
        fetch(`${API_BASE}/dashboard/actividades/`, { headers }),
        fetch(`${API_BASE}/dashboard/ocupacion-semanal/`, { headers }),
    ]);

    const safeJson = async (result: PromiseSettledResult<Response>, fallback: unknown) => {
        if (result.status === 'rejected') return fallback;
        if (!result.value.ok) return fallback;
        try { return await result.value.json(); } catch { return fallback; }
    };

    return {
        user: locals.user,
        stats:            await safeJson(statsRes, null),
        habitaciones:     await safeJson(habitacionesRes, []),
        actividades:      await safeJson(actividadesRes, []),
        ocupacionSemanal: await safeJson(ocupacionRes, { valores: [], dias: [] }),
    };
};