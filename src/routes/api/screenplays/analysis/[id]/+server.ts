import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { env } from '$env/dynamic/private';

const PYTHON_SERVICE_URL = env.PYTHON_SERVICE_URL || 'http://127.0.0.1:8001';

// Simple in-memory cache for completed analyses
const analysisCache = new Map<string, { data: any; timestamp: number }>();
const CACHE_TTL = 5 * 60 * 1000; // 5 minutes for completed analyses

export const GET: RequestHandler = async ({ params, locals }) => {
	try {
		// Check if user is authenticated
		if (!locals.user) {
			return json({ error: 'Authentication required' }, { status: 401 });
		}

		const { id } = params;

		if (!id) {
			return json({ error: 'Analysis ID is required' }, { status: 400 });
		}

		console.log(`📊 Getting analysis: ${id} (user: ${locals.user.id})`);

		// Check cache first for completed analyses
		const cacheKey = `${id}-${locals.user.id}`;
		const cached = analysisCache.get(cacheKey);
		if (cached && Date.now() - cached.timestamp < CACHE_TTL) {
			// Only use cache for completed analyses
			if (cached.data.status === 'completed') {
				console.log(`🚀 Cache hit for analysis: ${id}`);
				return json(cached.data, {
					headers: {
						'Cache-Control': 'public, max-age=300' // 5 minutes
					}
				});
			}
		}

		// Get analysis from Python service
		const response = await fetch(`${PYTHON_SERVICE_URL}/analysis/${id}`);

		if (!response.ok) {
			if (response.status === 404) {
				return json({ error: 'Analysis not found' }, { status: 404 });
			}
			
			const errorData = await response.text();
			console.error('Python service error:', errorData);
			return json({ 
				error: 'Analysis service unavailable', 
				detail: errorData 
			}, { status: response.status });
		}

		const result = await response.json();

		// Verify user owns this analysis
		if (result.result && result.result.user_id !== locals.user.id) {
			return json({ error: 'Access denied' }, { status: 403 });
		}

		// Enhance with database metadata (created_at, updated_at, public status)
		try {
			const { executeQuery } = await import('$lib/server/db');
			const dbResults = await executeQuery(`
				SELECT created_at, updated_at, is_public, public_share_token, shared_at 
				FROM screenplay_analyses 
				WHERE id = ? AND user_id = ?
			`, [id, locals.user.id]) as any[];
			
			if (dbResults.length > 0) {
				result.created_at = dbResults[0].created_at;
				result.updated_at = dbResults[0].updated_at;
				result.is_public = dbResults[0].is_public;
				result.public_share_token = dbResults[0].public_share_token;
				result.shared_at = dbResults[0].shared_at;
			}
		} catch (dbError) {
			console.warn('Could not fetch database metadata:', dbError);
			// Continue without metadata - not critical
		}

		// Cache completed analyses
		if (result.status === 'completed') {
			analysisCache.set(cacheKey, {
				data: result,
				timestamp: Date.now()
			});
			
			// Clean up old cache entries
			if (analysisCache.size > 100) {
				const oldestKey = analysisCache.keys().next().value;
				analysisCache.delete(oldestKey);
			}
		}

		return json(result, {
			headers: result.status === 'completed' ? {
				'Cache-Control': 'public, max-age=300' // 5 minutes for completed
			} : {
				'Cache-Control': 'no-cache' // No cache for processing
			}
		});

	} catch (error) {
		console.error('❌ Get analysis API error:', error);
		return json({ 
			error: 'Internal server error', 
			detail: error instanceof Error ? error.message : 'Unknown error' 
		}, { status: 500 });
	}
};
