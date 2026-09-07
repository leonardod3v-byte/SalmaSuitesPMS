export interface Usuario {
    id: number;
    username: string;
    email: string;
    role: 'admin' | 'recepcionista';
    nombre_completo: string;
    is_active: boolean;
    last_login: string | null;
}