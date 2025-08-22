import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { createUser, getUserByEmail } from '$lib/server/auth';

export const POST: RequestHandler = async ({ request }) => {
	try {
		const { email, password } = await request.json();

		// Validate input
		if (!email || !password) {
			return json({ error: 'Email and password are required' }, { status: 400 });
		}

		// Validate email format
		const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
		if (!emailRegex.test(email)) {
			return json({ error: 'Invalid email format' }, { status: 400 });
		}

		// Validate password strength
		if (password.length < 8) {
			return json({ error: 'Password must be at least 8 characters long' }, { status: 400 });
		}

		// Check if user already exists
		const existingUser = await getUserByEmail(email);
		if (existingUser) {
			return json({ error: 'User with this email already exists' }, { status: 409 });
		}

		// Create user
		const user = await createUser(email, password);

		return json({
			success: true,
			message: 'User created successfully',
			user: {
				id: user.id,
				email: user.email
			}
		});
	} catch (error) {
		console.error('Registration error:', error);
		return json({ error: 'Internal server error' }, { status: 500 });
	}
};
