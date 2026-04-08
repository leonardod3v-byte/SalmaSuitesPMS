import { toast } from '$lib/stores/toast';

const API_URL = 'http://localhost:8000/api';

interface FetchOptions extends RequestInit {
    headers?: Record<string, string>;
    silent?: boolean;
}

export async function apiFetch<T>(endpoint: string, options: FetchOptions = {}): Promise<T> {
    const { silent = false, ...fetchOptions } = options;
    const token = localStorage.getItem('token');

    try {
        const res = await fetch(`${API_URL}${endpoint}`, {
            ...fetchOptions,
            headers: {
                'Content-Type': 'application/json',
                ...(token ? { 'Authorization': `Token ${token}` } : {}),
                ...fetchOptions.headers
            }
        });

        // Manejo de sesión expirada
        if (res.status === 401 || res.status === 403) {
            localStorage.clear();
            toast.send("Sesión expirada", "info");
            setTimeout(() => window.location.href = '/login', 1000);
            throw new Error("Sesión expirada");
        }

        if (!res.ok) {
            const data = await res.json().catch(() => ({}));
            const msg = data.detail || data.error || `Error ${res.status}`;
            if (!silent) toast.send(msg, "error");
            throw new Error(msg);
        }

        return res.json();
    } catch (error: any) {
        if (error.message === 'Failed to fetch') {
            toast.send("Servidor fuera de línea", "error");
        }
        throw error;
    }
}