import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { executeQuery } from '$lib/server/db';

export const GET: RequestHandler = async ({ params, locals }) => {
	try {
		// Check authentication
		if (!locals.user) {
			return json({ error: 'Not authenticated' }, { status: 401 });
		}

		const { id } = params;

		// Get screenplay
		const results = await executeQuery(`
			SELECT id, title, filename, original_filename, file_size, status, content, created_at, updated_at
			FROM screenplays 
			WHERE id = ? AND user_id = ?
		`, [id, locals.user.id]) as any[];

		if (results.length === 0) {
			return json({ error: 'Screenplay not found' }, { status: 404 });
		}

		const screenplay = results[0];

		return json({
			success: true,
			screenplay: {
				id: screenplay.id,
				title: screenplay.title,
				filename: screenplay.filename,
				originalName: screenplay.original_filename,
				size: screenplay.file_size,
				status: screenplay.status,
				content: screenplay.content,
				createdAt: screenplay.created_at,
				updatedAt: screenplay.updated_at
			}
		});
	} catch (error) {
		console.error('Get screenplay error:', error);
		return json({ error: 'Internal server error' }, { status: 500 });
	}
};

export const PUT: RequestHandler = async ({ params, request, locals }) => {
	try {
		// Check authentication
		if (!locals.user) {
			return json({ error: 'Not authenticated' }, { status: 401 });
		}

		const { id } = params;
		const { title, status } = await request.json();

		// Validate input
		if (!title || !title.trim()) {
			return json({ error: 'Title is required' }, { status: 400 });
		}

		// Check if screenplay exists and belongs to user
		const existingResults = await executeQuery(
			'SELECT id FROM screenplays WHERE id = ? AND user_id = ?',
			[id, locals.user.id]
		) as any[];

		if (existingResults.length === 0) {
			return json({ error: 'Screenplay not found' }, { status: 404 });
		}

		// Update screenplay
		await executeQuery(
			'UPDATE screenplays SET title = ?, status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ? AND user_id = ?',
			[title.trim(), status || 'draft', id, locals.user.id]
		);

		return json({
			success: true,
			message: 'Screenplay updated successfully'
		});
	} catch (error) {
		console.error('Update screenplay error:', error);
		return json({ error: 'Internal server error' }, { status: 500 });
	}
};

export const DELETE: RequestHandler = async ({ params, locals }) => {
	try {
		// Check authentication
		if (!locals.user) {
			return json({ error: 'Not authenticated' }, { status: 401 });
		}

		const { id } = params;

		// Check if screenplay exists and belongs to user
		const existingResults = await executeQuery(
			'SELECT filename FROM screenplays WHERE id = ? AND user_id = ?',
			[id, locals.user.id]
		) as any[];

		if (existingResults.length === 0) {
			return json({ error: 'Screenplay not found' }, { status: 404 });
		}

		// Delete from database
		await executeQuery(
			'DELETE FROM screenplays WHERE id = ? AND user_id = ?',
			[id, locals.user.id]
		);

		// Delete file from disk if it exists
		if (screenplay.file_path) {
			try {
				const fs = await import('fs/promises');
				const path = await import('path');
				const filePath = path.join(process.cwd(), screenplay.file_path);
				await fs.unlink(filePath);
				console.log(`✅ Deleted file: ${filePath}`);
			} catch (error) {
				console.warn(`⚠️  Could not delete file ${screenplay.file_path}:`, error);
				// Don't fail the deletion if file cleanup fails
			}
		}

		return json({
			success: true,
			message: 'Screenplay deleted successfully'
		});
	} catch (error) {
		console.error('Delete screenplay error:', error);
		return json({ error: 'Internal server error' }, { status: 500 });
	}
};
