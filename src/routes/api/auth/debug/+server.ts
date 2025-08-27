import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { getCurrentSession } from '$lib/server/auth';

export const GET: RequestHandler = async ({ cookies, locals }) => {
	try {
		const sessionCookie = cookies.get('auth-session');
		const sessionData = locals.user ? { user: locals.user } : null;
		
		return json({
			hasCookie: !!sessionCookie,
			cookieValue: sessionCookie ? sessionCookie.substring(0, 10) + '...' : null,
			hasSession: !!sessionData,
			user: sessionData?.user ? {
				id: sessionData.user.id,
				email: sessionData.user.email
			} : null,
			locals: {
				hasUser: !!locals.user,
				userEmail: locals.user?.email
			}
		});
	} catch (error) {
		console.error('Debug auth error:', error);
		return json({ error: 'Debug failed', details: error.message }, { status: 500 });
	}
};
