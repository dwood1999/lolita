import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { env } from '$env/dynamic/private';
import { executeQuery } from '$lib/server/db';

const PYTHON_SERVICE_URL = env.PYTHON_SERVICE_URL || 'http://127.0.0.1:8001';

// Simple in-memory cache for public analyses
const publicAnalysisCache = new Map<string, { data: any; timestamp: number }>();
const CACHE_TTL = 10 * 60 * 1000; // 10 minutes for public analyses

export const GET: RequestHandler = async ({ params }) => {
	try {
		const { token } = params;

		if (!token) {
			return json({ error: 'Share token is required' }, { status: 400 });
		}

		console.log(`🌐 Getting public analysis with token: ${token.substring(0, 8)}...`);

		// Check cache first
		const cached = publicAnalysisCache.get(token);
		if (cached && Date.now() - cached.timestamp < CACHE_TTL) {
			console.log(`🚀 Cache hit for public analysis: ${token.substring(0, 8)}...`);
			return json(cached.data, {
				headers: {
					'Cache-Control': 'public, max-age=600' // 10 minutes
				}
			});
		}

		// Get analysis ID from database using the public share token
		const tokenResults = await executeQuery(`
			SELECT id, title, is_public 
			FROM screenplay_analyses 
			WHERE public_share_token = ? AND is_public = TRUE
		`, [token]) as any[];

		if (tokenResults.length === 0) {
			return json({ error: 'Analysis not found or not publicly shared' }, { status: 404 });
		}

		const analysisId = tokenResults[0].id;
		const title = tokenResults[0].title;

		// Get analysis from Python service
		const response = await fetch(`${PYTHON_SERVICE_URL}/analysis/${analysisId}`);

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

		// Enhance with database metadata for public view
		try {
			const dbResults = await executeQuery(`
				SELECT created_at, updated_at, shared_at, title, genre
				FROM screenplay_analyses 
				WHERE id = ? AND is_public = TRUE
			`, [analysisId]) as any[];
			
			if (dbResults.length > 0) {
				result.created_at = dbResults[0].created_at;
				result.updated_at = dbResults[0].updated_at;
				result.shared_at = dbResults[0].shared_at;
				result.is_public = true;
				result.public_view = true; // Flag to indicate this is a public view
			}
		} catch (dbError) {
			console.warn('Could not fetch database metadata for public analysis:', dbError);
		}

		// Cache the result
		if (result.status === 'completed') {
			publicAnalysisCache.set(token, {
				data: result,
				timestamp: Date.now()
			});
			
			// Clean up old cache entries
			if (publicAnalysisCache.size > 50) {
				const oldestKey = publicAnalysisCache.keys().next().value;
				publicAnalysisCache.delete(oldestKey);
			}
		}

		return json(result, {
			headers: {
				'Cache-Control': 'public, max-age=600' // 10 minutes
			}
		});

	} catch (error) {
		console.error('❌ Get public analysis API error:', error);
		return json({ 
			error: 'Internal server error', 
			detail: error instanceof Error ? error.message : 'Unknown error' 
		}, { status: 500 });
	}
};
