<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';

	let user: { id: string; email: string } | null = null;
	let screenplays: any[] = [];
	let loading = true;
	let error = '';

	onMount(async () => {
		try {
			const response = await fetch('/api/auth/me');
			const data = await response.json();
			
			if (data.success) {
				user = data.user;
				await loadScreenplays();
			} else {
				// Not authenticated, redirect to login
				goto('/auth/login?redirectTo=/screenplays');
			}
		} catch (error) {
			console.error('Failed to fetch user:', error);
			goto('/auth/login?redirectTo=/screenplays');
		} finally {
			loading = false;
		}
	});

	async function loadScreenplays() {
		try {
			// Load directly from database instead of hitting Python service
			const response = await fetch('/api/screenplays/analyses');
			const data = await response.json();
			
			if (response.ok) {
				screenplays = data.analyses || [];
				console.log(`✅ Loaded ${screenplays.length} analyses from database`);
			} else {
				console.error('Database load failed:', data.error);
				error = data.error || 'Failed to load analyses';
			}
		} catch (err) {
			console.error('Network error loading screenplays:', err);
			error = 'Network error. Please try again.';
		}
	}

	function formatFileSize(bytes: number): string {
		if (bytes === 0) return '0 Bytes';
		const k = 1024;
		const sizes = ['Bytes', 'KB', 'MB', 'GB'];
		const i = Math.floor(Math.log(bytes) / Math.log(k));
		return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
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
			case 'processing': return 'bg-yellow-100 text-yellow-800';
			case 'pending': return 'bg-blue-100 text-blue-800';
			case 'error': return 'bg-red-100 text-red-800';
			default: return 'bg-gray-100 text-gray-800';
		}
	}

	function getStatusText(status: string): string {
		switch (status) {
			case 'completed': return 'Complete';
			case 'processing': return 'Analyzing';
			case 'pending': return 'Pending';
			case 'error': return 'Failed';
			default: return 'Unknown';
		}
	}
</script>

<svelte:head>
	<title>Screenplays - Screenplay Evaluation Tool</title>
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
					Screenplay Analyses
				</h2>
				<p class="mt-1 text-sm text-gray-500">
					View your Claude Opus 4.1 analysis results and cost tracking
				</p>
			</div>
			<div class="mt-4 flex md:mt-0 md:ml-4">
				<a
					href="/screenplays/upload"
					class="btn-primary"
				>
					Analyze New Screenplay
				</a>
			</div>
		</div>

		{#if error}
			<div class="mt-8 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
				{error}
			</div>
		{/if}

		<!-- Screenplays list -->
		<div class="mt-8">
			{#if screenplays.length === 0}
				<div class="card">
					<div class="text-center py-12">
						<svg class="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
						</svg>
						<h3 class="mt-2 text-sm font-medium text-gray-900">No analyses yet</h3>
						<p class="mt-1 text-sm text-gray-500">Get started by uploading your first screenplay for Claude Opus 4.1 analysis.</p>
						<div class="mt-6">
							<a
								href="/screenplays/upload"
								class="btn-primary"
							>
								Analyze Your First Screenplay
							</a>
						</div>
					</div>
				</div>
			{:else}
				<div class="card">
					<div class="px-4 py-5 sm:p-6">
						<div class="space-y-6">
							{#each screenplays as analysis}
								<div class="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
									<div class="flex items-center space-x-4">
										<div class="flex-shrink-0">
											<div class="w-12 h-12 bg-blue-600 rounded-lg flex items-center justify-center">
												<svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
													<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
												</svg>
											</div>
										</div>
										<div class="min-w-0 flex-1">
											<p class="text-sm font-medium text-gray-900 truncate">
												{analysis.title}
											</p>
											<p class="text-sm text-gray-500">
												{analysis.genre || 'Unknown Genre'} • {analysis.ai_model || 'Claude 3.5 Sonnet'}
											</p>
											<div class="flex items-center space-x-4 mt-1">
												{#if analysis.overall_score}
													<span class="text-xs font-medium {analysis.overall_score >= 7 ? 'text-green-600' : analysis.overall_score >= 5 ? 'text-yellow-600' : 'text-red-600'}">
														⭐ {analysis.overall_score}/10
													</span>
												{/if}
												{#if analysis.cost}
													<span class="text-xs text-gray-500">
														💰 ${analysis.cost.toFixed(4)}
													</span>
												{/if}
												<span class="text-xs text-gray-400">
													{formatDate(analysis.created_at)}
												</span>
											</div>
										</div>
									</div>
									<div class="flex items-center space-x-4">
										<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium {getStatusColor(analysis.status)}">
											{getStatusText(analysis.status)}
										</span>
										{#if analysis.status === 'completed'}
											<a
												href="/screenplays/analysis/{analysis.id}"
												class="btn-primary text-sm"
											>
												View Analysis
											</a>
										{:else if analysis.status === 'processing'}
											<a
												href="/screenplays/analysis/{analysis.id}"
												class="btn-secondary text-sm"
											>
												Check Status
											</a>
										{:else}
											<button class="btn-secondary text-sm opacity-50 cursor-not-allowed">
												Failed
											</button>
										{/if}
									</div>
								</div>
							{/each}
						</div>
					</div>
				</div>
			{/if}
		</div>
	</div>
{/if}
