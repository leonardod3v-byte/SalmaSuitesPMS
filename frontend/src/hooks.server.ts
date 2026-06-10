import { redirect, type Handle } from '@sveltejs/kit';

const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000/api';
const COOKIE_NAME = 'auth_token';
const PUBLIC_ROUTES = ['/login', '/recuperar', '/'];
const ADMIN_ROUTES = ['/configuracion', '/usuarios']; // rutas exclusivas de admin

export const handle: Handle = async ({ event, resolve }) => {
    const token = event.cookies.get(COOKIE_NAME);
    const pathname = event.url.pathname;
    const isLogin = pathname === '/login';

    // Si no hay token y la ruta no es pública, redirigir al login
    if (!token && !PUBLIC_ROUTES.includes(pathname)) {
        throw redirect(303, '/login');
    }

    if (token) {
        // Verificar sesión contra la API
        try {
            const res = await fetch(`${API_URL}/auth/profile/`, {
                headers: { Cookie: `${COOKIE_NAME}=${token}` },
            });

            if (res.ok) {
                const data = await res.json();
                event.locals.user = {
                    id: data.id,
                    username: data.username,
                    email: data.email,
                    role: data.role,
                    nombre_completo: data.nombre_completo,
                };
            } else {
                // Token inválido o expirado
                event.cookies.delete(COOKIE_NAME, { path: '/' });
                event.locals.user = null;
                if (!PUBLIC_ROUTES.includes(pathname)) throw redirect(303, '/login');
            }
        } catch (err: any) {
            if (err?.status === 303) throw err;
            event.locals.user = null;
            if (!PUBLIC_ROUTES.includes(pathname)) throw redirect(303, '/login');
        }

        // Si ya logueado y está en /login, redirigir a dashboard
        if (isLogin && event.locals.user) {
            throw redirect(303, '/dashboard');
        }

        // Proteger rutas exclusivas de administrador
        if (event.locals.user?.role !== 'admin') {
            if (ADMIN_ROUTES.some(route => pathname.startsWith(route))) {
                throw redirect(303, '/dashboard');
            }
        }
    } else {
        event.locals.user = null;
    }

    return resolve(event);
};