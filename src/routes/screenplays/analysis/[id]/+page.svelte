<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';

	let loading = true;
	let analysis: any = null;
	let error = '';
	let pollingInterval: ReturnType<typeof setInterval> | null = null;
	let activeTab = 'dashboard';
	let activeSection = 'core';
	let sidebarCollapsed = false;
	let isPublic = false;
	let isUpdatingPublicStatus = false;
	let publicShareToken = null;
	let showShareUrl = false;
	
	// Lazy loading for tabs
	let loadedTabs = new Set(['dashboard']); // Always load dashboard first
	let tabContentCache = new Map();

	const analysisId = $page.params.id;

	// Organized navigation structure
	const navigationSections = {
		core: {
			label: 'Core Analysis',
			icon: '📊',
			color: 'blue',
			tabs: [
				{ id: 'dashboard', label: 'Executive Dashboard', icon: '📈', description: 'Key metrics and overview' },
				{ id: 'story', label: 'Story & Craft', icon: '📖', description: 'Structure, characters, writing quality' },
				{ id: 'financial', label: 'Financial Intelligence', icon: '💰', description: 'ROI, box office, market analysis' }
			]
		},
		insights: {
			label: 'Professional Insights',
			icon: '🔍',
			color: 'purple',
			tabs: [
				{ id: 'grok', label: 'Reality Check', icon: '🔍', description: 'Honest industry assessment' },
				{ id: 'gpt5', label: 'Excellence Analysis', icon: '🧠', description: 'Writing craft evaluation' },
				{ id: 'genre', label: 'Genre Intelligence', icon: '🎬', description: 'Genre conventions & expectations' }
			]
		},
		business: {
			label: 'Market & Business',
			icon: '📈',
			color: 'green',
			tabs: [
				{ id: 'market', label: 'Market Intelligence', icon: '📊', description: 'Industry trends & positioning' },
				{ id: 'producer', label: 'Producer Dashboard', icon: '🎬', description: 'Production insights' },
				{ id: 'production', label: 'Production Planning', icon: '🎭', description: 'Logistics & scheduling' }
			]
		},
		creative: {
			label: 'Creative & Media',
			icon: '🎨',
			color: 'indigo',
			tabs: [
				{ id: 'media', label: 'Media Assets', icon: '🎨', description: 'Visual content & materials' },
				{ id: 'improvements', label: 'Enhancement Notes', icon: '💡', description: 'Recommendations & feedback' }
			]
		}
	};

	// Legacy tabs array for backward compatibility
	const tabs = Object.values(navigationSections).flatMap(section => section.tabs);

	// Smart polling with exponential backoff
	let pollInterval = 2000; // Start with 2 seconds
	let maxPollInterval = 10000; // Max 10 seconds
	let pollAttempts = 0;

	onMount(() => {
		fetchAnalysis();
		startSmartPolling();
		
		// Handle legacy URL parameters for backward compatibility
		const urlParams = new URLSearchParams(window.location.search);
		const legacyTab = urlParams.get('tab');
		if (legacyTab && legacyTab !== 'dashboard') {
			// Map old tab names to new ones if needed
			const tabMapping: Record<string, string> = {
				'overview': 'dashboard'
			};
			const mappedTab = tabMapping[legacyTab] || legacyTab;
			if (tabs.some(tab => tab.id === mappedTab)) {
				navigateToTab(mappedTab);
			}
		}

		// Cleanup on unmount
		return () => {
			if (pollingInterval) {
				clearInterval(pollingInterval);
			}
		};
	});

	function startSmartPolling() {
		if (pollingInterval) {
			clearInterval(pollingInterval);
		}

		pollingInterval = setInterval(() => {
			if (analysis?.status === 'processing') {
				fetchAnalysis();
				pollAttempts++;
				
				// Exponential backoff - increase interval gradually
				if (pollAttempts > 3) {
					pollInterval = Math.min(pollInterval * 1.5, maxPollInterval);
					if (pollingInterval) clearInterval(pollingInterval);
					pollingInterval = setInterval(() => {
						if (analysis?.status === 'processing') {
							fetchAnalysis();
							pollAttempts++;
							
							// Exponential backoff - increase interval gradually
							if (pollAttempts > 3) {
								pollInterval = Math.min(pollInterval * 1.5, maxPollInterval);
								clearInterval(pollingInterval!);
								pollingInterval = setInterval(() => {
									if (analysis?.status === 'processing') {
										fetchAnalysis();
									} else if (pollingInterval) {
										clearInterval(pollingInterval);
										pollingInterval = null;
										pollInterval = 2000;
										pollAttempts = 0;
									}
								}, pollInterval);
							}
						} else if (pollingInterval) {
							clearInterval(pollingInterval);
							pollingInterval = null;
							pollInterval = 2000;
							pollAttempts = 0;
						}
					}, pollInterval);
				}
			} else if (pollingInterval) {
				clearInterval(pollingInterval);
				pollingInterval = null;
				pollInterval = 2000; // Reset for next time
				pollAttempts = 0;
			}
		}, pollInterval);
	}

	async function fetchAnalysis() {
		try {
			const response = await fetch(`/api/screenplays/analysis/${analysisId}`);
			const data = await response.json();

			if (!response.ok) {
				throw new Error(data.error || 'Failed to fetch analysis');
			}

			analysis = data;
			isPublic = data.is_public || false;
			publicShareToken = data.public_share_token || null;
			loading = false;

			// Stop polling if analysis is complete or failed
			if (data.status !== 'processing' && pollingInterval) {
				clearInterval(pollingInterval);
				pollingInterval = null;
			}
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

	// New navigation helper functions
	function navigateToTab(tabId: string) {
		const section = Object.keys(navigationSections).find(sectionKey => 
			navigationSections[sectionKey as keyof typeof navigationSections].tabs.some((tab: any) => tab.id === tabId)
		);
		if (section) {
			activeSection = section;
		}
		activeTab = tabId;
		
		// Add to loaded tabs for lazy loading
		if (!loadedTabs.has(tabId)) {
			loadedTabs.add(tabId);
			loadedTabs = loadedTabs; // Trigger reactivity
		}
	}

	function getTabCompletionStatus(tabId: string): 'complete' | 'partial' | 'none' {
		if (!analysis?.result) return 'none';
		
		switch (tabId) {
			case 'dashboard':
				return 'complete';
			case 'story':
				return (analysis.result.structural_analysis || analysis.result.character_analysis) ? 'complete' : 'partial';
			case 'financial':
				return analysis.result.deepseek_financial_score ? 'complete' : 'partial';
			case 'grok':
				return analysis.result.grok_verdict ? 'complete' : 'none';
			case 'gpt5':
				return analysis.result.openai_verdict ? 'complete' : 'none';
			case 'genre':
				return analysis.result.genre ? 'complete' : 'partial';
			case 'market':
				return analysis.result.perplexity_market_score ? 'complete' : 'partial';
			case 'producer':
				return analysis.result.recommendations ? 'complete' : 'partial';
			case 'production':
				return 'partial';
			case 'media':
				return 'partial';
			case 'improvements':
				return analysis.result.recommendations ? 'partial' : 'none';
			default:
				return 'none';
		}
	}

	function getScoreForPreview(tabId: string): number | null {
		if (!analysis?.result) return null;
		
		switch (tabId) {
			case 'story':
				return analysis.result.overall_score || null;
			case 'financial':
				return analysis.result.deepseek_financial_score || null;
			case 'grok':
				return analysis.result.grok_score || null;
			case 'market':
				return analysis.result.perplexity_market_score || null;
			default:
				return null;
		}
	}

	function getSectionColor(sectionKey: string): string {
		return navigationSections[sectionKey as keyof typeof navigationSections]?.color || 'gray';
	}

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

	function cleanGrokVerdict(verdict: string): string {
		if (!verdict) return verdict;
		
		// Remove JSON formatting artifacts
		let cleaned = verdict.replace(/^"recommendation":\s*"/, '');
		cleaned = cleaned.replace(/",?\s*$/, '');
		cleaned = cleaned.replace(/\\"/g, '"');
		
		// If it still looks like JSON, try to extract the actual message
		if (cleaned.includes('"') && cleaned.includes(':')) {
			try {
				const parsed = JSON.parse('{' + cleaned + '}');
				return parsed.recommendation || parsed.verdict || cleaned;
			} catch {
				// If parsing fails, just clean up quotes
				return cleaned.replace(/^"|"$/g, '');
			}
		}
		
		return cleaned;
	}

	function getDemographicAudit(): any {
		// Try to get from raw response since it's not properly extracted to cultural_analysis
		const raw = analysis?.result?.grok_raw_response;
		if (raw && typeof raw === 'string') {
			try {
				const parsed = JSON.parse(raw);
				return parsed.demographic_authenticity_audit || null;
			} catch {
				return null;
			}
		}
		return null;
	}

	function getDiscourseEngine(): any {
		// Try to get from raw response since it's not properly extracted to cultural_analysis
		const raw = analysis?.result?.grok_raw_response;
		if (raw && typeof raw === 'string') {
			try {
				const parsed = JSON.parse(raw);
				return parsed.discourse_prediction_engine || null;
			} catch {
				return null;
			}
		}
		return null;
	}

	function getGenreFreshness(): any {
		// Try to get from raw response since it's not properly extracted to cultural_analysis
		const raw = analysis?.result?.grok_raw_response;
		if (raw && typeof raw === 'string') {
			try {
				const parsed = JSON.parse(raw);
				return parsed.genre_freshness_assessment || null;
			} catch {
				return null;
			}
		}
		return null;
	}

	function getMarketIntelligence(): any {
		// Try to get from raw response since it's not properly extracted to cultural_analysis
		const raw = analysis?.result?.grok_raw_response;
		if (raw && typeof raw === 'string') {
			try {
				const parsed = JSON.parse(raw);
				return parsed.market_positioning_intelligence || null;
			} catch {
				return null;
			}
		}
		return null;
	}

	// GPT-5 Helper Functions
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
			voice_consistency: parsed.voice_consistency_assessment || 'No assessment available',
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
			pacing_through_prose: parsed.pacing_through_prose || 'Not available',
			show_vs_tell_balance: parsed.show_vs_tell_balance || 'Not available'
		};
	}

	function getGPT5EmotionalBeats(): any {
		const v = analysis?.result?.gpt5_emotional_beat_mapping;
		if (!v) return null;
		if (typeof v === 'string') {
			try {
				return JSON.parse(v);
			} catch {
				return null;
			}
		}
		return v;
	}

	function getGPT5ProfessionalMarkers(): any {
		const v = analysis?.result?.gpt5_professional_markers;
		if (!v) return null;
		let parsed = v;
		if (typeof v === 'string') {
			try {
				parsed = JSON.parse(v);
			} catch {
				return null;
			}
		}
		
		// Extract and combine all professional marker arrays
		const markers = [];
		if (parsed.industry_standard_elements && Array.isArray(parsed.industry_standard_elements)) {
			markers.push(...parsed.industry_standard_elements);
		}
		if (parsed.professional_craft_indicators && Array.isArray(parsed.professional_craft_indicators)) {
			markers.push(...parsed.professional_craft_indicators);
		}
		if (parsed.studio_ready_aspects && Array.isArray(parsed.studio_ready_aspects)) {
			markers.push(...parsed.studio_ready_aspects);
		}
		
		return markers.length > 0 ? markers : ['No professional markers identified'];
	}

	function getGPT5AmateurIndicators(): any {
		const v = analysis?.result?.gpt5_amateur_indicators;
		if (!v) return null;
		let parsed = v;
		if (typeof v === 'string') {
			try {
				parsed = JSON.parse(v);
			} catch {
				return null;
			}
		}
		
		// Extract and combine all amateur indicator arrays
		const indicators = [];
		if (parsed.red_flag_elements && Array.isArray(parsed.red_flag_elements)) {
			indicators.push(...parsed.red_flag_elements);
		}
		if (parsed.craft_improvement_needs && Array.isArray(parsed.craft_improvement_needs)) {
			indicators.push(...parsed.craft_improvement_needs);
		}
		if (parsed.amateur_writing_patterns && Array.isArray(parsed.amateur_writing_patterns)) {
			indicators.push(...parsed.amateur_writing_patterns);
		}
		
		return indicators.length > 0 ? indicators : ['No amateur indicators identified'];
	}

	function getGPT5IndustryComparison(): any {
		const v = analysis?.result?.gpt5_industry_comparison;
		if (!v) return null;
		let parsed = v;
		if (typeof v === 'string') {
			try {
				parsed = JSON.parse(v);
			} catch {
				return null;
			}
		}
		
		// Return the parsed object with individual properties accessible
		return {
			comparable_scripts: parsed.comparable_professional_scripts || [],
			competitive_positioning: parsed.competitive_positioning || 'No comparison available',
			market_readiness: parsed.market_readiness_assessment || 'Assessment not available'
		};
	}

	function getGPT5ExecutiveAssessment(): any {
		const v = analysis?.result?.gpt5_executive_assessment;
		console.log('getGPT5ExecutiveAssessment:', {
			hasValue: !!v,
			type: typeof v,
			value: v ? (typeof v === 'string' ? v.substring(0, 100) + '...' : JSON.stringify(v).substring(0, 100) + '...') : null
		});
		if (!v) return null;
		
		// Handle placeholder values
		if (v === 'Analysis completed' || v === 'Analysis incomplete') {
			console.log('GPT5 assessment is placeholder:', v);
			return null;
		}
		
		if (typeof v === 'string') {
			try {
				const parsed = JSON.parse(v);
				console.log('Parsed GPT5 assessment:', Object.keys(parsed));
				return parsed;
			} catch (e) {
				console.error('Failed to parse GPT5 assessment:', e);
				return null;
			}
		}
		return v;
	}

	function hasGPT5Data(): boolean {
		const hasData = !!(analysis?.result?.gpt5_score || 
				analysis?.result?.gpt5_character_voice_analysis || 
				analysis?.result?.gpt5_dialogue_authenticity || 
				analysis?.result?.gpt5_prose_quality);
		console.log('hasGPT5Data check:', {
			hasData,
			gpt5_score: analysis?.result?.gpt5_score,
			gpt5_character_voice_analysis: !!analysis?.result?.gpt5_character_voice_analysis,
			gpt5_dialogue_authenticity: !!analysis?.result?.gpt5_dialogue_authenticity,
			gpt5_prose_quality: !!analysis?.result?.gpt5_prose_quality,
			gpt5_executive_assessment: !!analysis?.result?.gpt5_executive_assessment
		});
		return hasData;
	}

	function switchTab(tabId: string) {
		activeTab = tabId;
		
		// Mark tab as loaded for lazy loading
		if (!loadedTabs.has(tabId)) {
			loadedTabs.add(tabId);
			loadedTabs = loadedTabs; // Trigger reactivity
		}
	}

	async function togglePublicStatus() {
		if (isUpdatingPublicStatus) return;
		
		isUpdatingPublicStatus = true;
		try {
			const response = await fetch(`/api/screenplays/analysis/${analysisId}/public`, {
				method: 'PATCH',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({ is_public: !isPublic })
			});

			if (!response.ok) {
				throw new Error('Failed to update sharing status');
			}

			const data = await response.json();
			isPublic = data.is_public;
			publicShareToken = data.public_share_token;
			
			// Show success message and share URL
			if (isPublic) {
				console.log('Analysis is now publicly sharable');
				showShareUrl = true;
				setTimeout(() => showShareUrl = false, 5000); // Hide after 5 seconds
			} else {
				console.log('Analysis is now private');
				showShareUrl = false;
			}
		} catch (err) {
			console.error('Failed to update sharing status:', err);
			// Revert the toggle on error
		} finally {
			isUpdatingPublicStatus = false;
		}
	}

	function copyShareUrl() {
		if (publicShareToken) {
			const shareUrl = `${window.location.origin}/public/analysis/${publicShareToken}`;
			navigator.clipboard.writeText(shareUrl).then(() => {
				console.log('Share URL copied to clipboard');
			}).catch(err => {
				console.error('Failed to copy URL:', err);
			});
		}
	}

</script>

<svelte:head>
	<title>Analysis Results - {analysis?.result?.title || 'Screenplay'} - Quilty</title>
</svelte:head>

{#if loading}
	<div class="min-h-screen bg-gray-50 flex items-center justify-center">
		<div class="text-center">
			<div class="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto mb-4"></div>
			<h2 class="text-xl font-semibold text-gray-900 mb-2">Loading Analysis...</h2>
			<p class="text-gray-600">Please wait while we fetch your professional analysis.</p>
		</div>
	</div>
{:else if error}
	<div class="min-h-screen bg-gray-50 flex items-center justify-center">
		<div class="text-center">
			<div class="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
				<svg class="w-8 h-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
				</svg>
			</div>
			<h2 class="text-xl font-semibold text-gray-900 mb-2">Error Loading Analysis</h2>
			<p class="text-gray-600 mb-4">{error}</p>
			<button 
				on:click={() => goto('/screenplays')}
				class="btn-primary"
			>
				Back to Screenplays
			</button>
		</div>
	</div>
{:else if analysis?.status === 'processing'}
	<div class="min-h-screen bg-gray-50 flex items-center justify-center">
		<div class="text-center">
			<div class="animate-pulse">
				<div class="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
					<svg class="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
					</svg>
				</div>
			</div>
			<h2 class="text-xl font-semibold text-gray-900 mb-2">Analysis in Progress</h2>
			<p class="text-gray-600 mb-4">Our analysis engine is evaluating your screenplay...</p>
			<div class="w-64 bg-gray-200 rounded-full h-2 mx-auto">
				<div class="bg-blue-600 h-2 rounded-full animate-pulse" style="width: 60%"></div>
			</div>
			<p class="text-sm text-gray-500 mt-4">This usually takes 15-30 seconds</p>
			<button 
				on:click={() => goto('/screenplays')}
				class="btn-secondary mt-4"
			>
				Back to Screenplays
			</button>
		</div>
	</div>
{:else if analysis?.status === 'error'}
	<div class="min-h-screen bg-gray-50 flex items-center justify-center">
		<div class="text-center">
			<div class="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
				<svg class="w-8 h-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
				</svg>
			</div>
			<h2 class="text-xl font-semibold text-gray-900 mb-2">Analysis Failed</h2>
			<p class="text-gray-600 mb-4">
				{analysis.error_message || 'The screenplay analysis encountered an error and could not be completed.'}
			</p>
			<div class="space-x-4">
				<button 
					on:click={() => goto('/screenplays/upload')}
					class="btn-primary"
				>
					Try Another Upload
				</button>
				<button 
					on:click={() => goto('/screenplays')}
					class="btn-secondary"
				>
					Back to Screenplays
				</button>
			</div>
		</div>
	</div>
{:else if analysis?.result}
	<!-- Analysis Results -->
	<div class="min-h-screen bg-gray-50">
		<!-- Header -->
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
								
								<!-- Budget Category Badge -->
								{#if analysis.result.user_proposed_budget}
									{@const budget = parseFloat(analysis.result.user_proposed_budget)}
									{@const category = budget < 1000000 ? 'Micro-budget' : budget < 5000000 ? 'Low-budget' : budget < 20000000 ? 'Mid-budget' : budget < 50000000 ? 'High-budget' : 'Tentpole'}
									{#if budget < 1000000}
										<span class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-gray-100 text-gray-800">
											💰 {category} (${(budget/1000000).toFixed(1)}M)
										</span>
									{:else if budget < 5000000}
										<span class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800">
											💰 {category} (${(budget/1000000).toFixed(0)}M)
										</span>
									{:else if budget < 20000000}
										<span class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800">
											💰 {category} (${(budget/1000000).toFixed(0)}M)
										</span>
									{:else if budget < 50000000}
										<span class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-orange-100 text-orange-800">
											💰 {category} (${(budget/1000000).toFixed(0)}M)
										</span>
									{:else}
										<span class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-purple-100 text-purple-800">
											💰 {category} (${(budget/1000000).toFixed(0)}M)
										</span>
									{/if}
								{:else if analysis.result.ai_budget_optimal}
									{@const budget = parseFloat(analysis.result.ai_budget_optimal)}
									{@const category = budget < 1000000 ? 'Micro-budget' : budget < 5000000 ? 'Low-budget' : budget < 20000000 ? 'Mid-budget' : budget < 50000000 ? 'High-budget' : 'Tentpole'}
									{#if budget < 1000000}
										<span class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-gray-100 text-gray-800">
											📊 Est: {category} (${(budget/1000000).toFixed(1)}M)
										</span>
									{:else if budget < 5000000}
										<span class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800">
											📊 Est: {category} (${(budget/1000000).toFixed(0)}M)
										</span>
									{:else if budget < 20000000}
										<span class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800">
											📊 Est: {category} (${(budget/1000000).toFixed(0)}M)
										</span>
									{:else if budget < 50000000}
										<span class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-orange-100 text-orange-800">
											📊 Est: {category} (${(budget/1000000).toFixed(0)}M)
										</span>
									{:else}
										<span class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-purple-100 text-purple-800">
											📊 Est: {category} (${(budget/1000000).toFixed(0)}M)
										</span>
									{/if}
								{/if}
								
								<!-- Source Material Badge -->
								{#if analysis.result.source_has_material}
									<span class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-orange-100 text-orange-800">
										📚 {analysis.result.source_type?.replace('_', ' ').toUpperCase() || 'ADAPTATION'}
									</span>
								{:else if analysis.result.source_success}
									<span class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800">
										✨ ORIGINAL
									</span>
								{/if}
								
								<span class="text-sm text-gray-500">
									Professional Analysis
								</span>
								<span class="text-sm text-gray-500">
									${parseFloat(analysis.result.cost || 0).toFixed(4)} cost
								</span>
								{#if analysis.created_at}
									<span class="text-sm text-gray-500">
										📅 {formatDate(analysis.created_at)}
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
							{:else}
								<div class="text-center opacity-50">
									<div class="text-2xl font-bold bg-gray-100 text-gray-400 px-3 py-2 rounded-lg">
										--/10
									</div>
									<div class="text-xs text-gray-400 mt-1">Reality Score</div>
									<div class="text-xs text-gray-400 mt-1">Brutal Honesty</div>
									<div class="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-gray-100 text-gray-400 border border-gray-200 mt-1">
										Unavailable
									</div>
								</div>
							{/if}
							
							<!-- Commercial Score -->
							{#if analysis.result.openai_score}
								<div class="text-center">
									<div class="text-2xl font-bold {getScoreColor(analysis.result.openai_score)} px-3 py-2 rounded-lg">
										{analysis.result.openai_score}/10
									</div>
									<div class="text-xs text-gray-500 mt-1">Commercial Score</div>
									<div class="text-xs text-gray-400 mt-1">Market Viability</div>
									<div class="inline-flex items-center px-2 py-1 rounded text-xs font-medium border {getRecommendationColor(analysis.result.openai_recommendation)} mt-1">
										{analysis.result.openai_recommendation}
									</div>
								</div>
							{:else}
								<div class="text-center opacity-50">
									<div class="text-2xl font-bold bg-gray-100 text-gray-400 px-3 py-2 rounded-lg">
										--/10
									</div>
									<div class="text-xs text-gray-400 mt-1">Commercial Score</div>
									<div class="text-xs text-gray-400 mt-1">Market Viability</div>
									<div class="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-gray-100 text-gray-400 border border-gray-200 mt-1">
										Unavailable
									</div>
								</div>
							{/if}
						</div>
						
						<!-- Make Sharable Toggle -->
						<div class="flex items-center space-x-3 ml-6">
							<span class="text-sm font-medium text-gray-700">Make Sharable:</span>
							<button
								on:click={togglePublicStatus}
								disabled={isUpdatingPublicStatus}
								class="relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 {isPublic ? 'bg-blue-600' : 'bg-gray-200'} {isUpdatingPublicStatus ? 'opacity-50 cursor-not-allowed' : ''}"
								role="switch"
								aria-checked={isPublic}
								aria-label="Toggle public sharing"
							>
								<span class="inline-block h-4 w-4 transform rounded-full bg-white transition-transform {isPublic ? 'translate-x-6' : 'translate-x-1'}"></span>
							</button>
							{#if isPublic}
								<span class="text-xs text-green-600 font-medium">🌐 Public</span>
							{:else}
								<span class="text-xs text-gray-500 font-medium">🔒 Private</span>
							{/if}
							{#if isUpdatingPublicStatus}
								<div class="animate-spin h-4 w-4 border-2 border-blue-600 border-t-transparent rounded-full"></div>
							{/if}
						</div>
					</div>

					<!-- Share URL Display -->
					{#if isPublic && publicShareToken && (showShareUrl || isPublic)}
						<div class="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg">
							<div class="flex items-center justify-between">
								<div class="flex-1">
									<p class="text-sm font-medium text-green-800 mb-2">🌐 Public Share URL:</p>
									<div class="flex items-center space-x-2">
										<input 
											type="text" 
											readonly 
											value="{window?.location?.origin || ''}/public/analysis/{publicShareToken}"
											class="flex-1 px-3 py-2 text-sm bg-white border border-green-300 rounded-md text-gray-700 font-mono"
										/>
										<button 
											on:click={copyShareUrl}
											class="px-3 py-2 bg-green-600 hover:bg-green-700 text-white text-sm font-medium rounded-md transition-colors"
										>
											Copy
										</button>
									</div>
								</div>
							</div>
							<p class="text-xs text-green-600 mt-2">Anyone with this link can view your analysis results without signing in.</p>
						</div>
					{/if}

					<!-- Analysis Verdicts - Only show on dashboard -->
					{#if activeTab === 'overview'}
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
											<p class="text-purple-900 font-medium italic">"{cleanGrokVerdict(analysis.result.grok_verdict)}"</p>
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
						
						<!-- Excellence Analysis Verdict -->
						{#if getGPT5ExecutiveAssessment() && getGPT5ExecutiveAssessment().professional_verdict}
							{@const gpt5Assessment = getGPT5ExecutiveAssessment()}
							<div class="bg-blue-50 border-l-4 border-blue-400 p-4 rounded-md">
								<div class="flex items-start">
									<div class="flex-shrink-0">
										<span class="text-blue-600 font-semibold text-sm">WRITING EXCELLENCE:</span>
									</div>
									<div class="ml-3">
										<p class="text-blue-900 font-medium italic">"{gpt5Assessment.professional_verdict}"</p>
									</div>
								</div>
							</div>
						{/if}
						</div>
					{/if}





				</div>
			</div>
		</div>

		<!-- Main Content Layout with Sidebar -->
		<div class="flex h-screen">
			<!-- Sidebar Navigation -->
			<div class="bg-white border-r border-gray-200 {sidebarCollapsed ? 'w-16' : 'w-80'} flex-shrink-0 transition-all duration-300 overflow-y-auto">
				<!-- Sidebar Header -->
				<div class="p-4 border-b border-gray-200">
					<div class="flex items-center justify-between">
						{#if !sidebarCollapsed}
							<h2 class="text-lg font-semibold text-gray-900">Analysis Navigation</h2>
						{/if}
						<button 
							on:click={() => sidebarCollapsed = !sidebarCollapsed}
							class="p-2 rounded-md hover:bg-gray-100 transition-colors"
							aria-label={sidebarCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
						>
							<svg class="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
							</svg>
						</button>
					</div>
				</div>

				<!-- Navigation Sections -->
				<div class="p-4 space-y-6">
					{#each Object.entries(navigationSections) as [sectionKey, section]}
						<div class="space-y-2">
							<!-- Section Header -->
							{#if !sidebarCollapsed}
								<div class="flex items-center space-x-2 px-2 py-1">
									<span class="text-lg">{section.icon}</span>
									<h3 class="text-sm font-semibold text-gray-700 uppercase tracking-wide">{section.label}</h3>
								</div>
							{:else}
								<div class="flex justify-center py-1">
									<span class="text-xl" title={section.label}>{section.icon}</span>
								</div>
							{/if}

							<!-- Section Tabs -->
							<div class="space-y-1">
								{#each section.tabs as tab}
									{@const status = getTabCompletionStatus(tab.id)}
									{@const score = getScoreForPreview(tab.id)}
									<button
										class="w-full text-left p-3 rounded-lg transition-all duration-200 group relative {
											activeTab === tab.id
												? (section.color === 'blue' ? 'bg-blue-50 border border-blue-200 text-blue-700' :
												   section.color === 'purple' ? 'bg-purple-50 border border-purple-200 text-purple-700' :
												   section.color === 'green' ? 'bg-green-50 border border-green-200 text-green-700' :
												   section.color === 'indigo' ? 'bg-indigo-50 border border-indigo-200 text-indigo-700' :
												   'bg-gray-50 border border-gray-200 text-gray-700')
												: 'hover:bg-gray-50 text-gray-600 hover:text-gray-900'
										}"
										on:click={() => navigateToTab(tab.id)}
									>
										<div class="flex items-center space-x-3">
											<span class="text-lg">{tab.icon}</span>
											{#if !sidebarCollapsed}
												<div class="flex-1 min-w-0">
													<div class="flex items-center justify-between">
														<span class="font-medium truncate">{tab.label}</span>
														<div class="flex items-center space-x-2">
															{#if score !== null}
																<span class="text-xs font-bold px-2 py-1 rounded-full {getScoreColor(score)}">{score}/10</span>
															{/if}
															<div class="w-2 h-2 rounded-full {
																status === 'complete' ? 'bg-green-400' : 
																status === 'partial' ? 'bg-yellow-400' : 'bg-gray-300'
															}"></div>
														</div>
													</div>
													<p class="text-xs text-gray-500 mt-1 truncate">{tab.description}</p>
												</div>
											{/if}
										</div>
									</button>
								{/each}
							</div>
						</div>
					{/each}
				</div>
			</div>

			<!-- Main Content Area -->
			<div class="flex-1 overflow-y-auto bg-gray-50">
				<div class="max-w-6xl mx-auto px-6 py-8">
			{#if activeTab === 'dashboard'}
				<!-- Executive Dashboard -->
				<div class="space-y-8">
					<!-- Dashboard Header -->
					<div class="bg-gradient-to-r from-blue-600 via-purple-600 to-blue-800 rounded-xl p-8 text-white">
						<div class="text-center">
							<h1 class="text-3xl font-bold mb-2">Executive Analysis Dashboard</h1>
							<p class="text-blue-100 text-lg">Comprehensive screenplay evaluation and investment intelligence</p>
						</div>
					</div>

					<!-- Key Metrics Grid -->
					<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
						<!-- Overall Score -->
						{#if analysis.result.overall_score}
							<div class="bg-white rounded-xl shadow-lg border border-gray-200 p-6 text-center">
								<div class="mb-3">
									<div class="w-16 h-16 bg-gradient-to-br from-blue-400 to-blue-600 rounded-full flex items-center justify-center mx-auto">
										<span class="text-white text-xl font-bold">{analysis.result.overall_score}</span>
									</div>
								</div>
								<h3 class="text-lg font-semibold text-gray-900 mb-1">Overall Score</h3>
								<div class="w-full bg-gray-200 rounded-full h-2">
									<div class="bg-gradient-to-r from-blue-400 to-blue-600 h-2 rounded-full transition-all duration-500" 
										 style="width: {(analysis.result.overall_score / 10) * 100}%"></div>
								</div>
							</div>
						{/if}

						<!-- Financial Score -->
						{#if analysis.result.deepseek_financial_score}
							<div class="bg-white rounded-xl shadow-lg border border-gray-200 p-6 text-center">
								<div class="mb-3">
									<div class="w-16 h-16 bg-gradient-to-br from-green-400 to-green-600 rounded-full flex items-center justify-center mx-auto">
										<span class="text-white text-xl font-bold">{analysis.result.deepseek_financial_score}</span>
									</div>
								</div>
								<h3 class="text-lg font-semibold text-gray-900 mb-1">Financial Viability</h3>
								<div class="w-full bg-gray-200 rounded-full h-2">
									<div class="bg-gradient-to-r from-green-400 to-green-600 h-2 rounded-full transition-all duration-500" 
										 style="width: {(analysis.result.deepseek_financial_score / 10) * 100}%"></div>
								</div>
							</div>
						{/if}

						<!-- Market Score -->
						{#if analysis.result.perplexity_market_score}
							<div class="bg-white rounded-xl shadow-lg border border-gray-200 p-6 text-center">
								<div class="mb-3">
									<div class="w-16 h-16 bg-gradient-to-br from-purple-400 to-purple-600 rounded-full flex items-center justify-center mx-auto">
										<span class="text-white text-xl font-bold">{analysis.result.perplexity_market_score}</span>
									</div>
								</div>
								<h3 class="text-lg font-semibold text-gray-900 mb-1">Market Potential</h3>
								<div class="w-full bg-gray-200 rounded-full h-2">
									<div class="bg-gradient-to-r from-purple-400 to-purple-600 h-2 rounded-full transition-all duration-500" 
										 style="width: {(analysis.result.perplexity_market_score / 10) * 100}%"></div>
								</div>
							</div>
						{/if}

						<!-- Investment Recommendation -->
						{#if analysis.result.recommendation}
							<div class="bg-white rounded-xl shadow-lg border border-gray-200 p-6 text-center">
								<div class="mb-3">
									<div class="w-16 h-16 bg-gradient-to-br from-yellow-400 to-orange-500 rounded-full flex items-center justify-center mx-auto">
										<span class="text-white text-2xl">🎯</span>
									</div>
								</div>
								<h3 class="text-lg font-semibold text-gray-900 mb-1">Recommendation</h3>
								<span class="inline-block px-3 py-1 rounded-full text-sm font-medium {getRecommendationColor(analysis.result.recommendation)}">
									{analysis.result.recommendation}
								</span>
							</div>
						{/if}
					</div>

					<!-- AI Verdicts Row -->
					<div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
						<!-- Claude Verdict -->
						{#if analysis.result.one_line_verdict}
							<div class="bg-gradient-to-br from-blue-50 to-indigo-50 border border-blue-200 rounded-xl p-6">
								<div class="flex items-start space-x-4">
									<div class="flex-shrink-0">
										<div class="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
											<span class="text-blue-600 font-bold">C</span>
										</div>
									</div>
									<div class="flex-1">
										<h4 class="text-lg font-semibold text-blue-900 mb-2">Craft Analysis</h4>
										<p class="text-blue-800 italic font-medium">"{analysis.result.one_line_verdict}"</p>
									</div>
								</div>
							</div>
						{/if}
						
						<!-- Grok Verdict -->
						{#if analysis.result.grok_verdict && analysis.result.grok_verdict !== 'Analysis incomplete'}
							<div class="bg-gradient-to-br from-purple-50 to-violet-50 border border-purple-200 rounded-xl p-6">
								<div class="flex items-start space-x-4">
									<div class="flex-shrink-0">
										<div class="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center">
											<span class="text-purple-600 font-bold">G</span>
										</div>
									</div>
									<div class="flex-1">
										<h4 class="text-lg font-semibold text-purple-900 mb-2">Reality Check</h4>
										<p class="text-purple-800 italic font-medium">"{cleanGrokVerdict(analysis.result.grok_verdict)}"</p>
									</div>
								</div>
							</div>
						{/if}
						
						<!-- OpenAI Verdict -->
						{#if analysis.result.openai_verdict && analysis.result.openai_verdict !== 'Analysis incomplete' && analysis.result.openai_verdict !== 'Analysis completed'}
							<div class="bg-gradient-to-br from-green-50 to-emerald-50 border border-green-200 rounded-xl p-6">
								<div class="flex items-start space-x-4">
									<div class="flex-shrink-0">
										<div class="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center">
											<span class="text-green-600 font-bold">O</span>
										</div>
									</div>
									<div class="flex-1">
										<h4 class="text-lg font-semibold text-green-900 mb-2">Commercial Analysis</h4>
										<p class="text-green-800 italic font-medium">"{analysis.result.openai_verdict}"</p>
									</div>
								</div>
							</div>
						{/if}
					</div>

					<!-- Quick Insights Grid -->
					<div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
						<!-- Analysis Preview Cards -->
						<div class="space-y-4">
							<h3 class="text-xl font-bold text-gray-900 mb-4">Analysis Overview</h3>
							
							{#each Object.values(navigationSections) as section}
								<div class="bg-white rounded-lg shadow-sm border border-gray-200 hover:shadow-md transition-shadow">
									<div class="p-4">
										<div class="flex items-center justify-between">
											<div class="flex items-center space-x-3">
												<span class="text-2xl">{section.icon}</span>
												<div>
													<h4 class="font-semibold text-gray-900">{section.label}</h4>
													<p class="text-sm text-gray-500">{section.tabs.length} analysis areas</p>
												</div>
											</div>
											<button 
												on:click={() => navigateToTab(section.tabs[0].id)}
												class="px-4 py-2 rounded-lg transition-colors text-sm font-medium {
													section.color === 'blue' ? 'bg-blue-50 text-blue-700 hover:bg-blue-100' :
													section.color === 'purple' ? 'bg-purple-50 text-purple-700 hover:bg-purple-100' :
													section.color === 'green' ? 'bg-green-50 text-green-700 hover:bg-green-100' :
													section.color === 'indigo' ? 'bg-indigo-50 text-indigo-700 hover:bg-indigo-100' :
													'bg-gray-50 text-gray-700 hover:bg-gray-100'
												}"
											>
												View Details
											</button>
										</div>
										
										<!-- Section tabs preview -->
										<div class="mt-3 flex flex-wrap gap-2">
											{#each section.tabs as tab}
												{@const status = getTabCompletionStatus(tab.id)}
												<div class="flex items-center space-x-1 text-xs">
													<div class="w-2 h-2 rounded-full {
														status === 'complete' ? 'bg-green-400' : 
														status === 'partial' ? 'bg-yellow-400' : 'bg-gray-300'
													}"></div>
													<span class="text-gray-600">{tab.label}</span>
												</div>
											{/each}
										</div>
									</div>
								</div>
							{/each}
						</div>

						<!-- Project Details & Key Info -->
						<div class="space-y-6">
							<!-- Logline -->
							{#if analysis.result.logline}
								<div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
									<h3 class="text-lg font-bold text-gray-900 mb-3 flex items-center">
										<span class="text-blue-600 mr-2">🎬</span>
										Logline
									</h3>
									<p class="text-gray-700 italic text-lg leading-relaxed">"{analysis.result.logline}"</p>
								</div>
							{/if}

							<!-- Strengths & Weaknesses -->
							<div class="grid grid-cols-1 gap-4">
								<!-- Strengths -->
								{#if parseJsonField(analysis.result.top_strengths).length > 0}
									<div class="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
										<h4 class="font-semibold text-gray-900 mb-3 flex items-center">
											<span class="text-green-600 mr-2">✅</span>
											Top Strengths
										</h4>
										<ul class="space-y-2">
											{#each parseJsonField(analysis.result.top_strengths).slice(0, 3) as strength}
												<li class="flex items-start text-sm">
													<span class="flex-shrink-0 text-green-600 mr-2 mt-0.5">•</span>
													<span class="text-gray-700">{strength}</span>
												</li>
											{/each}
										</ul>
									</div>
								{/if}

								<!-- Weaknesses -->
								{#if parseJsonField(analysis.result.key_weaknesses).length > 0}
									<div class="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
										<h4 class="font-semibold text-gray-900 mb-3 flex items-center">
											<span class="text-orange-600 mr-2">⚠️</span>
											Key Areas for Improvement
										</h4>
										<ul class="space-y-2">
											{#each parseJsonField(analysis.result.key_weaknesses).slice(0, 3) as weakness}
												<li class="flex items-start text-sm">
													<span class="flex-shrink-0 text-orange-600 mr-2 mt-0.5">•</span>
													<span class="text-gray-700">{weakness}</span>
												</li>
											{/each}
										</ul>
									</div>
								{/if}
							</div>
						</div>
					</div>
				</div>

			{:else if activeTab === 'story'}
				<!-- Story Analysis Tab (Structure + Characters + Themes) -->
				<div class="space-y-8">
					<!-- Structural Analysis -->
					<div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
						<h3 class="text-xl font-bold text-gray-900 mb-4 flex items-center">
							<span class="text-blue-600 mr-2">🏗️</span>
							Structural Analysis
						</h3>
						{#if analysis.result.structural_analysis}
							<div class="prose max-w-none text-gray-700">
								{@html analysis.result.structural_analysis.replace(/\n/g, '<br>')}
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
								{@html analysis.result.character_analysis.replace(/\n/g, '<br>')}
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
								{@html analysis.result.craft_evaluation.replace(/\n/g, '<br>')}
							</div>
						{:else}
							<p class="text-gray-500 italic">Craft evaluation will be available in enhanced results.</p>
						{/if}
					</div>

					<!-- Thematic Depth -->
					<div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
						<h3 class="text-xl font-bold text-gray-900 mb-4 flex items-center">
							<span class="text-indigo-600 mr-2">🎭</span>
							Thematic Depth
						</h3>
						{#if analysis.result.thematic_depth}
							<div class="prose max-w-none text-gray-700">
								{@html analysis.result.thematic_depth.replace(/\n/g, '<br>')}
							</div>
						{:else}
							<p class="text-gray-500 italic">Thematic analysis will be available in enhanced results.</p>
						{/if}
					</div>
				</div>

			{:else if activeTab === 'genre'}
				<!-- Genre Tab -->
				<div class="space-y-6">
					<!-- Genre Classification -->
					<div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
						<h3 class="text-xl font-bold text-gray-900 mb-4 flex items-center">
							<span class="text-red-600 mr-2">🎬</span>
							Genre Classification
						</h3>
						<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
							<!-- Primary Genre -->
							<div class="bg-red-50 border border-red-200 rounded-lg p-4">
								<h4 class="font-semibold text-red-900 mb-2">Primary Genre</h4>
								<span class="inline-flex items-center px-3 py-2 rounded-lg text-lg font-medium bg-red-100 text-red-800">
									{analysis.result.genre || analysis.result.detected_genre || 'Not specified'}
								</span>
							</div>
							
							<!-- Subgenre -->
							{#if analysis.result.subgenre}
								<div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
									<h4 class="font-semibold text-blue-900 mb-2">Subgenre</h4>
									<span class="inline-flex items-center px-3 py-2 rounded-lg text-lg font-medium bg-blue-100 text-blue-800">
										{analysis.result.subgenre}
									</span>
								</div>
							{/if}
							
							<!-- Detected Genre (if different) -->
							{#if analysis.result.detected_genre && analysis.result.detected_genre !== analysis.result.genre}
								<div class="bg-orange-50 border border-orange-200 rounded-lg p-4">
									<h4 class="font-semibold text-orange-900 mb-2">AI-Detected Genre</h4>
									<span class="inline-flex items-center px-3 py-2 rounded-lg text-lg font-medium bg-orange-100 text-orange-800">
										{analysis.result.detected_genre}
									</span>
								</div>
							{/if}
						</div>
					</div>

					<!-- Genre Mastery Analysis -->
					<div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
						<h3 class="text-xl font-bold text-gray-900 mb-4 flex items-center">
							<span class="text-red-600 mr-2">🎭</span>
							Genre Mastery Analysis
						</h3>
						{#if analysis.result.genre_mastery}
							<div class="prose max-w-none text-gray-700">
								{@html analysis.result.genre_mastery.replace(/\n/g, '<br>')}
							</div>
						{:else}
							<p class="text-gray-500 italic">Genre mastery analysis will be available in enhanced results.</p>
						{/if}
					</div>
				</div>

			{:else if activeTab === 'grok'}
				<!-- Grok Analysis Tab -->
				<div class="space-y-6">
					{#if analysis.result.grok_score || analysis.result.grok_cultural_analysis || analysis.result.grok_brutal_honesty || analysis.result.grok_controversy_analysis}
						<!-- Grok Overview -->
						<div class="bg-gradient-to-r from-purple-50 to-indigo-50 rounded-lg border border-purple-200 p-6">
							<div class="flex items-center justify-between mb-4">
								<h3 class="text-xl font-bold text-gray-900 flex items-center">
									<span class="text-purple-600 mr-2">🤖</span>
									Grok 4 Internet-Native Analysis
								</h3>
								<div class="text-right">
									{#if analysis.result.grok_score}
										<div class="text-2xl font-bold {getScoreColor(analysis.result.grok_score)}">
											{analysis.result.grok_score}/10
										</div>
										<div class="text-sm text-gray-500">Brutally Honest Score</div>
									{/if}
								</div>
							</div>
							{#if analysis.result.grok_verdict}
								<div class="bg-white rounded-lg p-4 border border-purple-200">
									<p class="text-purple-900 font-medium italic">"{analysis.result.grok_verdict}"</p>
								</div>
							{/if}
						</div>

						<!-- Cultural Reality Check -->
						{#if analysis.result.grok_cultural_analysis}
							<div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
								<h3 class="text-xl font-bold text-gray-900 mb-4 flex items-center">
									<span class="text-pink-600 mr-2">🎭</span>
									Cultural Reality Check
								</h3>
								<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
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
									<!-- Protagonist Likability -->
									<div class="p-4 bg-red-50 rounded-lg border border-red-200">
										<div class="text-sm font-medium text-red-800 mb-2 flex items-center">
											<span class="mr-1">👤</span>
											Protagonist Likability
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
									<!-- Representation Risk -->
									<div class="p-4 bg-amber-50 rounded-lg border border-amber-200">
										<div class="text-sm font-medium text-amber-800 mb-2 flex items-center">
											<span class="mr-1">🎭</span>
											Representation Issues
										</div>
										<div class="text-sm text-amber-700 leading-relaxed">
											{getControversy().representation_risk || 'Low risk'}
										</div>
									</div>
									
									<!-- Backlash Potential -->
									<div class="p-4 bg-red-50 rounded-lg border border-red-200">
										<div class="text-sm font-medium text-red-800 mb-2 flex items-center">
											<span class="mr-1">🔥</span>
											PR Nightmare Risk
										</div>
										<div class="text-sm text-red-700 leading-relaxed">
											{getControversy().backlash_potential || 'Minimal backlash expected'}
										</div>
									</div>
									
									<!-- Polarization Level -->
									<div class="p-4 bg-purple-50 rounded-lg border border-purple-200">
										<div class="text-sm font-medium text-purple-800 mb-2 flex items-center">
											<span class="mr-1">⚡</span>
											Polarization Risk
										</div>
										<div class="text-sm text-purple-700 leading-relaxed">
											{getControversy().polarization_level || 'Low polarization'}
										</div>
									</div>
									
									<!-- Boundary Assessment -->
									<div class="p-4 bg-gray-50 rounded-lg border border-gray-200">
										<div class="text-sm font-medium text-gray-800 mb-2 flex items-center">
											<span class="mr-1">🎯</span>
											Edgy vs Offensive
										</div>
										<div class="text-sm text-gray-700 leading-relaxed">
											{getControversy().boundary_assessment || 'Within acceptable boundaries'}
										</div>
									</div>
								</div>
							</div>
						{/if}
						
						<!-- Demographic Authenticity Audit -->
						{#if getDemographicAudit()}
							<div class="bg-white rounded-lg shadow-sm border border-blue-200 p-6">
								<h3 class="text-xl font-bold text-gray-900 mb-4 flex items-center">
									<span class="text-blue-600 mr-2">🔍</span>
									Demographic Authenticity Audit
									<span class="ml-2 text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded-full">Reality Check</span>
								</h3>
								<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
									<!-- Gen Z Dialogue -->
									<div class="p-4 bg-blue-50 rounded-lg border border-blue-200">
										<div class="text-sm font-medium text-blue-800 mb-2 flex items-center">
											<span class="mr-1">💬</span>
											Gen Z Dialogue Authenticity
										</div>
										<div class="text-sm text-blue-700 leading-relaxed">
											{getDemographicAudit().gen_z_dialogue_authenticity || 'Not assessed'}
										</div>
									</div>
									
									<!-- Subculture Authenticity -->
									<div class="p-4 bg-blue-50 rounded-lg border border-blue-200">
										<div class="text-sm font-medium text-blue-800 mb-2 flex items-center">
											<span class="mr-1">🎯</span>
											Subculture Authenticity
										</div>
										<div class="text-sm text-blue-700 leading-relaxed">
											{getDemographicAudit().subculture_authenticity_rating || 'Not assessed'}
										</div>
									</div>
									
									<!-- Social Media Realism -->
									<div class="p-4 bg-blue-50 rounded-lg border border-blue-200">
										<div class="text-sm font-medium text-blue-800 mb-2 flex items-center">
											<span class="mr-1">📱</span>
											Social Media Realism
										</div>
										<div class="text-sm text-blue-700 leading-relaxed">
											{getDemographicAudit().social_media_realism || 'Not assessed'}
										</div>
									</div>
									
									<!-- Demographic Accuracy -->
									<div class="p-4 bg-blue-50 rounded-lg border border-blue-200">
										<div class="text-sm font-medium text-blue-800 mb-2 flex items-center">
											<span class="mr-1">👥</span>
											Demographic Accuracy
										</div>
										<div class="text-sm text-blue-700 leading-relaxed">
											{getDemographicAudit().demographic_accuracy || 'Not assessed'}
										</div>
									</div>
								</div>
							</div>
						{/if}
						
						<!-- Discourse Prediction Engine -->
						{#if getDiscourseEngine()}
							<div class="bg-white rounded-lg shadow-sm border border-red-200 p-6">
								<h3 class="text-xl font-bold text-gray-900 mb-4 flex items-center">
									<span class="text-red-600 mr-2">🔮</span>
									Discourse Prediction Engine
									<span class="ml-2 text-xs bg-red-100 text-red-700 px-2 py-1 rounded-full">Internet Drama</span>
								</h3>
								<div class="space-y-4">
									<!-- Think Piece Titles -->
									{#if getDiscourseEngine().think_piece_titles && getDiscourseEngine().think_piece_titles.length > 0}
										<div class="p-4 bg-red-50 rounded-lg border border-red-200">
											<div class="text-sm font-medium text-red-800 mb-2 flex items-center">
												<span class="mr-1">📰</span>
												Predicted Think-Piece Titles
											</div>
											<div class="space-y-2">
												{#each getDiscourseEngine().think_piece_titles as title}
													<div class="text-sm text-red-700 bg-white p-2 rounded border border-red-100">
														"{title}"
													</div>
												{/each}
											</div>
										</div>
									{/if}
									
									<!-- Twitter Drama Assessment -->
									<div class="p-4 bg-red-50 rounded-lg border border-red-200">
										<div class="text-sm font-medium text-red-800 mb-2 flex items-center">
											<span class="mr-1">🐦</span>
											Twitter Drama Assessment
										</div>
										<div class="text-sm text-red-700 leading-relaxed">
											{getDiscourseEngine().twitter_drama_assessment || 'Low drama potential'}
										</div>
									</div>
									
									<!-- Quote Tweet Predictions -->
									{#if getDiscourseEngine().quote_tweet_predictions && getDiscourseEngine().quote_tweet_predictions.length > 0}
										<div class="p-4 bg-red-50 rounded-lg border border-red-200">
											<div class="text-sm font-medium text-red-800 mb-2 flex items-center">
												<span class="mr-1">💬</span>
												Quote Tweet Predictions
											</div>
											<div class="space-y-2">
												{#each getDiscourseEngine().quote_tweet_predictions as prediction}
													<div class="text-sm text-red-700 bg-white p-2 rounded border border-red-100">
														"{prediction}"
													</div>
												{/each}
											</div>
										</div>
									{/if}
									
									<!-- Viral Moment Scanner -->
									<div class="p-4 bg-red-50 rounded-lg border border-red-200">
										<div class="text-sm font-medium text-red-800 mb-2 flex items-center">
											<span class="mr-1">🔥</span>
											Viral Moment Scanner
										</div>
										<div class="text-sm text-red-700 leading-relaxed">
											{getDiscourseEngine().viral_moment_scanner || 'No obvious viral moments'}
										</div>
									</div>
								</div>
							</div>
						{/if}
						
						<!-- Genre Freshness Assessment -->
						{#if getGenreFreshness()}
							<div class="bg-white rounded-lg shadow-sm border border-green-200 p-6">
								<h3 class="text-xl font-bold text-gray-900 mb-4 flex items-center">
									<span class="text-green-600 mr-2">🎬</span>
									Genre Freshness Assessment
									<span class="ml-2 text-xs bg-green-100 text-green-700 px-2 py-1 rounded-full">Innovation Check</span>
								</h3>
								<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
									<!-- Innovation Scale -->
									<div class="p-4 bg-green-50 rounded-lg border border-green-200">
										<div class="text-sm font-medium text-green-800 mb-2 flex items-center">
											<span class="mr-1">⚡</span>
											Innovation Scale
										</div>
										<div class="text-sm text-green-700 leading-relaxed">
											{getGenreFreshness().innovation_scale || 'Standard execution'}
										</div>
									</div>
									
									<!-- Twitter Joke Fodder -->
									<div class="p-4 bg-green-50 rounded-lg border border-green-200">
										<div class="text-sm font-medium text-green-800 mb-2 flex items-center">
											<span class="mr-1">😂</span>
											Twitter Joke Fodder
										</div>
										<div class="text-sm text-green-700 leading-relaxed">
											{getGenreFreshness().twitter_joke_fodder || 'No obvious joke fodder'}
										</div>
									</div>
									
									<!-- Self-Awareness Check -->
									<div class="p-4 bg-green-50 rounded-lg border border-green-200">
										<div class="text-sm font-medium text-green-800 mb-2 flex items-center">
											<span class="mr-1">🪞</span>
											Self-Awareness Check
										</div>
										<div class="text-sm text-green-700 leading-relaxed">
											{getGenreFreshness().self_awareness_check || 'Self-awareness unclear'}
										</div>
									</div>
									
									<!-- Freshness Reality -->
									<div class="p-4 bg-green-50 rounded-lg border border-green-200">
										<div class="text-sm font-medium text-green-800 mb-2 flex items-center">
											<span class="mr-1">🌟</span>
											Freshness Reality
										</div>
										<div class="text-sm text-green-700 leading-relaxed">
											{getGenreFreshness().freshness_reality || 'Freshness assessment needed'}
										</div>
									</div>
								</div>
							</div>
						{/if}
						
						<!-- Market Positioning Intelligence -->
						{#if getMarketIntelligence()}
							<div class="bg-white rounded-lg shadow-sm border border-indigo-200 p-6">
								<h3 class="text-xl font-bold text-gray-900 mb-4 flex items-center">
									<span class="text-indigo-600 mr-2">📊</span>
									Market Positioning Intelligence
									<span class="ml-2 text-xs bg-indigo-100 text-indigo-700 px-2 py-1 rounded-full">Brutal Reality</span>
								</h3>
								<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
									<!-- Platform Fit -->
									<div class="p-4 bg-indigo-50 rounded-lg border border-indigo-200">
										<div class="text-sm font-medium text-indigo-800 mb-2 flex items-center">
											<span class="mr-1">📺</span>
											Platform Fit
										</div>
										<div class="text-sm text-indigo-700 leading-relaxed">
											{getMarketIntelligence().platform_fit || 'Platform unclear'}
										</div>
									</div>
									
									<!-- Target Demo Reality -->
									<div class="p-4 bg-indigo-50 rounded-lg border border-indigo-200">
										<div class="text-sm font-medium text-indigo-800 mb-2 flex items-center">
											<span class="mr-1">🎯</span>
											Target Demo Reality
										</div>
										<div class="text-sm text-indigo-700 leading-relaxed">
											{getMarketIntelligence().target_demo_reality || 'Target unclear'}
										</div>
									</div>
									
									<!-- Oscar Bait Detection -->
									<div class="p-4 bg-indigo-50 rounded-lg border border-indigo-200">
										<div class="text-sm font-medium text-indigo-800 mb-2 flex items-center">
											<span class="mr-1">🏆</span>
											Oscar Bait Detection
										</div>
										<div class="text-sm text-indigo-700 leading-relaxed">
											{getMarketIntelligence().oscar_bait_detection || 'Oscar potential unclear'}
										</div>
									</div>
									
									<!-- Comp Title Brutality -->
									<div class="p-4 bg-indigo-50 rounded-lg border border-indigo-200">
										<div class="text-sm font-medium text-indigo-800 mb-2 flex items-center">
											<span class="mr-1">⚔️</span>
											Comp Title Brutality
										</div>
										<div class="text-sm text-indigo-700 leading-relaxed">
											{getMarketIntelligence().comp_title_brutality || 'Comparison needed'}
										</div>
									</div>
								</div>
							</div>
						{/if}
					{:else}
						<!-- No Grok Analysis Available -->
						<div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6 text-center">
							<div class="text-gray-400 text-6xl mb-4">🤖</div>
							<h3 class="text-xl font-semibold text-gray-900 mb-2">Grok Analysis Unavailable</h3>
							<p class="text-gray-600 mb-4">This analysis was completed before Grok 4 integration was available.</p>
							<p class="text-sm text-gray-500">Re-analyze your screenplay to get brutally honest, internet-native feedback from Grok 4.</p>
						</div>
								{/if}
		</div>

		{:else if activeTab === 'gpt5'}
			<!-- GPT-5 Writing Excellence Tab -->
			<div class="space-y-6">
				{#if hasGPT5Data()}
					<!-- GPT-5 Overview -->
					<div class="bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg border border-blue-200 p-6">
						<div class="flex items-center justify-between mb-4">
							<h3 class="text-xl font-bold text-gray-900 flex items-center">
								<span class="text-blue-600 mr-2">🧠</span>
								GPT-5 Writing Excellence Analysis
							</h3>
							<div class="text-right">
								{#if analysis.result.gpt5_score}
									<div class="text-2xl font-bold {getScoreColor(analysis.result.gpt5_score)}">
										{analysis.result.gpt5_score}/10
									</div>
									<div class="text-sm text-gray-500">Writing Excellence Score</div>
								{/if}
							</div>
						</div>
						{#if getGPT5ExecutiveAssessment()}
							{@const gpt5Assessment = getGPT5ExecutiveAssessment()}
							<div class="bg-white rounded-lg p-4 border border-blue-200">
								<div class="space-y-3">
									{#if gpt5Assessment.professional_verdict}
										<p class="text-blue-900 font-medium italic">"{gpt5Assessment.professional_verdict}"</p>
									{/if}
									{#if gpt5Assessment.quick_impressions}
										<div class="text-sm text-blue-800 bg-blue-50 p-3 rounded border-l-4 border-blue-300">
											<div class="font-medium mb-1">Quick Impressions:</div>
											<div>{gpt5Assessment.quick_impressions}</div>
										</div>
									{/if}
									{#if gpt5Assessment.deep_analysis}
										<div class="text-sm text-blue-800 bg-blue-50 p-3 rounded border-l-4 border-blue-300">
											<div class="font-medium mb-1">Deep Analysis:</div>
											<div>{gpt5Assessment.deep_analysis}</div>
										</div>
									{/if}
								</div>
							</div>
						{/if}
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
							{#if getGPT5CharacterVoice().voice_consistency}
								<div class="mt-4 p-4 bg-gray-50 rounded-lg border border-gray-200">
									<div class="text-sm font-medium text-gray-800 mb-2">Voice Consistency Analysis</div>
									<div class="text-sm text-gray-700 leading-relaxed">
										{getGPT5CharacterVoice().voice_consistency}
									</div>
								</div>
							{/if}
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

					<!-- Professional vs Amateur Markers -->
					{#if getGPT5ProfessionalMarkers() || getGPT5AmateurIndicators()}
						<div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
							<h3 class="text-xl font-bold text-gray-900 mb-4 flex items-center">
								<span class="text-amber-600 mr-2">🏆</span>
								Professional Standards Analysis
							</h3>
							<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
								{#if getGPT5ProfessionalMarkers()}
									<div class="p-4 bg-green-50 rounded-lg border border-green-200">
										<div class="text-sm font-medium text-green-800 mb-2 flex items-center">
											<span class="mr-1">✅</span>
											Professional Markers
										</div>
										<div class="text-sm text-green-700 leading-relaxed">
											{#if Array.isArray(getGPT5ProfessionalMarkers())}
												<ul class="list-disc list-inside space-y-1">
													{#each getGPT5ProfessionalMarkers() as marker}
														<li>{marker}</li>
													{/each}
												</ul>
											{:else}
												{getGPT5ProfessionalMarkers()}
											{/if}
										</div>
									</div>
								{/if}
								{#if getGPT5AmateurIndicators()}
									<div class="p-4 bg-red-50 rounded-lg border border-red-200">
										<div class="text-sm font-medium text-red-800 mb-2 flex items-center">
											<span class="mr-1">⚠️</span>
											Amateur Indicators
										</div>
										<div class="text-sm text-red-700 leading-relaxed">
											{#if Array.isArray(getGPT5AmateurIndicators())}
												<ul class="list-disc list-inside space-y-1">
													{#each getGPT5AmateurIndicators() as indicator}
														<li>{indicator}</li>
													{/each}
												</ul>
											{:else}
												{getGPT5AmateurIndicators()}
											{/if}
										</div>
									</div>
								{/if}
							</div>
						</div>
					{/if}

					<!-- Industry Comparison -->
					{#if getGPT5IndustryComparison()}
						<div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
							<h3 class="text-xl font-bold text-gray-900 mb-4 flex items-center">
								<span class="text-blue-600 mr-2">🏆</span>
								Industry Comparison
							</h3>
							<div class="space-y-4">
								<div class="p-4 bg-blue-50 rounded-lg border border-blue-200">
									<div class="text-sm font-medium text-blue-800 mb-2 flex items-center">
										<span class="mr-1">📊</span>
										Competitive Positioning
									</div>
									<div class="text-sm text-blue-700 leading-relaxed">
										{getGPT5IndustryComparison().competitive_positioning}
									</div>
								</div>
								<div class="p-4 bg-blue-50 rounded-lg border border-blue-200">
									<div class="text-sm font-medium text-blue-800 mb-2 flex items-center">
										<span class="mr-1">🎯</span>
										Market Readiness Assessment
									</div>
									<div class="text-sm text-blue-700 leading-relaxed">
										{getGPT5IndustryComparison().market_readiness}
									</div>
								</div>
								{#if getGPT5IndustryComparison().comparable_scripts && getGPT5IndustryComparison().comparable_scripts.length > 0}
									<div class="p-4 bg-blue-50 rounded-lg border border-blue-200">
										<div class="text-sm font-medium text-blue-800 mb-2 flex items-center">
											<span class="mr-1">🎬</span>
											Comparable Professional Scripts
										</div>
										<div class="text-sm text-blue-700 leading-relaxed">
											<ul class="list-disc list-inside space-y-1">
												{#each getGPT5IndustryComparison().comparable_scripts as script}
													<li>{script}</li>
												{/each}
											</ul>
										</div>
									</div>
								{/if}
							</div>
						</div>
					{/if}

				{:else}
					<!-- No GPT-5 Analysis Available -->
					<div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6 text-center">
						<div class="text-gray-400 text-6xl mb-4">🧠</div>
						<h3 class="text-xl font-semibold text-gray-900 mb-2">GPT-5 Analysis Unavailable</h3>
						<p class="text-gray-600 mb-4">GPT-5 Writing Excellence analysis was not completed for this screenplay.</p>
						<p class="text-sm text-gray-500">This may be due to analysis failure or the feature not being available when this analysis was run.</p>
					</div>
				{/if}
			</div>

		{:else if activeTab === 'financial'}
			<!-- Financial Intelligence Tab -->
			<div class="space-y-8">
				{#if analysis.result.deepseek_financial_score || analysis.result.deepseek_box_office_prediction}
					<!-- Header with AI Badge -->
					<div class="bg-gradient-to-r from-emerald-500 via-blue-600 to-purple-600 rounded-xl p-1 shadow-lg">
						<div class="bg-white rounded-lg p-6">
							<div class="flex items-center justify-between">
								<div class="flex items-center space-x-3">
									<span class="text-3xl">💰</span>
									<div>
										<h2 class="text-2xl font-bold text-gray-900">Financial Analysis & Box Office Prediction</h2>
										<p class="text-gray-600">Comprehensive investment intelligence powered by AI</p>
									</div>
								</div>
								<div class="flex items-center space-x-2">
									<span class="text-xs bg-gradient-to-r from-blue-100 to-purple-100 text-blue-800 px-3 py-2 rounded-full font-medium">DeepSeek AI</span>
									<span class="text-xs bg-green-100 text-green-800 px-3 py-2 rounded-full font-medium">Real-time Analysis</span>
								</div>
							</div>
						</div>
					</div>

					<!-- 1. EXECUTIVE SUMMARY SECTION -->
					{#if analysis.result.deepseek_financial_score}
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
					{/if}

					<!-- 2. BOX OFFICE & REVENUE SECTION -->
					<div class="bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden">
						<div class="bg-gradient-to-r from-yellow-50 to-orange-50 px-6 py-4 border-b border-gray-200">
							<h3 class="text-xl font-bold text-gray-900 flex items-center">
								<span class="text-yellow-600 mr-3">🎯</span>
								Box Office & Revenue Projections
							</h3>
						</div>
						<div class="p-6 space-y-6">
							<!-- Box Office Predictions -->
							{#if analysis.result.deepseek_box_office_prediction}
								{@const prediction = typeof analysis.result.deepseek_box_office_prediction === 'string' 
									? JSON.parse(analysis.result.deepseek_box_office_prediction) 
									: analysis.result.deepseek_box_office_prediction}
								
								{#if prediction}
									<div>
										<h4 class="text-lg font-semibold text-gray-900 mb-4 flex items-center">
											<span class="text-blue-500 mr-2">📈</span>
											Box Office Prediction Model
										</h4>
										<div class="grid grid-cols-1 md:grid-cols-3 gap-4">
											{#if prediction.conservative_scenario}
												<div class="bg-gradient-to-br from-red-50 to-red-100 border border-red-200 rounded-xl p-6 text-center transform hover:scale-105 transition-transform duration-200">
													<div class="text-red-800 font-semibold mb-2 flex items-center justify-center">
														<span class="mr-2">📉</span>
														Conservative (P10)
													</div>
													<div class="text-3xl font-bold text-red-600 mb-2">
														${prediction.conservative_scenario?.toLocaleString()}
													</div>
													<div class="text-sm text-red-600 bg-red-100 px-3 py-1 rounded-full">10% chance of doing worse</div>
												</div>
											{/if}
											{#if prediction.expected_scenario}
												<div class="bg-gradient-to-br from-yellow-50 to-yellow-100 border border-yellow-300 rounded-xl p-6 text-center transform hover:scale-105 transition-transform duration-200 ring-2 ring-yellow-300">
													<div class="text-yellow-800 font-semibold mb-2 flex items-center justify-center">
														<span class="mr-2">📊</span>
														Expected (P50)
													</div>
													<div class="text-3xl font-bold text-yellow-700 mb-2">
														${prediction.expected_scenario?.toLocaleString()}
													</div>
													<div class="text-sm text-yellow-700 bg-yellow-100 px-3 py-1 rounded-full">Most likely outcome</div>
												</div>
											{/if}
											{#if prediction.optimistic_scenario}
												<div class="bg-gradient-to-br from-green-50 to-green-100 border border-green-200 rounded-xl p-6 text-center transform hover:scale-105 transition-transform duration-200">
													<div class="text-green-800 font-semibold mb-2 flex items-center justify-center">
														<span class="mr-2">📈</span>
														Optimistic (P90)
													</div>
													<div class="text-3xl font-bold text-green-600 mb-2">
														${prediction.optimistic_scenario?.toLocaleString()}
													</div>
													<div class="text-sm text-green-600 bg-green-100 px-3 py-1 rounded-full">10% chance of doing better</div>
												</div>
											{/if}
										</div>
										
										<!-- Methodology & Reasoning -->
										{#if prediction.methodology_explanation || prediction.why_these_numbers}
											<div class="mt-6 bg-gray-50 rounded-xl p-6 border border-gray-200">
												<h5 class="font-semibold text-gray-900 mb-4 flex items-center">
													<span class="text-blue-500 mr-2">🔬</span>
													Analysis Methodology
												</h5>
												<div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
													{#if prediction.methodology_explanation}
														<div>
															<div class="text-sm font-medium text-gray-700 mb-2">How We Calculated These Numbers</div>
															<div class="text-sm text-gray-600 leading-relaxed">{prediction.methodology_explanation}</div>
														</div>
													{/if}
													{#if prediction.why_these_numbers}
														<div>
															<div class="text-sm font-medium text-gray-700 mb-2">Why This Range Makes Sense</div>
															<div class="text-sm text-gray-600 leading-relaxed">{prediction.why_these_numbers}</div>
														</div>
													{/if}
												</div>
											</div>
										{/if}
									</div>
								{/if}
							{/if}

							<!-- Geographic Revenue Split - Coming Soon -->
							<div class="bg-purple-50 rounded-xl p-6 border border-purple-200">
								<h4 class="text-lg font-semibold text-gray-900 mb-3 flex items-center">
									<span class="text-purple-500 mr-2">🌍</span>
									Geographic Revenue Distribution
									<span class="ml-2 text-xs bg-purple-100 text-purple-700 px-2 py-1 rounded-full">Coming Soon</span>
								</h4>
								<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
									<div class="bg-blue-50 rounded-lg p-4 border border-blue-200">
										<div class="flex items-center justify-between mb-2">
											<span class="font-medium text-blue-900">🇺🇸 Domestic Analysis</span>
											<span class="text-sm text-blue-600">US/Canada Markets</span>
										</div>
										<div class="text-sm text-blue-800">Detailed domestic market breakdown and performance projections</div>
									</div>
									<div class="bg-green-50 rounded-lg p-4 border border-green-200">
										<div class="flex items-center justify-between mb-2">
											<span class="font-medium text-green-900">🌏 International Analysis</span>
											<span class="text-sm text-green-600">Global Markets</span>
										</div>
										<div class="text-sm text-green-800">International market opportunities and revenue potential</div>
									</div>
								</div>
							</div>

							<!-- Platform Revenue Analysis -->
							{#if analysis.result.deepseek_platform_analysis}
								{@const platform = typeof analysis.result.deepseek_platform_analysis === 'string' 
									? JSON.parse(analysis.result.deepseek_platform_analysis) 
									: analysis.result.deepseek_platform_analysis}
								{#if platform}
									<div>
										<h4 class="text-lg font-semibold text-gray-900 mb-4 flex items-center">
											<span class="text-indigo-500 mr-2">📱</span>
											Distribution & Platform Analysis
										</h4>
										
										{#if platform.streaming_deal_scenarios}
											<div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
												{#if platform.streaming_deal_scenarios.netflix_acquisition_estimate}
													<div class="bg-red-50 border border-red-200 rounded-lg p-4 text-center">
														<div class="text-red-800 font-semibold mb-2 flex items-center justify-center">
															<span class="mr-2">🎬</span>
															Netflix Acquisition
														</div>
														<div class="text-xl font-bold text-red-600">${platform.streaming_deal_scenarios.netflix_acquisition_estimate?.toLocaleString()}</div>
													</div>
												{/if}
												{#if platform.streaming_deal_scenarios.day_and_date_streaming}
													<div class="bg-yellow-50 border border-yellow-200 rounded-lg p-4 text-center">
														<div class="text-yellow-800 font-semibold mb-2 flex items-center justify-center">
															<span class="mr-2">⚡</span>
															Day-and-Date
														</div>
														<div class="text-xl font-bold text-yellow-600">${platform.streaming_deal_scenarios.day_and_date_streaming?.toLocaleString()}</div>
													</div>
												{/if}
												{#if platform.streaming_deal_scenarios.streaming_exclusive_value}
													<div class="bg-blue-50 border border-blue-200 rounded-lg p-4 text-center">
														<div class="text-blue-800 font-semibold mb-2 flex items-center justify-center">
															<span class="mr-2">💻</span>
															Streaming Exclusive
														</div>
														<div class="text-xl font-bold text-blue-600">${platform.streaming_deal_scenarios.streaming_exclusive_value?.toLocaleString()}</div>
													</div>
												{/if}
											</div>
										{/if}
										
										{#if platform.platform_strategy_explanation}
											<div class="bg-indigo-50 rounded-lg p-4 border border-indigo-200">
												<div class="text-sm font-medium text-indigo-900 mb-2">💡 Platform Strategy Recommendation</div>
												<div class="text-sm text-indigo-800">{platform.platform_strategy_explanation}</div>
											</div>
										{/if}
									</div>
								{/if}
							{/if}

							<!-- ROI Metrics -->
							{#if analysis.result.deepseek_roi_analysis}
								{@const roi = typeof analysis.result.deepseek_roi_analysis === 'string' 
									? JSON.parse(analysis.result.deepseek_roi_analysis) 
									: analysis.result.deepseek_roi_analysis}
								
								{#if roi}
									<div>
										<h4 class="text-lg font-semibold text-gray-900 mb-4 flex items-center">
											<span class="text-emerald-500 mr-2">💎</span>
											Return on Investment Analysis
										</h4>
										<div class="grid grid-cols-2 md:grid-cols-4 gap-4">
											{#if roi.expected_roi_percentage}
												<div class="bg-blue-50 border border-blue-200 rounded-xl p-4 text-center">
													<div class="text-blue-800 font-semibold mb-2 text-sm">Expected ROI</div>
													<div class="text-2xl font-bold text-blue-600">{roi.expected_roi_percentage}%</div>
												</div>
											{/if}
											{#if roi.break_even_point}
												<div class="bg-purple-50 border border-purple-200 rounded-xl p-4 text-center">
													<div class="text-purple-800 font-semibold mb-2 text-sm">Break Even</div>
													<div class="text-xl font-bold text-purple-600">${roi.break_even_point?.toLocaleString()}</div>
												</div>
											{/if}
											{#if roi.payback_period_months}
												<div class="bg-indigo-50 border border-indigo-200 rounded-xl p-4 text-center">
													<div class="text-indigo-800 font-semibold mb-2 text-sm">Payback Period</div>
													<div class="text-xl font-bold text-indigo-600">{roi.payback_period_months}mo</div>
												</div>
											{/if}
											{#if roi.internal_rate_return}
												<div class="bg-teal-50 border border-teal-200 rounded-xl p-4 text-center">
													<div class="text-teal-800 font-semibold mb-2 text-sm">IRR</div>
													<div class="text-xl font-bold text-teal-600">{roi.internal_rate_return}%</div>
												</div>
											{/if}
										</div>
									</div>
								{/if}
							{/if}
						</div>
					</div>

					<!-- 3. BUDGET & INVESTMENT SECTION -->
					{#if analysis.result.deepseek_budget_optimization}
						{@const budget = typeof analysis.result.deepseek_budget_optimization === 'string' 
							? JSON.parse(analysis.result.deepseek_budget_optimization) 
							: analysis.result.deepseek_budget_optimization}
						
						{#if budget}
							<div class="bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden">
								<div class="bg-gradient-to-r from-emerald-50 to-teal-50 px-6 py-4 border-b border-gray-200">
									<h3 class="text-xl font-bold text-gray-900 flex items-center">
										<span class="text-emerald-600 mr-3">💰</span>
										Budget & Investment Optimization
									</h3>
								</div>
								<div class="p-6 space-y-6">
									<!-- Budget Range Recommendations -->
									{#if budget.recommended_budget_range}
										<div>
											<h4 class="text-lg font-semibold text-gray-900 mb-4 flex items-center">
												<span class="text-green-500 mr-2">🎯</span>
												Recommended Budget Range
											</h4>
											<div class="grid grid-cols-1 md:grid-cols-3 gap-4">
												{#if budget.recommended_budget_range.minimum}
													<div class="bg-yellow-50 border border-yellow-200 rounded-xl p-6 text-center">
														<div class="text-yellow-800 font-semibold mb-2">💡 Minimum Viable</div>
														<div class="text-2xl font-bold text-yellow-600">${budget.recommended_budget_range.minimum?.toLocaleString()}</div>
														<div class="text-sm text-yellow-600 mt-2">Lean production</div>
													</div>
												{/if}
												{#if budget.recommended_budget_range.optimal}
													<div class="bg-green-50 border border-green-300 rounded-xl p-6 text-center ring-2 ring-green-300">
														<div class="text-green-800 font-semibold mb-2">⭐ Optimal</div>
														<div class="text-2xl font-bold text-green-600">${budget.recommended_budget_range.optimal?.toLocaleString()}</div>
														<div class="text-sm text-green-600 mt-2">Best ROI potential</div>
													</div>
												{/if}
												{#if budget.recommended_budget_range.maximum}
													<div class="bg-blue-50 border border-blue-200 rounded-xl p-6 text-center">
														<div class="text-blue-800 font-semibold mb-2">🚀 Maximum</div>
														<div class="text-2xl font-bold text-blue-600">${budget.recommended_budget_range.maximum?.toLocaleString()}</div>
														<div class="text-sm text-blue-600 mt-2">Premium production</div>
													</div>
												{/if}
											</div>
										</div>
									{/if}

									<!-- Cost Allocation Breakdown -->
									{#if budget.cost_allocation_recommendations}
										<div>
											<h4 class="text-lg font-semibold text-gray-900 mb-4 flex items-center">
												<span class="text-purple-500 mr-2">📊</span>
												Budget Allocation Strategy
											</h4>
											<div class="grid grid-cols-2 md:grid-cols-4 gap-4">
												{#if budget.cost_allocation_recommendations.above_line}
													<div class="bg-red-50 border border-red-200 rounded-lg p-4 text-center">
														<div class="text-red-800 font-semibold mb-1 text-sm">Above-the-Line</div>
														<div class="text-lg font-bold text-red-600">${budget.cost_allocation_recommendations.above_line?.toLocaleString()}</div>
														<div class="text-xs text-red-600 mt-1">Cast, Director, Producer</div>
													</div>
												{/if}
												{#if budget.cost_allocation_recommendations.below_line}
													<div class="bg-blue-50 border border-blue-200 rounded-lg p-4 text-center">
														<div class="text-blue-800 font-semibold mb-1 text-sm">Below-the-Line</div>
														<div class="text-lg font-bold text-blue-600">${budget.cost_allocation_recommendations.below_line?.toLocaleString()}</div>
														<div class="text-xs text-blue-600 mt-1">Crew, Equipment, Locations</div>
													</div>
												{/if}
												{#if budget.cost_allocation_recommendations.post_production}
													<div class="bg-green-50 border border-green-200 rounded-lg p-4 text-center">
														<div class="text-green-800 font-semibold mb-1 text-sm">Post-Production</div>
														<div class="text-lg font-bold text-green-600">${budget.cost_allocation_recommendations.post_production?.toLocaleString()}</div>
														<div class="text-xs text-green-600 mt-1">Editing, VFX, Sound</div>
													</div>
												{/if}
												{#if budget.cost_allocation_recommendations.marketing}
													<div class="bg-purple-50 border border-purple-200 rounded-lg p-4 text-center">
														<div class="text-purple-800 font-semibold mb-1 text-sm">Marketing</div>
														<div class="text-lg font-bold text-purple-600">${budget.cost_allocation_recommendations.marketing?.toLocaleString()}</div>
														<div class="text-xs text-purple-600 mt-1">P&A, Distribution</div>
													</div>
												{/if}
											</div>
										</div>
									{/if}

									<!-- Efficiency Opportunities -->
									{#if budget.efficiency_opportunities && budget.efficiency_opportunities.length > 0}
										<div class="bg-amber-50 rounded-xl p-6 border border-amber-200">
											<h5 class="font-semibold text-amber-900 mb-4 flex items-center">
												<span class="text-amber-600 mr-2">💡</span>
												Cost Optimization Opportunities
											</h5>
											<div class="grid grid-cols-1 md:grid-cols-2 gap-3">
												{#each budget.efficiency_opportunities as opportunity}
													<div class="text-sm text-amber-800 bg-amber-100 px-4 py-3 rounded-lg border border-amber-200 flex items-start">
														<span class="text-amber-600 mr-2 mt-0.5">✨</span>
														{opportunity}
													</div>
												{/each}
											</div>
										</div>
									{/if}
								</div>
							</div>
						{/if}
					{/if}

					<!-- 4. PRODUCTION INTELLIGENCE SECTION -->
					{#if analysis.result.deepseek_production_optimization}
						<div class="bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden">
							<div class="bg-gradient-to-r from-blue-50 to-indigo-50 px-6 py-4 border-b border-gray-200">
								<h3 class="text-xl font-bold text-gray-900 flex items-center">
									<span class="text-blue-600 mr-3">🏭</span>
									Production Intelligence
								</h3>
							</div>
							<div class="p-6 space-y-6">
								<!-- Production Optimization -->
								{#if analysis.result.deepseek_production_optimization}
									{@const production = typeof analysis.result.deepseek_production_optimization === 'string' 
										? JSON.parse(analysis.result.deepseek_production_optimization) 
										: analysis.result.deepseek_production_optimization}
									
									{#if production}
										<div>
											<h4 class="text-lg font-semibold text-gray-900 mb-4 flex items-center">
												<span class="text-indigo-500 mr-2">⚙️</span>
												Production Optimization
											</h4>
											<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
												{#if production.optimal_shooting_schedule}
													<div class="bg-indigo-50 rounded-lg p-4 border border-indigo-200">
														<div class="text-sm font-medium text-indigo-900 mb-2">📅 Shooting Schedule</div>
														<div class="text-sm text-indigo-800">{production.optimal_shooting_schedule}</div>
													</div>
												{/if}
												{#if production.crew_size_optimization}
													<div class="bg-blue-50 rounded-lg p-4 border border-blue-200">
														<div class="text-sm font-medium text-blue-900 mb-2">👥 Crew Optimization</div>
														<div class="text-sm text-blue-800">{production.crew_size_optimization}</div>
													</div>
												{/if}
												{#if production.location_cost_efficiency}
													<div class="bg-green-50 rounded-lg p-4 border border-green-200">
														<div class="text-sm font-medium text-green-900 mb-2">📍 Location Strategy</div>
														<div class="text-sm text-green-800">{production.location_cost_efficiency}</div>
													</div>
												{/if}
												{#if production.equipment_rental_strategy}
													<div class="bg-purple-50 rounded-lg p-4 border border-purple-200">
														<div class="text-sm font-medium text-purple-900 mb-2">🎥 Equipment Strategy</div>
														<div class="text-sm text-purple-800">{production.equipment_rental_strategy}</div>
													</div>
												{/if}
											</div>
										</div>
									{/if}
								{/if}

								<!-- Cast ROI Analysis - Coming Soon -->
								<div class="bg-yellow-50 rounded-xl p-6 border border-yellow-200">
									<h4 class="text-lg font-semibold text-gray-900 mb-4 flex items-center">
										<span class="text-yellow-500 mr-2">⭐</span>
										Cast ROI Strategy
										<span class="ml-2 text-xs bg-yellow-100 text-yellow-700 px-2 py-1 rounded-full">Coming Soon</span>
									</h4>
									<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
										<div class="bg-yellow-100 rounded-lg p-4 border border-yellow-300">
											<div class="text-sm font-medium text-yellow-900 mb-2">🌟 Star Power Analysis</div>
											<div class="text-sm text-yellow-800">Celebrity casting impact on box office performance</div>
										</div>
										<div class="bg-orange-100 rounded-lg p-4 border border-orange-300">
											<div class="text-sm font-medium text-orange-900 mb-2">💰 Cost-Benefit Modeling</div>
											<div class="text-sm text-orange-800">Cast investment vs projected revenue return</div>
										</div>
									</div>
								</div>

								<!-- Location Cost Analysis - Coming Soon -->
								<div class="bg-green-50 rounded-xl p-6 border border-green-200">
									<h4 class="text-lg font-semibold text-gray-900 mb-4 flex items-center">
										<span class="text-green-500 mr-2">📍</span>
										Location Cost Analysis
										<span class="ml-2 text-xs bg-green-100 text-green-700 px-2 py-1 rounded-full">Coming Soon</span>
									</h4>
									<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
										<div class="bg-green-100 rounded-lg p-4 border border-green-300">
											<div class="text-sm font-medium text-green-900 mb-2">💡 Cost-Effective Locations</div>
											<div class="text-sm text-green-800">Optimized filming locations for budget efficiency</div>
										</div>
										<div class="bg-blue-100 rounded-lg p-4 border border-blue-300">
											<div class="text-sm font-medium text-blue-900 mb-2">🎯 Tax Incentive Opportunities</div>
											<div class="text-sm text-blue-800">Available tax credits and production incentives</div>
										</div>
									</div>
								</div>
							</div>
						</div>
					{/if}

					<!-- 5. MARKET & STRATEGY SECTION -->
					<div class="bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden">
						<div class="bg-gradient-to-r from-purple-50 to-pink-50 px-6 py-4 border-b border-gray-200">
							<h3 class="text-xl font-bold text-gray-900 flex items-center">
								<span class="text-purple-600 mr-3">📈</span>
								Market Intelligence & Strategy
								<span class="ml-2 text-xs bg-purple-100 text-purple-700 px-2 py-1 rounded-full">Enhanced Analysis</span>
							</h3>
						</div>
						<div class="p-6 space-y-6">
							<!-- Market Analysis - Coming Soon -->
							<div class="bg-purple-50 rounded-xl p-6 border border-purple-200">
								<h4 class="text-lg font-semibold text-gray-900 mb-4 flex items-center">
									<span class="text-purple-500 mr-2">📊</span>
									Market Conditions & Volatility
									<span class="ml-2 text-xs bg-purple-100 text-purple-700 px-2 py-1 rounded-full">Coming Soon</span>
								</h4>
								<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
									<div class="bg-purple-100 rounded-lg p-4 border border-purple-300">
										<div class="text-sm font-medium text-purple-900 mb-2">🎬 Genre Stability Analysis</div>
										<div class="text-sm text-purple-800">Market performance trends for your specific genre</div>
									</div>
									<div class="bg-orange-100 rounded-lg p-4 border border-orange-300">
										<div class="text-sm font-medium text-orange-900 mb-2">💹 Economic Sensitivity</div>
										<div class="text-sm text-orange-800">Impact of economic conditions on box office performance</div>
									</div>
								</div>
							</div>

							<!-- Competitive Analysis - Coming Soon -->
							<div class="bg-red-50 rounded-xl p-6 border border-red-200">
								<h4 class="text-lg font-semibold text-gray-900 mb-4 flex items-center">
									<span class="text-red-500 mr-2">⚔️</span>
									Competitive Landscape
									<span class="ml-2 text-xs bg-red-100 text-red-700 px-2 py-1 rounded-full">Coming Soon</span>
								</h4>
								<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
									<div class="bg-red-100 rounded-lg p-4 border border-red-300">
										<div class="text-sm font-medium text-red-900 mb-2">🎯 Similar Projects Analysis</div>
										<div class="text-sm text-red-800">Competing films in development and release schedule</div>
									</div>
									<div class="bg-yellow-100 rounded-lg p-4 border border-yellow-300">
										<div class="text-sm font-medium text-yellow-900 mb-2">⚠️ Market Saturation Assessment</div>
										<div class="text-sm text-yellow-800">Genre saturation and audience fatigue analysis</div>
									</div>
								</div>
							</div>

							<!-- Release Strategy - Coming Soon -->
							<div class="bg-blue-50 rounded-xl p-6 border border-blue-200">
								<h4 class="text-lg font-semibold text-gray-900 mb-4 flex items-center">
									<span class="text-blue-500 mr-2">📅</span>
									Release Timing & Strategy
									<span class="ml-2 text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded-full">Coming Soon</span>
								</h4>
								<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
									<div class="bg-blue-100 rounded-lg p-4 border border-blue-300">
										<div class="text-sm font-medium text-blue-900 mb-2">🎯 Optimal Release Windows</div>
										<div class="text-sm text-blue-800">Best timing for theatrical and streaming releases</div>
									</div>
									<div class="bg-green-100 rounded-lg p-4 border border-green-300">
										<div class="text-sm font-medium text-green-900 mb-2">📈 Seasonal Performance Factors</div>
										<div class="text-sm text-green-800">Holiday and seasonal impact on box office performance</div>
									</div>
								</div>
							</div>
						</div>
					</div>

					<!-- 6. RISK ASSESSMENT SECTION (Enhanced) -->
					{#if analysis.result.deepseek_risk_assessment}
						{@const risk = typeof analysis.result.deepseek_risk_assessment === 'string' 
							? JSON.parse(analysis.result.deepseek_risk_assessment) 
							: analysis.result.deepseek_risk_assessment}
						
						{#if risk}
							<div class="bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden">
								<div class="bg-gradient-to-r from-red-50 to-orange-50 px-6 py-4 border-b border-gray-200">
									<h3 class="text-xl font-bold text-gray-900 flex items-center">
										<span class="text-red-600 mr-3">⚠️</span>
										Risk Assessment & Mitigation
									</h3>
								</div>
								<div class="p-6 space-y-6">
									<!-- Risk Score Overview -->
									{#if risk.overall_risk_score}
										<div class="bg-gray-50 rounded-xl p-6 border border-gray-200">
											<div class="flex items-center justify-between">
												<div>
													<h4 class="text-lg font-semibold text-gray-900 mb-2">Overall Risk Assessment</h4>
													<p class="text-gray-600">Comprehensive risk evaluation across all factors</p>
												</div>
												<div class="text-center">
													<div class="w-20 h-20 rounded-full flex items-center justify-center text-white text-2xl font-bold
														{risk.overall_risk_score <= 3 ? 'bg-green-500' : risk.overall_risk_score <= 6 ? 'bg-yellow-500' : 'bg-red-500'}">
														{risk.overall_risk_score}
													</div>
													<div class="text-sm text-gray-500 mt-2">Risk Score</div>
												</div>
											</div>
											{#if risk.risk_score_explanation}
												<div class="mt-4 p-4 bg-white rounded-lg border border-gray-200">
													<div class="text-sm font-medium text-gray-700 mb-2">Risk Score Explanation</div>
													<div class="text-sm text-gray-600">{risk.risk_score_explanation}</div>
												</div>
											{/if}
										</div>
									{/if}

									<!-- Risk Factors & Mitigation -->
									<div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
										{#if (risk.key_risk_factors || risk.major_risk_factors)}
											<div class="bg-red-50 border border-red-200 rounded-xl p-6">
												<h5 class="font-semibold text-red-900 mb-4 flex items-center">
													<span class="text-red-600 mr-2">⚠️</span>
													Key Risk Factors
												</h5>
												<div class="space-y-3">
													{#each (risk.key_risk_factors || risk.major_risk_factors) as factor}
														<div class="bg-red-100 border border-red-200 rounded-lg p-3 flex items-start">
															<span class="text-red-600 mr-2 mt-0.5">•</span>
															<span class="text-red-800 text-sm">{factor}</span>
														</div>
													{/each}
												</div>
											</div>
										{/if}
										{#if (risk.mitigation_strategies || risk.risk_mitigation_strategies)}
											<div class="bg-green-50 border border-green-200 rounded-xl p-6">
												<h5 class="font-semibold text-green-900 mb-4 flex items-center">
													<span class="text-green-600 mr-2">🛡️</span>
													Mitigation Strategies
												</h5>
												<div class="space-y-3">
													{#each (risk.mitigation_strategies || risk.risk_mitigation_strategies) as strategy}
														<div class="bg-green-100 border border-green-200 rounded-lg p-3 flex items-start">
															<span class="text-green-600 mr-2 mt-0.5">✓</span>
															<span class="text-green-800 text-sm">{strategy}</span>
														</div>
													{/each}
												</div>
											</div>
										{/if}
									</div>
								</div>
							</div>
						{/if}
					{/if}

				{:else}
					<!-- No Financial Analysis Available -->
					<div class="bg-white rounded-xl shadow-lg border border-gray-200 p-12 text-center">
						<div class="text-gray-400 text-8xl mb-6">💰</div>
						<h3 class="text-2xl font-semibold text-gray-900 mb-4">Financial Analysis Unavailable</h3>
						<p class="text-gray-600 mb-4 max-w-lg mx-auto">DeepSeek financial analysis was not completed for this screenplay. This may be due to analysis failure or the feature not being available when this analysis was run.</p>
						<div class="bg-gray-50 rounded-lg p-4 max-w-md mx-auto">
							<p class="text-sm text-gray-500">Try re-analyzing the screenplay to generate comprehensive financial intelligence.</p>
						</div>
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
											{trends.content}
										</div>
										{#if trends.sources && trends.sources.length > 0}
											<div class="mt-4 pt-4 border-t border-purple-200">
												<div class="text-sm font-medium text-purple-800 mb-2">Sources:</div>
												<div class="space-y-1">
													{#each trends.sources.slice(0, 3) as source}
														<div class="text-xs text-purple-600">{source}</div>
													{/each}
												</div>
											</div>
										{/if}
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
											{competitive.content}
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
											{distribution.content}
										</div>
									</div>
								</div>
							{/if}
						{/if}
						
						<!-- Industry Reports -->
						{#if analysis.result.perplexity_industry_reports}
							{@const industry = typeof analysis.result.perplexity_industry_reports === 'string' 
								? JSON.parse(analysis.result.perplexity_industry_reports) 
								: analysis.result.perplexity_industry_reports}
							
							{#if industry && industry.content}
								<div class="mb-6">
									<h4 class="text-lg font-semibold text-gray-900 mb-4">Industry Intelligence</h4>
									<div class="bg-indigo-50 border border-indigo-200 rounded-lg p-4">
										<div class="prose prose-sm max-w-none text-gray-700">
											{industry.content}
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
											{financial.content}
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
											{talent.content}
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

				<!-- Source Material Analysis -->
				{#if analysis.result.source_success}
					<div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
						<h3 class="text-xl font-bold text-gray-900 mb-6 flex items-center">
							<span class="text-indigo-600 mr-2">📚</span>
							Source Material & IP Analysis
							<span class="ml-2 text-xs bg-indigo-100 text-indigo-700 px-2 py-1 rounded-full">
								AI Detected
							</span>
						</h3>
						
						{#if analysis.result.source_has_material}
							<!-- Has Source Material -->
							<div class="space-y-6">
								<!-- Source Material Overview -->
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
								
								<!-- Market Advantages & Challenges -->
								<div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
									{#if analysis.result.source_market_advantages}
										{@const advantages = parseJsonField(analysis.result.source_market_advantages)}
										{#if advantages.length > 0}
											<div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
												<h5 class="font-semibold text-blue-900 mb-3 flex items-center">
													<span class="text-blue-600 mr-2">📈</span>
													Market Advantages
												</h5>
												<ul class="space-y-2">
													{#each advantages as advantage}
														<li class="flex items-start">
															<span class="flex-shrink-0 text-blue-600 mr-2 mt-1">•</span>
															<span class="text-blue-800 text-sm">{advantage}</span>
														</li>
													{/each}
												</ul>
											</div>
										{/if}
									{/if}
									
									{#if analysis.result.source_potential_challenges}
										{@const challenges = parseJsonField(analysis.result.source_potential_challenges)}
										{#if challenges.length > 0}
											<div class="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
												<h5 class="font-semibold text-yellow-900 mb-3 flex items-center">
													<span class="text-yellow-600 mr-2">⚠️</span>
													Potential Challenges
												</h5>
												<ul class="space-y-2">
													{#each challenges as challenge}
														<li class="flex items-start">
															<span class="flex-shrink-0 text-yellow-600 mr-2 mt-1">•</span>
															<span class="text-yellow-800 text-sm">{challenge}</span>
														</li>
													{/each}
												</ul>
											</div>
										{/if}
									{/if}
								</div>
								
								{#if analysis.result.source_adaptation_notes}
									<div class="bg-purple-50 border border-purple-200 rounded-lg p-4">
										<h5 class="font-semibold text-purple-900 mb-3 flex items-center">
											<span class="text-purple-600 mr-2">📝</span>
											Adaptation Notes
										</h5>
										<p class="text-purple-800 text-sm leading-relaxed">{analysis.result.source_adaptation_notes}</p>
									</div>
								{/if}
							</div>
						{:else}
							<!-- Original Work -->
							<div class="bg-gradient-to-r from-green-50 to-emerald-50 border border-green-200 rounded-lg p-6">
								<div class="flex items-center justify-between">
									<div>
										<h4 class="text-lg font-semibold text-green-900 mb-2">Original Screenplay</h4>
										<p class="text-green-700">This appears to be an original work, not based on existing source material.</p>
									</div>
									<div class="text-right">
										<div class="text-2xl font-bold text-green-600">
											{Math.round((analysis.result.source_confidence_score || 0) * 100)}%
										</div>
										<div class="text-xs text-green-600">Confidence</div>
									</div>
								</div>
							</div>
						{/if}
					</div>
				{/if}
			</div>

		{:else if activeTab === 'producer'}
			<!-- Producer Dashboard Tab -->
			<div class="space-y-6">
				<!-- Executive Summary -->
				<div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
					<h3 class="text-xl font-bold text-gray-900 mb-6 flex items-center">
						<span class="text-blue-600 mr-2">🎬</span>
						Executive Producer Dashboard
					</h3>
					
					<!-- Key Metrics Grid -->
					<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
						<!-- Story Quality -->
						<div class="bg-gradient-to-br from-blue-50 to-indigo-50 border border-blue-200 rounded-lg p-4 text-center">
							<div class="text-blue-800 font-semibold mb-2">Story Quality</div>
							<div class="text-2xl font-bold text-blue-600">{analysis.result.overall_score}/10</div>
							<div class="text-sm text-blue-600 mt-1">Claude Analysis</div>
						</div>
						
						<!-- Financial Viability -->
						{#if analysis.result.deepseek_financial_score}
							<div class="bg-gradient-to-br from-green-50 to-emerald-50 border border-green-200 rounded-lg p-4 text-center">
								<div class="text-green-800 font-semibold mb-2">Financial Viability</div>
								<div class="text-2xl font-bold text-green-600">{analysis.result.deepseek_financial_score}/10</div>
								<div class="text-sm text-green-600 mt-1">DeepSeek Analysis</div>
							</div>
						{/if}
						
						<!-- Market Opportunity -->
						{#if analysis.result.perplexity_market_score}
							<div class="bg-gradient-to-br from-purple-50 to-violet-50 border border-purple-200 rounded-lg p-4 text-center">
								<div class="text-purple-800 font-semibold mb-2">Market Opportunity</div>
								<div class="text-2xl font-bold text-purple-600">{analysis.result.perplexity_market_score}/10</div>
								<div class="text-sm text-purple-600 mt-1">Market Research</div>
							</div>
						{/if}
						
						<!-- Cultural Fit -->
						{#if analysis.result.grok_score}
							<div class="bg-gradient-to-br from-orange-50 to-red-50 border border-orange-200 rounded-lg p-4 text-center">
								<div class="text-orange-800 font-semibold mb-2">Cultural Fit</div>
								<div class="text-2xl font-bold text-orange-600">{analysis.result.grok_score}/10</div>
								<div class="text-sm text-orange-600 mt-1">Grok Analysis</div>
							</div>
						{/if}
					</div>
					
					<!-- Investment Recommendation -->
					<div class="p-4 bg-gradient-to-r from-gray-50 to-blue-50 rounded-lg border border-gray-200">
						<h4 class="text-lg font-semibold text-gray-900 mb-3">Investment Recommendation</h4>
						<div class="grid grid-cols-1 lg:grid-cols-3 gap-4">
							<div class="space-y-2">
								<div class="text-sm font-medium text-gray-700">Story Assessment</div>
								<div class="text-sm text-gray-600">{analysis.result.recommendation || 'No recommendation available'}</div>
							</div>
							{#if analysis.result.deepseek_recommendation}
								<div class="space-y-2">
									<div class="text-sm font-medium text-gray-700">Financial Assessment</div>
									<div class="text-sm text-gray-600">{analysis.result.deepseek_recommendation}</div>
								</div>
							{/if}
							{#if analysis.result.perplexity_recommendation}
								<div class="space-y-2">
									<div class="text-sm font-medium text-gray-700">Market Assessment</div>
									<div class="text-sm text-gray-600">{analysis.result.perplexity_recommendation}</div>
								</div>
							{/if}
						</div>
					</div>
				</div>
				
				<!-- Quick Actions -->
				<div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
					<h4 class="text-lg font-semibold text-gray-900 mb-4">Producer Actions</h4>
					<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
						<button class="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors text-left">
							<div class="text-blue-600 text-2xl mb-2">📊</div>
							<div class="font-medium text-gray-900">View Financial Details</div>
							<div class="text-sm text-gray-500">Detailed ROI and budget analysis</div>
						</button>
						<button class="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors text-left">
							<div class="text-purple-600 text-2xl mb-2">🔍</div>
							<div class="font-medium text-gray-900">Market Research</div>
							<div class="text-sm text-gray-500">Competitive landscape and trends</div>
						</button>
						<button class="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors text-left">
							<div class="text-green-600 text-2xl mb-2">🎯</div>
							<div class="font-medium text-gray-900">Generate Pitch Deck</div>
							<div class="text-sm text-gray-500">Investor-ready presentation</div>
						</button>
					</div>
				</div>
			</div>

		{:else if activeTab === 'media'}
				<!-- Media Tab -->
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
							
							<div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
								<!-- Best Poster Image -->
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
											on:load={() => console.log('Best poster image loaded successfully')}
										/>
										<div class="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-10 transition-all duration-300 rounded-lg"></div>
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
								
								<!-- Collection Details -->
								<div class="space-y-6">
									<div>
										<h4 class="text-lg font-semibold text-gray-900 mb-3">Collection Summary</h4>
										<div class="bg-purple-50 rounded-lg p-4 border border-purple-200">
											<div class="grid grid-cols-2 gap-4 text-sm">
												<div class="flex justify-between">
													<span class="text-gray-600">Success Rate:</span>
													<span class="font-medium text-gray-900">{analysis.result.poster_success_count || 0} successful</span>
												</div>
												<div class="flex justify-between">
													<span class="text-gray-600">Best Source:</span>
													<span class="font-medium text-gray-900">{analysis.result.poster_best_source || 'Unknown'}</span>
												</div>
												<div class="flex justify-between">
													<span class="text-gray-600">Total Cost:</span>
													<span class="font-medium text-gray-900">${analysis.result.poster_total_cost || '0.00'}</span>
												</div>
												<div class="flex justify-between">
													<span class="text-gray-600">Generation Time:</span>
													<span class="font-medium text-gray-900">{analysis.result.poster_total_time || 0}s</span>
												</div>
											</div>
										</div>
									</div>
								</div>
							</div>
						</div>
					{/if}

					<!-- Individual Poster Sources -->
					{#if analysis.result.openai_movie_poster_url || analysis.result.openai_poster_prompt}
						<div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
							<h3 class="text-xl font-bold text-gray-900 mb-6 flex items-center">
								<span class="text-green-600 mr-2">🎬</span>
								Hollywood Movie Poster
								<span class="ml-2 text-xs bg-green-100 text-green-700 px-2 py-1 rounded-full">DALL-E 3</span>
							</h3>
							
							<div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
								<!-- Poster Image -->
								<div class="space-y-4">
									{#if analysis.result.openai_movie_poster_url}
										<div class="relative group">
											<img 
												src={analysis.result.openai_movie_poster_url} 
												alt="Movie poster for {analysis.result.title}"
												class="w-full max-w-md mx-auto rounded-lg shadow-lg border border-gray-200 group-hover:shadow-xl transition-shadow duration-300"
												crossorigin="anonymous"
												on:error={(e) => {
													console.error('Poster image failed to load:', e);
													const target = e.target as HTMLImageElement;
													if (target) {
														target.style.backgroundColor = '#f3f4f6';
														target.style.border = '2px dashed #d1d5db';
														target.alt = 'Poster image failed to load - click "View Full Size" to access directly';
													}
												}}
												on:load={() => console.log('Poster image loaded successfully')}
											/>
											<div class="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-10 transition-all duration-300 rounded-lg"></div>
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
									{:else}
										<div class="w-full max-w-md mx-auto bg-gradient-to-b from-gray-100 to-gray-200 rounded-lg shadow-lg border border-gray-200 aspect-[2/3] flex items-center justify-center">
											<div class="text-center text-gray-500">
												<svg class="w-16 h-16 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
													<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
												</svg>
												<p class="text-sm">Poster Generation<br/>In Progress</p>
											</div>
										</div>
									{/if}
								</div>
								
								<!-- Poster Details -->
								<div class="space-y-6">
									<div>
										<h4 class="text-lg font-semibold text-gray-900 mb-3">Poster Concept</h4>
										{#if analysis.result.openai_poster_prompt}
											<div class="bg-gray-50 rounded-lg p-4 border border-gray-200">
												<p class="text-gray-700 leading-relaxed whitespace-pre-line">{analysis.result.openai_poster_prompt}</p>
											</div>
										{:else}
											<p class="text-gray-500 italic">Poster concept will be generated during analysis.</p>
										{/if}
									</div>
									
									<div>
										<h4 class="text-lg font-semibold text-gray-900 mb-3">Generation Details</h4>
										<div class="space-y-3 text-sm">
											<div class="flex justify-between">
												<span class="text-gray-600">Generated by:</span>
												<span class="font-medium text-gray-900">DALL-E 3 (OpenAI GPT-5)</span>
											</div>
											<div class="flex justify-between">
												<span class="text-gray-600">Style:</span>
												<span class="font-medium text-gray-900">Hollywood Movie Poster</span>
											</div>
											<div class="flex justify-between">
												<span class="text-gray-600">Aspect Ratio:</span>
												<span class="font-medium text-gray-900">1024x1792 (Movie Poster)</span>
											</div>
											<div class="flex justify-between">
												<span class="text-gray-600">Genre:</span>
												<span class="font-medium text-gray-900">{analysis.result.genre || 'Not specified'}</span>
											</div>
										</div>
									</div>
									
									{#if analysis.result.openai_score}
										<div>
											<h4 class="text-lg font-semibold text-gray-900 mb-3">Quality Assessment</h4>
											<div class="bg-green-50 rounded-lg p-4 border border-green-200">
												<div class="flex items-center justify-between mb-2">
													<span class="text-green-700 font-medium">Commercial Score</span>
													<span class="text-2xl font-bold text-green-600">{analysis.result.openai_score}/10</span>
												</div>
												<p class="text-green-600 text-sm">Poster style reflects commercial viability assessment</p>
											</div>
										</div>
									{/if}
								</div>
							</div>
						</div>
					{/if}
					
					<!-- PiAPI Poster Section -->
					{#if analysis.result.piapi_poster_url || analysis.result.piapi_poster_prompt}
						<div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
							<h3 class="text-xl font-bold text-gray-900 mb-6 flex items-center">
								<span class="text-purple-600 mr-2">🎨</span>
								PiAPI Hollywood Poster
							</h3>
							
							<div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
								<!-- Poster Image -->
								<div class="space-y-4">
									{#if analysis.result.piapi_poster_url}
										<div class="relative group">
											<img 
												src={analysis.result.piapi_poster_url} 
												alt="PiAPI poster for {analysis.result.title}"
												class="w-full max-w-md mx-auto rounded-lg shadow-lg border border-gray-200 group-hover:shadow-xl transition-shadow duration-300"
											/>
											<div class="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-10 transition-all duration-300 rounded-lg"></div>
										</div>
										<div class="text-center">
											<a 
												href={analysis.result.piapi_poster_url} 
												target="_blank" 
												class="inline-flex items-center px-4 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700 transition-colors text-sm"
											>
												<svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
													<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
												</svg>
												View Full Size
											</a>
										</div>
									{:else}
										<div class="w-full max-w-md mx-auto bg-gradient-to-b from-purple-100 to-purple-200 rounded-lg shadow-lg border border-purple-200 aspect-[2/3] flex items-center justify-center">
											<div class="text-center text-purple-600">
												<svg class="w-16 h-16 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
													<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 002 2v12a2 2 0 002 2z" />
												</svg>
												<p class="text-sm">PiAPI Poster<br/>Generation In Progress</p>
											</div>
										</div>
									{/if}
								</div>
								
								<!-- Poster Details -->
								<div class="space-y-6">
									<div>
										<h4 class="text-lg font-semibold text-gray-900 mb-3">Poster Concept</h4>
										{#if analysis.result.piapi_poster_prompt}
											<div class="bg-purple-50 rounded-lg p-4 border border-purple-200">
												<p class="text-gray-700 leading-relaxed whitespace-pre-line">{analysis.result.piapi_poster_prompt}</p>
											</div>
										{:else}
											<p class="text-gray-500 italic">PiAPI poster concept will be generated during analysis.</p>
										{/if}
									</div>
									
									<div>
										<h4 class="text-lg font-semibold text-gray-900 mb-3">Generation Details</h4>
										<div class="space-y-3 text-sm">
											<div class="flex justify-between">
												<span class="text-gray-600">Generated by:</span>
												<span class="font-medium text-gray-900">PiAPI (Flux-1.1-Pro)</span>
											</div>
											<div class="flex justify-between">
												<span class="text-gray-600">Style:</span>
												<span class="font-medium text-gray-900">Hollywood Movie Poster</span>
											</div>
											<div class="flex justify-between">
												<span class="text-gray-600">Aspect Ratio:</span>
												<span class="font-medium text-gray-900">1024x1792 (Movie Poster)</span>
											</div>
											<div class="flex justify-between">
												<span class="text-gray-600">Cost:</span>
												<span class="font-medium text-gray-900">${analysis.result.piapi_poster_cost || '0.02'}</span>
											</div>
										</div>
									</div>
								</div>
							</div>
						</div>
					{/if}
					
					<!-- No Posters Available -->
					{#if !analysis.result.openai_movie_poster_url && !analysis.result.openai_poster_prompt && !analysis.result.piapi_poster_url && !analysis.result.piapi_poster_prompt}
						<div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
							<div class="text-center py-12">
								<svg class="w-16 h-16 mx-auto text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
								</svg>
								<h3 class="text-lg font-medium text-gray-900 mb-2">No Media Available</h3>
								<p class="text-gray-500">Movie poster and other media will be generated during analysis.</p>
							</div>
						</div>
					{/if}
					
					<!-- Future Media Sections -->
					<div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
						<h3 class="text-xl font-bold text-gray-900 mb-4 flex items-center">
							<span class="text-purple-600 mr-2">🎨</span>
							Additional Media (Coming Soon)
						</h3>
						<div class="grid grid-cols-1 md:grid-cols-3 gap-4">
							<div class="text-center p-4 border border-gray-200 rounded-lg bg-gray-50">
								<div class="text-2xl mb-2">🎵</div>
								<h4 class="font-medium text-gray-900">Soundtrack Suggestions</h4>
								<p class="text-sm text-gray-500 mt-1">AI-curated music recommendations</p>
							</div>
							<div class="text-center p-4 border border-gray-200 rounded-lg bg-gray-50">
								<div class="text-2xl mb-2">🎬</div>
								<h4 class="font-medium text-gray-900">Trailer Concepts</h4>
								<p class="text-sm text-gray-500 mt-1">Marketing trailer breakdowns</p>
							</div>
							<div class="text-center p-4 border border-gray-200 rounded-lg bg-gray-50">
								<div class="text-2xl mb-2">📱</div>
								<h4 class="font-medium text-gray-900">Social Media Assets</h4>
								<p class="text-sm text-gray-500 mt-1">Promotional graphics and content</p>
							</div>
						</div>
					</div>
				</div>

			{:else if activeTab === 'improvements'}
				<!-- Improvements Tab -->
				<div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
					<h3 class="text-xl font-bold text-gray-900 mb-4 flex items-center">
						<span class="text-yellow-600 mr-2">💡</span>
						Improvement Strategies
					</h3>
					{#if parseJsonField(analysis.result.improvement_strategies || analysis.result.suggestions).length > 0}
						<div class="bg-yellow-50 rounded-lg p-6">
							<ul class="space-y-4">
								{#each parseJsonField(analysis.result.improvement_strategies || analysis.result.suggestions) as strategy, index}
									<li class="flex items-start">
										<span class="flex-shrink-0 bg-yellow-200 text-yellow-800 rounded-full w-6 h-6 flex items-center justify-center text-sm font-medium mr-3 mt-0.5">
											{index + 1}
										</span>
										<span class="text-yellow-900">{strategy}</span>
									</li>
								{/each}
							</ul>
						</div>
					{:else}
						<p class="text-gray-500 italic">Improvement strategies will be available in enhanced results.</p>
					{/if}
				</div>

				<!-- Source Material Analysis for Producer Tab -->
				{#if analysis.result.source_success}
					<div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
						<h3 class="text-xl font-bold text-gray-900 mb-6 flex items-center">
							<span class="text-indigo-600 mr-2">📚</span>
							Source Material & IP Analysis
						</h3>
						
						{#if analysis.result.source_has_material}
							<!-- Has Source Material -->
							<div class="space-y-6">
								<!-- Commercial & Legal Implications -->
									<div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
										{#if analysis.result.source_commercial_implications}
											<div class="bg-green-50 border border-green-200 rounded-lg p-4">
												<h5 class="font-semibold text-green-900 mb-3 flex items-center">
													<span class="text-green-600 mr-2">💰</span>
													Commercial Implications
												</h5>
												<p class="text-green-800 text-sm leading-relaxed">{analysis.result.source_commercial_implications}</p>
											</div>
										{/if}
										
										{#if analysis.result.source_legal_considerations}
											<div class="bg-red-50 border border-red-200 rounded-lg p-4">
												<h5 class="font-semibold text-red-900 mb-3 flex items-center">
													<span class="text-red-600 mr-2">⚖️</span>
													Legal Considerations
												</h5>
												<p class="text-red-800 text-sm leading-relaxed">{analysis.result.source_legal_considerations}</p>
											</div>
										{/if}
									</div>
									
									<!-- Market Advantages & Challenges -->
									<div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
										{#if analysis.result.source_market_advantages}
											{@const advantages = parseJsonField(analysis.result.source_market_advantages)}
											{#if advantages.length > 0}
												<div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
													<h5 class="font-semibold text-blue-900 mb-3 flex items-center">
														<span class="text-blue-600 mr-2">📈</span>
														Market Advantages
													</h5>
													<ul class="space-y-2">
														{#each advantages as advantage}
															<li class="flex items-start">
																<span class="flex-shrink-0 text-blue-600 mr-2 mt-1">•</span>
																<span class="text-blue-800 text-sm">{advantage}</span>
															</li>
														{/each}
													</ul>
												</div>
											{/if}
										{/if}
										
										{#if analysis.result.source_potential_challenges}
											{@const challenges = parseJsonField(analysis.result.source_potential_challenges)}
											{#if challenges.length > 0}
												<div class="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
													<h5 class="font-semibold text-yellow-900 mb-3 flex items-center">
														<span class="text-yellow-600 mr-2">⚠️</span>
														Potential Challenges
													</h5>
													<ul class="space-y-2">
														{#each challenges as challenge}
															<li class="flex items-start">
																<span class="flex-shrink-0 text-yellow-600 mr-2 mt-1">•</span>
																<span class="text-yellow-800 text-sm">{challenge}</span>
															</li>
														{/each}
													</ul>
												</div>
											{/if}
										{/if}
									</div>
									
									{#if analysis.result.source_adaptation_notes}
										<div class="bg-purple-50 border border-purple-200 rounded-lg p-4">
											<h5 class="font-semibold text-purple-900 mb-3 flex items-center">
												<span class="text-purple-600 mr-2">📝</span>
												Adaptation Notes
											</h5>
											<p class="text-purple-800 text-sm leading-relaxed">{analysis.result.source_adaptation_notes}</p>
										</div>
									{/if}
							</div>
							{:else}
								<!-- Original Work -->
								<div class="bg-gradient-to-r from-green-50 to-emerald-50 border border-green-200 rounded-lg p-6">
									<div class="flex items-center justify-between">
										<div>
											<h4 class="text-lg font-semibold text-green-900 mb-2">Original Screenplay</h4>
											<p class="text-green-700">This appears to be an original work, not based on existing source material.</p>
										</div>
										<div class="text-right">
											<div class="text-2xl font-bold text-green-600">
												{Math.round((analysis.result.source_confidence_score || 0) * 100)}%
											</div>
											<div class="text-xs text-green-600">Confidence</div>
										</div>
									</div>
									
									<div class="mt-4 pt-4 border-t border-green-200">
										<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
											<div class="flex items-center">
												<span class="text-green-600 mr-2">✨</span>
												<span class="text-green-800 text-sm">Creative freedom in development</span>
											</div>
											<div class="flex items-center">
												<span class="text-green-600 mr-2">🎯</span>
												<span class="text-green-800 text-sm">No existing audience expectations</span>
											</div>
											<div class="flex items-center">
												<span class="text-green-600 mr-2">⚖️</span>
												<span class="text-green-800 text-sm">Clear rights ownership</span>
											</div>
											<div class="flex items-center">
												<span class="text-green-600 mr-2">💡</span>
												<span class="text-green-800 text-sm">Unique storytelling opportunity</span>
											</div>
										</div>
									</div>
								</div>
							{/if}
						</div>
					{/if}

				<!-- Commercial Viability -->
					{#if analysis.result.commercial_viability}
						<div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
							<h3 class="text-xl font-bold text-gray-900 mb-4 flex items-center">
								<span class="text-green-600 mr-2">💼</span>
								Commercial Viability
							</h3>
							<div class="prose max-w-none text-gray-700">
								{@html analysis.result.commercial_viability.replace(/\n/g, '<br>')}
							</div>
						</div>
					{/if}

					<div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
						<!-- Target Audience -->
						{#if analysis.result.target_audience}
							<div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
								<h3 class="text-xl font-bold text-gray-900 mb-4 flex items-center">
									<span class="text-blue-600 mr-2">🎯</span>
									Target Audience
								</h3>
								<div class="text-gray-700">
									{@html analysis.result.target_audience.replace(/\n/g, '<br>')}
								</div>
							</div>
						{/if}

						<!-- Comparable Films -->
						{#if parseJsonField(analysis.result.comparable_films).length > 0}
							<div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
								<h3 class="text-xl font-bold text-gray-900 mb-4 flex items-center">
									<span class="text-purple-600 mr-2">🎭</span>
									Comparable Films
								</h3>
								<ul class="space-y-2">
									{#each parseJsonField(analysis.result.comparable_films) as film}
										<li class="flex items-center">
											<span class="flex-shrink-0 text-purple-600 mr-3">•</span>
											<span class="text-gray-700 font-medium">{film}</span>
										</li>
									{/each}
								</ul>
							</div>
						{/if}
					</div>

			{:else if activeTab === 'production'}
				<!-- Production Tab (Casting + Director) -->
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
							<p class="text-gray-500 italic">Casting suggestions will be available in enhanced results.</p>
						{/if}
					</div>
				</div>
			{/if}
				</div>
			</div>
		</div>

		<!-- Actions Footer -->
		<div class="bg-white border-t border-gray-200">
			<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
				<div class="flex flex-col sm:flex-row gap-4">
					<button 
						on:click={() => goto('/screenplays/upload')}
						class="btn-primary"
					>
						Analyze Another Screenplay
					</button>
					<button 
						on:click={() => goto('/screenplays')}
						class="btn-secondary"
					>
						View All Analyses
					</button>
				</div>
			</div>
		</div>
	</div>
{/if}