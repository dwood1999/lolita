import type { PageServerLoad } from './$types';
import { getCurrentSession } from '$lib/server/auth';
import { redirect } from '@sveltejs/kit';

export const load: PageServerLoad = async ({ params, cookies, fetch }) => {
	// Check authentication
	const session = await getCurrentSession({ cookies } as any);
	if (!session) {
		throw redirect(302, `/auth/login?redirectTo=/screenplays/analysis/${params.id}`);
	}

	// For large analysis data, we'll load it client-side to avoid SSR issues
	// Just return the user session and analysis ID
	return {
		analysisId: params.id,
		user: {
			id: session.user.id,
			email: session.user.email
		}
	};
};
