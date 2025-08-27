<script lang="ts">
	import AnalysisHeader from './AnalysisHeader.svelte';
	import AnalysisNavigation from './AnalysisNavigation.svelte';
	import AnalysisContent from './AnalysisContent.svelte';
	
	export let analysis: any;
	export let activeTab = 'dashboard';
	export let isPublic = false;
	
	// Allow parent components to control tab changes
	function handleTabChange(event: CustomEvent<string>) {
		activeTab = event.detail;
	}
</script>

<div class="min-h-screen bg-gray-50">
	<AnalysisHeader {analysis} {isPublic} />
	<AnalysisNavigation bind:activeTab {analysis} {isPublic} />
	<AnalysisContent {analysis} {activeTab} />
</div>
