import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { env } from '$env/dynamic/private';

const PYTHON_SERVICE_URL = env.PYTHON_SERVICE_URL || 'http://127.0.0.1:8001';

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

		console.log(`📊 Getting incentives for analysis: ${id} (user: ${locals.user.id})`);

		// Forward to Python service
		const pythonUrl = `${PYTHON_SERVICE_URL}/api/analysis/${id}/incentives`;
		const response = await fetch(pythonUrl);

		if (!response.ok) {
			if (response.status === 404) {
				return json({ error: 'Analysis incentives not found' }, { status: 404 });
			}
			
			const errorData = await response.text();
			console.error('Python service error:', errorData);
			return json({ 
				error: 'Incentives service unavailable', 
				detail: errorData 
			}, { status: response.status });
		}

		const result = await response.json();

		return json(result, {
			headers: {
				'Cache-Control': 'public, max-age=300' // 5 minutes cache
			}
		});

	} catch (error) {
		console.error('❌ Analysis incentives API error:', error);
		return json({ 
			error: 'Internal server error', 
			detail: error instanceof Error ? error.message : 'Unknown error' 
		}, { status: 500 });
	}
};
