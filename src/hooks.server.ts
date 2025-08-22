import type { Handle } from '@sveltejs/kit';
import { getCurrentSession } from '$lib/server/auth';

export const handle: Handle = async ({ event, resolve }) => {
	try {
		const sessionData = await getCurrentSession(event);

		if (sessionData) {
			event.locals.user = sessionData.user;
			event.locals.session = sessionData.session;
		} else {
			event.locals.user = null;
			event.locals.session = null;
		}
	} catch (err) {
		console.error('Session initialization error:', err);
		event.locals.user = null;
		event.locals.session = null;
	}

	return resolve(event);
};
