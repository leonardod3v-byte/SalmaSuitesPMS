import { writable } from 'svelte/store';
import { browser } from '$app/environment';
import { goto } from '$app/navigation';
import type { User, AuthState } from '$lib/types/auth';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

function createAuthStore() {
    // Estado inicial vacío — la fuente de verdad es el servidor
    const { subscribe, set, update } = writable<AuthState>({
        user: null,
        isAuthenticated: false,
        loading: true,
    });

    return {
        subscribe,
        
        // Permite forzar el estado (útil para la sincronización desde las Svelte Pages)
        init(user: User | null) {
            set({
                user,
                isAuthenticated: !!user,
                loading: false,
            });
        },

        async login(username: string, password: string): Promise<User> {
            update(s => ({ ...s, loading: true }));

            try {
                const res = await fetch(`${API_URL}/auth/login/`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username, password }),
                });

                const data = await res.json().catch(() => ({}));

                if (!res.ok) {
                    throw new Error(
                        data?.non_field_errors?.[0] || data?.detail || 'Credenciales inválidas'
                    );
                }

                const newState: AuthState = {
                    user: data.user,
                    isAuthenticated: true,
                    loading: false,
                };

                set(newState);
                return data.user;

            } catch (error: any) {
                update(s => ({ ...s, loading: false }));
                throw error instanceof Error ? error : new Error('Error de conexión');
            }
        },

        async logout() {
            if (!browser) return;

            try {
                // Django limpia la cookie desde el servidor
                await fetch(`${API_URL}/auth/logout/`, {
                    method: 'POST',
                    credentials: 'include',
                });
            } catch {
                // Si falla el fetch, igual limpiamos el estado local
            }

            set({ user: null, isAuthenticated: false, loading: false });
            // Usar goto para que SvelteKit recargue y hooks.server.ts detecte que la cookie fue borrada
            goto('/login', { invalidateAll: true });
        },
    };
}

export const auth = createAuthStore();