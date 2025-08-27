<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import { browser } from '$app/environment';
	
	export let incentives: any[] = [];
	export let onCountrySelect: (country: string) => void = () => {};
	
	let mapContainer: HTMLElement;
	let map: any = null;
	let L: any = null;
	let mounted = false;
	let initializing = false;
	
	onMount(async () => {
		mounted = true;
		if (browser && incentives.length > 0) {
			await initializeMap();
		}
	});
	
	onDestroy(() => {
		if (map) {
			map.remove();
			map = null;
		}
	});
	
	// Reactive statement to update map when incentives change
	$: if (mounted && browser && incentives.length > 0 && !map && !initializing) {
		initializeMap();
	}
	
	async function initializeMap() {
		if (!browser || !mapContainer || map || initializing) return;
		
		initializing = true;
		
		try {
			// Dynamically import Leaflet
			const leafletModule = await import('leaflet');
			L = leafletModule.default;
			
			// Initialize map
			map = L.map(mapContainer).setView([40.0, 0.0], 2);
			
			// Add tile layer
			L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
				attribution: '© OpenStreetMap contributors'
			}).addTo(map);
			
			// Add incentive markers
			addIncentiveMarkers();
			
			console.log('✅ Interactive map initialized successfully');
		} catch (error) {
			console.error('❌ Map initialization failed:', error);
		} finally {
			initializing = false;
		}
	}
	
	function addIncentiveMarkers() {
		if (!map || !L || !incentives.length) return;
		
		// Country coordinates mapping
		const countryCoords: Record<string, [number, number]> = {
			'United States': [39.8283, -98.5795],
			'Canada': [56.1304, -106.3468],
			'United Kingdom': [55.3781, -3.4360],
			'Ireland': [53.1424, -7.6921],
			'Australia': [-25.2744, 133.7751],
			'New Zealand': [-40.9006, 174.8860],
			'Germany': [51.1657, 10.4515],
			'France': [46.2276, 2.2137],
			'Italy': [41.8719, 12.5674],
			'Spain': [40.4637, -3.7492],
			'Czech Republic': [49.8175, 15.4730],
			'South Africa': [-30.5595, 22.9375],
			'Iceland': [64.9631, -19.0208],
			'Malta': [35.9375, 14.3754],
			'Hungary': [47.1625, 19.5033],
			'Croatia': [45.1000, 15.2000],
			'Belgium': [50.8503, 4.3517],
			'Netherlands': [52.1326, 5.2913],
			'Norway': [60.4720, 8.4689],
			'Sweden': [60.1282, 18.6435],
			'Denmark': [56.2639, 9.5018],
			'Finland': [61.9241, 25.7482],
			'Poland': [51.9194, 19.1451],
			'Japan': [36.2048, 138.2529],
			'South Korea': [35.9078, 127.7669],
			'Singapore': [1.3521, 103.8198],
			'Malaysia': [4.2105, 101.9758],
			'Thailand': [15.8700, 100.9925],
			'Philippines': [12.8797, 121.7740],
			'Mexico': [23.6345, -102.5528],
			'Colombia': [4.5709, -74.2973],
			'Argentina': [-38.4161, -63.6167],
			'Chile': [-35.6751, -71.5430],
			'Morocco': [31.7917, -7.0926],
			'Tunisia': [33.8869, 9.5375],
			'Jordan': [30.5852, 36.2384],
			'United Arab Emirates': [23.4241, 53.8478]
		};
		
		// Group incentives by country
		const incentivesByCountry = incentives.reduce((acc, incentive) => {
			const country = incentive.country;
			if (!acc[country]) acc[country] = [];
			acc[country].push(incentive);
			return acc;
		}, {} as Record<string, any[]>);
		
		// Create markers for each country
		Object.entries(incentivesByCountry).forEach(([country, countryIncentives]) => {
			const coords = countryCoords[country];
			if (!coords) return;
			
			// Calculate average percentage for marker color
			const avgPercentage = countryIncentives.reduce((sum, inc) => sum + (inc.percentage || 0), 0) / countryIncentives.length;
			
			// Create custom marker based on incentive strength
			const markerColor = getMarkerColor(avgPercentage);
			const markerSize = Math.max(10, Math.min(25, countryIncentives.length * 3));
			
			const marker = L.circleMarker(coords, {
				radius: markerSize,
				fillColor: markerColor,
				color: '#fff',
				weight: 2,
				opacity: 1,
				fillOpacity: 0.8
			}).addTo(map);
			
			// Create popup content
			const popupContent = createMarkerPopup(country, countryIncentives);
			marker.bindPopup(popupContent, { maxWidth: 400 });
			
			// Add click handler
			marker.on('click', () => {
				onCountrySelect(country);
			});
		});
	}
	
	function getMarkerColor(percentage: number): string {
		if (percentage >= 40) return '#dc2626'; // Red for high incentives
		if (percentage >= 30) return '#ea580c'; // Orange-red
		if (percentage >= 20) return '#d97706'; // Orange
		if (percentage >= 15) return '#ca8a04'; // Yellow-orange
		if (percentage >= 10) return '#65a30d'; // Yellow-green
		return '#16a34a'; // Green for lower incentives
	}
	
	function createMarkerPopup(country: string, countryIncentives: any[]): string {
		const maxIncentive = Math.max(...countryIncentives.map(i => i.percentage || 0));
		const totalIncentives = countryIncentives.length;
		
		let popupHtml = `
			<div class="p-3">
				<h3 class="font-bold text-lg mb-2">${country}</h3>
				<div class="space-y-1 text-sm">
					<div class="flex justify-between">
						<span>Total Incentives:</span>
						<span class="font-semibold">${totalIncentives}</span>
					</div>
					<div class="flex justify-between">
						<span>Max Percentage:</span>
						<span class="font-semibold text-green-600">${maxIncentive}%</span>
					</div>
				</div>
				<div class="mt-3">
					<h4 class="font-semibold mb-1">Top Incentives:</h4>
					<div class="space-y-1">
		`;
		
		// Show top 3 incentives
		const topIncentives = countryIncentives
			.sort((a, b) => (b.percentage || 0) - (a.percentage || 0))
			.slice(0, 3);
			
		topIncentives.forEach(incentive => {
			popupHtml += `
				<div class="text-xs bg-gray-100 p-1 rounded">
					<span class="font-medium">${incentive.percentage}%</span>
					${incentive.region ? ` - ${incentive.region}` : ''}
					<span class="text-gray-600">(${incentive.incentive_type.replace('_', ' ')})</span>
				</div>
			`;
		});
		
		popupHtml += `
					</div>
					<button class="mt-2 bg-indigo-600 text-white px-3 py-1 rounded text-xs hover:bg-indigo-700" 
							onclick="window.filterByCountry && window.filterByCountry('${country}')">
						View All ${country} Incentives
					</button>
				</div>
			</div>
		`;
		
		return popupHtml;
	}
	
	// Set up global function for popup buttons
	onMount(() => {
		if (browser) {
			(window as any).filterByCountry = (country: string) => {
				onCountrySelect(country);
			};
		}
	});
</script>

<svelte:head>
	{#if browser}
		<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" 
			  integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY=" 
			  crossorigin=""/>
	{/if}
</svelte:head>

<div class="bg-white rounded-lg shadow-lg p-6 mb-8">
	<div class="flex items-center justify-between mb-4">
		<h2 class="text-lg font-semibold text-gray-900">🗺️ Interactive Incentive Map</h2>
		<div class="text-sm text-gray-600">
			Click markers to filter by country
		</div>
	</div>
	<div bind:this={mapContainer} class="rounded-lg h-96 w-full border border-gray-200"></div>
	
	<!-- Map Legend -->
	<div class="mt-4 flex flex-wrap items-center gap-4 text-xs">
		<div class="flex items-center gap-2">
			<div class="w-3 h-3 rounded-full bg-red-600"></div>
			<span>40%+ Incentives</span>
		</div>
		<div class="flex items-center gap-2">
			<div class="w-3 h-3 rounded-full bg-orange-600"></div>
			<span>30-39%</span>
		</div>
		<div class="flex items-center gap-2">
			<div class="w-3 h-3 rounded-full bg-yellow-600"></div>
			<span>20-29%</span>
		</div>
		<div class="flex items-center gap-2">
			<div class="w-3 h-3 rounded-full bg-yellow-500"></div>
			<span>15-19%</span>
		</div>
		<div class="flex items-center gap-2">
			<div class="w-3 h-3 rounded-full bg-green-500"></div>
			<span>10-14%</span>
		</div>
		<div class="flex items-center gap-2">
			<div class="w-3 h-3 rounded-full bg-green-600"></div>
			<span>Under 10%</span>
		</div>
	</div>
</div>

<style>
	:global(.leaflet-popup-content-wrapper) {
		border-radius: 8px;
	}
	
	:global(.leaflet-popup-content) {
		margin: 0;
		padding: 0;
	}
	
	:global(.leaflet-container) {
		font-family: inherit;
	}
</style>
