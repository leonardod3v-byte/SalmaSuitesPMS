import type { LayoutServerLoad } from './$types';

export const load: LayoutServerLoad = async ({ cookies, fetch }) => {
    const token = cookies.get('auth_token');

    if (!token) {
        return { user: null };
    }

    try {
        const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';
        const res = await fetch(`${API_URL}/auth/profile/`, {
            headers: {
                'Authorization': `Token ${token}`,
            },
        });

        if (res.ok) {
            const user = await res.json();
            return { user };
        }
    } catch {
    }

    return { user: null };
};
