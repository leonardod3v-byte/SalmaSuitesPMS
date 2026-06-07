// frontend/src/lib/stores/auth.ts
import { writable } from 'svelte/store';
import { browser } from '$app/environment';
import { goto } from '$app/navigation';
import type { User, AuthState } from '$lib/types/auth';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';
const COOKIE_NAME = 'auth_token';

// Funciones auxiliares para manejar cookies en el cliente
function setCookie(name: string, value: string, days: number = 7) {
    if (!browser) return;
    const expires = new Date();
    expires.setTime(expires.getTime() + days * 24 * 60 * 60 * 1000);
    document.cookie = `${name}=${value}; expires=${expires.toUTCString()}; path=/; SameSite=Lax`;
}

function deleteCookie(name: string) {
    if (!browser) return;
    document.cookie = `${name}=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/; SameSite=Lax`;
}

function createAuthStore() {
    const { subscribe, set, update } = writable<AuthState>({
        user: null,
        isAuthenticated: false,
        loading: true,
    });

    return {
        subscribe,

        // Permite sincronizar el estado desde el servidor (usado en +layout.server.ts)
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
                    credentials: 'include', // importante para recibir cookies si el backend las enviara
                });

                const data = await res.json().catch(() => ({}));

                if (!res.ok) {
                    throw new Error(
                        data?.non_field_errors?.[0] || data?.detail || data?.error || 'Credenciales inválidas'
                    );
                }

                // Guardar el token en una cookie (para que hooks.server.ts lo lea)
                if (data.token) {
                    setCookie(COOKIE_NAME, data.token, 7);
                } else {
                    console.warn('No se recibió token del backend');
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
                // Llamar al endpoint de logout para invalidar el token en el backend
                await fetch(`${API_URL}/auth/logout/`, {
                    method: 'POST',
                    credentials: 'include',
                    headers: { 'Content-Type': 'application/json' },
                });
            } catch (err) {
                // Si falla, igual limpiamos localmente
                console.warn('Error en logout remoto', err);
            }

            // Eliminar la cookie
            deleteCookie(COOKIE_NAME);

            set({ user: null, isAuthenticated: false, loading: false });
            // Forzar recarga completa de la autenticación en el servidor
            goto('/login', { invalidateAll: true });
        },
    };
}

export const auth = createAuthStore();