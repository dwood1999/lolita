import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { invalidateSession, deleteSessionTokenCookie } from '$lib/server/auth';

export const POST: RequestHandler = async (event) => {
	try {
		const { locals } = event;

		if (locals.session) {
			await invalidateSession(locals.session.id);
		}

		await deleteSessionTokenCookie(event);

		return json({ success: true, message: 'Logged out successfully' });
	} catch (error) {
		console.error('Logout error:', error);
		return json({ error: 'Internal server error' }, { status: 500 });
	}
};
