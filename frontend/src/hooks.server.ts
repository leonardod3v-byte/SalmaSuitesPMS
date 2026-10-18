import { redirect, type Handle } from '@sveltejs/kit';

const COOKIE_NAME = 'auth_token';
const PUBLIC_ROUTES = ['/login', '/recuperar', '/'];
const ADMIN_ROUTES = ['/configuracion', '/usuarios'];

export const handle: Handle = async ({ event, resolve }) => {
    const token = event.cookies.get(COOKIE_NAME);
    const pathname = event.url.pathname;
    const isLogin = pathname === '/login';

    // Si no hay token y la ruta no es pública, redirigir al login
    if (!token && !PUBLIC_ROUTES.includes(pathname)) {
        throw redirect(303, '/login');
    }

    // Si hay token y está en login, redirigir al dashboard
    if (token && isLogin) {
        throw redirect(303, '/dashboard');
    }

    // No verificamos token aquí para evitar bloqueos por latencia.
    // La verificación real se hace en el cliente con apiFetch.
    event.locals.user = null;

    const response = await resolve(event);
    // Evitar que el navegador cachee páginas protegidas (Bug 3)
    response.headers.set('Cache-Control', 'no-store, must-revalidate');
    return response;
};