import { writable } from 'svelte/store';

export type ToastType = 'success' | 'error' | 'info' | 'warning';

export interface Toast {
    id: number;
    message: string;
    type: ToastType;
    duration: number;
}

function createToastStore() {
    const { subscribe, update } = writable<Toast[]>([]);
    let nextId = 0;

    function add(message: string, type: ToastType = 'info', duration: number = 4000) {
        const id = nextId++;
        update(toasts => [...toasts, { id, message, type, duration }]);
        if (duration > 0) {
            setTimeout(() => dismiss(id), duration);
        }
    }

    function dismiss(id: number) {
        update(toasts => toasts.filter(t => t.id !== id));
    }

    return {
        subscribe,
        success: (msg: string) => add(msg, 'success'),
        error: (msg: string) => add(msg, 'error', 6000),
        info: (msg: string) => add(msg, 'info'),
        warning: (msg: string) => add(msg, 'warning', 5000),
        dismiss,
    };
}

export const toast = createToastStore();