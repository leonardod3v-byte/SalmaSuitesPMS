export interface Huesped {
    id: number;
    tipo_documento: 'V' | 'E' | 'J' | 'P';
    numero_documento: string;
    nombres: string;
    apellidos: string;
    fecha_nacimiento: string;
    edad: number;
    nacionalidad: string;
    estado_civil: string;
    telefono: string;
    email: string;
    procedencia: string;
    tipo_cliente_profesion: string;
    categoria: 'VIP' | 'Estándar';
    credito_autorizado: boolean;
    limite_credito: number | null;
    observaciones: string;
}

export interface HuespedCreate {
    tipo_documento: string;
    numero_documento: string;
    nombres: string;
    apellidos: string;
    fecha_nacimiento: string;
    edad?: number;
    nacionalidad: string;
    estado_civil: string;
    telefono: string;
    email: string;
    procedencia: string;
    tipo_cliente_profesion: string;
    categoria: string;
    credito_autorizado: boolean;
    limite_credito: number | null;
    observaciones: string;
}