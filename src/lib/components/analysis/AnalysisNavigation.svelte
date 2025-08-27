<script lang="ts">
	export let activeTab = 'dashboard';
	export let analysis: any;
	export let isPublic = false; // For future use in filtering tabs
	
	// Navigation tabs - same for both public and private
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

	// Filter tabs based on available data
	$: availableTabs = allTabs.filter(tab => {
		switch (tab.id) {
			case 'dashboard':
				return true; // Always show dashboard
			case 'story':
				return analysis?.result?.structural_analysis || analysis?.result?.character_analysis;
			case 'financial':
				return analysis?.result?.deepseek_financial_score;
			case 'grok':
				return analysis?.result?.grok_verdict;
			case 'gpt5':
				return analysis?.result?.openai_verdict;
			case 'genre':
				return analysis?.result?.genre;
			case 'market':
				return analysis?.result?.perplexity_market_score;
			case 'improvements':
				return analysis?.result?.recommendations || analysis?.result?.improvement_strategies;
			default:
				return false; // Hide other tabs for now
		}
	});

	function handleTabClick(tabId: string) {
		activeTab = tabId;
	}
</script>

<div class="bg-white border-b border-gray-200">
	<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
		<nav class="flex space-x-8" aria-label="Tabs">
			{#each availableTabs as tab}
				<button
					on:click={() => handleTabClick(tab.id)}
					class="whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm transition-colors duration-200 {activeTab === tab.id 
						? 'border-blue-500 text-blue-600' 
						: 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}"
					aria-current={activeTab === tab.id ? 'page' : undefined}
				>
					<span class="mr-2">{tab.icon}</span>
					{tab.label}
				</button>
			{/each}
		</nav>
	</div>
</div>
