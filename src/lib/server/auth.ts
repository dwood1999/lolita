import type { RequestEvent } from '@sveltejs/kit';
import { sha256 } from '@oslojs/crypto/sha2';
import { encodeBase64url, encodeHexLowerCase } from '@oslojs/encoding';
import { hash, verify } from '@node-rs/argon2';
import { executeQuery } from '$lib/server/db';

const DAY_IN_MS = 1000 * 60 * 60 * 24;

export const sessionCookieName = 'auth-session';

export interface User {
	id: string;
	email: string;
	password_hash: string;
	created_at: string;
}

export interface Session {
	id: string;
	user_id: string;
	expires_at: Date;
	created_at: string;
}

export function generateSessionToken() {
	const bytes = crypto.getRandomValues(new Uint8Array(18));
	const token = encodeBase64url(bytes);
	return token;
}

export async function createSession(token: string, userId: string): Promise<Session> {
	const sessionId = encodeHexLowerCase(sha256(new TextEncoder().encode(token)));
	const expiresAt = new Date(Date.now() + DAY_IN_MS * 30);
	
	await executeQuery(
		'INSERT INTO sessions (id, user_id, expires_at) VALUES (?, ?, ?)',
		[sessionId, userId, expiresAt]
	);
	
	return {
		id: sessionId,
		user_id: userId,
		expires_at: expiresAt,
		created_at: new Date().toISOString()
	};
}

export async function validateSessionToken(token: string): Promise<{ session: Session; user: User } | null> {
	try {
		const sessionId = encodeHexLowerCase(sha256(new TextEncoder().encode(token)));
		
		const results = await executeQuery(`
			SELECT s.*, u.* FROM sessions s 
			JOIN users u ON s.user_id = u.id 
			WHERE s.id = ? AND s.expires_at > NOW()
		`, [sessionId]) as any[];
		
		if (results.length === 0) {
			return null;
		}
		
		const row = results[0];
		const session: Session = {
			id: row.id,
			user_id: row.user_id,
			expires_at: row.expires_at,
			created_at: row.created_at
		};
		
		const user: User = {
			id: row.user_id,
			email: row.email,
			password_hash: row.password_hash,
			created_at: row.created_at
		};
		
		// Refresh session if it's more than 15 days old
		if (Date.now() >= session.expires_at.getTime() - DAY_IN_MS * 15) {
			const newExpiresAt = new Date(Date.now() + DAY_IN_MS * 30);
			await executeQuery(
				'UPDATE sessions SET expires_at = ? WHERE id = ?',
				[newExpiresAt, sessionId]
			);
			session.expires_at = newExpiresAt;
		}
		
		return { session, user };
	} catch (error) {
		console.error('Session validation error:', error);
		return null;
	}
}

export async function invalidateSession(sessionId: string): Promise<void> {
	await executeQuery('DELETE FROM sessions WHERE id = ?', [sessionId]);
}

export async function invalidateUserSessions(userId: string): Promise<void> {
	await executeQuery('DELETE FROM sessions WHERE user_id = ?', [userId]);
}

export async function setSessionTokenCookie(event: RequestEvent, token: string, expiresAt: Date): Promise<void> {
	const isProduction = process.env.NODE_ENV === 'production';
	
	event.cookies.set(sessionCookieName, token, {
		expires: expiresAt,
		path: '/',
		httpOnly: true,    // Prevent XSS access via JavaScript
		secure: isProduction, // HTTPS only in production, HTTP allowed in dev
		sameSite: 'strict' // CSRF protection
	});
}

export async function deleteSessionTokenCookie(event: RequestEvent): Promise<void> {
	const isProduction = process.env.NODE_ENV === 'production';
	
	event.cookies.delete(sessionCookieName, {
		path: '/',
		httpOnly: true,
		secure: isProduction,
		sameSite: 'strict'
	});
}

export async function getCurrentSession(event: RequestEvent): Promise<{ session: Session; user: User } | null> {
	const token = event.cookies.get(sessionCookieName) ?? null;
	if (token === null) {
		return null;
	}
	const result = await validateSessionToken(token);
	if (result === null) {
		deleteSessionTokenCookie(event);
		return null;
	}
	return result;
}

// User management functions
export async function createUser(email: string, password: string): Promise<User> {
	const userId = crypto.randomUUID();
	const passwordHash = await hash(password, {
		memoryCost: 19456,
		timeCost: 2,
		outputLen: 32,
		parallelism: 1
	});
	
	// Insert with additional fields that exist in the current schema
	await executeQuery(
		'INSERT INTO users (id, email, password_hash, full_name, is_active, is_verified) VALUES (?, ?, ?, ?, ?, ?)',
		[userId, email, passwordHash, '', 1, 1]
	);
	
	return {
		id: userId,
		email,
		password_hash: passwordHash,
		created_at: new Date().toISOString()
	};
}

export async function getUserByEmail(email: string): Promise<User | null> {
	try {
		const results = await executeQuery(
			'SELECT * FROM users WHERE email = ?',
			[email]
		) as any[];
		
		if (results.length === 0) {
			return null;
		}
		
		return results[0] as User;
	} catch (error) {
		console.error('Error getting user by email:', error);
		return null;
	}
}

export async function verifyPassword(user: User, password: string): Promise<boolean> {
	return await verify(user.password_hash, password);
}
