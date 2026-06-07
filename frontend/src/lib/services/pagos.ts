import { apiFetch } from './api';

export const pagosApi = {
    registrar: (data: { reserva: number; monto: number; metodo: string; referencia: string }) =>
        apiFetch('/pagos/', { method: 'POST', body: JSON.stringify(data) }),
};