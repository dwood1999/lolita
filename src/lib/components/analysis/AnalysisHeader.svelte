<script lang="ts">
	export let analysis: any;
	export let isPublic = false;
	
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
</script>

<!-- Public Share Banner (only for public view) -->
{#if isPublic}
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
{/if}

<!-- Header Section -->
<div class="bg-white border-b border-gray-200">
	<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
		<div class="flex items-center justify-between">
			<div class="flex-1">
				<h1 class="text-3xl font-bold text-gray-900 mb-2">
					{analysis.result?.title || 'Screenplay Analysis'}
				</h1>
				<p class="text-gray-600">Professional AI-Powered Analysis</p>
			</div>
			<div class="flex items-center space-x-4">
				<!-- Craft Score -->
				<div class="text-center">
					<div class="text-2xl font-bold {getScoreColor(analysis.result?.overall_score)} px-3 py-2 rounded-lg">
						{analysis.result?.overall_score}/10
					</div>
					<div class="text-xs text-gray-500 mt-1">Craft Score</div>
					<div class="inline-flex items-center px-2 py-1 rounded text-xs font-medium border {getRecommendationColor(analysis.result?.recommendation)} mt-1">
						{analysis.result?.recommendation}
					</div>
				</div>
				
				<!-- Reality Score -->
				{#if analysis.result?.grok_score}
					<div class="text-center">
						<div class="text-2xl font-bold {getScoreColor(analysis.result.grok_score)} px-3 py-2 rounded-lg">
							{analysis.result.grok_score}/10
						</div>
						<div class="text-xs text-gray-500 mt-1">Reality Score</div>
						<div class="inline-flex items-center px-2 py-1 rounded text-xs font-medium border {getRecommendationColor(analysis.result?.grok_recommendation)} mt-1">
							{analysis.result?.grok_recommendation}
						</div>
					</div>
				{/if}

				<!-- Financial Score -->
				{#if analysis.result?.deepseek_financial_score}
					<div class="text-center">
						<div class="text-2xl font-bold {getScoreColor(analysis.result.deepseek_financial_score)} px-3 py-2 rounded-lg">
							{analysis.result.deepseek_financial_score}/10
						</div>
						<div class="text-xs text-gray-500 mt-1">Financial Score</div>
						<div class="inline-flex items-center px-2 py-1 rounded text-xs font-medium border {getRecommendationColor(analysis.result?.deepseek_recommendation)} mt-1">
							{analysis.result?.deepseek_recommendation || 'Investment Analysis'}
						</div>
					</div>
				{/if}

				<!-- Market Score -->
				{#if analysis.result?.perplexity_market_score}
					<div class="text-center">
						<div class="text-2xl font-bold {getScoreColor(analysis.result.perplexity_market_score)} px-3 py-2 rounded-lg">
							{analysis.result.perplexity_market_score}/10
						</div>
						<div class="text-xs text-gray-500 mt-1">Market Score</div>
						<div class="inline-flex items-center px-2 py-1 rounded text-xs font-medium border {getRecommendationColor(analysis.result?.perplexity_recommendation)} mt-1">
							{analysis.result?.perplexity_recommendation || 'Market Analysis'}
						</div>
					</div>
				{/if}
			</div>
		</div>
	</div>
</div>
