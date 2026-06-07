import { redirect } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';

const API_BASE   = process.env.VITE_API_URL ?? 'http://localhost:8000/api';
const COOKIE_NAME = 'auth_token';

export const load: PageServerLoad = async ({ locals, cookies, url }) => {
    if (!locals.user) throw redirect(303, '/login');

    const token   = cookies.get(COOKIE_NAME);
    const headers = { Cookie: `${COOKIE_NAME}=${token}` };

    const search = url.searchParams.get('search') ?? '';
    const vip    = url.searchParams.get('vip') ?? '';

    const params = new URLSearchParams();
    if (search) params.set('search', search);
    if (vip)    params.set('vip', vip);
    const qs = params.toString() ? `?${params}` : '';

    try {
        const res = await fetch(`${API_BASE}/huespedes/${qs}`, { headers });
        if (!res.ok) throw new Error();
        const data = await res.json();
        // Extraer el array de resultados (paginación)
        const huespedes = Array.isArray(data) ? data : (data.results || []);
        return { user: locals.user, huespedes, search, vip };
    } catch {
        return { user: locals.user, huespedes: [], search, vip };
    }
};