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

		// Forward query parameters to Python service
		const searchParams = url.searchParams;
		const pythonUrl = `${PYTHON_SERVICE_URL}/api/incentives/calculator?${searchParams.toString()}`;

		console.log(`💰 Calculating incentives from: ${pythonUrl}`);

		const response = await fetch(pythonUrl);

		if (!response.ok) {
			const errorData = await response.text();
			console.error('Python service error:', errorData);
			return json({ 
				error: 'Incentive calculator service unavailable', 
				detail: errorData 
			}, { status: response.status });
		}

		const result = await response.json();

		return json(result, {
			headers: {
				'Cache-Control': 'public, max-age=60' // 1 minute cache for calculations
			}
		});

	} catch (error) {
		console.error('❌ Incentive calculator API error:', error);
		return json({ 
			error: 'Internal server error', 
			detail: error instanceof Error ? error.message : 'Unknown error' 
		}, { status: 500 });
	}
};
