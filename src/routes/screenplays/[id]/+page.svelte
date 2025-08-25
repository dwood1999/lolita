<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { page } from '$app/stores';

	let user: { id: string; email: string } | null = null;
	let screenplay: any = null;
	let loading = true;
	let error = '';
	let editing = false;
	let editTitle = '';
	let analyzing = false;

	$: screenplayId = $page.params.id;

	onMount(async () => {
		try {
			const response = await fetch('/api/auth/me');
			const data = await response.json();
			
			if (data.success) {
				user = data.user;
				await loadScreenplay();
			} else {
				goto('/auth/login?redirectTo=' + encodeURIComponent($page.url.pathname));
			}
		} catch (error) {
			console.error('Failed to fetch user:', error);
			goto('/auth/login?redirectTo=' + encodeURIComponent($page.url.pathname));
		} finally {
			loading = false;
		}
	});

	async function loadScreenplay() {
		try {
			const response = await fetch(`/api/screenplays/${screenplayId}`);
			const data = await response.json();
			
			if (data.success) {
				screenplay = data.screenplay;
				editTitle = screenplay.title;
			} else {
				error = data.error || 'Failed to load screenplay';
			}
		} catch (err) {
			error = 'Network error. Please try again.';
		}
	}

	async function updateScreenplay() {
		if (!editTitle.trim()) {
			error = 'Title cannot be empty';
			return;
		}

		try {
			const response = await fetch(`/api/screenplays/${screenplayId}`, {
				method: 'PUT',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({
					title: editTitle.trim(),
					status: screenplay.status
				})
			});

			const data = await response.json();

			if (data.success) {
				screenplay.title = editTitle.trim();
				editing = false;
				error = '';
			} else {
				error = data.error || 'Failed to update screenplay';
			}
		} catch (err) {
			error = 'Network error. Please try again.';
		}
	}

	async function deleteScreenplay() {
		if (!confirm('Are you sure you want to delete this screenplay? This action cannot be undone.')) {
			return;
		}

		try {
			const response = await fetch(`/api/screenplays/${screenplayId}`, {
				method: 'DELETE'
			});

			const data = await response.json();

			if (data.success) {
				goto('/screenplays');
			} else {
				error = data.error || 'Failed to delete screenplay';
			}
		} catch (err) {
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
		if (!dateString) {
			return 'Unknown date';
		}
		
		const date = new Date(dateString);
		
		// Check if date is valid
		if (isNaN(date.getTime())) {
			return 'Invalid date';
		}
		
		return date.toLocaleDateString('en-US', {
			year: 'numeric',
			month: 'long',
			day: 'numeric',
			hour: '2-digit',
			minute: '2-digit'
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
			case 'analyzing': return 'Analyzing';
			case 'error': return 'Error';
			default: return 'Draft';
		}
	}

	async function startAnalysis() {
		if (analyzing) return;

		analyzing = true;
		error = '';

		try {
			const response = await fetch(`/api/screenplays/${screenplayId}/analyze`, {
				method: 'POST'
			});

			const data = await response.json();

			if (data.success) {
				screenplay.status = 'completed';
				// Reload screenplay to get updated data
				await loadScreenplay();
			} else {
				error = data.error || 'Analysis failed';
				screenplay.status = 'error';
			}
		} catch (err) {
			error = 'Network error. Please try again.';
			screenplay.status = 'error';
		} finally {
			analyzing = false;
		}
	}
</script>

<svelte:head>
	<title>{screenplay?.title || 'Loading...'} - Quilty</title>
</svelte:head>

{#if loading}
	<div class="flex items-center justify-center min-h-screen">
		<div class="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
	</div>
{:else if user && screenplay}
	<div class="max-w-4xl mx-auto py-6 sm:px-6 lg:px-8">
		<!-- Header -->
		<div class="mb-8">
			<nav class="flex" aria-label="Breadcrumb">
				<ol class="flex items-center space-x-4">
					<li>
						<a href="/screenplays" class="text-gray-500 hover:text-gray-700">
							Screenplays
						</a>
					</li>
					<li>
						<svg class="flex-shrink-0 h-5 w-5 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
							<path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd" />
						</svg>
					</li>
					<li>
						<span class="text-gray-500">{screenplay.title}</span>
					</li>
				</ol>
			</nav>
		</div>

		{#if error}
			<div class="mb-6 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
				{error}
			</div>
		{/if}

		<!-- Screenplay Info -->
		<div class="card mb-8">
			<div class="px-6 py-4 border-b border-gray-200">
				<div class="flex items-center justify-between">
					<div class="flex items-center space-x-3">
						{#if editing}
							<input
								type="text"
								bind:value={editTitle}
								class="text-2xl font-bold text-gray-900 border-none p-0 focus:ring-0"
								on:keydown={(e) => e.key === 'Enter' && updateScreenplay()}
							/>
						{:else}
							<h1 class="text-2xl font-bold text-gray-900">{screenplay.title}</h1>
						{/if}
						<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium {getStatusColor(screenplay.status)}">
							{getStatusText(screenplay.status)}
						</span>
					</div>
					<div class="flex items-center space-x-2">
						{#if editing}
							<button
								on:click={updateScreenplay}
								class="btn-primary text-sm"
							>
								Save
							</button>
							<button
								on:click={() => { editing = false; editTitle = screenplay.title; }}
								class="btn-secondary text-sm"
							>
								Cancel
							</button>
						{:else}
							<button
								on:click={() => editing = true}
								class="btn-secondary text-sm"
							>
								Edit
							</button>
							<button
								on:click={deleteScreenplay}
								class="btn-danger text-sm"
							>
								Delete
							</button>
						{/if}
					</div>
				</div>
			</div>
			
			<div class="px-6 py-4">
				<dl class="grid grid-cols-1 gap-x-4 gap-y-6 sm:grid-cols-2">
					<div>
						<dt class="text-sm font-medium text-gray-500">Original Filename</dt>
						<dd class="mt-1 text-sm text-gray-900">{screenplay.originalName}</dd>
					</div>
					<div>
						<dt class="text-sm font-medium text-gray-500">File Size</dt>
						<dd class="mt-1 text-sm text-gray-900">{formatFileSize(screenplay.size)}</dd>
					</div>
					<div>
						<dt class="text-sm font-medium text-gray-500">Uploaded</dt>
						<dd class="mt-1 text-sm text-gray-900">{formatDate(screenplay.createdAt)}</dd>
					</div>
					<div>
						<dt class="text-sm font-medium text-gray-500">Last Updated</dt>
						<dd class="mt-1 text-sm text-gray-900">{formatDate(screenplay.updatedAt)}</dd>
					</div>
				</dl>
			</div>
		</div>

		<!-- Actions -->
		<div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 mb-8">
			<button
				class="relative group bg-white p-6 focus-within:ring-2 focus-within:ring-inset focus-within:ring-blue-500 rounded-lg shadow hover:shadow-md transition-shadow"
				disabled
			>
				<div>
					<span class="rounded-lg inline-flex p-3 bg-blue-50 text-blue-700 ring-4 ring-white">
						<svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
						</svg>
					</span>
				</div>
				<div class="mt-8">
					<h3 class="text-lg font-medium text-gray-900">
						{#if analyzing}
							Analyzing...
						{:else if screenplay.status === 'completed'}
							Analysis Complete
						{:else if screenplay.status === 'analyzing'}
							Analysis in Progress
						{:else}
							Start Analysis
						{/if}
					</h3>
					<p class="mt-2 text-sm text-gray-500">
						{#if analyzing}
							Please wait while we analyze your screenplay
						{:else if screenplay.status === 'completed'}
							View your comprehensive screenplay analysis below
						{:else if screenplay.status === 'analyzing'}
							Analysis is currently in progress
						{:else}
							Begin comprehensive screenplay analysis
						{/if}
					</p>
				</div>
			</button>

			<button
				class="relative group bg-white p-6 focus-within:ring-2 focus-within:ring-inset focus-within:ring-blue-500 rounded-lg shadow hover:shadow-md transition-shadow"
				disabled
			>
				<div>
					<span class="rounded-lg inline-flex p-3 bg-green-50 text-green-700 ring-4 ring-white">
						<svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
						</svg>
					</span>
				</div>
				<div class="mt-8">
					<h3 class="text-lg font-medium text-gray-900">
						View Content
					</h3>
					<p class="mt-2 text-sm text-gray-500">
						Read screenplay content (Coming Soon)
					</p>
				</div>
			</button>

			<button
				class="relative group bg-white p-6 focus-within:ring-2 focus-within:ring-inset focus-within:ring-blue-500 rounded-lg shadow hover:shadow-md transition-shadow"
				disabled
			>
				<div>
					<span class="rounded-lg inline-flex p-3 bg-purple-50 text-purple-700 ring-4 ring-white">
						<svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
						</svg>
					</span>
				</div>
				<div class="mt-8">
					<h3 class="text-lg font-medium text-gray-900">
						Download Report
					</h3>
					<p class="mt-2 text-sm text-gray-500">
						Export analysis report (Coming Soon)
					</p>
				</div>
			</button>
		</div>

		<!-- Analysis Results Placeholder -->
		<div class="card">
			<div class="px-6 py-4 border-b border-gray-200">
				<h2 class="text-lg font-medium text-gray-900">Analysis Results</h2>
			</div>
			<div class="px-6 py-8">
				<div class="text-center">
					<svg class="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
					</svg>
					<h3 class="mt-2 text-sm font-medium text-gray-900">No analysis yet</h3>
					<p class="mt-1 text-sm text-gray-500">
						Start an analysis to see detailed feedback on your screenplay.
					</p>
					<div class="mt-6">
						<button
							class="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
							disabled={screenplay.status === 'analyzing' || screenplay.status === 'completed' || analyzing}
							on:click={startAnalysis}
						>
							{#if analyzing}
								<svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
									<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
									<path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
								</svg>
								Analyzing...
							{:else if screenplay.status === 'completed'}
								Analysis Complete
							{:else if screenplay.status === 'analyzing'}
								Analysis in Progress
							{:else}
								Start Analysis
							{/if}
						</button>
					</div>
				</div>
			</div>
		</div>
	</div>
{:else}
	<div class="flex items-center justify-center min-h-screen">
		<div class="text-center">
			<h2 class="text-2xl font-bold text-gray-900">Screenplay not found</h2>
			<p class="mt-2 text-gray-600">The screenplay you're looking for doesn't exist or you don't have access to it.</p>
			<div class="mt-6">
				<a href="/screenplays" class="btn-primary">
					Back to Screenplays
				</a>
			</div>
		</div>
	</div>
{/if}
