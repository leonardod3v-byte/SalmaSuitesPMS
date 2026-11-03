import { type Handle, redirect } from '@sveltejs/kit';

const PUBLIC_ROUTES = ['/login', '/recuperar'];

export const handle: Handle = async ({ event, resolve }) => {
    const response = await resolve(event);
    response.headers.set('Cache-Control', 'no-store, must-revalidate, max-age=0');
    response.headers.set('Pragma', 'no-cache');
    response.headers.set('Expires', '0');

    return response;
};
