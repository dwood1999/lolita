<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';

	let user: { id: string; email: string } | null = null;
	let stats: any = null;
	let loading = true;
	let error = '';

	onMount(async () => {
		try {
			const response = await fetch('/api/auth/me');
			const data = await response.json();
			
			if (data.success) {
				user = data.user;
				await loadStats();
			} else {
				// Not authenticated, redirect to login
				goto('/auth/login?redirectTo=/dashboard');
			}
		} catch (error) {
			console.error('Failed to fetch user:', error);
			goto('/auth/login?redirectTo=/dashboard');
		} finally {
			loading = false;
		}
	});

	async function loadStats() {
		try {
			const response = await fetch('/api/dashboard/stats');
			const data = await response.json();
			
			if (data.success) {
				stats = data.stats;
			} else {
				error = data.error || 'Failed to load dashboard data';
			}
		} catch (err) {
			error = 'Network error. Please try again.';
		}
	}

	function formatDate(dateString: string): string {
		return new Date(dateString).toLocaleDateString('en-US', {
			year: 'numeric',
			month: 'short',
			day: 'numeric'
		});
	}

	function getStatusColor(status: string): string {
		switch (status) {
			case 'completed': return 'bg-green-100 text-green-800';
			case 'analyzing': return 'bg-yellow-100 text-yellow-800';
			case 'error': return 'bg-red-100 text-red-800';
			default: return 'bg-gray-100 text-gray-800';
		}
	}

	function getStatusText(status: string): string {
		switch (status) {
			case 'completed': return 'Analysis Complete';
			case 'processing': return 'Analyzing';
			case 'pending': return 'Pending';
			case 'error': return 'Error';
			default: return 'Draft';
		}
	}

	function getScoreColor(score: number): string {
		if (score >= 8.5) return 'bg-green-100 text-green-800';
		if (score >= 7.5) return 'bg-green-50 text-green-700';
		if (score >= 6.5) return 'bg-yellow-100 text-yellow-800';
		if (score >= 5) return 'bg-orange-100 text-orange-800';
		return 'bg-red-100 text-red-800';
	}

	function getRecommendationColor(recommendation: string): string {
		switch (recommendation) {
			case 'Strong Recommend': return 'bg-green-100 text-green-800';
			case 'Recommend': return 'bg-green-50 text-green-700';
			case 'Consider': return 'bg-yellow-100 text-yellow-800';
			case 'Pass': return 'bg-red-100 text-red-800';
			default: return 'bg-gray-100 text-gray-800';
		}
	}
</script>

<svelte:head>
	<title>Dashboard - Quilty</title>
</svelte:head>

{#if loading}
	<div class="flex items-center justify-center min-h-screen">
		<div class="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
	</div>
{:else if user}
	<div class="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
		<!-- Page header -->
		<div class="md:flex md:items-center md:justify-between">
			<div class="flex-1 min-w-0">
				<h2 class="text-2xl font-bold leading-7 text-gray-900 sm:text-3xl sm:truncate">
					Welcome back, {user.email.split('@')[0]}!
				</h2>
				<p class="mt-1 text-sm text-gray-500">
					Ready to analyze your next screenplay?
				</p>
			</div>
			<div class="mt-4 flex md:mt-0 md:ml-4">
				<a
					href="/screenplays/upload"
					class="btn-primary"
				>
					Upload Screenplay
				</a>
			</div>
		</div>

		<!-- Stats -->
		<div class="mt-8">
			<div class="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
				<!-- Total Screenplays -->
				<div class="card">
					<div class="flex items-center">
						<div class="flex-shrink-0">
							<div class="w-8 h-8 bg-blue-500 rounded-md flex items-center justify-center">
								<svg class="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 20 20">
									<path fill-rule="evenodd" d="M4 4a2 2 0 00-2 2v8a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2H4zm2 6a1 1 0 011-1h6a1 1 0 110 2H7a1 1 0 01-1-1zm1 3a1 1 0 100 2h6a1 1 0 100-2H7z" clip-rule="evenodd" />
								</svg>
							</div>
						</div>
						<div class="ml-5 w-0 flex-1">
							<dl>
								<dt class="text-sm font-medium text-gray-500 truncate">
									Total Screenplays
								</dt>
								<dd class="text-lg font-medium text-gray-900">
									{stats?.totalScreenplays || 0}
								</dd>
							</dl>
						</div>
					</div>
				</div>

				<!-- Completed Analyses -->
				<div class="card">
					<div class="flex items-center">
						<div class="flex-shrink-0">
							<div class="w-8 h-8 bg-green-500 rounded-md flex items-center justify-center">
								<svg class="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 20 20">
									<path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
								</svg>
							</div>
						</div>
						<div class="ml-5 w-0 flex-1">
							<dl>
								<dt class="text-sm font-medium text-gray-500 truncate">
									Completed Analyses
								</dt>
								<dd class="text-lg font-medium text-gray-900">
									{stats?.completedAnalyses || 0}
								</dd>
							</dl>
						</div>
					</div>
				</div>

				<!-- In Progress -->
				<div class="card">
					<div class="flex items-center">
						<div class="flex-shrink-0">
							<div class="w-8 h-8 bg-yellow-500 rounded-md flex items-center justify-center">
								<svg class="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 20 20">
									<path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clip-rule="evenodd" />
								</svg>
							</div>
						</div>
						<div class="ml-5 w-0 flex-1">
							<dl>
								<dt class="text-sm font-medium text-gray-500 truncate">
									In Progress
								</dt>
								<dd class="text-lg font-medium text-gray-900">
									{stats?.inProgress || 0}
								</dd>
							</dl>
						</div>
					</div>
				</div>
			</div>
		</div>

		<!-- Quick Actions -->
		<div class="mt-8">
			<h3 class="text-lg leading-6 font-medium text-gray-900 mb-4">Quick Actions</h3>
			<div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
				<a
					href="/screenplays/upload"
					class="relative group bg-white p-6 focus-within:ring-2 focus-within:ring-inset focus-within:ring-blue-500 rounded-lg shadow hover:shadow-md transition-shadow"
				>
					<div>
						<span class="rounded-lg inline-flex p-3 bg-blue-50 text-blue-700 ring-4 ring-white">
							<svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
							</svg>
						</span>
					</div>
					<div class="mt-8">
						<h3 class="text-lg font-medium">
							<span class="absolute inset-0" aria-hidden="true"></span>
							Upload New Screenplay
						</h3>
						<p class="mt-2 text-sm text-gray-500">
							Upload a new screenplay for professional analysis and feedback.
						</p>
					</div>
					<span class="pointer-events-none absolute top-6 right-6 text-gray-300 group-hover:text-gray-400" aria-hidden="true">
						<svg class="h-6 w-6" fill="currentColor" viewBox="0 0 24 24">
							<path d="M20 4h1a1 1 0 00-1-1v1zm-1 12a1 1 0 102 0h-2zM8 3a1 1 0 000 2V3zM3.293 19.293a1 1 0 101.414 1.414l-1.414-1.414zM19 4v12h2V4h-2zm1-1H8v2h12V3zm-.707.293l-16 16 1.414 1.414 16-16-1.414-1.414z"/>
						</svg>
					</span>
				</a>

				<a
					href="/screenplays"
					class="relative group bg-white p-6 focus-within:ring-2 focus-within:ring-inset focus-within:ring-blue-500 rounded-lg shadow hover:shadow-md transition-shadow"
				>
					<div>
						<span class="rounded-lg inline-flex p-3 bg-green-50 text-green-700 ring-4 ring-white">
							<svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
							</svg>
						</span>
					</div>
					<div class="mt-8">
						<h3 class="text-lg font-medium">
							<span class="absolute inset-0" aria-hidden="true"></span>
							View All Screenplays
						</h3>
						<p class="mt-2 text-sm text-gray-500">
							Browse and manage all your uploaded screenplays and their analyses.
						</p>
					</div>
					<span class="pointer-events-none absolute top-6 right-6 text-gray-300 group-hover:text-gray-400" aria-hidden="true">
						<svg class="h-6 w-6" fill="currentColor" viewBox="0 0 24 24">
							<path d="M20 4h1a1 1 0 00-1-1v1zm-1 12a1 1 0 102 0h-2zM8 3a1 1 0 000 2V3zM3.293 19.293a1 1 0 101.414 1.414l-1.414-1.414zM19 4v12h2V4h-2zm1-1H8v2h12V3zm-.707.293l-16 16 1.414 1.414 16-16-1.414-1.414z"/>
						</svg>
					</span>
				</a>

				<a
					href="/profile"
					class="relative group bg-white p-6 focus-within:ring-2 focus-within:ring-inset focus-within:ring-blue-500 rounded-lg shadow hover:shadow-md transition-shadow"
				>
					<div>
						<span class="rounded-lg inline-flex p-3 bg-purple-50 text-purple-700 ring-4 ring-white">
							<svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
							</svg>
						</span>
					</div>
					<div class="mt-8">
						<h3 class="text-lg font-medium">
							<span class="absolute inset-0" aria-hidden="true"></span>
							Profile Settings
						</h3>
						<p class="mt-2 text-sm text-gray-500">
							Manage your account settings and preferences.
						</p>
					</div>
					<span class="pointer-events-none absolute top-6 right-6 text-gray-300 group-hover:text-gray-400" aria-hidden="true">
						<svg class="h-6 w-6" fill="currentColor" viewBox="0 0 24 24">
							<path d="M20 4h1a1 1 0 00-1-1v1zm-1 12a1 1 0 102 0h-2zM8 3a1 1 0 000 2V3zM3.293 19.293a1 1 0 101.414 1.414l-1.414-1.414zM19 4v12h2V4h-2zm1-1H8v2h12V3zm-.707.293l-16 16 1.414 1.414 16-16-1.414-1.414z"/>
						</svg>
					</span>
				</a>
			</div>
		</div>

		{#if error}
			<div class="mt-8 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
				{error}
			</div>
		{/if}

		<!-- Recent Activity -->
		<div class="mt-8">
			<h3 class="text-lg leading-6 font-medium text-gray-900 mb-4">Recent Activity</h3>
			<div class="card">
				{#if stats?.recentScreenplays && stats.recentScreenplays.length > 0}
					<div class="px-6 py-4">
						<div class="space-y-4">
							{#each stats.recentScreenplays as screenplay}
								<div class="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
									<div class="flex items-center space-x-4">
										<div class="flex-shrink-0">
											{#if screenplay.status === 'completed' && screenplay.score}
												<div class="w-12 h-12 rounded-full flex items-center justify-center text-sm font-bold {getScoreColor(screenplay.score)}">
													{screenplay.score}
												</div>
											{:else}
												<svg class="h-10 w-10 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
													<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
												</svg>
											{/if}
										</div>
										<div class="flex-1">
											<p class="text-sm font-medium text-gray-900">{screenplay.title}</p>
											<div class="flex items-center space-x-2 mt-1">
												<p class="text-xs text-gray-500">Updated {formatDate(screenplay.updatedAt)}</p>
												{#if screenplay.recommendation}
													<span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium {getRecommendationColor(screenplay.recommendation)}">
														{screenplay.recommendation}
													</span>
												{/if}
											</div>
										</div>
									</div>
									<div class="flex items-center space-x-3">
										<span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium {getStatusColor(screenplay.status)}">
											{getStatusText(screenplay.status)}
										</span>
										{#if screenplay.status === 'completed'}
											<a
												href="/screenplays/analysis/{screenplay.id}"
												class="text-blue-600 hover:text-blue-800 text-sm font-medium"
											>
												View Analysis
											</a>
										{:else}
											<a
												href="/screenplays/{screenplay.id}"
												class="text-blue-600 hover:text-blue-800 text-sm font-medium"
											>
												View
											</a>
										{/if}
									</div>
								</div>
							{/each}
						</div>
					</div>
				{:else}
					<div class="text-center py-12">
						<svg class="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
						</svg>
						<h3 class="mt-2 text-sm font-medium text-gray-900">No screenplays yet</h3>
						<p class="mt-1 text-sm text-gray-500">Get started by uploading your first screenplay.</p>
						<div class="mt-6">
							<a
								href="/screenplays/upload"
								class="btn-primary"
							>
								Upload Screenplay
							</a>
						</div>
					</div>
				{/if}
			</div>
		</div>
	</div>
{/if}
