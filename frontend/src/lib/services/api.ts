import { toast } from '$lib/stores/toast';
import { auth } from '$lib/stores/auth';
import { browser } from '$app/environment';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

interface FetchOptions extends RequestInit {
    headers?: Record<string, string>;
    silent?: boolean;
}

export async function apiFetch<T>(endpoint: string, options: FetchOptions = {}): Promise<T> {
    const { silent = false, ...fetchOptions } = options;

    try {
        const res = await fetch(`${API_URL}${endpoint}`, {
            ...fetchOptions,
            // credentials: 'include' hace que el browser envíe
            // la cookie HttpOnly automáticamente en cada request
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json',
                ...fetchOptions.headers,
            },
        });

        if (res.status === 401 || res.status === 403) {
            if (browser) {
                toast.send('Sesión expirada', 'info');
                // logout() llama al endpoint de Django para borrar la cookie
                setTimeout(() => auth.logout(), 1000);
            }
            throw new Error('Sesión expirada');
        }

        if (!res.ok) {
            const data = await res.json().catch(() => ({}));
            const msg = data.detail || data.error || `Error ${res.status}`;
            if (!silent) toast.send(msg, 'error');
            throw new Error(msg);
        }

        return res.json();
    } catch (error: any) {
        if (error.message === 'Failed to fetch') {
            toast.send('Servidor fuera de línea', 'error');
        }
        throw error;
    }
}