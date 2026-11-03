import { redirect } from '@sveltejs/kit';
import type { LayoutServerLoad } from './$types';

const PUBLIC_ROUTES = ['/login', '/recuperar'];

export const load: LayoutServerLoad = async ({ cookies, url, fetch }) => {
    const token = cookies.get('auth_token');
    const isPublicRoute = PUBLIC_ROUTES.includes(url.pathname);

    if (!token && !isPublicRoute) {
        throw redirect(303, `/login?redirectTo=${encodeURIComponent(url.pathname)}`);
    }

    if (token) {
        try {
            const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';
            const res = await fetch(`${API_URL}/auth/profile/`, {
                headers: {
                    'Authorization': `Token ${token}`,
                    'Cookie': `auth_token=${token}`,
                },
            });

            if (res.ok) {
                const user = await res.json();

                if (isPublicRoute && url.pathname === '/login') {
                    throw redirect(303, '/dashboard');
                }

                return { user };
            } else {
                cookies.delete('auth_token', { path: '/' });
                if (!isPublicRoute) {
                    throw redirect(303, '/login');
                }
            }
        } catch (e: any) {
            if (e?.status === 303 || e?.status === 302) throw e;

            cookies.delete('auth_token', { path: '/' });
            if (!isPublicRoute) {
                throw redirect(303, '/login');
            }
        }
    }

    return { user: null };
};
