import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { executeQuery } from '$lib/server/db';
import { analyzeScreenplay } from '$lib/server/analysis';

export const POST: RequestHandler = async ({ params, locals }) => {
	try {
		// Check authentication
		if (!locals.user) {
			return json({ error: 'Not authenticated' }, { status: 401 });
		}

		const { id } = params;

		// Get screenplay
		const results = await executeQuery(`
			SELECT id, filename, status
			FROM screenplays 
			WHERE id = ? AND user_id = ?
		`, [id, locals.user.id]) as any[];

		if (results.length === 0) {
			return json({ error: 'Screenplay not found' }, { status: 404 });
		}

		const screenplay = results[0];

		// Check if already analyzing or completed
		if (screenplay.status === 'analyzing') {
			return json({ error: 'Analysis already in progress' }, { status: 400 });
		}

		// Update status to analyzing
		await executeQuery(
			'UPDATE screenplays SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
			['analyzing', id]
		);

		// Start analysis (in a real app, this would be async/background job)
		try {
			const analysis = await analyzeScreenplay(id, screenplay.filename);
			
			// Store analysis results (you'd create an analyses table for this)
			// For now, we'll just update the screenplay status
			await executeQuery(
				'UPDATE screenplays SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
				['completed', id]
			);

			return json({
				success: true,
				message: 'Analysis completed successfully',
				analysis
			});
		} catch (analysisError) {
			// Update status to error
			await executeQuery(
				'UPDATE screenplays SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
				['error', id]
			);

			console.error('Analysis failed:', analysisError);
			return json({ error: 'Analysis failed' }, { status: 500 });
		}
	} catch (error) {
		console.error('Analyze screenplay error:', error);
		return json({ error: 'Internal server error' }, { status: 500 });
	}
};
