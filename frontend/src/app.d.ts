import { icons } from '$lib/components/Icons.svelte';

declare global {
    namespace App {
        interface Locals {
            user: {
                id: string;
                username: string;
                email: string;
                role: 'admin' | 'recepcion';
                first_name?: string;
                last_name?: string;
            } | null;
        }
        interface PageData {
            user?: App.Locals['user'];
        }
    }

    type IconKey = keyof typeof icons;
}

export {};