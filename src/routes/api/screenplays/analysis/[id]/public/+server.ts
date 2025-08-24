import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { executeQuery } from '$lib/server/db';
import crypto from 'crypto';

export const PATCH: RequestHandler = async ({ params, request, locals }) => {
	try {
		// Check if user is authenticated
		if (!locals.user) {
			return json({ error: 'Authentication required' }, { status: 401 });
		}

		const { id } = params;
		const { is_public } = await request.json();

		if (!id) {
			return json({ error: 'Analysis ID is required' }, { status: 400 });
		}

		console.log(`🔄 Updating public status for analysis: ${id} (user: ${locals.user.id}) to ${is_public}`);

		// Verify user owns this analysis
		const ownershipCheck = await executeQuery(`
			SELECT user_id FROM screenplay_analyses 
			WHERE id = ?
		`, [id]) as any[];

		if (ownershipCheck.length === 0) {
			return json({ error: 'Analysis not found' }, { status: 404 });
		}

		if (ownershipCheck[0].user_id !== locals.user.id) {
			return json({ error: 'Access denied' }, { status: 403 });
		}

		// Generate or clear public share token
		let public_share_token = null;
		let shared_at = null;

		if (is_public) {
			// Generate a secure random token for public sharing
			public_share_token = crypto.randomBytes(32).toString('hex');
			shared_at = new Date().toISOString();
		}

		// Update the analysis public status
		await executeQuery(`
			UPDATE screenplay_analyses 
			SET is_public = ?, 
				public_share_token = ?, 
				shared_at = ?
			WHERE id = ? AND user_id = ?
		`, [is_public, public_share_token, shared_at, id, locals.user.id]);

		console.log(`✅ Updated analysis ${id} public status to ${is_public}`);

		return json({ 
			success: true, 
			is_public,
			public_share_token: is_public ? public_share_token : null,
			message: is_public ? 'Analysis is now publicly sharable' : 'Analysis is now private'
		});

	} catch (error) {
		console.error('❌ Update public status API error:', error);
		return json({ 
			error: 'Internal server error', 
			detail: error instanceof Error ? error.message : 'Unknown error' 
		}, { status: 500 });
	}
};
