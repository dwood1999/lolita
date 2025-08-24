<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/stores';

	let loading = true;
	let analysis: any = null;
	let error = '';
	let activeTab = 'dashboard';

	const shareToken = $page.params.token;

	// Simple navigation tabs
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
		{ id: 'posters', label: 'Movie Posters', icon: '🎨' },
		{ id: 'casting', label: 'Casting Vision', icon: '🎭' },
		{ id: 'media', label: 'Media Strategy', icon: '📺' }
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
										tab.id === 'gpt5' ? analysis.result.gpt5_score : null}
						
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
				<div class="space-y-8">
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
					<div class="text-center py-12">
						<div class="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
							<span class="text-2xl">🎭</span>
						</div>
						<h3 class="text-xl font-semibold text-gray-900 mb-2">Production Planning</h3>
						<p class="text-gray-600 mb-6">Detailed production planning features are available in the full platform.</p>
						<a href="/auth/register" class="inline-flex items-center justify-center px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg">
							Access Full Platform
						</a>
					</div>
				</div>

			<!-- Movie Posters Tab -->
			{:else if activeTab === 'posters'}
				<div class="space-y-8">
					<div class="text-center py-12">
						<div class="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
							<span class="text-2xl">🎨</span>
						</div>
						<h3 class="text-xl font-semibold text-gray-900 mb-2">AI-Generated Movie Posters</h3>
						<p class="text-gray-600 mb-6">Create stunning movie posters with AI visualization tools.</p>
						<a href="/auth/register" class="inline-flex items-center justify-center px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg">
							Create Posters
						</a>
					</div>
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