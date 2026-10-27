import { type Handle } from '@sveltejs/kit';

export const handle: Handle = async ({ event, resolve }) => {
    const response = await resolve(event);
    response.headers.set('Cache-Control', 'no-store, must-revalidate');
    return response;
};
