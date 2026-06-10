const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000/api';

export async function loginRequest(username: string, password: string) {
    const res = await fetch(`${API_URL}/auth/login/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password }),
        credentials: 'include',
    });
    if (!res.ok) {
        const errorData = await res.json().catch(() => ({}));
        throw new Error(errorData.error || errorData.detail || 'Error al iniciar sesión');
    }
    return res.json();
}

export async function logoutRequest() {
    const res = await fetch(`${API_URL}/auth/logout/`, {
        method: 'POST',
        credentials: 'include',
    });
    return res.json();
}

export async function fetchProfile() {
    const res = await fetch(`${API_URL}/auth/profile/`, {
        credentials: 'include',
    });
    if (!res.ok) throw new Error('No autenticado');
    return res.json();
}

export async function cambiarPassword(newPassword: string) {
    const res = await fetch(`${API_URL}/auth/cambiar-password/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ new_password: newPassword }),
        credentials: 'include',
    });
    if (!res.ok) {
        const error = await res.json().catch(() => ({}));
        throw new Error(error.error || 'Error al cambiar contraseña');
    }
    return res.json();
}

// Funciones de administración de usuarios (solo admin)
export async function fetchUsuarios() {
    const res = await fetch(`${API_URL}/auth/usuarios/`, { credentials: 'include' });
    if (!res.ok) throw new Error('Acceso denegado');
    return res.json();
}

export async function createUsuario(data: any) {
    const res = await fetch(`${API_URL}/auth/usuarios/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
        credentials: 'include',
    });
    if (!res.ok) {
        const error = await res.json().catch(() => ({}));
        throw new Error(error.error || 'Error al crear usuario');
    }
    return res.json();
}

export async function updateUsuario(id: number, data: any) {
    const res = await fetch(`${API_URL}/auth/usuarios/${id}/`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
        credentials: 'include',
    });
    if (!res.ok) throw new Error('Error al actualizar');
    return res.json();
}

export async function deactivateUsuario(id: number) {
    const res = await fetch(`${API_URL}/auth/usuarios/${id}/`, {
        method: 'DELETE',
        credentials: 'include',
    });
    if (!res.ok) throw new Error('Error al desactivar');
    return res.json();
}