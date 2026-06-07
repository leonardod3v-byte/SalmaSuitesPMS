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

    let habitacionesData = await safeJson(habitacionesRes, { results: [] });
    // Extraer array de resultados paginados
    let habitacionesArray = Array.isArray(habitacionesData) ? habitacionesData : (habitacionesData.results || []);

    // Mapear a la estructura que espera el componente
    const habitaciones = habitacionesArray.map((item: any) => ({
        id: item.id,
        numero: item.numero,
        piso: item.piso,
        estado: item.estado,
        tiene_minibar: item.tiene_minibar,
        // tipo puede ser objeto o ID; normalizamos
        tipo: typeof item.tipo === 'object' ? item.tipo.id : item.tipo,
        tipo_nombre: typeof item.tipo === 'object' ? item.tipo.nombre : (item.tipo_nombre || 'Estándar'),
        tipo_precio: item.tipo_precio,
        capacidad_maxima: item.capacidad_maxima 
    }));

    const tipos = await safeJson(tiposRes, []);

    return {
        user: locals.user,
        habitaciones,
        tipos
    };
};