<script lang="ts">
	import { parseMarkdown } from '$lib/utils/markdown.js';
	
	export let analysis: any;
	export let activeTab = 'dashboard';
	
	// Helper functions
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

	function hasDeepSeekData(): boolean {
		return !!(analysis?.result?.deepseek_financial_score || analysis?.result?.deepseek_box_office_prediction);
	}

	function hasPerplexityData(): boolean {
		return !!(analysis?.result?.perplexity_market_score || analysis?.result?.perplexity_market_trends);
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

	function getGPT5ExecutiveAssessment(): any {
		const assessment = analysis?.result?.gpt5_executive_assessment;
		if (!assessment) return null;
		if (typeof assessment === 'string') {
			try {
				return JSON.parse(assessment);
			} catch {
				return null;
			}
		}
		return assessment;
	}
</script>

<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
	{#if activeTab === 'dashboard'}
		<div class="space-y-8">
			<!-- Analysis Verdicts -->
			<div class="space-y-4">
				{#if analysis.result?.one_line_verdict}
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

				{#if analysis.result?.grok_verdict}
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

				{#if analysis.result?.openai_verdict}
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
				{#if analysis.result?.executive_summary}
					<div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6 md:col-span-2 lg:col-span-3">
						<h3 class="text-xl font-bold text-gray-900 mb-4 flex items-center">
							<span class="text-blue-600 mr-2">📋</span>
							Executive Summary
						</h3>
						<div class="prose max-w-none">
							<div class="text-gray-700 leading-relaxed">{@html parseMarkdown(analysis.result.executive_summary)}</div>
						</div>
					</div>
				{/if}

				<!-- Logline -->
				{#if analysis.result?.logline}
					<div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6 md:col-span-2">
						<h3 class="text-lg font-bold text-gray-900 mb-4 flex items-center">
							<span class="text-purple-600 mr-2">🎬</span>
							Logline
						</h3>
						<div class="prose max-w-none">
							<div class="text-gray-700 italic leading-relaxed">"{@html parseMarkdown(analysis.result.logline)}"</div>
						</div>
					</div>
				{/if}

				<!-- Top Strengths -->
				{#if analysis.result?.top_strengths}
					<div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
						<h3 class="text-lg font-bold text-gray-900 mb-4 flex items-center">
							<span class="text-green-600 mr-2">✅</span>
							Top Strengths
						</h3>
						<div class="prose max-w-none">
							<div class="text-gray-700">{@html parseMarkdown(analysis.result.top_strengths)}</div>
						</div>
					</div>
				{/if}

				<!-- Key Weaknesses -->
				{#if analysis.result?.key_weaknesses}
					<div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
						<h3 class="text-lg font-bold text-gray-900 mb-4 flex items-center">
							<span class="text-red-600 mr-2">⚠️</span>
							Key Areas for Improvement
						</h3>
						<div class="prose max-w-none">
							<div class="text-gray-700">{@html parseMarkdown(analysis.result.key_weaknesses)}</div>
						</div>
					</div>
				{/if}

				<!-- Commercial Viability -->
				{#if analysis.result?.commercial_viability}
					<div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
						<h3 class="text-lg font-bold text-gray-900 mb-4 flex items-center">
							<span class="text-green-600 mr-2">💰</span>
							Commercial Viability
						</h3>
						<div class="prose max-w-none">
							<div class="text-gray-700">{@html parseMarkdown(analysis.result.commercial_viability)}</div>
						</div>
					</div>
				{/if}

				<!-- Target Audience -->
				{#if analysis.result?.target_audience}
					<div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
						<h3 class="text-lg font-bold text-gray-900 mb-4 flex items-center">
							<span class="text-pink-600 mr-2">🎯</span>
							Target Audience
						</h3>
						<div class="prose max-w-none">
							<div class="text-gray-700">{@html parseMarkdown(analysis.result.target_audience)}</div>
						</div>
					</div>
				{/if}
			</div>
		</div>

	{:else if activeTab === 'story'}
		<div class="space-y-8">
			<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
				<!-- Character Analysis -->
				{#if analysis.result?.character_analysis}
					<div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
						<h3 class="text-lg font-bold text-gray-900 mb-4 flex items-center">
							<span class="text-indigo-600 mr-2">👥</span>
							Character Analysis
						</h3>
						<div class="prose max-w-none">
							<div class="text-gray-700">{@html parseMarkdown(analysis.result.character_analysis)}</div>
						</div>
					</div>
				{/if}

				<!-- Structural Analysis -->
				{#if analysis.result?.structural_analysis}
					<div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
						<h3 class="text-lg font-bold text-gray-900 mb-4 flex items-center">
							<span class="text-orange-600 mr-2">🏗️</span>
							Structural Analysis
						</h3>
						<div class="prose max-w-none">
							<div class="text-gray-700">{@html parseMarkdown(analysis.result.structural_analysis)}</div>
						</div>
					</div>
				{/if}

				<!-- Thematic Depth -->
				{#if analysis.result?.thematic_depth}
					<div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
						<h3 class="text-lg font-bold text-gray-900 mb-4 flex items-center">
							<span class="text-purple-600 mr-2">🎭</span>
							Thematic Depth
						</h3>
						<div class="prose max-w-none">
							<div class="text-gray-700">{@html parseMarkdown(analysis.result.thematic_depth)}</div>
						</div>
					</div>
				{/if}

				<!-- Craft Evaluation -->
				{#if analysis.result?.craft_evaluation}
					<div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
						<h3 class="text-lg font-bold text-gray-900 mb-4 flex items-center">
							<span class="text-blue-600 mr-2">✍️</span>
							Craft Evaluation
						</h3>
						<div class="prose max-w-none">
							<div class="text-gray-700">{@html parseMarkdown(analysis.result.craft_evaluation)}</div>
						</div>
					</div>
				{/if}

				<!-- Improvement Strategies -->
				{#if analysis.result?.improvement_strategies}
					<div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
						<h3 class="text-lg font-bold text-gray-900 mb-4 flex items-center">
							<span class="text-yellow-600 mr-2">💡</span>
							Improvement Strategies
						</h3>
						<div class="prose max-w-none">
							<div class="text-gray-700">{@html parseMarkdown(analysis.result.improvement_strategies)}</div>
						</div>
					</div>
				{/if}

				<!-- Suggestions -->
				{#if analysis.result?.suggestions}
					<div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
						<h3 class="text-lg font-bold text-gray-900 mb-4 flex items-center">
							<span class="text-yellow-600 mr-2">💡</span>
							Suggestions
						</h3>
						<div class="prose max-w-none">
							<div class="text-gray-700">{@html parseMarkdown(analysis.result.suggestions)}</div>
						</div>
					</div>
				{/if}
			</div>
		</div>

	{:else if activeTab === 'financial'}
		<!-- Financial Intelligence content would go here -->
		<div class="text-center py-12">
			<p class="text-gray-500">Financial Intelligence tab content</p>
		</div>

	{:else if activeTab === 'grok'}
		<!-- Reality Check content would go here -->
		<div class="text-center py-12">
			<p class="text-gray-500">Reality Check tab content</p>
		</div>

	{:else if activeTab === 'gpt5'}
		<!-- Excellence Analysis content would go here -->
		<div class="text-center py-12">
			<p class="text-gray-500">Excellence Analysis tab content</p>
		</div>

	{:else if activeTab === 'genre'}
		<!-- Genre Intelligence content would go here -->
		<div class="text-center py-12">
			<p class="text-gray-500">Genre Intelligence tab content</p>
		</div>

	{:else if activeTab === 'market'}
		<!-- Market Intelligence content would go here -->
		<div class="text-center py-12">
			<p class="text-gray-500">Market Intelligence tab content</p>
		</div>

	{:else if activeTab === 'improvements'}
		<!-- Enhancement Notes content would go here -->
		<div class="text-center py-12">
			<p class="text-gray-500">Enhancement Notes tab content</p>
		</div>

	{:else}
		<!-- Default/other tabs -->
		<div class="text-center py-12">
			<p class="text-gray-500">Content for {activeTab} tab</p>
		</div>
	{/if}
</div>
