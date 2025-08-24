<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';

	let user: { id: string; email: string } | null = null;

	onMount(async () => {
		try {
			const response = await fetch('/api/auth/me');
			const data = await response.json();
			if (data.success) {
				user = data.user;
			}
		} catch (error) {
			// User not logged in, that's fine for about page
		}
	});
</script>

<svelte:head>
	<title>About - Lolita Screenplay Analysis Tool</title>
	<meta name="description" content="Learn about Lolita, the professional AI-powered screenplay analysis platform that combines Claude Opus 4.1, Grok 4, and ChatGPT-5 for comprehensive script evaluation." />
</svelte:head>

<div class="bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 min-h-screen">
	<!-- Hero Section -->
	<div class="relative overflow-hidden">
		<div class="absolute inset-0 opacity-20">
			<div class="w-full h-full" style="background-image: url('data:image/svg+xml,<svg width=&quot;60&quot; height=&quot;60&quot; viewBox=&quot;0 0 60 60&quot; xmlns=&quot;http://www.w3.org/2000/svg&quot;><g fill=&quot;none&quot; fill-rule=&quot;evenodd&quot;><g fill=&quot;%23ffffff&quot; fill-opacity=&quot;0.02&quot;><circle cx=&quot;30&quot; cy=&quot;30&quot; r=&quot;2&quot;/></g></g></svg>');"></div>
		</div>
		
		<div class="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24">
			<div class="text-center">
				<h1 class="text-5xl sm:text-6xl lg:text-7xl font-bold tracking-tight mb-8">
					<span class="block text-white mb-2">About</span>
					<span class="block bg-gradient-to-r from-blue-400 via-purple-400 to-yellow-400 bg-clip-text text-transparent">
						Lolita
					</span>
				</h1>
				<p class="text-xl text-blue-100 max-w-4xl mx-auto leading-relaxed">
					The world's most advanced screenplay analysis platform, combining professional narrative expertise, 
					brutally honest industry insights, and comprehensive commercial evaluation to deliver unparalleled script assessment.
				</p>
			</div>
		</div>
	</div>

	<!-- Mission Section -->
	<div class="py-20 bg-white">
		<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
			<div class="text-center mb-16">
				<h2 class="text-4xl font-bold text-gray-900 mb-6">Our Mission</h2>
				<p class="text-xl text-gray-600 max-w-4xl mx-auto leading-relaxed">
					To democratize professional screenplay analysis by providing writers with access to the same level of insight 
					that top Hollywood executives and script consultants use, powered by cutting-edge artificial intelligence.
				</p>
			</div>

			<div class="grid grid-cols-1 md:grid-cols-3 gap-8">
				<div class="text-center">
					<div class="w-20 h-20 mx-auto mb-6 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full flex items-center justify-center">
						<span class="text-white text-3xl">🎯</span>
					</div>
					<h3 class="text-xl font-semibold text-gray-900 mb-4">Professional Quality</h3>
					<p class="text-gray-600">
						Deliver Hollywood-level script analysis with detailed feedback on structure, character development, 
						dialogue, and market potential.
					</p>
				</div>

				<div class="text-center">
					<div class="w-20 h-20 mx-auto mb-6 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full flex items-center justify-center">
						<span class="text-white text-3xl">🤖</span>
					</div>
					<h3 class="text-xl font-semibold text-gray-900 mb-4">AI Innovation</h3>
					<p class="text-gray-600">
						Leverage the latest AI models to provide multiple perspectives and comprehensive analysis 
						that traditional methods cannot match.
					</p>
				</div>

				<div class="text-center">
					<div class="w-20 h-20 mx-auto mb-6 bg-gradient-to-r from-green-500 to-teal-500 rounded-full flex items-center justify-center">
						<span class="text-white text-3xl">🚀</span>
					</div>
					<h3 class="text-xl font-semibold text-gray-900 mb-4">Accessibility</h3>
					<p class="text-gray-600">
						Make professional script analysis accessible to writers at all levels, from beginners 
						to established professionals.
					</p>
				</div>
			</div>
		</div>
	</div>

	<!-- Technology Section -->
	<div class="py-20 bg-gradient-to-b from-slate-50 to-white">
		<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
			<div class="text-center mb-16">
				<h2 class="text-4xl font-bold text-gray-900 mb-6">Cutting-Edge Technology</h2>
				<p class="text-xl text-gray-600 max-w-4xl mx-auto">
					Built with modern web technologies and powered by advanced analysis engines for 
					unparalleled screenplay evaluation capabilities.
				</p>
			</div>

			<div class="grid grid-cols-1 lg:grid-cols-2 gap-12">
				<!-- Analysis Methodology -->
				<div class="space-y-6">
					<h3 class="text-2xl font-bold text-gray-900 mb-6">Analysis Methodology</h3>
					
					<div class="space-y-4">
						<div class="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
							<div class="flex items-center mb-3">
								<div class="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-500 rounded-lg flex items-center justify-center mr-4">
									<span class="text-white text-lg">🎯</span>
								</div>
								<h4 class="text-lg font-semibold text-gray-900">Craft Analysis</h4>
							</div>
							<p class="text-gray-600">
								Professional narrative structure analysis, character development insights, 
								and craft evaluation with industry-standard terminology and methodology.
							</p>
						</div>

						<div class="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
							<div class="flex items-center mb-3">
								<div class="w-10 h-10 bg-gradient-to-r from-purple-500 to-pink-500 rounded-lg flex items-center justify-center mr-4">
									<span class="text-white text-lg">💀</span>
								</div>
								<h4 class="text-lg font-semibold text-gray-900">Reality Check</h4>
							</div>
							<p class="text-gray-600">
								Brutally honest feedback with cultural awareness, 
								providing unfiltered industry reality checks and market viability insights.
							</p>
						</div>

						<div class="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
							<div class="flex items-center mb-3">
								<div class="w-10 h-10 bg-gradient-to-r from-green-500 to-emerald-500 rounded-lg flex items-center justify-center mr-4">
									<span class="text-white text-lg">🏢</span>
								</div>
								<h4 class="text-lg font-semibold text-gray-900">Commercial Intelligence</h4>
							</div>
							<p class="text-gray-600">
								Commercial viability assessment, studio fit evaluation, and professional development 
								insights with industry-focused market intelligence.
							</p>
						</div>
					</div>
				</div>

				<!-- Tech Stack -->
				<div class="space-y-6">
					<h3 class="text-2xl font-bold text-gray-900 mb-6">Technical Architecture</h3>
					
					<div class="space-y-4">
						<div class="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
							<div class="flex items-center mb-3">
								<div class="w-10 h-10 bg-gradient-to-r from-orange-500 to-red-500 rounded-lg flex items-center justify-center mr-4">
									<span class="text-white text-lg">⚡</span>
								</div>
								<h4 class="text-lg font-semibold text-gray-900">Frontend</h4>
							</div>
							<p class="text-gray-600">
								SvelteKit 2.x with TypeScript and Tailwind CSS 4.x for a modern, responsive, 
								and lightning-fast user experience.
							</p>
						</div>

						<div class="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
							<div class="flex items-center mb-3">
								<div class="w-10 h-10 bg-gradient-to-r from-blue-500 to-cyan-500 rounded-lg flex items-center justify-center mr-4">
									<span class="text-white text-lg">🐍</span>
								</div>
								<h4 class="text-lg font-semibold text-gray-900">Backend</h4>
							</div>
							<p class="text-gray-600">
								Python FastAPI for AI processing with Node.js API routes for user management, 
								providing optimal performance and scalability.
							</p>
						</div>

						<div class="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
							<div class="flex items-center mb-3">
								<div class="w-10 h-10 bg-gradient-to-r from-yellow-500 to-orange-500 rounded-lg flex items-center justify-center mr-4">
									<span class="text-white text-lg">🗄️</span>
								</div>
								<h4 class="text-lg font-semibold text-gray-900">Database</h4>
							</div>
							<p class="text-gray-600">
								MySQL with connection pooling for reliable data storage and efficient 
								query performance for large-scale analysis tracking.
							</p>
						</div>
					</div>
				</div>
			</div>
		</div>
	</div>

	<!-- Features Section -->
	<div class="py-20 bg-white">
		<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
			<div class="text-center mb-16">
				<h2 class="text-4xl font-bold text-gray-900 mb-6">Comprehensive Features</h2>
				<p class="text-xl text-gray-600 max-w-4xl mx-auto">
					Everything you need for professional screenplay analysis, from AI-powered feedback 
					to Hollywood poster generation and market intelligence.
				</p>
			</div>

			<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
				<div class="bg-gradient-to-br from-blue-50 to-purple-50 rounded-xl p-8 border border-blue-200">
					<div class="w-12 h-12 bg-gradient-to-r from-blue-500 to-purple-500 rounded-lg flex items-center justify-center mb-4">
						<span class="text-white text-xl">📊</span>
					</div>
					<h3 class="text-xl font-semibold text-gray-900 mb-3">Triple AI Analysis</h3>
					<p class="text-gray-600">
						Get comprehensive feedback from three different AI perspectives, each specializing 
						in different aspects of screenplay evaluation.
					</p>
				</div>

				<div class="bg-gradient-to-br from-purple-50 to-pink-50 rounded-xl p-8 border border-purple-200">
					<div class="w-12 h-12 bg-gradient-to-r from-purple-500 to-pink-500 rounded-lg flex items-center justify-center mb-4">
						<span class="text-white text-xl">🎬</span>
					</div>
					<h3 class="text-xl font-semibold text-gray-900 mb-3">Hollywood Posters</h3>
					<p class="text-gray-600">
						AI-generated movie poster concepts that visualize your story's cinematic potential 
						and help you pitch your screenplay.
					</p>
				</div>

				<div class="bg-gradient-to-br from-green-50 to-emerald-50 rounded-xl p-8 border border-green-200">
					<div class="w-12 h-12 bg-gradient-to-r from-green-500 to-emerald-500 rounded-lg flex items-center justify-center mb-4">
						<span class="text-white text-xl">💰</span>
					</div>
					<h3 class="text-xl font-semibold text-gray-900 mb-3">Financial Analysis</h3>
					<p class="text-gray-600">
						Detailed cost analysis, budget estimates, and commercial viability assessment 
						for your screenplay project.
					</p>
				</div>

				<div class="bg-gradient-to-br from-yellow-50 to-orange-50 rounded-xl p-8 border border-yellow-200">
					<div class="w-12 h-12 bg-gradient-to-r from-yellow-500 to-orange-500 rounded-lg flex items-center justify-center mb-4">
						<span class="text-white text-xl">📈</span>
					</div>
					<h3 class="text-xl font-semibold text-gray-900 mb-3">Market Intelligence</h3>
					<p class="text-gray-600">
						Industry insights, target audience analysis, and competitive landscape evaluation 
						to position your script for success.
					</p>
				</div>

				<div class="bg-gradient-to-br from-red-50 to-pink-50 rounded-xl p-8 border border-red-200">
					<div class="w-12 h-12 bg-gradient-to-r from-red-500 to-pink-500 rounded-lg flex items-center justify-center mb-4">
						<span class="text-white text-xl">🎭</span>
					</div>
					<h3 class="text-xl font-semibold text-gray-900 mb-3">Production Insights</h3>
					<p class="text-gray-600">
						Detailed production considerations, casting suggestions, and technical requirements 
						for bringing your script to life.
					</p>
				</div>

				<div class="bg-gradient-to-br from-indigo-50 to-blue-50 rounded-xl p-8 border border-indigo-200">
					<div class="w-12 h-12 bg-gradient-to-r from-indigo-500 to-blue-500 rounded-lg flex items-center justify-center mb-4">
						<span class="text-white text-xl">💡</span>
					</div>
					<h3 class="text-xl font-semibold text-gray-900 mb-3">Improvement Suggestions</h3>
					<p class="text-gray-600">
						Actionable feedback and specific recommendations to enhance your screenplay's 
						structure, characters, and market appeal.
					</p>
				</div>
			</div>
		</div>
	</div>

	<!-- Call to Action -->
	<div class="py-20 bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900">
		<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
			<h2 class="text-4xl font-bold text-white mb-6">Ready to Transform Your Screenplay?</h2>
			<p class="text-xl text-blue-100 mb-8 max-w-3xl mx-auto">
				Join thousands of writers who are already using Lolita to elevate their scripts 
				with professional AI-powered analysis and insights.
			</p>
			<div class="flex flex-col sm:flex-row gap-4 justify-center">
				{#if user}
					<a
						href="/dashboard"
						class="inline-flex items-center justify-center px-8 py-4 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white font-semibold rounded-lg transform hover:scale-105 transition-all duration-200 shadow-lg"
					>
						Go to Dashboard
					</a>
				{:else}
					<a
						href="/auth/register"
						class="inline-flex items-center justify-center px-8 py-4 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white font-semibold rounded-lg transform hover:scale-105 transition-all duration-200 shadow-lg"
					>
						Start Free Analysis
					</a>
					<a
						href="/auth/login"
						class="inline-flex items-center justify-center px-8 py-4 border-2 border-blue-400 text-blue-300 hover:bg-blue-400 hover:text-white font-semibold rounded-lg transition-all duration-200"
					>
						Sign In
					</a>
				{/if}
			</div>
		</div>
	</div>
</div>



