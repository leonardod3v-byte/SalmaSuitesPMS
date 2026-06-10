export interface User {
    id: number;
    username: string;
    email: string;
    role: 'admin' | 'recepcionista';
    nombre_completo: string;
}

export interface AuthState {
    user: User | null;
    isAuthenticated: boolean;
    loading: boolean;
}