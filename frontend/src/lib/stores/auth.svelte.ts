import { apiFetch } from '$lib/services/api';
import { goto, invalidateAll } from '$app/navigation';

export interface User {
    id: number;
    username: string;
    email: string;
    role: 'admin' | 'recepcionista';
    nombre_completo: string;
}

let user = $state<User | null>(null);
let loading = $state<boolean>(true);

export const auth = {
    init(serverUser: User | null) {
        user = serverUser;
        loading = false;
    },

    async hydrate(): Promise<void> {
        if (user) return;

        if (typeof window !== 'undefined') {
            const token = localStorage.getItem('auth_token');
            if (token) {
                try {
                    const profile = await apiFetch<User>('/auth/profile/');
                    user = profile;
                } catch {
                    localStorage.removeItem('auth_token');
                }
            }
        }
    },

    async login(username: string, password: string): Promise<User> {
        loading = true;
        try {
            const data = await apiFetch<{ token: string; user: User }>('/auth/login/', {
                method: 'POST',
                body: JSON.stringify({ username, password }),
            } as any);

            user = data.user;
            if (typeof window !== 'undefined') {
                localStorage.setItem('auth_token', data.token);
            }
            return data.user;
        } finally {
            loading = false;
        }
    },

    async logout() {
        try {
            await apiFetch('/auth/logout/', { method: 'POST' });
        } catch {
        }

        user = null;

        if (typeof window !== 'undefined') {
            localStorage.removeItem('auth_token');
        }

        await invalidateAll();
        await goto('/login', { replaceState: true });
    },

    get user() { return user; },
    get loading() { return loading; },
    get isAuthenticated() { return !!user; },
    get isAdmin() { return user?.role === 'admin'; },
};
