import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { executeQuery } from '$lib/server/db';

export const GET: RequestHandler = async ({ url, locals }) => {
	try {
		// Check authentication
		if (!locals.user) {
			return json({ error: 'Authentication required' }, { status: 401 });
		}

		const limit = parseInt(url.searchParams.get('limit') || '50');
		const offset = parseInt(url.searchParams.get('offset') || '0');

		console.log(`📚 Getting user analyses from DB: ${locals.user.id} (limit: ${limit}, offset: ${offset})`);

		// Get analyses directly from screenplay_analyses table with optimized query
		const analyses = await executeQuery(`
			SELECT 
				id, 
				title, 
				genre,
				overall_score,
				recommendation,
				status,
				file_size,
				original_filename,
				cost,
				created_at,
				updated_at,
				ai_model,
				grok_score,
				gpt5_score,
				deepseek_financial_score,
				perplexity_market_score,
				openai_score
			FROM screenplay_analyses 
			WHERE user_id = ? 
			ORDER BY updated_at DESC 
			LIMIT ? OFFSET ?
		`, [locals.user.id, limit, offset]) as any[];

		// Get total count
		const countResult = await executeQuery(
			'SELECT COUNT(*) as total FROM screenplay_analyses WHERE user_id = ?',
			[locals.user.id]
		) as any[];
		
		const total = countResult[0]?.total || 0;

		// Format the response to match the expected structure
		const formattedAnalyses = analyses.map(analysis => ({
			id: analysis.id,
			title: analysis.title,
			genre: analysis.genre,
			score: analysis.overall_score,
			recommendation: analysis.recommendation,
			status: analysis.status,
			fileSize: analysis.file_size,
			filename: analysis.original_filename,
			cost: parseFloat(analysis.cost || 0),
			createdAt: analysis.created_at,
			updatedAt: analysis.updated_at,
			aiModel: analysis.ai_model,
			// All dynamic scores now available
			craftScore: analysis.overall_score,           // Story craft & structure
			realityScore: analysis.grok_score,           // Brutal reality check (dynamic)
			writingScore: analysis.gpt5_score,           // Writing excellence (dynamic)
			financialScore: analysis.deepseek_financial_score, // Financial intelligence (dynamic)
			marketScore: analysis.perplexity_market_score,     // Market opportunity (dynamic)
			commercialScore: analysis.openai_score       // Commercial viability (dynamic)
		}));

		return json({
			success: true,
			analyses: formattedAnalyses,
			pagination: {
				limit,
				offset,
				total,
				hasMore: offset + limit < total
			}
		}, {
			headers: {
				'Cache-Control': 'private, max-age=60' // Cache for 1 minute
			}
		});

	} catch (error) {
		console.error('❌ Get analyses from DB error:', error);
		return json({ 
			error: 'Database error', 
			detail: error instanceof Error ? error.message : 'Unknown error' 
		}, { status: 500 });
	}
};
