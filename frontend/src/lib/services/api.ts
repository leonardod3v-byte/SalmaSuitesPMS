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

    const isPublicRoute = path.includes('/auth/login') || path.includes('/auth/register');
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
        // NO borramos el token aquí. Solo lanzamos el error.
        // El layout o el componente decidirán si redirigir o no.
        throw new Error('Sesión expirada. Inicia sesión de nuevo.');
    }

    if (!res.ok) {
        const error = await res.json().catch(() => ({ detail: 'Error desconocido' }));
        const message = error.detail || error.error || 'Error en la petición';
        throw new Error(message);
    }

    if (res.status === 204) return undefined as T;
    return res.json();
}
