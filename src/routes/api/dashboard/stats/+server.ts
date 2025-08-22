import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { executeQuery } from '$lib/server/db';

export const GET: RequestHandler = async ({ locals }) => {
	try {
		// Check authentication
		if (!locals.user) {
			return json({ error: 'Not authenticated' }, { status: 401 });
		}

		// Get total analyses count from screenplay_analyses table
		const totalResult = await executeQuery(
			'SELECT COUNT(*) as total FROM screenplay_analyses WHERE user_id = ?',
			[locals.user.id]
		) as any[];
		const totalScreenplays = totalResult[0]?.total || 0;

		// Get completed analyses count
		const completedResult = await executeQuery(
			'SELECT COUNT(*) as completed FROM screenplay_analyses WHERE user_id = ? AND status = ?',
			[locals.user.id, 'completed']
		) as any[];
		const completedAnalyses = completedResult[0]?.completed || 0;

		// Get in progress count
		const inProgressResult = await executeQuery(
			'SELECT COUNT(*) as in_progress FROM screenplay_analyses WHERE user_id = ? AND status IN (?, ?)',
			[locals.user.id, 'processing', 'pending']
		) as any[];
		const inProgress = inProgressResult[0]?.in_progress || 0;

		// Get recent analyses with scores
		const recentScreenplays = await executeQuery(`
			SELECT id, title, status, overall_score, recommendation, created_at, updated_at
			FROM screenplay_analyses 
			WHERE user_id = ? 
			ORDER BY updated_at DESC 
			LIMIT 5
		`, [locals.user.id]) as any[];

		return json({
			success: true,
			stats: {
				totalScreenplays,
				completedAnalyses,
				inProgress,
				recentScreenplays: recentScreenplays.map(screenplay => ({
					id: screenplay.id,
					title: screenplay.title,
					status: screenplay.status,
					score: screenplay.overall_score,
					recommendation: screenplay.recommendation,
					createdAt: screenplay.created_at,
					updatedAt: screenplay.updated_at
				}))
			}
		}, {
			headers: {
				'Cache-Control': 'private, max-age=30' // Cache for 30 seconds
			}
		});
	} catch (error) {
		console.error('Get dashboard stats error:', error);
		return json({ error: 'Internal server error' }, { status: 500 });
	}
};
