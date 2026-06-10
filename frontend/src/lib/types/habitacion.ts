export interface Habitacion {
    id: number;
    numero: string;
    piso: number;
    cantidad_camas: number;
    capacidad_maxima: number;
    categoria_tipo: string;
    precio_por_noche: string;
    estado: 'Limpia' | 'Ocupada' | 'Sucia' | 'Mantenimiento' | 'Obra';
    notas: string;
    imagen: string | null;
    imagen_url: string | null;
}

export interface HabitacionCreate {
    numero: string;
    piso: number;
    cantidad_camas: number;
    capacidad_maxima: number;
    categoria_tipo: string;
    precio_por_noche: number;
    estado: string;
    notas?: string;
    imagen?: string | null;
    imagen_url?: string | null;
}