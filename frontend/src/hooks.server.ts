import { redirect, type Handle } from '@sveltejs/kit';

const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000/api';
const COOKIE_NAME = 'auth_token';
const PUBLIC_ROUTES = ['/login', '/recuperar', '/'];
const ADMIN_ROUTES = ['/configuracion', '/usuarios'];

export const handle: Handle = async ({ event, resolve }) => {
    const token = event.cookies.get(COOKIE_NAME);
    const pathname = event.url.pathname;
    const isLogin = pathname === '/login';
    const isBuild = event.url.hostname === 'localhost' && !event.request.headers.get('user-agent');

    // Durante el build de Vercel no redirigir
    if (isBuild) {
        return resolve(event);
    }

    if (!token && !PUBLIC_ROUTES.includes(pathname)) {
        throw redirect(303, '/login');
    }

    if (token) {
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
                event.cookies.delete(COOKIE_NAME, { path: '/' });
                event.locals.user = null;
                if (!PUBLIC_ROUTES.includes(pathname)) throw redirect(303, '/login');
            }
        } catch (err: any) {
            if (err?.status === 303) throw err;
            event.locals.user = null;
            if (!PUBLIC_ROUTES.includes(pathname)) throw redirect(303, '/login');
        }

        if (isLogin && event.locals.user) {
            throw redirect(303, '/dashboard');
        }

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