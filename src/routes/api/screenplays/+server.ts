import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { executeQuery } from '$lib/server/db';

export const GET: RequestHandler = async ({ locals, url }) => {
	try {
		// Check authentication
		if (!locals.user) {
			return json({ error: 'Not authenticated' }, { status: 401 });
		}

		const page = parseInt(url.searchParams.get('page') || '1');
		const limit = parseInt(url.searchParams.get('limit') || '10');
		const offset = (page - 1) * limit;

		// Get user's screenplays
		const screenplays = await executeQuery(`
			SELECT id, title, filename, original_filename, file_size, status, created_at, updated_at
			FROM screenplays 
			WHERE user_id = ? 
			ORDER BY updated_at DESC 
			LIMIT ? OFFSET ?
		`, [locals.user.id, limit, offset]) as any[];

		// Get total count
		const countResult = await executeQuery(
			'SELECT COUNT(*) as total FROM screenplays WHERE user_id = ?',
			[locals.user.id]
		) as any[];
		
		const total = countResult[0]?.total || 0;

		return json({
			success: true,
			screenplays: screenplays.map(screenplay => ({
				id: screenplay.id,
				title: screenplay.title,
				filename: screenplay.filename,
				originalName: screenplay.original_filename,
				size: screenplay.file_size,
				status: screenplay.status,
				createdAt: screenplay.created_at,
				updatedAt: screenplay.updated_at
			})),
			pagination: {
				page,
				limit,
				total,
				totalPages: Math.ceil(total / limit)
			}
		});
	} catch (error) {
		console.error('Get screenplays error:', error);
		return json({ error: 'Internal server error' }, { status: 500 });
	}
};
