import { redirect, type Handle } from '@sveltejs/kit';

export const handle: Handle = async ({ event, resolve }) => {
    const token = event.cookies.get('token');
    const isDashboard = event.url.pathname.startsWith('/dashboard');
    const isLogin = event.url.pathname === '/login';

    if (isDashboard && !token) {
        throw redirect(303, '/login');
    }

    if (isLogin && token) {
        throw redirect(303, '/dashboard');
    }

    return await resolve(event);
};