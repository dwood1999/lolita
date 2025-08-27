<script lang="ts">
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';

	let user: { id: string; email: string } | null = null;
	let showUserMenu = false;

	onMount(async () => {
		await checkAuthStatus();
	});

	async function checkAuthStatus() {
		try {
			const response = await fetch('/api/auth/me', {
				credentials: 'include' // Include cookies for session
			});
			const data = await response.json();
			if (data.success) {
				user = data.user;
				console.log('Navigation: User authenticated:', user.email);
			} else {
				user = null;
				console.log('Navigation: User not authenticated');
			}
		} catch (error) {
			console.error('Navigation: Failed to fetch user:', error);
			user = null;
		}
	}

	// Listen for custom auth events from other components
	function handleAuthChange(event: CustomEvent) {
		if (event.detail.user) {
			user = event.detail.user;
		} else {
			user = null;
		}
	}

	async function handleLogout() {
		try {
			// Clear frontend state immediately
			user = null;
			showUserMenu = false;
			
			// Call SvelteKit logout endpoint to clear session cookies
			await fetch('/api/auth/logout', { 
				method: 'POST',
				credentials: 'include' // Include cookies for session
			});
			
			// Also call FastAPI logout to clear that session too
			await fetch('/api/auth/logout', { 
				method: 'POST'
			});
			
			// Force complete page reload and redirect to login with logout flag
			window.location.replace('/auth/login?logout=true');
			
		} catch (error) {
			console.error('Logout failed:', error);
			// Force redirect even if logout calls fail
			user = null;
			showUserMenu = false;
			window.location.replace('/auth/login?logout=true');
		}
	}

	function toggleUserMenu() {
		showUserMenu = !showUserMenu;
	}

	function closeUserMenu() {
		showUserMenu = false;
	}

	// Close menu when clicking outside
	function handleClickOutside(event: MouseEvent) {
		const target = event.target as HTMLElement;
		if (!target.closest('.user-menu-container')) {
			showUserMenu = false;
		}
	}

	$: currentPath = $page.url.pathname;
</script>

<svelte:window on:click={handleClickOutside} on:authchange={handleAuthChange} />

<nav class="bg-white shadow-sm border-b border-gray-200">
	<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
		<div class="flex justify-between h-16">
			<div class="flex">
				<div class="flex-shrink-0 flex items-center">
					<a href="/" class="text-xl font-bold text-gray-900">
						Quilty
					</a>
				</div>
				
				<div class="hidden sm:ml-6 sm:flex sm:space-x-8">
					<a
						href="/about"
						class="nav-link {currentPath === '/about' ? 'active' : ''}"
					>
						About
					</a>
					<a
						href="/incentives"
						class="nav-link {currentPath === '/incentives' ? 'active' : ''}"
					>
						Incentives
					</a>
					{#if user}
						<a
							href="/dashboard"
							class="nav-link {currentPath === '/dashboard' ? 'active' : ''}"
						>
							Dashboard
						</a>
						<a
							href="/screenplays"
							class="nav-link {currentPath.startsWith('/screenplays') ? 'active' : ''}"
						>
							Screenplays
						</a>
					{/if}
				</div>
			</div>

			<div class="flex items-center">
				{#if user}
					<div class="relative user-menu-container">
						<button
							type="button"
							class="flex items-center text-sm rounded-full focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
							on:click={toggleUserMenu}
						>
							<span class="sr-only">Open user menu</span>
							<div class="h-8 w-8 rounded-full bg-blue-600 flex items-center justify-center">
								<span class="text-white text-sm font-medium">
									{user.email.charAt(0).toUpperCase()}
								</span>
							</div>
						</button>

						{#if showUserMenu}
							<div class="origin-top-right absolute right-0 mt-2 w-48 rounded-md shadow-lg bg-white ring-1 ring-black ring-opacity-5 focus:outline-none z-50">
								<div class="py-1">
									<div class="px-4 py-2 text-sm text-gray-700 border-b border-gray-100">
										{user.email}
									</div>
									<a
										href="/profile"
										class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
										on:click={closeUserMenu}
									>
										Profile
									</a>
									<button
										type="button"
										class="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
										on:click={handleLogout}
									>
										Sign out
									</button>
								</div>
							</div>
						{/if}
					</div>
				{:else}
					<div class="flex items-center space-x-4">
						<a
							href="/auth/login"
							class="text-gray-600 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium"
						>
							Sign in
						</a>
						<a
							href="/auth/register"
							class="btn-primary"
						>
							Sign up
						</a>
					</div>
				{/if}
			</div>
		</div>
	</div>
</nav>
