import { redirect, type Handle } from '@sveltejs/kit';

const API_URL = process.env.VITE_API_URL ?? 'http://localhost:8000/api';
const COOKIE_NAME = 'auth_token';
const PUBLIC_ROUTES = ['/login', '/recuperar', '/'];

// Caché en memoria del servidor: token → { user, expiry }
// Evita validar contra Django en cada request
const userCache = new Map<string, { user: App.Locals['user']; expiry: number }>();
const CACHE_TTL = 5 * 60 * 1000; // 5 minutos

export const handle: Handle = async ({ event, resolve }) => {
    const token    = event.cookies.get(COOKIE_NAME);
    const pathname = event.url.pathname;

    const isProtected = pathname.startsWith('/dashboard') ||
                        pathname.startsWith('/habitaciones') ||
                        pathname.startsWith('/reservaciones');
    const isLogin = pathname === '/login';

    if (isProtected && !token) {
        throw redirect(303, '/login');
    }

    if (token) {
        // Verificar caché antes de llamar a Django
        const cached = userCache.get(token);
        if (cached && cached.expiry > Date.now()) {
            event.locals.user = cached.user;
        } else {
            // Solo llama a Django si el caché expiró o no existe
            try {
                const res = await fetch(`${API_URL}/auth/profile/`, {
                    headers: { Cookie: `${COOKIE_NAME}=${token}` },
                });

                if (res.ok) {
                    const data = await res.json();
                    const user = {
                        id: String(data.id),
                        username: data.username,
                        email: data.email,
                        role: data.role,
                        first_name: data.first_name,
                        last_name: data.last_name,
                    };
                    // Guardar en caché
                    userCache.set(token, { user, expiry: Date.now() + CACHE_TTL });
                    event.locals.user = user;
                } else {
                    userCache.delete(token);
                    event.locals.user = null;
                    event.cookies.delete(COOKIE_NAME, { path: '/' });
                    if (isProtected) throw redirect(303, '/login');
                }
            } catch (err) {
                if (err && typeof err === 'object' && 'status' in err) throw err;
                event.locals.user = null;
                if (isProtected) throw redirect(303, '/login');
            }
        }

        if (isLogin && event.locals.user) throw redirect(303, '/dashboard');
    } else {
        event.locals.user = null;
    }

    return resolve(event);
};