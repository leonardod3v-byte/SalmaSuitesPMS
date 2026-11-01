const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000/api';

function getToken(): string | null {
    if (typeof window === 'undefined') return null;
    return localStorage.getItem('auth_token');
}

export async function apiFetch<T = unknown>(
    path: string,
    options: {
        method?: string;
        headers?: Record<string, string>;
        body?: BodyInit | null;
    } = {}
): Promise<T> {
    const url = `${API_URL}${path}`;

    const isPublicRoute = path.includes('/auth/login') || path.includes('/auth/register') || path.includes('/auth/password-reset');
    const token = isPublicRoute ? null : getToken();

    const headers: Record<string, string> = {};

    if (!(options.body instanceof FormData)) {
        headers['Content-Type'] = 'application/json';
    }

    if (token) {
        headers['Authorization'] = `Token ${token}`;
    }

    if (options.headers) {
        Object.assign(headers, options.headers);
    }

    const config: RequestInit = {
        method: options.method ?? 'GET',
        headers,
        credentials: 'include',
        body: options.body ?? undefined,
    };

    const res = await fetch(url, config);

    if (res.status === 401) {
        const error = await res.json().catch(() => ({}));
        const msg = error.detail || 'Tu sesión expiró. Inicia sesión de nuevo.';
        throw new Error(msg);
    }

    if (!res.ok) {
        const error = await res.json().catch(() => ({ detail: 'Error desconocido' }));

        let message = 'Error en la petición';
        if (typeof error.detail === 'string') {
            message = error.detail;
        } else if (typeof error.error === 'string') {
            message = error.error;
        } else if (error.non_field_errors && Array.isArray(error.non_field_errors)) {
            message = error.non_field_errors[0];
        } else if (Array.isArray(error)) {
            message = error[0];
        } else if (typeof error === 'object') {
            const firstKey = Object.keys(error)[0];
            if (firstKey && Array.isArray(error[firstKey])) {
                message = `${error[firstKey][0]}`;
            }
        }

        throw new Error(message);
    }

    if (res.status === 204) return undefined as T;
    return res.json();
}
