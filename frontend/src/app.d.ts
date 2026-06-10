import { type User } from '$lib/types/auth';
import { icons } from '$components/ui/Icons.svelte';

declare global {
    namespace App {
        interface Locals {
            user: User | null;
        }
        interface PageData {
            user?: App.Locals['user'];
        }
    }

    type IconKey = keyof typeof icons;
}

export {};