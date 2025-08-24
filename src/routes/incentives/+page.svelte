<script lang="ts">
	import { onMount } from 'svelte';
	import { browser } from '$app/environment';
	import IncentiveMap from '$lib/components/IncentiveMap.svelte';
	
	let loading = true;
	let error = '';
	let incentives: any[] = [];
	let filteredIncentives: any[] = [];
	let selectedIncentive: any = null;
	let showCalculator = false;
	let showComparison = false;
	let showGrants = false;
	let comparisonList: any[] = [];
	
	// Grants data
	let grants: any[] = [];
	let filteredGrants: any[] = [];
	let selectedGrant: any = null;
	let eligibleGrants: any[] = [];
	
	// Grant eligibility filters
	let filmmakerDemographics = '';
	let projectGenre = '';
	let projectStage = '';
	let budgetRange = '';
	let filmmakerLocation = '';
	
	// Filters
	let selectedCountry = '';
	let selectedType = '';
	let minPercentage = 0;
	let maxBudget = 100000000;
	let minBudget = 0;
	let searchQuery = '';
	
	// Calculator
	let calculatorBudget = 5000000;
	let calculatorResults: any[] = [];
	
	// Unique values for filters
	let countries: string[] = [];
	let incentiveTypes: string[] = [];
	
	onMount(async () => {
		await loadIncentives();
		await loadGrants();
	});
	
	async function loadIncentives() {
		try {
			const response = await fetch('/api/incentives');
			const data = await response.json();
			
			if (data.success) {
				incentives = data.incentives;
				filteredIncentives = [...incentives];
				
				// Extract unique values for filters
				countries = [...new Set(incentives.map(i => i.country))].sort();
				incentiveTypes = [...new Set(incentives.map(i => i.incentive_type))].sort();
				
				loading = false;
			} else {
				error = 'Failed to load incentives';
				loading = false;
			}
		} catch (err) {
			error = 'Network error loading incentives';
			loading = false;
		}
	}
	
	async function loadGrants() {
		try {
			const response = await fetch('/api/grants');
			const data = await response.json();
			
			if (data.success) {
				grants = data.grants;
				filteredGrants = [...grants];
			} else {
				console.error('Failed to load grants:', data.error);
			}
		} catch (err) {
			console.error('Network error loading grants:', err);
		}
	}
	
	async function checkGrantEligibility() {
		try {
			const params = new URLSearchParams();
			if (filmmakerDemographics) params.append('filmmaker_demographics', filmmakerDemographics);
			if (projectGenre) params.append('project_genre', projectGenre);
			if (projectStage) params.append('project_stage', projectStage);
			if (budgetRange) params.append('budget_range', budgetRange);
			if (filmmakerLocation) params.append('location', filmmakerLocation);
			
			const response = await fetch(`/api/grants/eligibility?${params.toString()}`);
			const data = await response.json();
			
			if (data.success) {
				eligibleGrants = data.eligible_grants;
			}
		} catch (err) {
			console.error('Grant eligibility check error:', err);
		}
	}
	
	function handleCountrySelect(country: string) {
		selectedCountry = country;
		applyFilters();
	}
	

	
	function applyFilters() {
		filteredIncentives = incentives.filter(incentive => {
			if (selectedCountry && incentive.country !== selectedCountry) return false;
			if (selectedType && incentive.incentive_type !== selectedType) return false;
			if (incentive.percentage < minPercentage) return false;
			if (incentive.minimum_spend && incentive.minimum_spend > maxBudget) return false;
			if (incentive.maximum_spend && incentive.maximum_spend < minBudget) return false;
			if (searchQuery && !incentive.country.toLowerCase().includes(searchQuery.toLowerCase()) && 
				!incentive.region?.toLowerCase().includes(searchQuery.toLowerCase())) return false;
			
			return true;
		});
	}
	
	function resetFilters() {
		selectedCountry = '';
		selectedType = '';
		minPercentage = 0;
		maxBudget = 100000000;
		minBudget = 0;
		searchQuery = '';
		applyFilters();
	}
	
	async function calculateIncentives() {
		try {
			const response = await fetch(`/api/incentives/calculator?budget=${calculatorBudget}&min_percentage=0`);
			const data = await response.json();
			
			if (data.success) {
				calculatorResults = data.savings_options;
			}
		} catch (err) {
			console.error('Calculator error:', err);
		}
	}
	
	function addToComparison(incentive: any) {
		if (comparisonList.length < 4 && !comparisonList.find(i => i.id === incentive.id)) {
			comparisonList = [...comparisonList, incentive];
		}
	}
	
	function removeFromComparison(incentiveId: number) {
		comparisonList = comparisonList.filter(i => i.id !== incentiveId);
	}
	
	function formatCurrency(amount: number | null) {
		if (!amount) return 'No limit';
		return new Intl.NumberFormat('en-US', {
			style: 'currency',
			currency: 'USD',
			minimumFractionDigits: 0,
			maximumFractionDigits: 0
		}).format(amount);
	}
	
	function getIncentiveTypeColor(type: string) {
		const colors = {
			'tax_credit': 'bg-blue-100 text-blue-800',
			'rebate': 'bg-green-100 text-green-800',
			'grant': 'bg-purple-100 text-purple-800',
			'loan': 'bg-yellow-100 text-yellow-800',
			'infrastructure': 'bg-orange-100 text-orange-800',
			'service_credit': 'bg-pink-100 text-pink-800'
		};
		return colors[type as keyof typeof colors] || 'bg-gray-100 text-gray-800';
	}
	
	function getPercentageColor(percentage: number) {
		if (percentage >= 30) return 'text-green-600';
		if (percentage >= 20) return 'text-yellow-600';
		return 'text-red-600';
	}
	
	// Reactive statements
	$: if (selectedCountry || selectedType || minPercentage || maxBudget !== 100000000 || minBudget || searchQuery) {
		applyFilters();
	}
</script>

<svelte:head>
	<title>Film Incentives Hub - Quilty</title>
	<meta name="description" content="Comprehensive global film incentives database with interactive maps, calculators, and comparison tools for filmmakers and producers." />
</svelte:head>

<!-- Hero Section -->
<div class="relative overflow-hidden bg-gradient-to-br from-indigo-900 via-purple-900 to-pink-900">
	<div class="absolute inset-0 opacity-20">
		<div class="w-full h-full" style="background-image: url('data:image/svg+xml,<svg width=&quot;60&quot; height=&quot;60&quot; viewBox=&quot;0 0 60 60&quot; xmlns=&quot;http://www.w3.org/2000/svg&quot;><g fill=&quot;none&quot; fill-rule=&quot;evenodd&quot;><g fill=&quot;%23ffffff&quot; fill-opacity=&quot;0.02&quot;><circle cx=&quot;30&quot; cy=&quot;30&quot; r=&quot;2&quot;/></g></g></svg>');"></div>
	</div>
	
	<div class="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
		<div class="text-center">
			<h1 class="text-3xl sm:text-4xl font-bold tracking-tight mb-4">
				<span class="text-white">Global Film </span>
				<span class="bg-gradient-to-r from-yellow-400 via-orange-400 to-red-400 bg-clip-text text-transparent">
					Incentives Hub
				</span>
			</h1>
			<p class="text-lg text-indigo-100 max-w-3xl mx-auto mb-6">
				Discover film incentives, tax credits, and grants with interactive maps and calculators.
			</p>
			
			<!-- Quick Stats -->
			<div class="grid grid-cols-2 md:grid-cols-4 gap-4 max-w-2xl mx-auto">
				<div class="text-center">
					<div class="text-2xl font-bold text-yellow-400">{incentives.length}</div>
					<div class="text-xs text-indigo-200">Active Incentives</div>
				</div>
				<div class="text-center">
					<div class="text-2xl font-bold text-green-400">{countries.length}</div>
					<div class="text-xs text-indigo-200">Countries</div>
				</div>
				<div class="text-center">
					<div class="text-2xl font-bold text-blue-400">35%</div>
					<div class="text-xs text-indigo-200">Max Incentive</div>
				</div>
				<div class="text-center">
					<div class="text-2xl font-bold text-purple-400">$50M</div>
					<div class="text-xs text-indigo-200">Largest Cap</div>
				</div>
			</div>
		</div>
	</div>
</div>

{#if loading}
	<div class="min-h-screen bg-gray-50 flex items-center justify-center">
		<div class="text-center">
			<div class="animate-spin rounded-full h-16 w-16 border-b-2 border-indigo-600 mx-auto mb-4"></div>
			<h2 class="text-xl font-semibold text-gray-900 mb-2">Loading Incentives...</h2>
			<p class="text-gray-600">Fetching global film incentive data...</p>
		</div>
	</div>
{:else if error}
	<div class="min-h-screen bg-gray-50 flex items-center justify-center">
		<div class="text-center">
			<div class="text-red-500 text-6xl mb-4">⚠️</div>
			<h2 class="text-xl font-semibold text-gray-900 mb-2">Error Loading Incentives</h2>
			<p class="text-gray-600 mb-4">{error}</p>
			<button 
				on:click={loadIncentives}
				class="btn-primary"
			>
				Try Again
			</button>
		</div>
	</div>
{:else}
	<!-- Main Content -->
	<div class="bg-gray-50 min-h-screen">
		<!-- Navigation Tabs -->
		<div class="bg-white border-b border-gray-200 sticky top-0 z-40">
			<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
				<nav class="flex space-x-8" aria-label="Tabs">
					<button 
						class="py-4 px-1 border-b-2 font-medium text-sm {!showCalculator && !showComparison && !showGrants ? 'border-indigo-500 text-indigo-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}"
						on:click={() => { showCalculator = false; showComparison = false; showGrants = false; }}
					>
						🗺️ Tax Credits & Rebates
					</button>
					<button 
						class="py-4 px-1 border-b-2 font-medium text-sm {showGrants ? 'border-indigo-500 text-indigo-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}"
						on:click={() => { showGrants = true; showCalculator = false; showComparison = false; }}
					>
						🎯 Grants & Awards ({grants.length})
					</button>
					<button 
						class="py-4 px-1 border-b-2 font-medium text-sm {showCalculator ? 'border-indigo-500 text-indigo-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}"
						on:click={() => { showCalculator = true; showComparison = false; showGrants = false; }}
					>
						🧮 Incentive Calculator
					</button>
					<button 
						class="py-4 px-1 border-b-2 font-medium text-sm {showComparison ? 'border-indigo-500 text-indigo-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}"
						on:click={() => { showComparison = true; showCalculator = false; showGrants = false; }}
					>
						⚖️ Location Comparison ({comparisonList.length})
					</button>
				</nav>
			</div>
		</div>
		
		{#if showCalculator}
			<!-- Calculator Section -->
			<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
				<div class="bg-white rounded-lg shadow-lg p-8">
					<h2 class="text-3xl font-bold text-gray-900 mb-6">💰 Film Incentive Calculator</h2>
					<p class="text-gray-600 mb-8">Calculate potential savings and find the best locations for your production budget.</p>
					
					<div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
						<!-- Calculator Input -->
						<div class="lg:col-span-1">
							<div class="bg-gradient-to-br from-indigo-50 to-purple-50 rounded-lg p-6">
								<h3 class="text-lg font-semibold text-gray-900 mb-4">Production Budget</h3>
								
								<div class="space-y-4">
									<div>
										<label class="block text-sm font-medium text-gray-700 mb-2">Budget Amount</label>
										<div class="relative">
											<span class="absolute left-3 top-3 text-gray-500">$</span>
											<input 
												type="number" 
												bind:value={calculatorBudget}
												class="w-full pl-8 pr-4 py-3 border border-gray-300 rounded-md focus:ring-indigo-500 focus:border-indigo-500"
												placeholder="5000000"
											/>
										</div>
									</div>
									
									<!-- Quick Budget Buttons -->
									<div class="grid grid-cols-2 gap-2">
										<button 
											on:click={() => calculatorBudget = 1000000}
											class="px-3 py-2 text-sm bg-white border border-gray-300 rounded-md hover:bg-gray-50"
										>
											$1M
										</button>
										<button 
											on:click={() => calculatorBudget = 5000000}
											class="px-3 py-2 text-sm bg-white border border-gray-300 rounded-md hover:bg-gray-50"
										>
											$5M
										</button>
										<button 
											on:click={() => calculatorBudget = 15000000}
											class="px-3 py-2 text-sm bg-white border border-gray-300 rounded-md hover:bg-gray-50"
										>
											$15M
										</button>
										<button 
											on:click={() => calculatorBudget = 50000000}
											class="px-3 py-2 text-sm bg-white border border-gray-300 rounded-md hover:bg-gray-50"
										>
											$50M
										</button>
									</div>
									
									<button 
										on:click={calculateIncentives}
										class="w-full btn-primary"
									>
										Calculate Savings
									</button>
								</div>
							</div>
						</div>
						
						<!-- Calculator Results -->
						<div class="lg:col-span-2">
							{#if calculatorResults.length > 0}
								<h3 class="text-lg font-semibold text-gray-900 mb-4">💡 Best Incentive Opportunities</h3>
								<div class="space-y-4">
									{#each calculatorResults.slice(0, 8) as result}
										<div class="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow">
											<div class="flex justify-between items-start">
												<div class="flex-1">
													<h4 class="text-lg font-semibold text-gray-900">
														{result.country}{result.region ? `, ${result.region}` : ''}
													</h4>
													<div class="flex items-center space-x-4 mt-2">
														<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium {getIncentiveTypeColor(result.incentive_type)}">
															{result.incentive_type.replace('_', ' ').toUpperCase()}
														</span>
														<span class="text-2xl font-bold {getPercentageColor(result.percentage)}">
															{result.percentage}%
														</span>
													</div>
												</div>
												<div class="text-right">
													<div class="text-2xl font-bold text-green-600">
														{formatCurrency(result.final_savings)}
													</div>
													<div class="text-sm text-gray-500">Potential Savings</div>
													<div class="text-sm text-gray-600 mt-1">
														Net Cost: {formatCurrency(result.net_production_cost)}
													</div>
												</div>
											</div>
											
											<div class="mt-4 grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
												<div>
													<span class="text-gray-500">Qualifying Spend:</span>
													<div class="font-medium">{formatCurrency(result.qualifying_spend)}</div>
												</div>
												<div>
													<span class="text-gray-500">Gross Savings:</span>
													<div class="font-medium">{formatCurrency(result.gross_savings)}</div>
												</div>
												<div>
													<span class="text-gray-500">Savings %:</span>
													<div class="font-medium">{result.savings_percentage.toFixed(1)}%</div>
												</div>
												<div>
													<span class="text-gray-500">Max Credit:</span>
													<div class="font-medium {result.max_credit_applied ? 'text-orange-600' : 'text-gray-900'}">
														{result.max_credit_applied ? 'Applied' : 'No Limit'}
													</div>
												</div>
											</div>
										</div>
									{/each}
								</div>
							{:else}
								<div class="text-center py-12">
									<div class="text-6xl mb-4">🧮</div>
									<h3 class="text-lg font-medium text-gray-900 mb-2">Ready to Calculate</h3>
									<p class="text-gray-600">Enter your budget and click "Calculate Savings" to see the best incentive opportunities.</p>
								</div>
							{/if}
						</div>
					</div>
				</div>
			</div>
		{:else if showComparison}
			<!-- Comparison Section -->
			<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
				<div class="bg-white rounded-lg shadow-lg p-8">
					<h2 class="text-3xl font-bold text-gray-900 mb-6">⚖️ Location Comparison Tool</h2>
					
					{#if comparisonList.length === 0}
						<div class="text-center py-12">
							<div class="text-6xl mb-4">⚖️</div>
							<h3 class="text-lg font-medium text-gray-900 mb-2">No Locations Selected</h3>
							<p class="text-gray-600 mb-4">Browse incentives and click "Add to Compare" to start comparing locations.</p>
							<button 
								on:click={() => { showComparison = false; showCalculator = false; }}
								class="btn-primary"
							>
								Browse Incentives
							</button>
						</div>
					{:else}
						<div class="overflow-x-auto">
							<table class="min-w-full divide-y divide-gray-200">
								<thead class="bg-gray-50">
									<tr>
										<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Location</th>
										<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Type</th>
										<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Percentage</th>
										<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Min Spend</th>
										<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Max Credit</th>
										<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Processing</th>
										<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
									</tr>
								</thead>
								<tbody class="bg-white divide-y divide-gray-200">
									{#each comparisonList as incentive}
										<tr>
											<td class="px-6 py-4 whitespace-nowrap">
												<div class="font-medium text-gray-900">{incentive.country}</div>
												{#if incentive.region}
													<div class="text-sm text-gray-500">{incentive.region}</div>
												{/if}
											</td>
											<td class="px-6 py-4 whitespace-nowrap">
												<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium {getIncentiveTypeColor(incentive.incentive_type)}">
													{incentive.incentive_type.replace('_', ' ').toUpperCase()}
												</span>
											</td>
											<td class="px-6 py-4 whitespace-nowrap">
												<span class="text-lg font-bold {getPercentageColor(incentive.percentage)}">
													{incentive.percentage}%
												</span>
											</td>
											<td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
												{formatCurrency(incentive.minimum_spend)}
											</td>
											<td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
												{formatCurrency(incentive.max_credit)}
											</td>
											<td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
												{incentive.processing_time_days ? `${incentive.processing_time_days} days` : 'Not specified'}
											</td>
											<td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
												<button 
													on:click={() => removeFromComparison(incentive.id)}
													class="text-red-600 hover:text-red-900"
												>
													Remove
												</button>
											</td>
										</tr>
									{/each}
								</tbody>
							</table>
						</div>
					{/if}
				</div>
			</div>
		{:else if showGrants}
			<!-- Grants & Awards Section -->
			<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
				<div class="bg-white rounded-lg shadow-lg p-8 mb-8">
					<h2 class="text-3xl font-bold text-gray-900 mb-6">🎯 Film Grants & Awards</h2>
					<p class="text-gray-600 mb-8">Discover funding opportunities, development grants, and awards that match your filmmaker profile and project needs.</p>
					
					<!-- Eligibility Checker -->
					<div class="bg-gradient-to-br from-purple-50 to-pink-50 rounded-lg p-6 mb-8">
						<h3 class="text-lg font-semibold text-gray-900 mb-4">🔍 Find Your Perfect Grants</h3>
						<p class="text-gray-600 mb-4">Tell us about yourself and your project to find the most relevant funding opportunities.</p>
						
						<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-4">
							<div>
								<label class="block text-sm font-medium text-gray-700 mb-2">Filmmaker Demographics</label>
								<select bind:value={filmmakerDemographics} class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-purple-500 focus:border-purple-500">
									<option value="">Select demographics</option>
									<option value="BIPOC filmmakers">BIPOC Filmmaker</option>
									<option value="Women filmmakers">Women Filmmaker</option>
									<option value="LGBTQ+ filmmakers">LGBTQ+ Filmmaker</option>
									<option value="Emerging filmmakers">Emerging Filmmaker</option>
									<option value="International filmmakers">International Filmmaker</option>
									<option value="Indigenous filmmakers">Indigenous Filmmaker</option>
								</select>
							</div>
							
							<div>
								<label class="block text-sm font-medium text-gray-700 mb-2">Project Genre</label>
								<select bind:value={projectGenre} class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-purple-500 focus:border-purple-500">
									<option value="">Select genre</option>
									<option value="documentary">Documentary</option>
									<option value="narrative">Narrative/Fiction</option>
									<option value="experimental">Experimental</option>
									<option value="animation">Animation</option>
									<option value="short_film">Short Film</option>
									<option value="feature_film">Feature Film</option>
								</select>
							</div>
							
							<div>
								<label class="block text-sm font-medium text-gray-700 mb-2">Project Stage</label>
								<select bind:value={projectStage} class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-purple-500 focus:border-purple-500">
									<option value="">Select stage</option>
									<option value="development">Development</option>
									<option value="production">Production</option>
									<option value="post_production">Post-Production</option>
									<option value="distribution">Distribution</option>
									<option value="festival">Festival Circuit</option>
								</select>
							</div>
							
							<div>
								<label class="block text-sm font-medium text-gray-700 mb-2">Budget Range</label>
								<select bind:value={budgetRange} class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-purple-500 focus:border-purple-500">
									<option value="">Select budget</option>
									<option value="under_50k">Under $50K</option>
									<option value="50k_250k">$50K - $250K</option>
									<option value="250k_1m">$250K - $1M</option>
									<option value="1m_5m">$1M - $5M</option>
									<option value="over_5m">Over $5M</option>
								</select>
							</div>
							
							<div>
								<label class="block text-sm font-medium text-gray-700 mb-2">Your Location</label>
								<input 
									type="text" 
									bind:value={filmmakerLocation}
									class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-purple-500 focus:border-purple-500"
									placeholder="e.g., New York, Canada, UK"
								/>
							</div>
							
							<div class="flex items-end">
								<button 
									on:click={checkGrantEligibility}
									class="w-full bg-purple-600 text-white px-4 py-2 rounded-md hover:bg-purple-700 transition-colors font-medium"
								>
									Find Matching Grants
								</button>
							</div>
						</div>
					</div>
					
					<!-- Eligible Grants Results -->
					{#if eligibleGrants.length > 0}
						<div class="mb-8">
							<h3 class="text-lg font-semibold text-gray-900 mb-4">✨ Your Personalized Grant Matches</h3>
							<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
								{#each eligibleGrants.slice(0, 6) as grant}
									<div class="bg-gradient-to-br from-purple-50 to-pink-50 border border-purple-200 rounded-lg p-6">
										<div class="flex justify-between items-start mb-3">
											<h4 class="text-lg font-semibold text-gray-900 pr-4">{grant.name}</h4>
											<div class="text-right">
												<div class="text-sm font-medium text-purple-600">{grant.eligibility_score.toFixed(0)}% Match</div>
												<div class="text-xs text-gray-500">Success Rate: {grant.success_rate_percentage}%</div>
											</div>
										</div>
										
										<p class="text-sm text-gray-600 mb-3">{grant.organization} • {grant.country}</p>
										
										<div class="flex justify-between items-center mb-3">
											<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
												{grant.grant_type.replace('_', ' ').toUpperCase()}
											</span>
											<div class="text-right">
												<div class="text-lg font-bold text-green-600">
													{formatCurrency(grant.amount_min)} - {formatCurrency(grant.amount_max)}
												</div>
												<div class="text-xs text-gray-500">Avg: {formatCurrency(grant.average_award_amount)}</div>
											</div>
										</div>
										
										{#if grant.match_reasons && grant.match_reasons.length > 0}
											<div class="mb-3">
												<div class="text-xs text-gray-500 mb-1">Why you match:</div>
												{#each grant.match_reasons as reason}
													<div class="text-xs bg-green-100 text-green-800 px-2 py-1 rounded inline-block mr-1 mb-1">
														{reason}
													</div>
												{/each}
											</div>
										{/if}
										
										<div class="flex space-x-2">
											<button 
												on:click={() => selectedGrant = grant}
												class="flex-1 bg-purple-600 text-white px-3 py-2 rounded-md hover:bg-purple-700 transition-colors text-sm font-medium"
											>
												View Details
											</button>
											{#if grant.website_url}
												<a 
													href={grant.website_url} 
													target="_blank"
													class="px-3 py-2 border border-purple-300 text-purple-700 rounded-md hover:bg-purple-50 transition-colors text-sm font-medium"
												>
													Apply →
												</a>
											{/if}
										</div>
									</div>
								{/each}
							</div>
						</div>
					{/if}
					
					<!-- All Grants Grid -->
					<h3 class="text-lg font-semibold text-gray-900 mb-4">📚 All Available Grants & Awards</h3>
					<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
						{#each grants.slice(0, 12) as grant}
							<div class="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow">
								<div class="mb-4">
									<h4 class="text-lg font-semibold text-gray-900 mb-2">{grant.name}</h4>
									<p class="text-sm text-gray-600">{grant.organization}</p>
									<p class="text-sm text-gray-500">{grant.country}{grant.region ? `, ${grant.region}` : ''}</p>
								</div>
								
								<div class="flex justify-between items-center mb-4">
									<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-indigo-100 text-indigo-800">
										{grant.grant_type.replace('_', ' ').toUpperCase()}
									</span>
									<div class="text-right">
										<div class="text-lg font-bold text-green-600">
											{formatCurrency(grant.average_award_amount)}
										</div>
										<div class="text-xs text-gray-500">Average Award</div>
									</div>
								</div>
								
								<div class="text-sm space-y-2 mb-4">
									<div class="flex justify-between">
										<span class="text-gray-500">Range:</span>
										<span class="font-medium">{formatCurrency(grant.amount_min)} - {formatCurrency(grant.amount_max)}</span>
									</div>
									<div class="flex justify-between">
										<span class="text-gray-500">Success Rate:</span>
										<span class="font-medium">{grant.success_rate_percentage}%</span>
									</div>
									<div class="flex justify-between">
										<span class="text-gray-500">Frequency:</span>
										<span class="font-medium capitalize">{grant.application_frequency}</span>
									</div>
								</div>
								
								<div class="flex space-x-2">
									<button 
										on:click={() => selectedGrant = grant}
										class="flex-1 bg-indigo-600 text-white px-3 py-2 rounded-md hover:bg-indigo-700 transition-colors text-sm font-medium"
									>
										Details
									</button>
									{#if grant.website_url}
										<a 
											href={grant.website_url} 
											target="_blank"
											class="px-3 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 transition-colors text-sm font-medium"
										>
											Apply
										</a>
									{/if}
								</div>
							</div>
						{/each}
					</div>
				</div>
			</div>
		{:else}
			<!-- Main Browse Section -->
			<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
				<!-- Filters -->
				<div class="bg-white rounded-lg shadow-lg p-6 mb-8">
					<h2 class="text-lg font-semibold text-gray-900 mb-4">🔍 Filter & Search</h2>
					
					<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
						<div>
							<label class="block text-sm font-medium text-gray-700 mb-2">Country</label>
							<select bind:value={selectedCountry} class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-indigo-500 focus:border-indigo-500">
								<option value="">All Countries</option>
								{#each countries as country}
									<option value={country}>{country}</option>
								{/each}
							</select>
						</div>
						
						<div>
							<label class="block text-sm font-medium text-gray-700 mb-2">Incentive Type</label>
							<select bind:value={selectedType} class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-indigo-500 focus:border-indigo-500">
								<option value="">All Types</option>
								{#each incentiveTypes as type}
									<option value={type}>{type.replace('_', ' ').toUpperCase()}</option>
								{/each}
							</select>
						</div>
						
						<div>
							<label class="block text-sm font-medium text-gray-700 mb-2">Min Percentage</label>
							<input 
								type="number" 
								bind:value={minPercentage}
								min="0" 
								max="100"
								class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-indigo-500 focus:border-indigo-500"
								placeholder="0"
							/>
						</div>
						
						<div>
							<label class="block text-sm font-medium text-gray-700 mb-2">Search</label>
							<input 
								type="text" 
								bind:value={searchQuery}
								class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-indigo-500 focus:border-indigo-500"
								placeholder="Search locations..."
							/>
						</div>
					</div>
					
					<div class="flex justify-between items-center">
						<div class="text-sm text-gray-600">
							Showing {filteredIncentives.length} of {incentives.length} incentives
						</div>
						<button 
							on:click={resetFilters}
							class="text-sm text-indigo-600 hover:text-indigo-800"
						>
							Reset Filters
						</button>
					</div>
				</div>
				
				<!-- Interactive Map -->
				<IncentiveMap 
					{incentives} 
					onCountrySelect={handleCountrySelect} 
				/>
				
				<!-- Incentives Grid -->
				<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
					{#each filteredIncentives as incentive}
						<div class="bg-white rounded-lg shadow-lg hover:shadow-xl transition-shadow duration-200 overflow-hidden">
							<!-- Header -->
							<div class="bg-gradient-to-r from-indigo-500 to-purple-600 px-6 py-4">
								<h3 class="text-lg font-semibold text-white">
									{incentive.country}
								</h3>
								{#if incentive.region}
									<p class="text-indigo-100 text-sm">{incentive.region}</p>
								{/if}
							</div>
							
							<!-- Content -->
							<div class="p-6">
								<div class="flex items-center justify-between mb-4">
									<span class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium {getIncentiveTypeColor(incentive.incentive_type)}">
										{incentive.incentive_type.replace('_', ' ').toUpperCase()}
									</span>
									<span class="text-3xl font-bold {getPercentageColor(incentive.percentage)}">
										{incentive.percentage}%
									</span>
								</div>
								
								<div class="space-y-3 text-sm">
									<div class="flex justify-between">
										<span class="text-gray-500">Minimum Spend:</span>
										<span class="font-medium">{formatCurrency(incentive.minimum_spend)}</span>
									</div>
									<div class="flex justify-between">
										<span class="text-gray-500">Maximum Credit:</span>
										<span class="font-medium">{formatCurrency(incentive.max_credit)}</span>
									</div>
									{#if incentive.processing_time_days}
										<div class="flex justify-between">
											<span class="text-gray-500">Processing Time:</span>
											<span class="font-medium">{incentive.processing_time_days} days</span>
										</div>
									{/if}
								</div>
								
								<!-- Actions -->
								<div class="mt-6 flex space-x-2">
									<button 
										on:click={() => selectedIncentive = incentive}
										class="flex-1 bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700 transition-colors text-sm font-medium"
									>
										View Details
									</button>
									<button 
										on:click={() => addToComparison(incentive)}
										class="px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 transition-colors text-sm font-medium"
										disabled={comparisonList.length >= 4 || comparisonList.find(i => i.id === incentive.id)}
									>
										{comparisonList.find(i => i.id === incentive.id) ? '✓' : '+'}
									</button>
								</div>
							</div>
						</div>
					{/each}
				</div>
				
				{#if filteredIncentives.length === 0}
					<div class="text-center py-12">
						<div class="text-6xl mb-4">🔍</div>
						<h3 class="text-lg font-medium text-gray-900 mb-2">No Incentives Found</h3>
						<p class="text-gray-600 mb-4">Try adjusting your filters to see more results.</p>
						<button 
							on:click={resetFilters}
							class="btn-primary"
						>
							Reset Filters
						</button>
					</div>
				{/if}
			</div>
		{/if}
	</div>
	
	<!-- Detail Modal -->
	{#if selectedIncentive}
		<div class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50" on:click={() => selectedIncentive = null}>
			<div class="relative top-20 mx-auto p-5 border w-11/12 md:w-3/4 lg:w-1/2 shadow-lg rounded-md bg-white" on:click|stopPropagation>
				<div class="mt-3">
					<div class="flex justify-between items-start mb-4">
						<h3 class="text-2xl font-bold text-gray-900">
							{selectedIncentive.country}
							{#if selectedIncentive.region}
								<span class="text-lg text-gray-600">- {selectedIncentive.region}</span>
							{/if}
						</h3>
						<button 
							on:click={() => selectedIncentive = null}
							class="text-gray-400 hover:text-gray-600 text-2xl"
						>
							×
						</button>
					</div>
					
					<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
						<div>
							<h4 class="font-semibold text-gray-900 mb-3">Incentive Details</h4>
							<div class="space-y-2 text-sm">
								<div class="flex justify-between">
									<span class="text-gray-500">Type:</span>
									<span class="font-medium">{selectedIncentive.incentive_type.replace('_', ' ').toUpperCase()}</span>
								</div>
								<div class="flex justify-between">
									<span class="text-gray-500">Percentage:</span>
									<span class="font-bold text-lg {getPercentageColor(selectedIncentive.percentage)}">{selectedIncentive.percentage}%</span>
								</div>
								<div class="flex justify-between">
									<span class="text-gray-500">Minimum Spend:</span>
									<span class="font-medium">{formatCurrency(selectedIncentive.minimum_spend)}</span>
								</div>
								<div class="flex justify-between">
									<span class="text-gray-500">Maximum Credit:</span>
									<span class="font-medium">{formatCurrency(selectedIncentive.max_credit)}</span>
								</div>
								{#if selectedIncentive.processing_time_days}
									<div class="flex justify-between">
										<span class="text-gray-500">Processing Time:</span>
										<span class="font-medium">{selectedIncentive.processing_time_days} days</span>
									</div>
								{/if}
							</div>
						</div>
						
						<div>
							<h4 class="font-semibold text-gray-900 mb-3">Requirements</h4>
							{#if selectedIncentive.requirements && Object.keys(selectedIncentive.requirements).length > 0}
								<div class="text-sm space-y-1">
									{#each Object.entries(selectedIncentive.requirements) as [key, value]}
										<div class="flex justify-between">
											<span class="text-gray-500 capitalize">{key.replace('_', ' ')}:</span>
											<span class="font-medium">{value}</span>
										</div>
									{/each}
								</div>
							{:else}
								<p class="text-sm text-gray-500">No specific requirements listed</p>
							{/if}
						</div>
					</div>
					
					<div class="mt-6 flex space-x-3">
						<button 
							on:click={() => addToComparison(selectedIncentive)}
							class="flex-1 bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700 transition-colors font-medium"
							disabled={comparisonList.length >= 4 || comparisonList.find(i => i.id === selectedIncentive.id)}
						>
							{comparisonList.find(i => i.id === selectedIncentive.id) ? 'Already in Comparison' : 'Add to Comparison'}
						</button>
						<button 
							on:click={() => selectedIncentive = null}
							class="px-6 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 transition-colors font-medium"
						>
							Close
						</button>
					</div>
				</div>
			</div>
		</div>
	{/if}
	
	<!-- Grant Detail Modal -->
	{#if selectedGrant}
		<div class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50" on:click={() => selectedGrant = null}>
			<div class="relative top-20 mx-auto p-5 border w-11/12 md:w-3/4 lg:w-1/2 shadow-lg rounded-md bg-white" on:click|stopPropagation>
				<div class="mt-3">
					<div class="flex justify-between items-start mb-4">
						<div>
							<h3 class="text-2xl font-bold text-gray-900">{selectedGrant.name}</h3>
							<p class="text-lg text-gray-600">{selectedGrant.organization}</p>
							<p class="text-sm text-gray-500">{selectedGrant.country}{selectedGrant.region ? `, ${selectedGrant.region}` : ''}</p>
						</div>
						<button 
							on:click={() => selectedGrant = null}
							class="text-gray-400 hover:text-gray-600 text-2xl"
						>
							×
						</button>
					</div>
					
					<div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
						<div>
							<h4 class="font-semibold text-gray-900 mb-3">Grant Details</h4>
							<div class="space-y-2 text-sm">
								<div class="flex justify-between">
									<span class="text-gray-500">Type:</span>
									<span class="font-medium capitalize">{selectedGrant.grant_type.replace('_', ' ')}</span>
								</div>
								<div class="flex justify-between">
									<span class="text-gray-500">Amount Range:</span>
									<span class="font-medium">{formatCurrency(selectedGrant.amount_min)} - {formatCurrency(selectedGrant.amount_max)}</span>
								</div>
								<div class="flex justify-between">
									<span class="text-gray-500">Average Award:</span>
									<span class="font-bold text-green-600">{formatCurrency(selectedGrant.average_award_amount)}</span>
								</div>
								<div class="flex justify-between">
									<span class="text-gray-500">Success Rate:</span>
									<span class="font-medium">{selectedGrant.success_rate_percentage}%</span>
								</div>
								<div class="flex justify-between">
									<span class="text-gray-500">Application Frequency:</span>
									<span class="font-medium capitalize">{selectedGrant.application_frequency}</span>
								</div>
								{#if selectedGrant.application_deadline}
									<div class="flex justify-between">
										<span class="text-gray-500">Next Deadline:</span>
										<span class="font-medium">{new Date(selectedGrant.application_deadline).toLocaleDateString()}</span>
									</div>
								{/if}
							</div>
						</div>
						
						<div>
							<h4 class="font-semibold text-gray-900 mb-3">Target Demographics</h4>
							{#if selectedGrant.target_demographics && selectedGrant.target_demographics.length > 0}
								<div class="flex flex-wrap gap-1 mb-4">
									{#each selectedGrant.target_demographics as demo}
										<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
											{demo}
										</span>
									{/each}
								</div>
							{:else}
								<p class="text-sm text-gray-500 mb-4">Open to all filmmakers</p>
							{/if}
							
							<h4 class="font-semibold text-gray-900 mb-3">Genre Focus</h4>
							{#if selectedGrant.genre_focus && selectedGrant.genre_focus.length > 0}
								<div class="flex flex-wrap gap-1">
									{#each selectedGrant.genre_focus as genre}
										<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-indigo-100 text-indigo-800">
											{genre}
										</span>
									{/each}
								</div>
							{:else}
								<p class="text-sm text-gray-500">All genres accepted</p>
							{/if}
						</div>
					</div>
					
					{#if selectedGrant.eligibility_requirements && Object.keys(selectedGrant.eligibility_requirements).length > 0}
						<div class="mb-6">
							<h4 class="font-semibold text-gray-900 mb-3">Eligibility Requirements</h4>
							<div class="bg-gray-50 rounded-lg p-4">
								<div class="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
									{#each Object.entries(selectedGrant.eligibility_requirements) as [key, value]}
										<div>
											<span class="text-gray-500 capitalize">{key.replace('_', ' ')}:</span>
											<span class="font-medium ml-2">{value}</span>
										</div>
									{/each}
								</div>
							</div>
						</div>
					{/if}
					
					<div class="flex space-x-3">
						{#if selectedGrant.website_url}
							<a 
								href={selectedGrant.website_url} 
								target="_blank"
								class="flex-1 bg-purple-600 text-white px-4 py-2 rounded-md hover:bg-purple-700 transition-colors font-medium text-center"
							>
								Visit Official Website →
							</a>
						{/if}
						<button 
							on:click={() => selectedGrant = null}
							class="px-6 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 transition-colors font-medium"
						>
							Close
						</button>
					</div>
				</div>
			</div>
		</div>
			{/if}
{/if}


