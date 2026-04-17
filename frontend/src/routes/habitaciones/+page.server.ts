import { redirect } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';

const API_BASE = process.env.VITE_API_URL ?? 'http://localhost:8000/api';
const COOKIE_NAME = 'auth_token';

export const load: PageServerLoad = async ({ locals, cookies }) => {
    if (!locals.user) throw redirect(303, '/login');

    const token = cookies.get(COOKIE_NAME);
    const headers = { Cookie: `${COOKIE_NAME}=${token}` };

    const [habitacionesRes, tiposRes] = await Promise.allSettled([
        fetch(`${API_BASE}/habitaciones/`, { headers }),
        fetch(`${API_BASE}/habitaciones/tipos/`, { headers }),
    ]);

    const safeJson = async (r: PromiseSettledResult<Response>, fallback: unknown) => {
        if (r.status === 'rejected' || !r.value.ok) return fallback;
        try { return await r.value.json(); } catch { return fallback; }
    };

    return {
        user: locals.user,
        habitaciones: await safeJson(habitacionesRes, []),
        tipos:        await safeJson(tiposRes, []),
    };
};