import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { getUserByEmail, verifyPassword, generateSessionToken, createSession, setSessionTokenCookie } from '$lib/server/auth';

export const POST: RequestHandler = async ({ request, cookies }) => {
	try {
		const { email, password } = await request.json();

		// Validate input
		if (!email || !password) {
			return json({ error: 'Email and password are required' }, { status: 400 });
		}

		// Find user
		const user = await getUserByEmail(email);
		if (!user) {
			return json({ error: 'Invalid email or password' }, { status: 401 });
		}

		// Verify password
		const isValidPassword = await verifyPassword(user, password);
		if (!isValidPassword) {
			return json({ error: 'Invalid email or password' }, { status: 401 });
		}

		// Create session
		const sessionToken = generateSessionToken();
		const session = await createSession(sessionToken, user.id);

		// Set cookie
		await setSessionTokenCookie({ cookies } as any, sessionToken, session.expires_at);

		return json({
			success: true,
			user: {
				id: user.id,
				email: user.email
			}
		});
	} catch (error) {
		console.error('Login error:', error);
		return json({ error: 'Internal server error' }, { status: 500 });
	}
};
