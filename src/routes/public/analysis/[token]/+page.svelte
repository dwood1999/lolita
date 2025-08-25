<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/stores';

	let loading = true;
	let analysis: any = null;
	let error = '';
	let activeTab = 'dashboard';

	const shareToken = $page.params.token;

	// Complete navigation tabs (matching private analysis)
	const allTabs = [
		{ id: 'dashboard', label: 'Executive Dashboard', icon: '📈' },
		{ id: 'story', label: 'Story & Craft', icon: '📖' },
		{ id: 'financial', label: 'Financial Intelligence', icon: '💰' },
		{ id: 'grok', label: 'Reality Check', icon: '🔍' },
		{ id: 'gpt5', label: 'Excellence Analysis', icon: '🧠' },
		{ id: 'genre', label: 'Genre Intelligence', icon: '🎬' },
		{ id: 'market', label: 'Market Intelligence', icon: '📊' },
		{ id: 'producer', label: 'Producer Dashboard', icon: '🎬' },
		{ id: 'production', label: 'Production Planning', icon: '🎭' },
		{ id: 'media', label: 'Media Assets', icon: '🎨' },
		{ id: 'casting', label: 'Casting Vision', icon: '🎭' },
		{ id: 'improvements', label: 'Enhancement Notes', icon: '💡' }
	];

	onMount(async () => {
		await fetchAnalysis();
	});

	async function fetchAnalysis() {
		try {
			const response = await fetch(`/api/public/analysis/${shareToken}`);
			const data = await response.json();

			if (!response.ok) {
				throw new Error(data.error || 'Failed to fetch analysis');
			}

			analysis = data;
			loading = false;
		} catch (err) {
			error = err instanceof Error ? err.message : 'Failed to load analysis';
			loading = false;
		}
	}

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

	function switchTab(tabId: string) {
		activeTab = tabId;
	}

	// Parse JSON field helper (same as original page)
	function parseJsonField(field: any): any[] {
		if (Array.isArray(field)) return field;
		if (typeof field === 'string') {
			try {
				return JSON.parse(field);
			} catch {
				return [];
			}
		}
		return [];
	}

	// Parse Grok analysis data (same as original page)
	function getCultural(): any {
		const v = analysis?.result?.grok_cultural_analysis;
		if (!v) return {};
		if (typeof v === 'string') {
			try {
				const parsed = JSON.parse(v);
				return parsed.cultural_reality_check || {};
			} catch {
				return {};
			}
		}
		return v.cultural_reality_check || {};
	}

	function getBrutal(): any {
		const v = analysis?.result?.grok_brutal_honesty;
		if (!v) return {};
		if (typeof v === 'string') {
			try {
				return JSON.parse(v);
			} catch {
				return {};
			}
		}
		return v;
	}

	// GPT-5 Helper Functions (same as original page)
	function getGPT5CharacterVoice(): any {
		const v = analysis?.result?.gpt5_character_voice_analysis;
		if (!v) return null;
		let parsed = v;
		if (typeof v === 'string') {
			try {
				parsed = JSON.parse(v);
			} catch {
				return null;
			}
		}
		
		// Return structured character voice data
		return {
			voice_distinction_score: parsed.voice_distinction_score || 0,
			authenticity_rating: parsed.authenticity_rating || 'Not available',
			voice_consistency: parsed.voice_consistency || 'Not available',
			distinctiveness: parsed.distinctiveness || '',
			character_examples: parsed.character_voice_examples || [],
			dialogue_issues: parsed.interchangeable_dialogue_issues || []
		};
	}

	function getGPT5DialogueAuth(): any {
		const v = analysis?.result?.gpt5_dialogue_authenticity;
		if (!v) return null;
		let parsed = v;
		if (typeof v === 'string') {
			try {
				parsed = JSON.parse(v);
			} catch {
				return null;
			}
		}
		
		// Return structured dialogue authenticity data
		return {
			naturalism_score: parsed.naturalism_score || 0,
			exposition_handling: parsed.exposition_handling || 'Not available',
			subtext_quality: parsed.subtext_quality || 'Not available',
			speech_pattern_authenticity: parsed.speech_pattern_authenticity || 'Not available',
			on_the_nose_examples: parsed.on_the_nose_examples || []
		};
	}

	function getGPT5ProseQuality(): any {
		const v = analysis?.result?.gpt5_prose_quality;
		if (!v) return null;
		let parsed = v;
		if (typeof v === 'string') {
			try {
				parsed = JSON.parse(v);
			} catch {
				return null;
			}
		}
		
		// Return structured prose quality data
		return {
			visual_storytelling_score: parsed.visual_storytelling_score || 0,
			action_line_efficiency: parsed.action_line_efficiency || 'Not available',
			cinematic_language: parsed.cinematic_language || 'Not available',
			show_vs_tell_balance: parsed.show_vs_tell_balance || 'Not available'
		};
	}

	// Helper function to check if we have DeepSeek financial data
	function hasDeepSeekData(): boolean {
		return !!(analysis?.result?.deepseek_financial_score || analysis?.result?.deepseek_box_office_prediction);
	}

	// Helper function to check if we have Perplexity market data
	function hasPerplexityData(): boolean {
		return !!(analysis?.result?.perplexity_market_score || analysis?.result?.perplexity_market_trends);
	}

	// Helper function to get controversy analysis
	function getControversy(): any {
		const v = analysis?.result?.grok_controversy_analysis;
		if (!v) return {};
		if (typeof v === 'string') {
			try {
				return JSON.parse(v);
			} catch {
				return {};
			}
		}
		return v;
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
						Shared on {new Date(analysis.shared_at).toLocaleDateString()}
					</div>
				</div>
			</div>
		</div>

		<!-- Header Section -->
		<div class="bg-white border-b border-gray-200">
			<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
				<div class="flex items-center justify-between">
					<div class="flex-1">
						<h1 class="text-3xl font-bold text-gray-900 mb-2">
							{analysis.result.title || 'Screenplay Analysis'}
						</h1>
						<p class="text-gray-600">Professional AI-Powered Analysis</p>
					</div>
					<div class="flex items-center space-x-4">
						<!-- Craft Score -->
						<div class="text-center">
							<div class="text-2xl font-bold text-blue-600 bg-blue-50 px-3 py-2 rounded-lg">
								{analysis.result.overall_score}/10
							</div>
							<div class="text-xs text-gray-500 mt-1">Craft Score</div>
							<div class="inline-flex items-center px-2 py-1 rounded text-xs font-medium border text-green-600 bg-green-50 border-green-200 mt-1">
								{analysis.result.recommendation}
							</div>
						</div>
						
						<!-- Reality Score -->
						{#if analysis.result.grok_score}
							<div class="text-center">
								<div class="text-2xl font-bold text-purple-600 bg-purple-50 px-3 py-2 rounded-lg">
									{analysis.result.grok_score}/10
								</div>
								<div class="text-xs text-gray-500 mt-1">Reality Score</div>
								<div class="inline-flex items-center px-2 py-1 rounded text-xs font-medium border text-purple-600 bg-purple-50 border-purple-200 mt-1">
									{analysis.result.grok_recommendation}
								</div>
							</div>
						{/if}

						<!-- Financial Score -->
						{#if analysis.result.deepseek_financial_score}
							<div class="text-center">
								<div class="text-2xl font-bold text-green-600 bg-green-50 px-3 py-2 rounded-lg">
									{analysis.result.deepseek_financial_score}/10
								</div>
								<div class="text-xs text-gray-500 mt-1">Financial Score</div>
								<div class="inline-flex items-center px-2 py-1 rounded text-xs font-medium border text-green-600 bg-green-50 border-green-200 mt-1">
									{analysis.result.deepseek_recommendation || 'Investment Analysis'}
								</div>
							</div>
						{/if}

						<!-- Market Score -->
						{#if analysis.result.perplexity_market_score}
							<div class="text-center">
								<div class="text-2xl font-bold text-indigo-600 bg-indigo-50 px-3 py-2 rounded-lg">
									{analysis.result.perplexity_market_score}/10
								</div>
								<div class="text-xs text-gray-500 mt-1">Market Score</div>
								<div class="inline-flex items-center px-2 py-1 rounded text-xs font-medium border text-indigo-600 bg-indigo-50 border-indigo-200 mt-1">
									{analysis.result.perplexity_recommendation || 'Market Research'}
								</div>
							</div>
						{/if}

						<!-- OpenAI Score -->
						{#if analysis.result.openai_score}
							<div class="text-center">
								<div class="text-2xl font-bold text-orange-600 bg-orange-50 px-3 py-2 rounded-lg">
									{analysis.result.openai_score}/10
								</div>
								<div class="text-xs text-gray-500 mt-1">Commercial Score</div>
								<div class="inline-flex items-center px-2 py-1 rounded text-xs font-medium border text-orange-600 bg-orange-50 border-orange-200 mt-1">
									{analysis.result.openai_recommendation || 'Commercial Analysis'}
								</div>
							</div>
						{/if}
					</div>
				</div>
			</div>
		</div>

		<!-- Horizontal Navigation -->
		<div class="bg-white border-b border-gray-200 sticky top-0 z-10">
			<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
				<div class="flex space-x-1 overflow-x-auto py-4">
					{#each allTabs as tab}
						{@const isActive = activeTab === tab.id}
						{@const score = tab.id === 'dashboard' ? analysis.result.overall_score : 
										tab.id === 'grok' ? analysis.result.grok_score :
										tab.id === 'gpt5' ? analysis.result.gpt5_score :
										tab.id === 'financial' ? analysis.result.deepseek_financial_score :
										tab.id === 'market' ? analysis.result.perplexity_market_score : null}
						
						<button
							on:click={() => switchTab(tab.id)}
							class="flex-shrink-0 px-4 py-2 text-sm font-medium rounded-lg transition-colors {
								isActive 
									? 'bg-blue-100 text-blue-700 border border-blue-200' 
									: 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
							}"
						>
							<div class="flex items-center space-x-2">
								<span>{tab.icon}</span>
								<span class="hidden sm:inline">{tab.label}</span>
								{#if score !== null}
									<span class="text-xs font-bold px-1.5 py-0.5 rounded-full bg-blue-100 text-blue-700">{score}</span>
								{/if}
							</div>
						</button>
					{/each}
				</div>
			</div>
		</div>

		<!-- Main Content - Tab-Based Navigation -->
		<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
			<!-- Dashboard Tab -->
			{#if activeTab === 'dashboard'}
				<div class="space-y-8">
					<!-- Analysis Verdicts -->
					<div class="space-y-4">
						{#if analysis.result.one_line_verdict}
							<div class="bg-blue-50 border-l-4 border-blue-400 p-4 rounded-md">
								<div class="flex items-start">
									<div class="flex-shrink-0">
										<span class="text-blue-600 font-semibold text-sm">PROFESSIONAL VERDICT:</span>
									</div>
									<div class="ml-3">
										<p class="text-blue-900 font-medium italic">"{analysis.result.one_line_verdict}"</p>
									</div>
								</div>
							</div>
						{/if}

						{#if analysis.result.grok_verdict}
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

						{#if analysis.result.openai_verdict}
							<div class="bg-green-50 border-l-4 border-green-400 p-4 rounded-md">
								<div class="flex items-start">
									<div class="flex-shrink-0">
										<span class="text-green-600 font-semibold text-sm">COMMERCIAL ASSESSMENT:</span>
									</div>
									<div class="ml-3">
										<p class="text-green-900 font-medium italic">"{analysis.result.openai_verdict}"</p>
									</div>
								</div>
							</div>
						{/if}
					</div>

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
									<p class="text-gray-700 leading-relaxed">{analysis.result.executive_summary}</p>
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
									<p class="text-gray-700 italic leading-relaxed">"{analysis.result.logline}"</p>
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
									<p class="text-gray-700">{analysis.result.top_strengths}</p>
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
									<p class="text-gray-700">{analysis.result.key_weaknesses}</p>
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
									<p class="text-gray-700">{analysis.result.commercial_viability}</p>
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
								<div class="prose max-w-none">
									<p class="text-gray-700">{analysis.result.target_audience}</p>
								</div>
							</div>
						{/if}
					</div>
				</div>

			<!-- Story & Craft Tab -->
			{:else if activeTab === 'story'}
				<div class="space-y-8">
					<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
						<!-- Character Analysis -->
						{#if analysis.result.character_analysis}
							<div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
								<h3 class="text-lg font-bold text-gray-900 mb-4 flex items-center">
									<span class="text-indigo-600 mr-2">👥</span>
									Character Analysis
								</h3>
								<div class="prose max-w-none">
									<p class="text-gray-700">{analysis.result.character_analysis}</p>
								</div>
							</div>
						{/if}

						<!-- Structural Analysis -->
						{#if analysis.result.structural_analysis}
							<div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
								<h3 class="text-lg font-bold text-gray-900 mb-4 flex items-center">
									<span class="text-orange-600 mr-2">🏗️</span>
									Structural Analysis
								</h3>
								<div class="prose max-w-none">
									<p class="text-gray-700">{analysis.result.structural_analysis}</p>
								</div>
							</div>
						{/if}

						<!-- Thematic Depth -->
						{#if analysis.result.thematic_depth}
							<div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
								<h3 class="text-lg font-bold text-gray-900 mb-4 flex items-center">
									<span class="text-purple-600 mr-2">🎭</span>
									Thematic Depth
								</h3>
								<div class="prose max-w-none">
									<p class="text-gray-700">{analysis.result.thematic_depth}</p>
								</div>
							</div>
						{/if}

						<!-- Craft Evaluation -->
						{#if analysis.result.craft_evaluation}
							<div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
								<h3 class="text-lg font-bold text-gray-900 mb-4 flex items-center">
									<span class="text-blue-600 mr-2">✍️</span>
									Craft Evaluation
								</h3>
								<div class="prose max-w-none">
									<p class="text-gray-700">{analysis.result.craft_evaluation}</p>
								</div>
							</div>
						{/if}

						<!-- Improvement Strategies -->
						{#if analysis.result.improvement_strategies}
							<div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
								<h3 class="text-lg font-bold text-gray-900 mb-4 flex items-center">
									<span class="text-yellow-600 mr-2">💡</span>
									Improvement Strategies
								</h3>
								<div class="prose max-w-none">
									<p class="text-gray-700">{analysis.result.improvement_strategies}</p>
								</div>
							</div>
						{/if}

						<!-- Suggestions -->
						{#if analysis.result.suggestions}
							<div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
								<h3 class="text-lg font-bold text-gray-900 mb-4 flex items-center">
									<span class="text-yellow-600 mr-2">💡</span>
									Suggestions
								</h3>
								<div class="prose max-w-none">
									<p class="text-gray-700">{analysis.result.suggestions}</p>
								</div>
							</div>
						{/if}
					</div>
				</div>

			<!-- Financial Intelligence Tab -->
			{:else if activeTab === 'financial'}
				<div class="space-y-8">
					{#if hasDeepSeekData()}
						<!-- Header with AI Badge -->
						<div class="bg-gradient-to-r from-emerald-500 via-blue-600 to-purple-600 rounded-xl p-1 shadow-lg">
							<div class="bg-white rounded-lg p-6">
								<div class="flex items-center justify-between">
									<div class="flex items-center">
										<div class="w-12 h-12 bg-gradient-to-br from-emerald-400 to-blue-500 rounded-full flex items-center justify-center mr-4">
											<span class="text-white text-xl">🤖</span>
										</div>
										<div>
											<h2 class="text-2xl font-bold text-gray-900">DeepSeek Financial Intelligence</h2>
											<p class="text-gray-600">AI-Powered Investment & ROI Analysis</p>
										</div>
									</div>
									<div class="text-xs bg-gradient-to-r from-emerald-100 to-blue-100 text-emerald-800 px-3 py-1 rounded-full font-medium">
										Advanced AI Analysis
									</div>
								</div>
							</div>
						</div>

						<!-- Executive Summary Section -->
						{#if analysis.result.deepseek_financial_score}
							<div class="bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden">
								<div class="bg-gradient-to-r from-green-50 to-blue-50 px-6 py-4 border-b border-gray-200">
									<h3 class="text-xl font-bold text-gray-900 flex items-center">
										<span class="text-green-600 mr-2">📊</span>
										Investment Analysis Summary
										<span class="ml-2 text-xs bg-green-100 text-green-700 px-2 py-1 rounded-full">DeepSeek AI</span>
									</h3>
								</div>
								<div class="p-6">
									<div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
										<!-- Score Display -->
										<div class="lg:col-span-1">
											<div class="flex-shrink-0">
												<div class="w-20 h-20 bg-gradient-to-br from-green-400 to-blue-500 rounded-full flex items-center justify-center">
													<span class="text-white text-2xl font-bold">{analysis.result.deepseek_financial_score}</span>
												</div>
											</div>
											<div class="mt-4">
												<div class="w-full bg-gray-200 rounded-full h-3 mb-3">
													<div class="bg-gradient-to-r from-green-400 to-blue-500 h-3 rounded-full transition-all duration-500" 
														 style="width: {(analysis.result.deepseek_financial_score / 10) * 100}%"></div>
												</div>
												<p class="text-gray-600 text-sm leading-relaxed">
													{analysis.result.deepseek_recommendation || 'Investment analysis complete. This score reflects overall financial viability based on market analysis, risk assessment, and revenue projections.'}
												</p>
											</div>
										</div>

										<!-- Quick Stats -->
										<div class="lg:col-span-2 space-y-4">
											{#if analysis.result.deepseek_confidence}
												<div class="bg-gray-50 rounded-lg p-4">
													<div class="text-sm font-medium text-gray-700">Confidence Level</div>
													<div class="text-2xl font-bold text-gray-900">{Math.round(analysis.result.deepseek_confidence * 100)}%</div>
												</div>
											{/if}
											
											<!-- Basic Financial Info -->
											<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
												{#if analysis.result.commercial_viability}
													<div class="bg-blue-50 rounded-lg p-4">
														<div class="text-sm font-medium text-blue-800 mb-2">Commercial Viability</div>
														<div class="text-sm text-blue-700">{analysis.result.commercial_viability}</div>
													</div>
												{/if}
												{#if analysis.result.target_audience}
													<div class="bg-purple-50 rounded-lg p-4">
														<div class="text-sm font-medium text-purple-800 mb-2">Target Audience</div>
														<div class="text-sm text-purple-700">{analysis.result.target_audience}</div>
													</div>
												{/if}
											</div>
										</div>
									</div>
								</div>
							</div>
						{/if}

						<!-- Box Office Predictions -->
						{#if analysis.result.deepseek_box_office_prediction}
							{@const prediction = typeof analysis.result.deepseek_box_office_prediction === 'string' 
								? JSON.parse(analysis.result.deepseek_box_office_prediction) 
								: analysis.result.deepseek_box_office_prediction}
							
							{#if prediction}
								<div class="bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden">
									<div class="bg-gradient-to-r from-purple-50 to-pink-50 px-6 py-4 border-b border-gray-200">
										<h3 class="text-xl font-bold text-gray-900 flex items-center">
											<span class="text-purple-600 mr-2">🎬</span>
											Box Office Projections
											<span class="ml-2 text-xs bg-purple-100 text-purple-700 px-2 py-1 rounded-full">AI Predicted</span>
										</h3>
									</div>
									<div class="p-6 space-y-6">
										{#if prediction.domestic_box_office}
											<div class="grid grid-cols-1 md:grid-cols-3 gap-4">
												<div class="text-center p-4 bg-green-50 rounded-lg border border-green-200">
													<div class="text-2xl font-bold text-green-600 mb-1">
														${(prediction.domestic_box_office / 1000000).toFixed(1)}M
													</div>
													<div class="text-sm font-medium text-green-800">Domestic Box Office</div>
													<div class="text-xs text-green-600 mt-1">US & Canada</div>
												</div>
												
												{#if prediction.international_box_office}
													<div class="text-center p-4 bg-blue-50 rounded-lg border border-blue-200">
														<div class="text-2xl font-bold text-blue-600 mb-1">
															${(prediction.international_box_office / 1000000).toFixed(1)}M
														</div>
														<div class="text-sm font-medium text-blue-800">International</div>
														<div class="text-xs text-blue-600 mt-1">Worldwide excluding US/CA</div>
													</div>
												{/if}
												
												{#if prediction.total_box_office}
													<div class="text-center p-4 bg-purple-50 rounded-lg border border-purple-200">
														<div class="text-2xl font-bold text-purple-600 mb-1">
															${(prediction.total_box_office / 1000000).toFixed(1)}M
														</div>
														<div class="text-sm font-medium text-purple-800">Total Worldwide</div>
														<div class="text-xs text-purple-600 mt-1">Combined revenue</div>
													</div>
												{/if}
											</div>
										{/if}
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
								<div class="bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden">
									<div class="bg-gradient-to-r from-emerald-50 to-teal-50 px-6 py-4 border-b border-gray-200">
										<h3 class="text-xl font-bold text-gray-900 flex items-center">
											<span class="text-emerald-600 mr-2">📈</span>
											Return on Investment Analysis
											<span class="ml-2 text-xs bg-emerald-100 text-emerald-700 px-2 py-1 rounded-full">ROI Metrics</span>
										</h3>
									</div>
									<div class="p-6">
										<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
											{#if roi.expected_roi}
												<div class="text-center p-4 bg-emerald-50 rounded-lg border border-emerald-200">
													<div class="text-2xl font-bold text-emerald-600 mb-1">
														{(roi.expected_roi * 100).toFixed(1)}%
													</div>
													<div class="text-sm font-medium text-emerald-800">Expected ROI</div>
												</div>
											{/if}
											{#if roi.break_even_point}
												<div class="text-center p-4 bg-blue-50 rounded-lg border border-blue-200">
													<div class="text-2xl font-bold text-blue-600 mb-1">
														${(roi.break_even_point / 1000000).toFixed(1)}M
													</div>
													<div class="text-sm font-medium text-blue-800">Break Even</div>
												</div>
											{/if}
											{#if roi.profit_margin}
												<div class="text-center p-4 bg-purple-50 rounded-lg border border-purple-200">
													<div class="text-2xl font-bold text-purple-600 mb-1">
														{(roi.profit_margin * 100).toFixed(1)}%
													</div>
													<div class="text-sm font-medium text-purple-800">Profit Margin</div>
												</div>
											{/if}
											{#if roi.risk_level}
												<div class="text-center p-4 bg-orange-50 rounded-lg border border-orange-200">
													<div class="text-lg font-bold text-orange-600 mb-1 capitalize">
														{roi.risk_level}
													</div>
													<div class="text-sm font-medium text-orange-800">Risk Level</div>
												</div>
											{/if}
										</div>
									</div>
								</div>
							{/if}
						{/if}

					{:else}
						<!-- Fallback to basic financial info -->
						<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
							<!-- Commercial Viability -->
							{#if analysis.result.commercial_viability}
								<div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6 md:col-span-2">
									<h3 class="text-lg font-bold text-gray-900 mb-4 flex items-center">
										<span class="text-green-600 mr-2">💰</span>
										Commercial Viability
									</h3>
									<div class="prose max-w-none">
										<p class="text-gray-700">{analysis.result.commercial_viability}</p>
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
									<div class="prose max-w-none">
										<p class="text-gray-700">{analysis.result.target_audience}</p>
									</div>
								</div>
							{/if}

							<!-- Comparable Films -->
							{#if analysis.result.comparable_films}
								<div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6 md:col-span-2 lg:col-span-3">
									<h3 class="text-lg font-bold text-gray-900 mb-4 flex items-center">
										<span class="text-blue-600 mr-2">🎥</span>
										Comparable Films
									</h3>
									<div class="prose max-w-none">
										<p class="text-gray-700">{analysis.result.comparable_films}</p>
									</div>
								</div>
							{/if}
						</div>
					{/if}
				</div>

			<!-- Grok Reality Check Tab -->
			{:else if activeTab === 'grok'}
				<div class="space-y-6">
					{#if analysis.result.grok_score || analysis.result.grok_cultural_analysis || analysis.result.grok_brutal_honesty}
						<!-- Grok Overview -->
						<div class="bg-gradient-to-r from-purple-50 to-indigo-50 rounded-lg border border-purple-200 p-6">
							<div class="flex items-center justify-between mb-4">
								<h3 class="text-xl font-bold text-gray-900 flex items-center">
									<span class="text-purple-600 mr-2">🤖</span>
									Grok AI Reality Check
									<span class="ml-2 text-xs bg-purple-100 text-purple-700 px-2 py-1 rounded-full">
										Brutally Honest
									</span>
								</h3>
								{#if analysis.result.grok_score}
									<div class="text-center">
										<div class="text-3xl font-bold text-purple-600 mb-1">
											{analysis.result.grok_score}<span class="text-lg">/10</span>
										</div>
										<div class="text-xs text-purple-600">Reality Score</div>
									</div>
								{/if}
							</div>
						</div>

						<!-- Cultural Reality Check -->
						{#if analysis.result.grok_cultural_analysis}
							<div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
								<h3 class="text-xl font-bold text-gray-900 mb-4 flex items-center">
									<span class="text-pink-600 mr-2">🎭</span>
									Cultural Reality Check
								</h3>
								
								<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
									<!-- Cringe Factor -->
									<div class="text-center p-4 bg-pink-50 rounded-lg border border-pink-200">
										<div class="text-3xl font-bold text-pink-600 mb-1">
											{getCultural().cringe_factor || 'N/A'}<span class="text-lg">/10</span>
										</div>
										<div class="text-sm font-medium text-pink-800 mb-2">Cringe Factor</div>
										<div class="text-xs text-pink-600 mb-2">Dialogue authenticity for target demographics</div>
										<div class="text-xs text-pink-500 leading-tight">
											<strong>High (8-10):</strong> Extremely cringey, out-of-touch dialogue<br/>
											<strong>Low (1-3):</strong> Authentic, natural speech patterns
										</div>
									</div>
									
									<!-- Zeitgeist Score -->
									<div class="text-center p-4 bg-blue-50 rounded-lg border border-blue-200">
										<div class="text-3xl font-bold text-blue-600 mb-1">
											{getCultural().zeitgeist_score || 'N/A'}<span class="text-lg">/10</span>
										</div>
										<div class="text-sm font-medium text-blue-800 mb-2">Zeitgeist Score</div>
										<div class="text-xs text-blue-600 mb-2">How current/outdated cultural references are</div>
										<div class="text-xs text-blue-500 leading-tight">
											<strong>High (8-10):</strong> Perfectly captures current cultural moment<br/>
											<strong>Low (1-3):</strong> Outdated references, feels disconnected
										</div>
									</div>
									
									<!-- Meme Potential -->
									<div class="p-4 bg-yellow-50 rounded-lg border border-yellow-200">
										<div class="text-sm font-medium text-yellow-800 mb-2 flex items-center">
											<span class="mr-1">🔥</span>
											Meme Potential
										</div>
										<div class="text-xs text-yellow-700 leading-relaxed">
											{getCultural().meme_potential || 'No specific meme potential identified'}
										</div>
									</div>
									
									<!-- Twitter Discourse -->
									<div class="p-4 bg-indigo-50 rounded-lg border border-indigo-200">
										<div class="text-sm font-medium text-indigo-800 mb-2 flex items-center">
											<span class="mr-1">🐦</span>
											Film Twitter Take
										</div>
										<div class="text-xs text-indigo-700 leading-relaxed">
											{getCultural().twitter_discourse || 'Neutral reception expected'}
										</div>
									</div>
								</div>
							</div>
						{/if}
						
						<!-- Brutal Honesty Assessment -->
						{#if analysis.result.grok_brutal_honesty}
							<div class="bg-white rounded-lg shadow-sm border border-red-200 p-6">
								<h3 class="text-xl font-bold text-gray-900 mb-4 flex items-center">
									<span class="text-red-600 mr-2">💀</span>
									Brutal Honesty Assessment
									<span class="ml-2 text-xs bg-red-100 text-red-700 px-2 py-1 rounded-full">No Sugar-Coating</span>
								</h3>
								
								<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
									<!-- Protagonist Reality Check -->
									<div class="p-4 bg-red-50 rounded-lg border border-red-200">
										<div class="text-sm font-medium text-red-800 mb-2 flex items-center">
											<span class="mr-1">👤</span>
											Protagonist Reality Check
										</div>
										<div class="text-sm text-red-700 leading-relaxed">
											{getBrutal().protagonist_reality_check || 'Assessment not available'}
										</div>
									</div>
									
									<!-- Attention Retention -->
									<div class="p-4 bg-orange-50 rounded-lg border border-orange-200">
										<div class="text-sm font-medium text-orange-800 mb-2 flex items-center">
											<span class="mr-1">⏱️</span>
											TikTok-Brain Test
										</div>
										<div class="text-sm text-orange-700 leading-relaxed">
											{getBrutal().tiktok_brain_pacing || 'Assessment not available'}
										</div>
									</div>
									
									<!-- Competition Reality -->
									<div class="p-4 bg-yellow-50 rounded-lg border border-yellow-200">
										<div class="text-sm font-medium text-yellow-800 mb-2 flex items-center">
											<span class="mr-1">🥊</span>
											Competition Reality
										</div>
										<div class="text-sm text-yellow-700 leading-relaxed">
											{getBrutal().competition_brutality || 'Assessment not available'}
										</div>
									</div>
									
									<!-- Production Feasibility -->
									<div class="p-4 bg-green-50 rounded-lg border border-green-200">
										<div class="text-sm font-medium text-green-800 mb-2 flex items-center">
											<span class="mr-1">💰</span>
											Budget Reality Check
										</div>
										<div class="text-sm text-green-700 leading-relaxed">
											{getBrutal().production_reality || 'Assessment not available'}
										</div>
									</div>
								</div>
							</div>
						{/if}
						
						<!-- Controversy Scanner -->
						{#if analysis.result.grok_controversy_analysis}
							<div class="bg-white rounded-lg shadow-sm border border-amber-200 p-6">
								<h3 class="text-xl font-bold text-gray-900 mb-4 flex items-center">
									<span class="text-amber-600 mr-2">⚠️</span>
									Controversy Scanner
									<span class="ml-2 text-xs bg-amber-100 text-amber-700 px-2 py-1 rounded-full">Risk Assessment</span>
								</h3>
								
								<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
									<!-- Political Sensitivity -->
									<div class="p-4 bg-red-50 rounded-lg border border-red-200">
										<div class="text-sm font-medium text-red-800 mb-2 flex items-center">
											<span class="mr-1">🏛️</span>
											Political Sensitivity
										</div>
										<div class="text-sm text-red-700 leading-relaxed">
											{getControversy().political_sensitivity || 'No significant political content detected'}
										</div>
									</div>
									
									<!-- Cultural Sensitivity -->
									<div class="p-4 bg-orange-50 rounded-lg border border-orange-200">
										<div class="text-sm font-medium text-orange-800 mb-2 flex items-center">
											<span class="mr-1">🌍</span>
											Cultural Sensitivity
										</div>
										<div class="text-sm text-orange-700 leading-relaxed">
											{getControversy().cultural_sensitivity || 'No major cultural concerns identified'}
										</div>
									</div>
									
									<!-- Social Media Risk -->
									<div class="p-4 bg-yellow-50 rounded-lg border border-yellow-200">
										<div class="text-sm font-medium text-yellow-800 mb-2 flex items-center">
											<span class="mr-1">📱</span>
											Social Media Risk
										</div>
										<div class="text-sm text-yellow-700 leading-relaxed">
											{getControversy().social_media_risk || 'Low risk of social media backlash'}
										</div>
									</div>
									
									<!-- Cancel Culture Risk -->
									<div class="p-4 bg-pink-50 rounded-lg border border-pink-200">
										<div class="text-sm font-medium text-pink-800 mb-2 flex items-center">
											<span class="mr-1">🚫</span>
											Cancel Culture Risk
										</div>
										<div class="text-sm text-pink-700 leading-relaxed">
											{getControversy().cancel_culture_risk || 'Minimal cancel culture exposure'}
										</div>
									</div>
								</div>
							</div>
						{/if}
					{:else}
						<div class="text-center py-12">
							<div class="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
								<span class="text-2xl">🤖</span>
							</div>
							<h3 class="text-xl font-semibold text-gray-900 mb-2">Grok Analysis Not Available</h3>
							<p class="text-gray-600">This analysis doesn't include Grok AI reality check data.</p>
						</div>
					{/if}
				</div>

			<!-- GPT-5 Excellence Analysis Tab -->
			{:else if activeTab === 'gpt5'}
				<div class="space-y-6">
					{#if analysis.result.gpt5_score || analysis.result.gpt5_character_voice_analysis || analysis.result.gpt5_dialogue_authenticity || analysis.result.gpt5_prose_quality}
						<!-- GPT-5 Overview -->
						<div class="bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg border border-blue-200 p-6">
							<div class="flex items-center justify-between mb-4">
								<h3 class="text-xl font-bold text-gray-900 flex items-center">
									<span class="text-blue-600 mr-2">🧠</span>
									GPT-5 Writing Excellence Analysis
									<span class="ml-2 text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded-full">
										Writing Craft
									</span>
								</h3>
								{#if analysis.result.gpt5_score}
									<div class="text-center">
										<div class="text-3xl font-bold text-blue-600 mb-1">
											{analysis.result.gpt5_score}<span class="text-lg">/10</span>
										</div>
										<div class="text-xs text-blue-600">Excellence Score</div>
									</div>
								{/if}
							</div>
						</div>

						<!-- Character Voice Analysis -->
						{#if getGPT5CharacterVoice()}
							<div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
								<h3 class="text-xl font-bold text-gray-900 mb-4 flex items-center">
									<span class="text-purple-600 mr-2">🗣️</span>
									Character Voice Analysis
								</h3>
								<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
									<div class="text-center p-4 bg-purple-50 rounded-lg border border-purple-200">
										<div class="text-3xl font-bold text-purple-600 mb-1">
											{getGPT5CharacterVoice().voice_distinction_score}<span class="text-lg">/10</span>
										</div>
										<div class="text-sm font-medium text-purple-800 mb-2">Voice Distinction Score</div>
										<div class="text-xs text-purple-600">Character voice uniqueness</div>
									</div>
									<div class="p-4 bg-purple-50 rounded-lg border border-purple-200">
										<div class="text-sm font-medium text-purple-800 mb-2">Authenticity Rating</div>
										<div class="text-sm text-purple-700 leading-relaxed">
											{getGPT5CharacterVoice().authenticity_rating}
										</div>
									</div>
									<div class="p-4 bg-purple-50 rounded-lg border border-purple-200 md:col-span-2">
										<div class="text-sm font-medium text-purple-800 mb-2">Voice Consistency Assessment</div>
										<div class="text-sm text-purple-700 leading-relaxed">
											{getGPT5CharacterVoice().voice_consistency}
										</div>
									</div>
									{#if getGPT5CharacterVoice().distinctiveness}
										<div class="p-4 bg-purple-50 rounded-lg border border-purple-200">
											<div class="text-sm font-medium text-purple-800 mb-2 flex items-center">
												<span class="mr-1">🎭</span>
												Voice Distinctiveness
											</div>
											<div class="text-sm text-purple-700 leading-relaxed">
												{getGPT5CharacterVoice().distinctiveness}
											</div>
										</div>
									{/if}
								</div>
							</div>
						{/if}

						<!-- Dialogue Authenticity -->
						{#if getGPT5DialogueAuth()}
							<div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
								<h3 class="text-xl font-bold text-gray-900 mb-4 flex items-center">
									<span class="text-green-600 mr-2">💬</span>
									Dialogue Authenticity
								</h3>
								<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
									<div class="text-center p-4 bg-green-50 rounded-lg border border-green-200">
										<div class="text-3xl font-bold text-green-600 mb-1">
											{getGPT5DialogueAuth().naturalism_score}<span class="text-lg">/10</span>
										</div>
										<div class="text-sm font-medium text-green-800 mb-2">Naturalism Score</div>
										<div class="text-xs text-green-600">How natural dialogue sounds</div>
									</div>
									<div class="p-4 bg-green-50 rounded-lg border border-green-200">
										<div class="text-sm font-medium text-green-800 mb-2">Exposition Handling</div>
										<div class="text-sm text-green-700 leading-relaxed">
											{getGPT5DialogueAuth().exposition_handling}
										</div>
									</div>
									<div class="p-4 bg-green-50 rounded-lg border border-green-200">
										<div class="text-sm font-medium text-green-800 mb-2">Subtext Quality</div>
										<div class="text-sm text-green-700 leading-relaxed">
											{getGPT5DialogueAuth().subtext_quality}
										</div>
									</div>
									<div class="p-4 bg-green-50 rounded-lg border border-green-200">
										<div class="text-sm font-medium text-green-800 mb-2">Speech Pattern Authenticity</div>
										<div class="text-sm text-green-700 leading-relaxed">
											{getGPT5DialogueAuth().speech_pattern_authenticity}
										</div>
									</div>
								</div>
							</div>
						{/if}

						<!-- Prose Quality -->
						{#if getGPT5ProseQuality()}
							<div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
								<h3 class="text-xl font-bold text-gray-900 mb-4 flex items-center">
									<span class="text-indigo-600 mr-2">✍️</span>
									Prose Quality Assessment
								</h3>
								<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
									<div class="text-center p-4 bg-indigo-50 rounded-lg border border-indigo-200">
										<div class="text-3xl font-bold text-indigo-600 mb-1">
											{getGPT5ProseQuality().visual_storytelling_score}<span class="text-lg">/10</span>
										</div>
										<div class="text-sm font-medium text-indigo-800 mb-2">Visual Storytelling Score</div>
										<div class="text-xs text-indigo-600">Cinematic prose quality</div>
									</div>
									<div class="p-4 bg-indigo-50 rounded-lg border border-indigo-200">
										<div class="text-sm font-medium text-indigo-800 mb-2">Action Line Efficiency</div>
										<div class="text-sm text-indigo-700 leading-relaxed">
											{getGPT5ProseQuality().action_line_efficiency}
										</div>
									</div>
									<div class="p-4 bg-indigo-50 rounded-lg border border-indigo-200">
										<div class="text-sm font-medium text-indigo-800 mb-2">Cinematic Language</div>
										<div class="text-sm text-indigo-700 leading-relaxed">
											{getGPT5ProseQuality().cinematic_language}
										</div>
									</div>
									<div class="p-4 bg-indigo-50 rounded-lg border border-indigo-200">
										<div class="text-sm font-medium text-indigo-800 mb-2">Show vs Tell Balance</div>
										<div class="text-sm text-indigo-700 leading-relaxed">
											{getGPT5ProseQuality().show_vs_tell_balance}
										</div>
									</div>
								</div>
							</div>
						{/if}
					{:else}
						<div class="text-center py-12">
							<div class="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
								<span class="text-2xl">🧠</span>
							</div>
							<h3 class="text-xl font-semibold text-gray-900 mb-2">GPT-5 Analysis Not Available</h3>
							<p class="text-gray-600">This analysis doesn't include GPT-5 writing excellence data.</p>
						</div>
					{/if}
				</div>

			<!-- Genre Intelligence Tab -->
			{:else if activeTab === 'genre'}
				<div class="space-y-8">
					<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
						<!-- Genre Mastery -->
						{#if analysis.result.genre_mastery}
							<div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
								<h3 class="text-lg font-bold text-gray-900 mb-4 flex items-center">
									<span class="text-red-600 mr-2">🎬</span>
									Genre Mastery
								</h3>
								<div class="prose max-w-none">
									<p class="text-gray-700">{analysis.result.genre_mastery}</p>
								</div>
							</div>
						{/if}

						<!-- Comparable Films -->
						{#if analysis.result.comparable_films}
							<div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
								<h3 class="text-lg font-bold text-gray-900 mb-4 flex items-center">
									<span class="text-blue-600 mr-2">🎥</span>
									Comparable Films
								</h3>
								<div class="prose max-w-none">
									<p class="text-gray-700">{analysis.result.comparable_films}</p>
								</div>
							</div>
						{/if}
					</div>

					<!-- Source Material Analysis -->
					{#if analysis.result.source_success && analysis.result.source_has_material}
						<div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
							<h3 class="text-xl font-bold text-gray-900 mb-6 flex items-center">
								<span class="text-indigo-600 mr-2">📚</span>
								Source Material & IP Analysis
								<span class="ml-2 text-xs bg-indigo-100 text-indigo-700 px-2 py-1 rounded-full">
									AI Detected
								</span>
							</h3>
							
							<div class="bg-gradient-to-r from-orange-50 to-amber-50 border border-orange-200 rounded-lg p-6">
								<div class="flex items-start justify-between">
									<div class="flex-1">
										<h4 class="text-lg font-semibold text-orange-900 mb-2">
											Based on {analysis.result.source_type?.replace('_', ' ').toLowerCase() || 'existing material'}
										</h4>
										{#if analysis.result.source_title}
											<p class="text-xl font-bold text-orange-800 mb-2">"{analysis.result.source_title}"</p>
										{/if}
										{#if analysis.result.source_author}
											<p class="text-orange-700">by {analysis.result.source_author}</p>
										{/if}
									</div>
									<div class="text-right">
										<div class="text-2xl font-bold text-orange-600">
											{Math.round((analysis.result.source_confidence_score || 0) * 100)}%
										</div>
										<div class="text-xs text-orange-600">Confidence</div>
									</div>
								</div>
								
								{#if analysis.result.source_description}
									<div class="mt-4 pt-4 border-t border-orange-200">
										<p class="text-orange-800 leading-relaxed">{analysis.result.source_description}</p>
									</div>
								{/if}
							</div>
						</div>
					{/if}
				</div>

			<!-- Market Intelligence Tab -->
			{:else if activeTab === 'market'}
				<div class="space-y-6">
					{#if hasPerplexityData()}
						<!-- Perplexity Market Research -->
						<div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
							<h3 class="text-xl font-bold text-gray-900 mb-6 flex items-center">
								<span class="text-purple-600 mr-2">🔍</span>
								Perplexity Market Research
								<span class="ml-2 text-xs bg-purple-100 text-purple-700 px-2 py-1 rounded-full">AI Market Intelligence</span>
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
										<h4 class="text-lg font-semibold text-gray-900 mb-4 flex items-center">
											<span class="text-blue-600 mr-2">📈</span>
											Current Market Trends
										</h4>
										<div class="bg-blue-50 rounded-lg p-4 border border-blue-200">
											<div class="prose max-w-none">
												<p class="text-blue-900 leading-relaxed">{trends.content}</p>
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
										<h4 class="text-lg font-semibold text-gray-900 mb-4 flex items-center">
											<span class="text-red-600 mr-2">⚔️</span>
											Competitive Landscape
										</h4>
										<div class="bg-red-50 rounded-lg p-4 border border-red-200">
											<div class="prose max-w-none">
												<p class="text-red-900 leading-relaxed">{competitive.content}</p>
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
									<div>
										<h4 class="text-lg font-semibold text-gray-900 mb-4 flex items-center">
											<span class="text-green-600 mr-2">👥</span>
											Target Demographics
										</h4>
										<div class="bg-green-50 rounded-lg p-4 border border-green-200">
											<div class="prose max-w-none">
												<p class="text-green-900 leading-relaxed">{demographics.content}</p>
											</div>
										</div>
									</div>
								{/if}
							{/if}
						</div>
					{:else}
						<!-- Fallback to basic market info -->
						<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
							<!-- Commercial Viability -->
							{#if analysis.result.commercial_viability}
								<div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
									<h3 class="text-lg font-bold text-gray-900 mb-4 flex items-center">
										<span class="text-green-600 mr-2">💰</span>
										Commercial Viability
									</h3>
									<div class="prose max-w-none">
										<p class="text-gray-700">{analysis.result.commercial_viability}</p>
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
									<div class="prose max-w-none">
										<p class="text-gray-700">{analysis.result.target_audience}</p>
									</div>
								</div>
							{/if}
						</div>
					{/if}
				</div>

			<!-- Producer Dashboard Tab -->
			{:else if activeTab === 'producer'}
				<div class="space-y-8">
					<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
						<!-- Director Recommendation -->
						{#if analysis.result.director_recommendation}
							<div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
								<h3 class="text-lg font-bold text-gray-900 mb-4 flex items-center">
									<span class="text-indigo-600 mr-2">🎬</span>
									Director Recommendation
								</h3>
								<div class="prose max-w-none">
									<p class="text-gray-700">{analysis.result.director_recommendation}</p>
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
									<p class="text-gray-700">{analysis.result.commercial_viability}</p>
								</div>
							</div>
						{/if}
					</div>
				</div>

			<!-- Production Planning Tab -->
			{:else if activeTab === 'production'}
				<div class="space-y-8">
					<!-- Director Recommendation -->
					<div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
						<h3 class="text-xl font-bold text-gray-900 mb-4 flex items-center">
							<span class="text-purple-600 mr-2">🎥</span>
							Director Recommendation
						</h3>
						{#if analysis.result.director_recommendation}
							<div class="bg-purple-50 border-l-4 border-purple-400 p-6 rounded-md">
								<div class="flex items-start">
									<div class="flex-shrink-0">
										<span class="text-purple-600 text-2xl">🎬</span>
									</div>
									<div class="ml-4">
										<h4 class="text-lg font-semibold text-purple-900 mb-3">Ideal Director Vision</h4>
										<div class="text-purple-800 whitespace-pre-line leading-relaxed">
											{analysis.result.director_recommendation}
										</div>
									</div>
								</div>
							</div>
						{:else}
							<p class="text-gray-500 italic">Director recommendations will be available in enhanced results.</p>
						{/if}
					</div>

					<!-- Casting Vision -->
					<div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
						<h3 class="text-xl font-bold text-gray-900 mb-4 flex items-center">
							<span class="text-red-600 mr-2">🌟</span>
							Casting Vision
						</h3>
						{#if parseJsonField(analysis.result.casting_vision || analysis.result.casting_suggestions).length > 0}
							<div class="space-y-6">
								{#each parseJsonField(analysis.result.casting_vision || analysis.result.casting_suggestions) as casting}
									<div class="border-b border-gray-200 pb-6 last:border-0">
										<h4 class="font-semibold text-gray-900 mb-3 text-lg">{casting.character}</h4>
										{#if casting.reasoning}
											<p class="text-gray-600 mb-3 italic">{casting.reasoning}</p>
										{/if}
										<div class="flex flex-wrap gap-2">
											{#each (casting.actors || []) as actor}
												<span class="inline-flex items-center px-3 py-2 rounded-lg text-sm bg-red-50 text-red-800 border border-red-200">
													<span class="mr-1">🎭</span>
													{actor}
												</span>
											{/each}
										</div>
									</div>
								{/each}
							</div>
						{:else}
							<p class="text-gray-500 italic">Casting recommendations will be available in enhanced results.</p>
						{/if}
					</div>

					<!-- Commercial Viability for Production -->
					{#if analysis.result.commercial_viability}
						<div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
							<h3 class="text-xl font-bold text-gray-900 mb-4 flex items-center">
								<span class="text-green-600 mr-2">💰</span>
								Production Viability
							</h3>
							<div class="bg-green-50 border-l-4 border-green-400 p-6 rounded-md">
								<div class="flex items-start">
									<div class="flex-shrink-0">
										<span class="text-green-600 text-2xl">💼</span>
									</div>
									<div class="ml-4">
										<h4 class="text-lg font-semibold text-green-900 mb-3">Commercial Assessment</h4>
										<div class="text-green-800 leading-relaxed">
											{analysis.result.commercial_viability}
										</div>
									</div>
								</div>
							</div>
						</div>
					{/if}
				</div>

			<!-- Media Assets Tab -->
			{:else if activeTab === 'media'}
				<div class="space-y-6">
					<!-- Best Poster Collection Section -->
					{#if analysis.result.poster_best_url}
						<div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
							<h3 class="text-xl font-bold text-gray-900 mb-6 flex items-center">
								<span class="text-purple-600 mr-2">🏆</span>
								Best Movie Poster
								<span class="ml-2 text-xs bg-purple-100 text-purple-700 px-2 py-1 rounded-full">{analysis.result.poster_best_source || 'AI Generated'}</span>
								{#if analysis.result.poster_success_count > 1}
									<span class="ml-2 text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded-full">{analysis.result.poster_success_count} variations</span>
								{/if}
							</h3>
							
							<div class="flex justify-center">
								<div class="space-y-4">
									<div class="relative group">
										<img 
											src={analysis.result.poster_best_url} 
											alt="Best movie poster for {analysis.result.title}"
											class="w-full max-w-md mx-auto rounded-lg shadow-lg border border-gray-200 group-hover:shadow-xl transition-shadow duration-300"
											crossorigin="anonymous"
											on:error={(e) => {
												console.error('Best poster image failed to load:', e);
												const target = e.target as HTMLImageElement;
												if (target) {
													target.style.backgroundColor = '#f3f4f6';
													target.style.border = '2px dashed #d1d5db';
													target.alt = 'Poster image failed to load - click "View Full Size" to access directly';
												}
											}}
										/>
									</div>
									<div class="text-center">
										<a 
											href={analysis.result.poster_best_url} 
											target="_blank" 
											class="inline-flex items-center px-4 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700 transition-colors text-sm"
										>
											<svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
												<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
											</svg>
											View Full Size
										</a>
									</div>
								</div>
							</div>
						</div>
					{/if}

					<!-- OpenAI Generated Posters -->
					{#if analysis.result.openai_movie_poster_url}
						<div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
							<h3 class="text-xl font-bold text-gray-900 mb-6 flex items-center">
								<span class="text-green-600 mr-2">🤖</span>
								OpenAI Generated Poster
								<span class="ml-2 text-xs bg-green-100 text-green-700 px-2 py-1 rounded-full">DALL-E 3</span>
							</h3>
							
							<div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
								<div class="space-y-4">
									<div class="relative group">
										<img 
											src={analysis.result.openai_movie_poster_url} 
											alt="OpenAI generated movie poster for {analysis.result.title}"
											class="w-full rounded-lg shadow-lg border border-gray-200 group-hover:shadow-xl transition-shadow duration-300"
											crossorigin="anonymous"
											on:error={(e) => {
												console.error('OpenAI poster image failed to load:', e);
												const target = e.target as HTMLImageElement;
												if (target) {
													target.style.backgroundColor = '#f3f4f6';
													target.style.border = '2px dashed #d1d5db';
													target.alt = 'OpenAI poster image failed to load - click "View Full Size" to access directly';
												}
											}}
										/>
									</div>
									<div class="text-center">
										<a 
											href={analysis.result.openai_movie_poster_url} 
											target="_blank" 
											class="inline-flex items-center px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors text-sm"
										>
											<svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
												<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
											</svg>
											View Full Size
										</a>
									</div>
								</div>
								
								{#if analysis.result.openai_poster_prompt}
									<div class="space-y-4">
										<h4 class="text-lg font-semibold text-gray-900 flex items-center">
											<span class="text-blue-600 mr-2">💭</span>
											AI Prompt Used
										</h4>
										<div class="bg-gray-50 rounded-lg p-4 border border-gray-200">
											<p class="text-gray-700 text-sm leading-relaxed font-mono">
												{analysis.result.openai_poster_prompt}
											</p>
										</div>
									</div>
								{/if}
							</div>
						</div>
					{/if}

					<!-- PiAPI Generated Posters -->
					{#if analysis.result.piapi_poster_url}
						<div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
							<h3 class="text-xl font-bold text-gray-900 mb-6 flex items-center">
								<span class="text-blue-600 mr-2">🎨</span>
								PiAPI Generated Poster
								<span class="ml-2 text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded-full">Alternative AI</span>
							</h3>
							
							<div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
								<div class="space-y-4">
									<div class="relative group">
										<img 
											src={analysis.result.piapi_poster_url} 
											alt="PiAPI generated movie poster for {analysis.result.title}"
											class="w-full rounded-lg shadow-lg border border-gray-200 group-hover:shadow-xl transition-shadow duration-300"
											crossorigin="anonymous"
											on:error={(e) => {
												console.error('PiAPI poster image failed to load:', e);
												const target = e.target as HTMLImageElement;
												if (target) {
													target.style.backgroundColor = '#f3f4f6';
													target.style.border = '2px dashed #d1d5db';
													target.alt = 'PiAPI poster image failed to load - click "View Full Size" to access directly';
												}
											}}
										/>
									</div>
									<div class="text-center">
										<a 
											href={analysis.result.piapi_poster_url} 
											target="_blank" 
											class="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors text-sm"
										>
											<svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
												<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
											</svg>
											View Full Size
										</a>
									</div>
								</div>
								
								{#if analysis.result.piapi_poster_prompt}
									<div class="space-y-4">
										<h4 class="text-lg font-semibold text-gray-900 flex items-center">
											<span class="text-purple-600 mr-2">💭</span>
											AI Prompt Used
										</h4>
										<div class="bg-gray-50 rounded-lg p-4 border border-gray-200">
											<p class="text-gray-700 text-sm leading-relaxed font-mono">
												{analysis.result.piapi_poster_prompt}
											</p>
										</div>
									</div>
								{/if}
							</div>
						</div>
					{/if}
					
					<!-- No Posters Available -->
					{#if !analysis.result.openai_movie_poster_url && !analysis.result.openai_poster_prompt && !analysis.result.piapi_poster_url && !analysis.result.piapi_poster_prompt && !analysis.result.poster_best_url}
						<div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
							<div class="text-center py-12">
								<svg class="w-16 h-16 mx-auto text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
								</svg>
								<h3 class="text-lg font-medium text-gray-900 mb-2">No Media Available</h3>
								<p class="text-gray-500 mb-6">Movie poster and other media will be generated during analysis.</p>
								<a href="/auth/register" class="inline-flex items-center justify-center px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg">
									Get Full Analysis
								</a>
							</div>
						</div>
					{/if}
				</div>

			<!-- Casting Vision Tab -->
			{:else if activeTab === 'casting'}
				<div class="space-y-8">
					{#if parseJsonField(analysis.result.casting_vision || analysis.result.casting_suggestions).length > 0}
						<div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
							<h3 class="text-xl font-bold text-gray-900 mb-4 flex items-center">
								<span class="text-red-600 mr-2">🌟</span>
								Casting Vision
							</h3>
							<div class="space-y-6">
								{#each parseJsonField(analysis.result.casting_vision || analysis.result.casting_suggestions) as casting}
									<div class="border-b border-gray-200 pb-6 last:border-0">
										<h4 class="font-semibold text-gray-900 mb-3 text-lg">{casting.character}</h4>
										{#if casting.reasoning}
											<p class="text-gray-600 mb-3 italic">{casting.reasoning}</p>
										{/if}
										<div class="flex flex-wrap gap-2">
											{#each (casting.actors || []) as actor}
												<span class="inline-flex items-center px-3 py-2 rounded-lg text-sm bg-red-50 text-red-800 border border-red-200">
													<span class="mr-1">🎭</span>
													{actor}
												</span>
											{/each}
										</div>
									</div>
								{/each}
							</div>
						</div>
					{:else}
						<div class="text-center py-12">
							<div class="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
								<span class="text-2xl">🎭</span>
							</div>
							<h3 class="text-xl font-semibold text-gray-900 mb-2">Casting Analysis Not Available</h3>
							<p class="text-gray-600">This analysis doesn't include casting vision or suggestions data.</p>
						</div>
					{/if}
				</div>

			<!-- Media Strategy Tab -->
			{:else if activeTab === 'media'}
				<div class="space-y-8">
					<div class="text-center py-12">
						<div class="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
							<span class="text-2xl">📺</span>
						</div>
						<h3 class="text-xl font-semibold text-gray-900 mb-2">Media Strategy & Marketing</h3>
						<p class="text-gray-600 mb-6">Comprehensive media strategy and marketing analysis tools.</p>
						<a href="/auth/register" class="inline-flex items-center justify-center px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg">
							Access Full Analysis
						</a>
					</div>
				</div>

			<!-- Enhancement Notes Tab -->
			{:else if activeTab === 'improvements'}
				<div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
					<h3 class="text-xl font-bold text-gray-900 mb-4 flex items-center">
						<span class="text-yellow-600 mr-2">💡</span>
						Improvement Strategies
						<span class="ml-2 text-xs bg-yellow-100 text-yellow-700 px-2 py-1 rounded-full">Enhancement Recommendations</span>
					</h3>
					
					<div class="space-y-6">
						<!-- Improvement Strategies -->
						{#if analysis.result.improvement_strategies}
							<div class="bg-yellow-50 rounded-lg p-6 border border-yellow-200">
								<h4 class="text-lg font-semibold text-yellow-900 mb-4 flex items-center">
									<span class="text-yellow-600 mr-2">🎯</span>
									Strategic Improvements
								</h4>
								<div class="prose max-w-none">
									<p class="text-yellow-800 leading-relaxed">{analysis.result.improvement_strategies}</p>
								</div>
							</div>
						{/if}

						<!-- Suggestions -->
						{#if analysis.result.suggestions}
							<div class="bg-blue-50 rounded-lg p-6 border border-blue-200">
								<h4 class="text-lg font-semibold text-blue-900 mb-4 flex items-center">
									<span class="text-blue-600 mr-2">💭</span>
									Professional Suggestions
								</h4>
								<div class="prose max-w-none">
									<p class="text-blue-800 leading-relaxed">{analysis.result.suggestions}</p>
								</div>
							</div>
						{/if}

						<!-- Key Weaknesses -->
						{#if analysis.result.key_weaknesses}
							<div class="bg-red-50 rounded-lg p-6 border border-red-200">
								<h4 class="text-lg font-semibold text-red-900 mb-4 flex items-center">
									<span class="text-red-600 mr-2">⚠️</span>
									Areas Requiring Attention
								</h4>
								<div class="prose max-w-none">
									<p class="text-red-800 leading-relaxed">{analysis.result.key_weaknesses}</p>
								</div>
							</div>
						{/if}

						<!-- Craft Evaluation -->
						{#if analysis.result.craft_evaluation}
							<div class="bg-purple-50 rounded-lg p-6 border border-purple-200">
								<h4 class="text-lg font-semibold text-purple-900 mb-4 flex items-center">
									<span class="text-purple-600 mr-2">✍️</span>
									Craft Assessment
								</h4>
								<div class="prose max-w-none">
									<p class="text-purple-800 leading-relaxed">{analysis.result.craft_evaluation}</p>
								</div>
							</div>
						{/if}

						<!-- No Improvements Available -->
						{#if !analysis.result.improvement_strategies && !analysis.result.suggestions && !analysis.result.key_weaknesses && !analysis.result.craft_evaluation}
							<div class="text-center py-12">
								<div class="w-16 h-16 bg-yellow-100 rounded-full flex items-center justify-center mx-auto mb-4">
									<span class="text-2xl">💡</span>
								</div>
								<h3 class="text-xl font-semibold text-gray-900 mb-2">Enhancement Notes Not Available</h3>
								<p class="text-gray-600">Detailed improvement recommendations are generated during comprehensive analysis.</p>
							</div>
						{/if}
					</div>
				</div>

			{/if}

			<!-- Call to Action (shown on all tabs) -->
			<div class="bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg p-8 text-center mt-12">
				<h3 class="text-2xl font-bold text-white mb-4">Want Your Own Professional Analysis?</h3>
				<p class="text-blue-100 mb-6 max-w-2xl mx-auto">
					Get comprehensive AI-powered screenplay analysis with detailed insights, market intelligence, and professional recommendations.
				</p>
				<div class="space-x-4">
					<a href="/auth/register" class="bg-white text-blue-600 px-6 py-3 rounded-lg font-semibold hover:bg-blue-50 transition-colors">
						Start Your Analysis
					</a>
					<a href="/about" class="text-white border border-white px-6 py-3 rounded-lg font-semibold hover:bg-white hover:bg-opacity-10 transition-colors">
						Learn More
					</a>
				</div>
			</div>
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