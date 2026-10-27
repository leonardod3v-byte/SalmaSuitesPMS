import { apiFetch } from '$lib/services/api';
import { goto } from '$app/navigation';
import { invalidateAll } from '$app/navigation';

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
            // Ignorar errores de red al cerrar sesión
        }
        user = null;
        if (typeof window !== 'undefined') {
            localStorage.removeItem('auth_token');
            window.location.replace('/login');
        }
    },

    get user() { return user; },
    get loading() { return loading; },
    get isAuthenticated() { return !!user; },
    get isAdmin() { return user?.role === 'admin'; },
};
