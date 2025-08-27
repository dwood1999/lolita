<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { parseMarkdown } from '$lib/utils/markdown.js';

	let loading = true;
	let analysis: any = null;
	let error = '';
	let activeTab = 'dashboard';

	const shareToken = $page.params.token;

	onMount(async () => {
		await fetchAnalysis();
	});

	async function fetchAnalysis() {
		try {
			console.log(`🌐 Fetching public analysis with token: ${shareToken?.substring(0, 8)}...`);
			
			const response = await fetch(`/api/public/analysis/${shareToken}`);
			const data = await response.json();

			if (!response.ok) {
				throw new Error(data.error || 'Failed to fetch analysis');
			}

			analysis = data;
			loading = false;
			console.log(`✅ Loaded public analysis: ${analysis.result?.title}`);
		} catch (err) {
			console.error('❌ Error loading public analysis:', err);
			error = err instanceof Error ? err.message : 'Failed to load analysis';
			loading = false;
		}
	}

	// EXACT SAME HELPER FUNCTIONS AS PRIVATE PAGE
	function getScoreColor(score: number): string {
		if (score >= 8.5) return 'text-green-600 bg-green-50';
		if (score >= 7.5) return 'text-green-500 bg-green-50';
		if (score >= 6.5) return 'text-yellow-600 bg-yellow-50';
		if (score >= 5) return 'text-orange-600 bg-orange-50';
		return 'text-red-600 bg-red-50';
	}

	function getRecommendationColor(recommendation: string): string {
		switch (recommendation) {
			case 'Strong Recommend': return 'text-green-600 bg-green-50 border-green-200';
			case 'Recommend': return 'text-green-500 bg-green-50 border-green-200';
			case 'Consider': return 'text-yellow-600 bg-yellow-50 border-yellow-200';
			case 'Pass': return 'text-red-600 bg-red-50 border-red-200';
			default: return 'text-gray-600 bg-gray-50 border-gray-200';
		}
	}

	function formatDate(dateString: string): string {
		if (!dateString) return 'Unknown date';
		const date = new Date(dateString);
		if (isNaN(date.getTime())) return 'Invalid date';
		return date.toLocaleDateString('en-US', {
			year: 'numeric',
			month: 'short',
			day: 'numeric'
		});
	}

	function parseJsonField(field: any): any[] {
		if (!field) return [];
		if (typeof field === 'string') {
			try {
				const parsed = JSON.parse(field);
				return Array.isArray(parsed) ? parsed : [parsed];
			} catch {
				return [field];
			}
		}
		return Array.isArray(field) ? field : [field];
	}
</script>

<svelte:head>
	<title>Public Analysis - {analysis?.result?.title || 'Screenplay'} - Quilty</title>
	<meta name="description" content="Publicly shared screenplay analysis results from Quilty AI-powered analysis platform." />
</svelte:head>

{#if loading}
	<div class="min-h-screen bg-gray-50 flex items-center justify-center">
		<div class="text-center">
			<div class="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto mb-4"></div>
			<h2 class="text-xl font-semibold text-gray-900 mb-2">Loading Public Analysis...</h2>
			<p class="text-gray-600">Please wait while we fetch the shared analysis.</p>
		</div>
	</div>
{:else if error}
	<div class="min-h-screen bg-gray-50 flex items-center justify-center">
		<div class="text-center">
			<div class="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
				<svg class="w-8 h-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
				</svg>
			</div>
			<h2 class="text-xl font-semibold text-gray-900 mb-2">Analysis Not Available</h2>
			<p class="text-gray-600 mb-4">{error}</p>
			<div class="space-x-4">
				<a href="/" class="inline-flex items-center justify-center px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg">
					Go to Quilty
				</a>
				<a href="/auth/register" class="inline-flex items-center justify-center px-4 py-2 bg-white hover:bg-gray-50 text-gray-700 font-semibold rounded-lg border border-gray-300">
					Create Account
				</a>
			</div>
		</div>
	</div>
{:else if analysis}
	<div class="min-h-screen bg-gray-50">
		<!-- Public Share Banner -->
		<div class="bg-blue-50 border-b border-blue-200">
			<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3">
				<div class="flex items-center justify-between">
					<div class="flex items-center">
						<span class="text-blue-600 mr-2">🌐</span>
						<span class="text-sm font-medium text-blue-900">
							This is a publicly shared analysis from Quilty
						</span>
					</div>
					<div class="text-xs text-blue-600">
						Shared on {formatDate(analysis.shared_at)}
					</div>
				</div>
			</div>
		</div>

		<!-- EXACT SAME HEADER AS PRIVATE PAGE -->
		<div class="bg-white border-b border-gray-200">
			<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
				<div class="py-6">
					<div class="flex items-center justify-between">
						<div class="flex-1">
							<h1 class="text-3xl font-bold text-gray-900">{analysis.result.title}</h1>
							<div class="flex items-center space-x-4 mt-2">
								<span class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800">
									{analysis.result.genre}
								</span>
								<span class="text-sm text-gray-500">
									${parseFloat(analysis.result.cost || 0).toFixed(4)} cost
								</span>
								{#if analysis.created_at}
									<span class="text-sm text-gray-500">
										{formatDate(analysis.created_at)}
									</span>
								{/if}
							</div>
						</div>
						<div class="flex items-center space-x-4">
							<!-- Craft Score -->
							<div class="text-center">
								<div class="text-2xl font-bold {getScoreColor(analysis.result.overall_score)} px-3 py-2 rounded-lg">
									{analysis.result.overall_score}/10
								</div>
								<div class="text-xs text-gray-500 mt-1">Craft Score</div>
								<div class="text-xs text-gray-400 mt-1">Story & Structure</div>
								<div class="inline-flex items-center px-2 py-1 rounded text-xs font-medium border {getRecommendationColor(analysis.result.recommendation)} mt-1">
									{analysis.result.recommendation}
								</div>
							</div>
							
							<!-- Reality Score -->
							{#if analysis.result.grok_score}
								<div class="text-center">
									<div class="text-2xl font-bold {getScoreColor(analysis.result.grok_score)} px-3 py-2 rounded-lg">
										{analysis.result.grok_score}/10
									</div>
									<div class="text-xs text-gray-500 mt-1">Reality Score</div>
									<div class="text-xs text-gray-400 mt-1">Brutal Honesty</div>
									<div class="inline-flex items-center px-2 py-1 rounded text-xs font-medium border {getRecommendationColor(analysis.result.grok_recommendation)} mt-1">
										{analysis.result.grok_recommendation}
									</div>
								</div>
							{/if}

							<!-- Financial Score -->
							{#if analysis.result.deepseek_financial_score}
								<div class="text-center">
									<div class="text-2xl font-bold {getScoreColor(analysis.result.deepseek_financial_score)} px-3 py-2 rounded-lg">
										{analysis.result.deepseek_financial_score}/10
									</div>
									<div class="text-xs text-gray-500 mt-1">Financial Score</div>
									<div class="text-xs text-gray-400 mt-1">Investment Analysis</div>
									<div class="inline-flex items-center px-2 py-1 rounded text-xs font-medium border {getRecommendationColor(analysis.result.deepseek_recommendation)} mt-1">
										{analysis.result.deepseek_recommendation || 'Investment Analysis'}
									</div>
								</div>
							{/if}

							<!-- Market Score -->
							{#if analysis.result.perplexity_market_score}
								<div class="text-center">
									<div class="text-2xl font-bold {getScoreColor(analysis.result.perplexity_market_score)} px-3 py-2 rounded-lg">
										{analysis.result.perplexity_market_score}/10
									</div>
									<div class="text-xs text-gray-500 mt-1">Market Score</div>
									<div class="text-xs text-gray-400 mt-1">Commercial Viability</div>
									<div class="inline-flex items-center px-2 py-1 rounded text-xs font-medium border {getRecommendationColor(analysis.result.perplexity_recommendation)} mt-1">
										{analysis.result.perplexity_recommendation || 'Market Analysis'}
									</div>
								</div>
							{/if}
						</div>
					</div>

					<!-- Analysis Verdicts -->
					<div class="mt-6 space-y-4">
						<!-- Craft Analysis Verdict -->
						{#if analysis.result.one_line_verdict}
							<div class="bg-blue-50 border-l-4 border-blue-400 p-4 rounded-md">
								<div class="flex items-start">
									<div class="flex-shrink-0">
										<span class="text-blue-600 font-semibold text-sm">CRAFT ANALYSIS:</span>
									</div>
									<div class="ml-3">
										<p class="text-blue-900 font-medium italic">"{analysis.result.one_line_verdict}"</p>
									</div>
								</div>
							</div>
						{/if}
						
						<!-- Reality Check Verdict -->
						{#if analysis.result.grok_verdict && analysis.result.grok_verdict !== 'Analysis incomplete'}
							<div class="bg-purple-50 border-l-4 border-purple-400 p-4 rounded-md">
								<div class="flex items-start">
									<div class="flex-shrink-0">
										<span class="text-purple-600 font-semibold text-sm">REALITY CHECK:</span>
									</div>
									<div class="ml-3">
										<p class="text-purple-900 font-medium italic">"{analysis.result.grok_verdict}"</p>
									</div>
								</div>
							</div>
						{/if}
						
						<!-- Commercial Analysis Verdict -->
						{#if analysis.result.openai_verdict && analysis.result.openai_verdict !== 'Analysis incomplete' && analysis.result.openai_verdict !== 'Analysis completed'}
							<div class="bg-green-50 border-l-4 border-green-400 p-4 rounded-md">
								<div class="flex items-start">
									<div class="flex-shrink-0">
										<span class="text-green-600 font-semibold text-sm">COMMERCIAL ANALYSIS:</span>
									</div>
									<div class="ml-3">
										<p class="text-green-900 font-medium italic">"{analysis.result.openai_verdict}"</p>
									</div>
								</div>
							</div>
						{/if}
					</div>
				</div>
			</div>
		</div>

		<!-- Navigation Tabs -->
		<div class="bg-white border-b border-gray-200">
			<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
				<nav class="flex space-x-8" aria-label="Tabs">
					<button
						on:click={() => activeTab = 'dashboard'}
						class="whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm transition-colors duration-200 {activeTab === 'dashboard' 
							? 'border-blue-500 text-blue-600' 
							: 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}"
					>
						<span class="mr-2">📈</span>
						Executive Dashboard
					</button>
					{#if analysis.result.structural_analysis || analysis.result.character_analysis}
						<button
							on:click={() => activeTab = 'story'}
							class="whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm transition-colors duration-200 {activeTab === 'story' 
								? 'border-blue-500 text-blue-600' 
								: 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}"
						>
							<span class="mr-2">📖</span>
							Story & Craft
						</button>
					{/if}
					{#if analysis.result.deepseek_financial_score}
						<button
							on:click={() => activeTab = 'financial'}
							class="whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm transition-colors duration-200 {activeTab === 'financial' 
								? 'border-blue-500 text-blue-600' 
								: 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}"
						>
							<span class="mr-2">💰</span>
							Financial Intelligence
						</button>
					{/if}
					{#if analysis.result.gpt5_score || analysis.result.gpt5_executive_assessment}
						<button
							on:click={() => activeTab = 'gpt5'}
							class="whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm transition-colors duration-200 {activeTab === 'gpt5' 
								? 'border-blue-500 text-blue-600' 
								: 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}"
						>
							<span class="mr-2">🧠</span>
							Excellence Analysis
						</button>
					{/if}
					{#if analysis.result.genre || analysis.result.detected_genre || analysis.result.genre_mastery}
						<button
							on:click={() => activeTab = 'genre'}
							class="whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm transition-colors duration-200 {activeTab === 'genre' 
								? 'border-blue-500 text-blue-600' 
								: 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}"
						>
							<span class="mr-2">🎬</span>
							Genre Intelligence
						</button>
					{/if}
					{#if analysis.result.perplexity_market_score || analysis.result.perplexity_market_trends}
						<button
							on:click={() => activeTab = 'market'}
							class="whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm transition-colors duration-200 {activeTab === 'market' 
								? 'border-blue-500 text-blue-600' 
								: 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}"
						>
							<span class="mr-2">📊</span>
							Market Intelligence
						</button>
					{/if}
					{#if analysis.result.improvement_strategies}
						<button
							on:click={() => activeTab = 'improvements'}
							class="whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm transition-colors duration-200 {activeTab === 'improvements' 
								? 'border-blue-500 text-blue-600' 
								: 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}"
						>
							<span class="mr-2">💡</span>
							Enhancement Notes
						</button>
					{/if}
				</nav>
			</div>
		</div>

		<!-- Main Content -->
		<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
			{#if activeTab === 'dashboard'}
				<!-- EXACT SAME DASHBOARD CONTENT AS PRIVATE PAGE -->
				<div class="space-y-8">
					<!-- Executive Summary Grid -->
					<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
						<!-- Executive Summary -->
						{#if analysis.result.executive_summary}
							<div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6 md:col-span-2 lg:col-span-3">
								<h3 class="text-xl font-bold text-gray-900 mb-4 flex items-center">
									<span class="text-blue-600 mr-2">📋</span>
									Executive Summary
								</h3>
								<div class="prose max-w-none">
									<p class="text-gray-700 leading-relaxed">{@html parseMarkdown(analysis.result.executive_summary)}</p>
								</div>
							</div>
						{/if}

						<!-- Logline -->
						{#if analysis.result.logline}
							<div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6 md:col-span-2">
								<h3 class="text-lg font-bold text-gray-900 mb-4 flex items-center">
									<span class="text-purple-600 mr-2">🎬</span>
									Logline
								</h3>
								<div class="prose max-w-none">
									<p class="text-gray-700 italic leading-relaxed">"{@html parseMarkdown(analysis.result.logline)}"</p>
								</div>
							</div>
						{/if}

						<!-- Top Strengths -->
						{#if analysis.result.top_strengths}
							<div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
								<h3 class="text-lg font-bold text-gray-900 mb-4 flex items-center">
									<span class="text-green-600 mr-2">✅</span>
									Top Strengths
								</h3>
								<div class="prose max-w-none">
									<p class="text-gray-700">{@html parseMarkdown(analysis.result.top_strengths)}</p>
								</div>
							</div>
						{/if}

						<!-- Key Weaknesses -->
						{#if analysis.result.key_weaknesses}
							<div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
								<h3 class="text-lg font-bold text-gray-900 mb-4 flex items-center">
									<span class="text-red-600 mr-2">⚠️</span>
									Key Areas for Improvement
								</h3>
								<div class="prose max-w-none">
									<p class="text-gray-700">{@html parseMarkdown(analysis.result.key_weaknesses)}</p>
								</div>
							</div>
						{/if}

						<!-- Commercial Viability -->
						{#if analysis.result.commercial_viability}
							<div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
								<h3 class="text-lg font-bold text-gray-900 mb-4 flex items-center">
									<span class="text-green-600 mr-2">💰</span>
									Commercial Viability
								</h3>
								<div class="prose max-w-none">
									<p class="text-gray-700">{@html parseMarkdown(analysis.result.commercial_viability)}</p>
								</div>
							</div>
						{/if}

						<!-- Target Audience -->
						{#if analysis.result.target_audience}
							<div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
								<h3 class="text-lg font-bold text-gray-900 mb-4 flex items-center">
									<span class="text-pink-600 mr-2">🎯</span>
									Target Audience
								</h3>
								<div class="prose max-w-none text-gray-700">
									{@html parseMarkdown(analysis.result.target_audience)}
								</div>
							</div>
						{/if}
					</div>
				</div>

			{:else if activeTab === 'story'}
				<!-- EXACT SAME STORY CONTENT AS PRIVATE PAGE -->
				<div class="space-y-8">
					<!-- Structural Analysis -->
					<div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
						<h3 class="text-xl font-bold text-gray-900 mb-4 flex items-center">
							<span class="text-blue-600 mr-2">🏗️</span>
							Structural Analysis
						</h3>
						{#if analysis.result.structural_analysis}
							<div class="prose max-w-none text-gray-700">
								{@html parseMarkdown(analysis.result.structural_analysis)}
							</div>
						{:else}
							<p class="text-gray-500 italic">Structural analysis will be available in enhanced results.</p>
						{/if}
					</div>

					<!-- Character Analysis -->
					<div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
						<h3 class="text-xl font-bold text-gray-900 mb-4 flex items-center">
							<span class="text-purple-600 mr-2">👥</span>
							Character Analysis
						</h3>
						{#if analysis.result.character_analysis}
							<div class="prose max-w-none text-gray-700">
								{@html parseMarkdown(analysis.result.character_analysis)}
							</div>
						{:else}
							<p class="text-gray-500 italic">Character analysis will be available in enhanced results.</p>
						{/if}
					</div>

					<!-- Craft Evaluation -->
					<div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
						<h3 class="text-xl font-bold text-gray-900 mb-4 flex items-center">
							<span class="text-green-600 mr-2">✍️</span>
							Craft Evaluation
						</h3>
						{#if analysis.result.craft_evaluation}
							<div class="prose max-w-none text-gray-700">
								{@html parseMarkdown(analysis.result.craft_evaluation)}
							</div>
						{:else}
							<p class="text-gray-500 italic">Craft evaluation will be available in enhanced results.</p>
						{/if}
					</div>

					<!-- Thematic Depth -->
					<div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
						<h3 class="text-xl font-bold text-gray-900 mb-4 flex items-center">
							<span class="text-purple-600 mr-2">🎭</span>
							Thematic Depth
						</h3>
						{#if analysis.result.thematic_depth}
							<div class="prose max-w-none text-gray-700">
								{@html parseMarkdown(analysis.result.thematic_depth)}
							</div>
						{:else}
							<p class="text-gray-500 italic">Thematic analysis will be available in enhanced results.</p>
						{/if}
					</div>
				</div>

			{:else if activeTab === 'financial'}
				<!-- Financial Intelligence Tab -->
				<div class="space-y-8">
					{#if analysis.result.deepseek_financial_score}
						<!-- Header with AI Badge -->
						<div class="bg-gradient-to-r from-emerald-500 via-blue-600 to-purple-600 rounded-xl p-1 shadow-lg">
							<div class="bg-white rounded-lg p-6">
								<div class="flex items-center justify-between">
									<div class="flex items-center space-x-3">
										<span class="text-3xl">💰</span>
										<div>
											<h2 class="text-2xl font-bold text-gray-900">Financial Analysis & Investment Intelligence</h2>
											<p class="text-gray-600">Comprehensive financial modeling powered by DeepSeek AI</p>
										</div>
									</div>
									<div class="flex items-center space-x-2">
										<span class="text-xs bg-gradient-to-r from-blue-100 to-purple-100 text-blue-800 px-3 py-2 rounded-full font-medium">DeepSeek AI</span>
										<span class="text-xs bg-green-100 text-green-800 px-3 py-2 rounded-full font-medium">Real-time Analysis</span>
									</div>
								</div>
							</div>
						</div>

						<!-- Executive Summary -->
						<div class="bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden">
							<div class="bg-gradient-to-r from-green-50 to-blue-50 px-6 py-4 border-b border-gray-200">
								<h3 class="text-xl font-bold text-gray-900 flex items-center">
									<span class="text-green-600 mr-3">📊</span>
									Executive Summary
								</h3>
							</div>
							<div class="p-6">
								<div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
									<!-- Financial Score -->
									<div class="lg:col-span-2">
										<div class="flex items-start space-x-4">
											<div class="flex-shrink-0">
												<div class="w-20 h-20 bg-gradient-to-br from-green-400 to-blue-500 rounded-full flex items-center justify-center">
													<span class="text-white text-2xl font-bold">{analysis.result.deepseek_financial_score}</span>
												</div>
											</div>
											<div class="flex-1">
												<h4 class="text-xl font-semibold text-gray-900 mb-2">Overall Financial Viability</h4>
												<div class="w-full bg-gray-200 rounded-full h-3 mb-3">
													<div class="bg-gradient-to-r from-green-400 to-blue-500 h-3 rounded-full transition-all duration-500" 
														 style="width: {(analysis.result.deepseek_financial_score / 10) * 100}%"></div>
												</div>
												<p class="text-gray-600 text-sm leading-relaxed">
													{analysis.result.deepseek_recommendation || 'Investment analysis complete. This score reflects overall financial viability based on market analysis, risk assessment, and revenue projections.'}
												</p>
											</div>
										</div>
									</div>
									<!-- Quick Stats -->
									<div class="space-y-4">
										{#if analysis.result.deepseek_confidence}
											<div class="bg-gray-50 rounded-lg p-4">
												<div class="text-sm font-medium text-gray-700">Confidence Level</div>
												<div class="text-2xl font-bold text-gray-900">{Math.round(analysis.result.deepseek_confidence * 100)}%</div>
											</div>
										{/if}
										<div class="bg-gray-50 rounded-lg p-4">
											<div class="text-sm font-medium text-gray-700">Analysis Depth</div>
											<div class="text-lg font-semibold text-gray-900">Comprehensive</div>
										</div>
									</div>
								</div>
							</div>
						</div>

						<!-- Budget & ROI Analysis -->
						<div class="bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden">
							<div class="bg-gradient-to-r from-yellow-50 to-orange-50 px-6 py-4 border-b border-gray-200">
								<h3 class="text-xl font-bold text-gray-900 flex items-center">
									<span class="text-yellow-600 mr-3">🎯</span>
									Budget Optimization & ROI Analysis
								</h3>
							</div>
							<div class="p-6 space-y-6">
								<!-- Budget Optimization -->
								{#if analysis.result.deepseek_budget_optimization}
									{@const budget = typeof analysis.result.deepseek_budget_optimization === 'string' 
										? JSON.parse(analysis.result.deepseek_budget_optimization) 
										: analysis.result.deepseek_budget_optimization}
									
									{#if budget && budget.recommended_budget_range}
										<div>
											<h4 class="text-lg font-semibold text-gray-900 mb-4 flex items-center">
												<span class="text-blue-500 mr-2">💰</span>
												Budget Optimization Analysis
											</h4>
											<div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
												<div class="bg-gradient-to-br from-red-50 to-red-100 border border-red-200 rounded-xl p-6 text-center">
													<div class="text-red-800 font-semibold mb-2">Minimum Budget</div>
													<div class="text-2xl font-bold text-red-600 mb-2">
														${budget.recommended_budget_range.minimum?.toLocaleString()}
													</div>
													<div class="text-sm text-red-600">Bare minimum viable</div>
												</div>
												<div class="bg-gradient-to-br from-green-50 to-green-100 border border-green-300 rounded-xl p-6 text-center ring-2 ring-green-300">
													<div class="text-green-800 font-semibold mb-2">Optimal Budget</div>
													<div class="text-2xl font-bold text-green-600 mb-2">
														${budget.recommended_budget_range.optimal?.toLocaleString()}
													</div>
													<div class="text-sm text-green-600">Recommended target</div>
												</div>
												<div class="bg-gradient-to-br from-blue-50 to-blue-100 border border-blue-200 rounded-xl p-6 text-center">
													<div class="text-blue-800 font-semibold mb-2">Maximum Budget</div>
													<div class="text-2xl font-bold text-blue-600 mb-2">
														${budget.recommended_budget_range.maximum?.toLocaleString()}
													</div>
													<div class="text-sm text-blue-600">Upper limit</div>
												</div>
											</div>
										</div>
									{/if}
								{/if}
								
								<!-- ROI Analysis -->
								{#if analysis.result.deepseek_roi_analysis}
									{@const roi = typeof analysis.result.deepseek_roi_analysis === 'string' 
										? JSON.parse(analysis.result.deepseek_roi_analysis) 
										: analysis.result.deepseek_roi_analysis}
									
									{#if roi}
										<div class="mt-6">
											<h4 class="text-lg font-semibold text-gray-900 mb-4 flex items-center">
												<span class="text-green-500 mr-2">📊</span>
												Return on Investment Analysis
											</h4>
											
											<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
												<!-- Break Even Analysis -->
												{#if roi.break_even_point}
													<div class="bg-yellow-50 rounded-xl p-6 border border-yellow-200">
														<h5 class="font-semibold text-yellow-900 mb-3">Break-Even Point</h5>
														<div class="text-2xl font-bold text-yellow-700 mb-2">
															${roi.break_even_point?.toLocaleString()}
														</div>
														{#if roi.break_even_explanation}
															<div class="text-sm text-yellow-800 leading-relaxed">
																{roi.break_even_explanation}
															</div>
														{/if}
													</div>
												{/if}
												
												<!-- ROI Scenarios -->
												{#if roi.roi_scenarios}
													<div class="bg-green-50 rounded-xl p-6 border border-green-200">
														<h5 class="font-semibold text-green-900 mb-3">ROI Scenarios</h5>
														<div class="space-y-3">
															{#each Object.entries(roi.roi_scenarios) as [scenario, value]}
																<div class="flex justify-between items-center">
																	<span class="text-sm font-medium text-green-800 capitalize">{scenario.replace('_', ' ')}</span>
																	<span class="text-sm font-bold text-green-700">{value}%</span>
																</div>
															{/each}
														</div>
													</div>
												{/if}
											</div>
										</div>
									{/if}
								{/if}
								
								<!-- Risk Assessment -->
								{#if analysis.result.deepseek_risk_assessment}
									{@const risk = typeof analysis.result.deepseek_risk_assessment === 'string' 
										? JSON.parse(analysis.result.deepseek_risk_assessment) 
										: analysis.result.deepseek_risk_assessment}
									
									{#if risk}
										<div class="mt-6">
											<h4 class="text-lg font-semibold text-gray-900 mb-4 flex items-center">
												<span class="text-red-500 mr-2">⚠️</span>
												Risk Assessment
											</h4>
											
											<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
												{#if risk.overall_risk_level}
													<div class="bg-red-50 rounded-xl p-6 border border-red-200">
														<h5 class="font-semibold text-red-900 mb-3">Overall Risk Level</h5>
														<div class="text-2xl font-bold text-red-700 mb-2 capitalize">
															{risk.overall_risk_level}
														</div>
														{#if risk.risk_explanation}
															<div class="text-sm text-red-800 leading-relaxed">
																{risk.risk_explanation}
															</div>
														{/if}
													</div>
												{/if}
												
												{#if risk.risk_factors}
													<div class="bg-orange-50 rounded-xl p-6 border border-orange-200">
														<h5 class="font-semibold text-orange-900 mb-3">Key Risk Factors</h5>
														<div class="space-y-2">
															{#each risk.risk_factors as factor}
																<div class="flex items-start space-x-2">
																	<span class="text-orange-600 mt-1">•</span>
																	<span class="text-sm text-orange-800">{factor}</span>
																</div>
															{/each}
														</div>
													</div>
												{/if}
											</div>
										</div>
									{/if}
								{/if}
							</div>
						</div>
					{:else}
						<!-- No Financial Analysis Available -->
						<div class="bg-white rounded-xl shadow-lg border border-gray-200 p-12 text-center">
							<div class="text-gray-400 text-8xl mb-6">💰</div>
							<h3 class="text-2xl font-semibold text-gray-900 mb-4">Financial Analysis Unavailable</h3>
							<p class="text-gray-600 mb-4 max-w-lg mx-auto">DeepSeek financial analysis was not completed for this screenplay.</p>
						</div>
					{/if}
				</div>

			{:else if activeTab === 'market'}
				<!-- Market Intelligence Tab -->
				<div class="space-y-6">
					{#if analysis.result.perplexity_market_score || analysis.result.perplexity_market_trends}
						<!-- Perplexity Market Research -->
						<div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
							<h3 class="text-xl font-bold text-gray-900 mb-6 flex items-center">
								<span class="text-purple-600 mr-2">📊</span>
								Market Intelligence & Industry Analysis
								<span class="ml-2 text-xs bg-purple-100 text-purple-700 px-2 py-1 rounded-full">Perplexity AI</span>
							</h3>
							
							<!-- Market Score Overview -->
							{#if analysis.result.perplexity_market_score}
								<div class="mb-6 p-4 bg-gradient-to-r from-purple-50 to-indigo-50 rounded-lg border border-purple-200">
									<div class="flex items-center justify-between">
										<div>
											<h4 class="text-lg font-semibold text-gray-900 mb-2">Market Opportunity Assessment</h4>
											<p class="text-gray-600">{analysis.result.perplexity_recommendation || 'Market research complete'}</p>
										</div>
										<div class="text-center">
											<div class="text-3xl font-bold text-purple-600">
												{analysis.result.perplexity_market_score}/10
											</div>
											<div class="text-sm text-gray-500">Market Score</div>
										</div>
									</div>
								</div>
							{/if}
							
							<!-- Market Trends -->
							{#if analysis.result.perplexity_market_trends}
								{@const trends = typeof analysis.result.perplexity_market_trends === 'string' 
									? JSON.parse(analysis.result.perplexity_market_trends) 
									: analysis.result.perplexity_market_trends}
								
								{#if trends && trends.content}
									<div class="mb-6">
										<h4 class="text-lg font-semibold text-gray-900 mb-4">Current Market Trends</h4>
										<div class="bg-purple-50 border border-purple-200 rounded-lg p-4">
											<div class="prose prose-sm max-w-none text-gray-700">
												{@html parseMarkdown(trends.content)}
											</div>
										</div>
									</div>
								{/if}
							{/if}
							
							<!-- Competitive Analysis -->
							{#if analysis.result.perplexity_competitive_analysis}
								{@const competitive = typeof analysis.result.perplexity_competitive_analysis === 'string' 
									? JSON.parse(analysis.result.perplexity_competitive_analysis) 
									: analysis.result.perplexity_competitive_analysis}
								
								{#if competitive && competitive.content}
									<div class="mb-6">
										<h4 class="text-lg font-semibold text-gray-900 mb-4">Competitive Landscape</h4>
										<div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
											<div class="prose prose-sm max-w-none text-gray-700">
												{@html parseMarkdown(competitive.content)}
											</div>
										</div>
									</div>
								{/if}
							{/if}
							
							<!-- Audience Demographics -->
							{#if analysis.result.perplexity_audience_demographics}
								{@const demographics = typeof analysis.result.perplexity_audience_demographics === 'string' 
									? JSON.parse(analysis.result.perplexity_audience_demographics) 
									: analysis.result.perplexity_audience_demographics}
								
								{#if demographics && demographics.content}
									<div class="mb-6">
										<h4 class="text-lg font-semibold text-gray-900 mb-4">Audience Demographics</h4>
										<div class="bg-teal-50 border border-teal-200 rounded-lg p-4">
											<div class="prose prose-sm max-w-none text-gray-700">
												{@html parseMarkdown(demographics.content)}
											</div>
										</div>
									</div>
								{/if}
							{/if}
							
							<!-- Distribution Strategy -->
							{#if analysis.result.perplexity_distribution_strategy}
								{@const distribution = typeof analysis.result.perplexity_distribution_strategy === 'string' 
									? JSON.parse(analysis.result.perplexity_distribution_strategy) 
									: analysis.result.perplexity_distribution_strategy}
								
								{#if distribution && distribution.content}
									<div class="mb-6">
										<h4 class="text-lg font-semibold text-gray-900 mb-4">Distribution Strategy</h4>
										<div class="bg-green-50 border border-green-200 rounded-lg p-4">
											<div class="prose prose-sm max-w-none text-gray-700">
												{@html parseMarkdown(distribution.content)}
											</div>
										</div>
									</div>
								{/if}
							{/if}
							
							<!-- Financial Intelligence -->
							{#if analysis.result.perplexity_financial_intelligence}
								{@const financial = typeof analysis.result.perplexity_financial_intelligence === 'string' 
									? JSON.parse(analysis.result.perplexity_financial_intelligence) 
									: analysis.result.perplexity_financial_intelligence}
								
								{#if financial && financial.content}
									<div class="mb-6">
										<h4 class="text-lg font-semibold text-gray-900 mb-4">Financial Intelligence</h4>
										<div class="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
											<div class="prose prose-sm max-w-none text-gray-700">
												{@html parseMarkdown(financial.content)}
											</div>
										</div>
									</div>
								{/if}
							{/if}
							
							<!-- Talent Intelligence -->
							{#if analysis.result.perplexity_talent_intelligence}
								{@const talent = typeof analysis.result.perplexity_talent_intelligence === 'string' 
									? JSON.parse(analysis.result.perplexity_talent_intelligence) 
									: analysis.result.perplexity_talent_intelligence}
								
								{#if talent && talent.content}
									<div class="mb-6">
										<h4 class="text-lg font-semibold text-gray-900 mb-4">Talent Intelligence</h4>
										<div class="bg-pink-50 border border-pink-200 rounded-lg p-4">
											<div class="prose prose-sm max-w-none text-gray-700">
												{@html parseMarkdown(talent.content)}
											</div>
										</div>
									</div>
								{/if}
							{/if}

							<!-- Data Freshness -->
							{#if analysis.result.perplexity_data_freshness}
								<div class="mt-4 p-3 bg-gray-50 rounded-lg">
									<div class="flex items-center justify-between">
										<span class="text-sm font-medium text-gray-700">Data Freshness</span>
										<span class="text-sm text-gray-600">{analysis.result.perplexity_data_freshness}</span>
									</div>
								</div>
							{/if}
						</div>
					{:else}
						<!-- No Market Intelligence Available -->
						<div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6 text-center">
							<div class="text-gray-400 text-6xl mb-4">📊</div>
							<h3 class="text-xl font-semibold text-gray-900 mb-2">Market Intelligence Unavailable</h3>
							<p class="text-gray-600 mb-4">Perplexity market research was not completed for this screenplay.</p>
							<p class="text-sm text-gray-500">This may be due to analysis failure or the feature not being available when this analysis was run.</p>
						</div>
					{/if}
				</div>

			{:else if activeTab === 'gpt5'}
				<!-- GPT-5 Excellence Analysis Tab -->
				<div class="space-y-8">
					{#if analysis.result.gpt5_score || analysis.result.gpt5_executive_assessment}
						<!-- Header with AI Badge -->
						<div class="bg-gradient-to-r from-blue-500 via-purple-600 to-indigo-600 rounded-xl p-1 shadow-lg">
							<div class="bg-white rounded-lg p-6">
								<div class="flex items-center justify-between">
									<div class="flex items-center space-x-3">
										<span class="text-3xl">🧠</span>
										<div>
											<h2 class="text-2xl font-bold text-gray-900">GPT-5 Writing Excellence Analysis</h2>
											<p class="text-gray-600">Advanced craft evaluation powered by GPT-5</p>
										</div>
									</div>
									<div class="flex items-center space-x-2">
										<span class="text-xs bg-gradient-to-r from-blue-100 to-purple-100 text-blue-800 px-3 py-2 rounded-full font-medium">GPT-5</span>
										<span class="text-xs bg-green-100 text-green-800 px-3 py-2 rounded-full font-medium">Writing Craft</span>
									</div>
								</div>
							</div>
						</div>

						<!-- Executive Summary -->
						{#if analysis.result.gpt5_score}
							<div class="bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden">
								<div class="bg-gradient-to-r from-blue-50 to-purple-50 px-6 py-4 border-b border-gray-200">
									<h3 class="text-xl font-bold text-gray-900 flex items-center">
										<span class="text-blue-600 mr-3">📊</span>
										Writing Excellence Score
									</h3>
								</div>
								<div class="p-6">
									<div class="flex items-center space-x-6">
										<div class="flex-shrink-0">
											<div class="w-24 h-24 bg-gradient-to-br from-blue-400 to-purple-500 rounded-full flex items-center justify-center">
												<span class="text-white text-3xl font-bold">{analysis.result.gpt5_score}</span>
											</div>
										</div>
										<div class="flex-1">
											<h4 class="text-xl font-semibold text-gray-900 mb-2">Overall Writing Quality</h4>
											<div class="w-full bg-gray-200 rounded-full h-3 mb-3">
												<div class="bg-gradient-to-r from-blue-400 to-purple-500 h-3 rounded-full transition-all duration-500" 
													 style="width: {(analysis.result.gpt5_score / 10) * 100}%"></div>
											</div>
											<p class="text-gray-600 text-sm leading-relaxed">
												{analysis.result.gpt5_recommendation || 'Professional writing craft assessment complete.'}
											</p>
										</div>
									</div>
								</div>
							</div>
						{/if}

						<!-- Detailed Assessment -->
						{#if analysis.result.gpt5_executive_assessment}
							{@const gpt5Assessment = typeof analysis.result.gpt5_executive_assessment === 'string' 
								? JSON.parse(analysis.result.gpt5_executive_assessment) 
								: analysis.result.gpt5_executive_assessment}
							
							{#if gpt5Assessment}
								<div class="bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden">
									<div class="bg-gradient-to-r from-purple-50 to-indigo-50 px-6 py-4 border-b border-gray-200">
										<h3 class="text-xl font-bold text-gray-900 flex items-center">
											<span class="text-purple-600 mr-3">🎭</span>
											Professional Assessment
										</h3>
									</div>
									<div class="p-6 space-y-6">
										<!-- Professional Verdict -->
										{#if gpt5Assessment.professional_verdict}
											<div class="bg-blue-50 border-l-4 border-blue-400 p-6 rounded-r-lg">
												<h4 class="text-lg font-semibold text-blue-900 mb-3 flex items-center">
													<span class="text-blue-600 mr-2">⭐</span>
													Professional Verdict
												</h4>
												<p class="text-blue-800 font-medium text-lg italic leading-relaxed">
													"{gpt5Assessment.professional_verdict}"
												</p>
											</div>
										{/if}

										<!-- Quick Impressions -->
										{#if gpt5Assessment.quick_impressions}
											<div class="bg-green-50 border border-green-200 rounded-lg p-6">
												<h4 class="text-lg font-semibold text-green-900 mb-3 flex items-center">
													<span class="text-green-600 mr-2">👁️</span>
													First Impressions
												</h4>
												<div class="prose prose-sm max-w-none text-green-800 leading-relaxed">
													{@html parseMarkdown(gpt5Assessment.quick_impressions)}
												</div>
											</div>
										{/if}

										<!-- Deep Analysis -->
										{#if gpt5Assessment.deep_analysis}
											<div class="bg-purple-50 border border-purple-200 rounded-lg p-6">
												<h4 class="text-lg font-semibold text-purple-900 mb-3 flex items-center">
													<span class="text-purple-600 mr-2">🔍</span>
													Deep Craft Analysis
												</h4>
												<div class="prose prose-sm max-w-none text-purple-800 leading-relaxed">
													{@html parseMarkdown(gpt5Assessment.deep_analysis)}
												</div>
											</div>
										{/if}
									</div>
								</div>
							{/if}
						{/if}
					{:else}
						<!-- No GPT-5 Analysis Available -->
						<div class="bg-white rounded-xl shadow-lg border border-gray-200 p-12 text-center">
							<div class="text-gray-400 text-8xl mb-6">🧠</div>
							<h3 class="text-2xl font-semibold text-gray-900 mb-4">GPT-5 Analysis Unavailable</h3>
							<p class="text-gray-600 mb-4 max-w-lg mx-auto">GPT-5 Writing Excellence analysis was not completed for this screenplay.</p>
						</div>
					{/if}
				</div>

			{:else if activeTab === 'genre'}
				<!-- Genre Intelligence Tab -->
				<div class="space-y-8">
					{#if analysis.result.genre || analysis.result.detected_genre || analysis.result.genre_mastery}
						<!-- Header with AI Badge -->
						<div class="bg-gradient-to-r from-red-500 via-pink-600 to-purple-600 rounded-xl p-1 shadow-lg">
							<div class="bg-white rounded-lg p-6">
								<div class="flex items-center justify-between">
									<div class="flex items-center space-x-3">
										<span class="text-3xl">🎬</span>
										<div>
											<h2 class="text-2xl font-bold text-gray-900">Genre Intelligence & Conventions</h2>
											<p class="text-gray-600">Genre mastery analysis and market expectations</p>
										</div>
									</div>
									<div class="flex items-center space-x-2">
										<span class="text-xs bg-gradient-to-r from-red-100 to-pink-100 text-red-800 px-3 py-2 rounded-full font-medium">Genre AI</span>
										<span class="text-xs bg-green-100 text-green-800 px-3 py-2 rounded-full font-medium">Market Analysis</span>
									</div>
								</div>
							</div>
						</div>

						<!-- Genre Classification -->
						<div class="bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden">
							<div class="bg-gradient-to-r from-red-50 to-pink-50 px-6 py-4 border-b border-gray-200">
								<h3 class="text-xl font-bold text-gray-900 flex items-center">
									<span class="text-red-600 mr-3">🏷️</span>
									Genre Classification
								</h3>
							</div>
							<div class="p-6">
								<div class="grid grid-cols-1 md:grid-cols-3 gap-6">
									<!-- Primary Genre -->
									<div class="text-center">
										<div class="w-20 h-20 bg-gradient-to-br from-red-400 to-pink-500 rounded-full flex items-center justify-center mx-auto mb-3">
											<span class="text-white text-2xl font-bold">🎬</span>
										</div>
										<h4 class="text-lg font-semibold text-gray-900 mb-2">Primary Genre</h4>
										<span class="inline-flex items-center px-4 py-2 rounded-full text-lg font-medium bg-red-100 text-red-800">
											{analysis.result.genre || analysis.result.detected_genre || 'Not specified'}
										</span>
									</div>
									
									<!-- Subgenre -->
									{#if analysis.result.subgenre}
										<div class="text-center">
											<div class="w-20 h-20 bg-gradient-to-br from-blue-400 to-indigo-500 rounded-full flex items-center justify-center mx-auto mb-3">
												<span class="text-white text-2xl font-bold">🎭</span>
											</div>
											<h4 class="text-lg font-semibold text-gray-900 mb-2">Subgenre</h4>
											<span class="inline-flex items-center px-4 py-2 rounded-full text-lg font-medium bg-blue-100 text-blue-800">
												{analysis.result.subgenre}
											</span>
										</div>
									{/if}
									
									<!-- AI Detection -->
									{#if analysis.result.detected_genre}
										<div class="text-center">
											<div class="w-20 h-20 bg-gradient-to-br from-purple-400 to-indigo-500 rounded-full flex items-center justify-center mx-auto mb-3">
												<span class="text-white text-2xl font-bold">🤖</span>
											</div>
											<h4 class="text-lg font-semibold text-gray-900 mb-2">AI Detection</h4>
											<span class="inline-flex items-center px-4 py-2 rounded-full text-lg font-medium bg-purple-100 text-purple-800">
												{analysis.result.detected_genre}
											</span>
											{#if analysis.result.detected_genre !== analysis.result.genre}
												<p class="text-sm text-purple-600 mt-2">Differs from declared genre</p>
											{:else}
												<p class="text-sm text-green-600 mt-2">Matches declared genre</p>
											{/if}
										</div>
									{/if}
								</div>
							</div>
						</div>

						<!-- Genre Mastery Analysis -->
						{#if analysis.result.genre_mastery}
							<div class="bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden">
								<div class="bg-gradient-to-r from-purple-50 to-indigo-50 px-6 py-4 border-b border-gray-200">
									<h3 class="text-xl font-bold text-gray-900 flex items-center">
										<span class="text-purple-600 mr-3">🎭</span>
										Genre Mastery & Conventions
									</h3>
								</div>
								<div class="p-6">
									<div class="prose prose-lg max-w-none text-gray-700 leading-relaxed">
										{@html parseMarkdown(analysis.result.genre_mastery)}
									</div>
								</div>
							</div>
						{/if}
					{:else}
						<!-- No Genre Analysis Available -->
						<div class="bg-white rounded-xl shadow-lg border border-gray-200 p-12 text-center">
							<div class="text-gray-400 text-8xl mb-6">🎬</div>
							<h3 class="text-2xl font-semibold text-gray-900 mb-4">Genre Analysis Unavailable</h3>
							<p class="text-gray-600 mb-4 max-w-lg mx-auto">Genre classification and mastery analysis was not completed for this screenplay.</p>
						</div>
					{/if}
				</div>

			{:else if activeTab === 'improvements'}
				<!-- Enhancement Notes Tab -->
				<div class="space-y-8">
					{#if analysis.result.improvement_strategies}
						<!-- Header with AI Badge -->
						<div class="bg-gradient-to-r from-yellow-500 via-orange-600 to-red-600 rounded-xl p-1 shadow-lg">
							<div class="bg-white rounded-lg p-6">
								<div class="flex items-center justify-between">
									<div class="flex items-center space-x-3">
										<span class="text-3xl">💡</span>
										<div>
											<h2 class="text-2xl font-bold text-gray-900">Enhancement Notes & Recommendations</h2>
											<p class="text-gray-600">Structured improvement strategies for your screenplay</p>
										</div>
									</div>
									<div class="flex items-center space-x-2">
										<span class="text-xs bg-gradient-to-r from-yellow-100 to-orange-100 text-yellow-800 px-3 py-2 rounded-full font-medium">Enhancement AI</span>
										<span class="text-xs bg-green-100 text-green-800 px-3 py-2 rounded-full font-medium">Actionable</span>
									</div>
								</div>
							</div>
						</div>

						<!-- Improvement Strategies -->
						<div class="bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden">
							<div class="bg-gradient-to-r from-yellow-50 to-orange-50 px-6 py-4 border-b border-gray-200">
								<h3 class="text-xl font-bold text-gray-900 flex items-center">
									<span class="text-yellow-600 mr-3">🎯</span>
									Prioritized Improvement Strategies
								</h3>
							</div>
							<div class="p-6">
								{#if analysis.result.improvement_strategies}
									{@const strategies = typeof analysis.result.improvement_strategies === 'string' ? JSON.parse(analysis.result.improvement_strategies) : analysis.result.improvement_strategies}
									{#if Array.isArray(strategies) && strategies.length > 0}
										<div class="space-y-6">
											{#each strategies as strategy, index}
												<div class="bg-gradient-to-r from-yellow-50 to-orange-50 border border-yellow-200 rounded-lg p-6">
													<div class="flex items-start space-x-4">
														<div class="flex-shrink-0">
															<div class="w-12 h-12 bg-gradient-to-br from-yellow-400 to-orange-500 rounded-full flex items-center justify-center">
																<span class="text-white text-lg font-bold">{index + 1}</span>
															</div>
														</div>
														<div class="flex-1">
															<div class="prose prose-sm max-w-none text-gray-800 leading-relaxed">
																{@html parseMarkdown(strategy)}
															</div>
														</div>
														<div class="flex-shrink-0">
															{@const priority = index < 3 ? 'High' : index < 6 ? 'Medium' : 'Low'}
															{@const priorityColor = priority === 'High' ? 'bg-red-100 text-red-800' : priority === 'Medium' ? 'bg-yellow-100 text-yellow-800' : 'bg-green-100 text-green-800'}
															<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium {priorityColor}">
																{priority} Priority
															</span>
														</div>
													</div>
												</div>
											{/each}
										</div>
									{:else}
										<div class="text-center py-8">
											<div class="text-gray-400 text-6xl mb-4">💡</div>
											<p class="text-gray-500">No specific improvement strategies available.</p>
										</div>
									{/if}
								{:else}
									<div class="text-center py-8">
										<div class="text-gray-400 text-6xl mb-4">💡</div>
										<p class="text-gray-500">No improvement strategies data available.</p>
									</div>
								{/if}
							</div>
						</div>
					{:else}
						<!-- No Enhancement Notes Available -->
						<div class="bg-white rounded-xl shadow-lg border border-gray-200 p-12 text-center">
							<div class="text-gray-400 text-8xl mb-6">💡</div>
							<h3 class="text-2xl font-semibold text-gray-900 mb-4">Enhancement Notes Unavailable</h3>
							<p class="text-gray-600 mb-4 max-w-lg mx-auto">Structured improvement recommendations were not generated for this screenplay.</p>
						</div>
					{/if}
				</div>
			{/if}
		</div>
	</div>
{:else}
	<div class="min-h-screen bg-gray-50 flex items-center justify-center">
		<div class="text-center">
			<h2 class="text-xl font-semibold text-gray-900 mb-2">No Analysis Data</h2>
			<p class="text-gray-600">Unable to load analysis information.</p>
		</div>
	</div>
{/if}