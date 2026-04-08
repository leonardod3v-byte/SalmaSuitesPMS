import { writable } from 'svelte/store';
import { browser } from '$app/environment';

// ── Tipado Estricto ────────────────────────────────────────────────────────
export interface User {
    id: number;
    username: string;
    email: string;
    role: 'admin' | 'recepcion';
    first_name?: string;
    last_name?: string;
}

interface AuthState {
    user: User | null;
    token: string | null;
    isAuthenticated: boolean;
    loading: boolean;
}

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

const getInitialState = (): AuthState => {
    if (!browser) return { user: null, token: null, isAuthenticated: false, loading: false };

    try {
        const user = localStorage.getItem('user');
        const token = localStorage.getItem('token');
        return {
            user: user ? JSON.parse(user) : null,
            token: token || null,
            isAuthenticated: !!token,
            loading: false
        };
    } catch {
        return { user: null, token: null, isAuthenticated: false, loading: false };
    }
};

function createAuthStore() {
    const { subscribe, set, update } = writable<AuthState>(getInitialState());

    return {
        subscribe,

        async login(username: string, password: string): Promise<User> {
            update(s => ({ ...s, loading: true }));

            try {
                const res = await fetch(`${API_URL}/auth/login/`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username, password })
                });

                const data = await res.json().catch(() => ({ detail: 'Error de respuesta del servidor' }));

                if (!res.ok) {
                    throw new Error(data?.non_field_errors?.[0] || data?.detail || 'Credenciales inválidas');
                }

                const newState: AuthState = {
                    user: data.user,
                    token: data.token,
                    isAuthenticated: true,
                    loading: false
                };

                if (browser) {
                    localStorage.setItem('token', data.token);
                    localStorage.setItem('user', JSON.stringify(data.user));
                    document.cookie = `token=${data.token}; path=/; max-age=604800; samesite=strict`;
                }

                set(newState);
                return data.user;

            } catch (error: any) {
                update(s => ({ ...s, loading: false }));
                throw error.message || 'Error de conexión';
            }
        },

        logout() {
            if (!browser) return;

            const token = localStorage.getItem('token');
            
            set({ user: null, token: null, isAuthenticated: false, loading: false });
            localStorage.clear();
            sessionStorage.clear();

            document.cookie = "token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 UTC; samesite=strict";

            if (token) {
                fetch(`${API_URL}/auth/logout/`, {
                    method: 'POST',
                    headers: { 'Authorization': `Token ${token}` }
                }).catch(() => {});
            }

            window.location.href = '/login';
        },

        updateUser(newUserData: Partial<User>) {
            update(s => {
                if (!s.user) return s;
                const updatedUser = { ...s.user, ...newUserData };
                if (browser) {
                    localStorage.setItem('user', JSON.stringify(updatedUser));
                }
                return { ...s, user: updatedUser };
            });
        }
    };
}

export const auth = createAuthStore();