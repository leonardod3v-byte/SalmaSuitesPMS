export interface User {
    id: number; // Mantenemos number para alinearlo con el ID secuencial o BigAutofield de Django
    username: string;
    email: string;
    role: 'admin' | 'recepcion';
    first_name?: string;
    last_name?: string;
}

export interface AuthState {
    user: User | null;
    isAuthenticated: boolean;
    loading: boolean;
}