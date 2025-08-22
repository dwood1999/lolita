import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { env } from '$env/dynamic/private';

const PYTHON_SERVICE_URL = env.PYTHON_SERVICE_URL || 'http://127.0.0.1:8001';

export const POST: RequestHandler = async ({ request, locals }) => {
	try {
		// Check if user is authenticated
		if (!locals.user) {
			return json({ error: 'Authentication required' }, { status: 401 });
		}

		const formData = await request.formData();
		const file = formData.get('file') as File;
		const title = formData.get('title') as string;
		const genre = formData.get('genre') as string;
        const budgetEstimate = formData.get('budget_estimate') as string | null;

		if (!file) {
			return json({ error: 'No file provided' }, { status: 400 });
		}

		if (!title) {
			return json({ error: 'Title is required' }, { status: 400 });
		}

		// Validate budget if provided
		if (budgetEstimate) {
			const budget = parseFloat(budgetEstimate);
			if (isNaN(budget) || budget < 0) {
				return json({ error: 'Budget must be a positive number' }, { status: 400 });
			}
			if (budget > 1_000_000_000) {
				return json({ error: 'Budget cannot exceed $1 billion' }, { status: 400 });
			}
			if (budget > 0 && budget < 1000) {
				return json({ error: 'Budget must be at least $1,000 for professional analysis' }, { status: 400 });
			}
		}

		console.log(`🎬 Starting screenplay analysis: ${title} (user: ${locals.user.id})`);

		// Create FormData for Python service
		const pythonFormData = new FormData();
		pythonFormData.append('file', file);
		pythonFormData.append('title', title);
		pythonFormData.append('genre', genre || '');
		pythonFormData.append('user_id', locals.user.id);
        if (budgetEstimate && budgetEstimate.trim() !== '') {
            pythonFormData.append('budget_estimate', budgetEstimate);
        }

		// Forward to Python service
		const response = await fetch(`${PYTHON_SERVICE_URL}/analyze/pdf`, {
			method: 'POST',
			body: pythonFormData
		});

		if (!response.ok) {
			const errorData = await response.text();
			console.error('Python service error:', errorData);
			return json({ 
				error: 'Analysis service unavailable', 
				detail: errorData 
			}, { status: response.status });
		}

		const result = await response.json();
		console.log('✅ Analysis started:', result.analysis_id);

		return json(result);

	} catch (error) {
		console.error('❌ Analysis API error:', error);
		return json({ 
			error: 'Internal server error', 
			detail: error instanceof Error ? error.message : 'Unknown error' 
		}, { status: 500 });
	}
};
