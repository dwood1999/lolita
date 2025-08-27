import type { PageServerLoad } from './$types';
import { getCurrentSession } from '$lib/server/auth';
import { redirect } from '@sveltejs/kit';

export const load: PageServerLoad = async ({ params, cookies, fetch }) => {
	// Check authentication
	const session = await getCurrentSession({ cookies } as any);
	if (!session) {
		throw redirect(302, `/auth/login?redirectTo=/screenplays/analysis/${params.id}`);
	}

	try {
		// Fetch analysis data server-side
		const response = await fetch(`/api/screenplays/analysis/${params.id}`);
		
		if (!response.ok) {
			if (response.status === 404) {
				throw redirect(302, '/screenplays');
			}
			throw new Error('Failed to load analysis');
		}

		const analysis = await response.json();
		
		return {
			analysis,
			user: {
				id: session.user.id,
				email: session.user.email
			}
		};
	} catch (error) {
		console.error('Error loading analysis:', error);
		throw redirect(302, '/screenplays');
	}
};
