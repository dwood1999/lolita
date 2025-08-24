import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';

const PYTHON_SERVICE_URL = 'http://127.0.0.1:8001';

export const GET: RequestHandler = async ({ url }) => {
	try {
		const searchParams = url.searchParams;
		const queryString = searchParams.toString();
		
		const response = await fetch(`${PYTHON_SERVICE_URL}/api/grants/eligibility${queryString ? `?${queryString}` : ''}`);
		const data = await response.json();
		
		if (!response.ok) {
			throw new Error(data.detail || 'Failed to check grant eligibility');
		}
		
		return json(data);
	} catch (error) {
		console.error('Grant eligibility API error:', error);
		return json(
			{ 
				success: false, 
				error: 'Failed to check grant eligibility',
				detail: error instanceof Error ? error.message : 'Unknown error'
			}, 
			{ status: 500 }
		);
	}
};
