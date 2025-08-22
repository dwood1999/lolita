import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { env } from '$env/dynamic/private';

const PYTHON_SERVICE_URL = env.PYTHON_SERVICE_URL || 'http://127.0.0.1:8001';

export const GET: RequestHandler = async ({ url, locals }) => {
	try {
		// Check if user is authenticated
		if (!locals.user) {
			return json({ error: 'Authentication required' }, { status: 401 });
		}

		const limit = parseInt(url.searchParams.get('limit') || '50');
		const offset = parseInt(url.searchParams.get('offset') || '0');

		console.log(`📚 Getting user analyses: ${locals.user.id} (limit: ${limit}, offset: ${offset})`);

		// Get analyses from Python service
		const response = await fetch(
			`${PYTHON_SERVICE_URL}/user/${locals.user.id}/analyses?limit=${limit}&offset=${offset}`
		);

		if (!response.ok) {
			const errorData = await response.text();
			console.error('Python service error:', errorData);
			return json({ 
				error: 'Analysis service unavailable', 
				detail: errorData 
			}, { status: response.status });
		}

		const result = await response.json();

		return json(result);

	} catch (error) {
		console.error('❌ Get user analyses API error:', error);
		return json({ 
			error: 'Internal server error', 
			detail: error instanceof Error ? error.message : 'Unknown error' 
		}, { status: 500 });
	}
};
