<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';

	let user: { id: string; email: string } | null = null;
	let loading = true;

	onMount(async () => {
		try {
			const response = await fetch('/api/auth/me');
			const data = await response.json();
			
			if (data.success) {
				user = data.user;
			} else {
				// Not authenticated, redirect to login
				goto('/auth/login?redirectTo=/profile');
			}
		} catch (error) {
			console.error('Failed to fetch user:', error);
			goto('/auth/login?redirectTo=/profile');
		} finally {
			loading = false;
		}
	});
</script>

<svelte:head>
	<title>Profile - Screenplay Evaluation Tool</title>
</svelte:head>

{#if loading}
	<div class="flex items-center justify-center min-h-screen">
		<div class="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
	</div>
{:else if user}
	<div class="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
		<div class="md:grid md:grid-cols-3 md:gap-6">
			<div class="md:col-span-1">
				<div class="px-4 sm:px-0">
					<h3 class="text-lg font-medium leading-6 text-gray-900">Profile</h3>
					<p class="mt-1 text-sm text-gray-600">
						Manage your account information and preferences.
					</p>
				</div>
			</div>
			<div class="mt-5 md:mt-0 md:col-span-2">
				<div class="card">
					<div class="px-4 py-5 sm:p-6">
						<div class="grid grid-cols-6 gap-6">
							<div class="col-span-6 sm:col-span-4">
								<label for="email" class="form-label">Email address</label>
								<input
									type="email"
									name="email"
									id="email"
									value={user.email}
									disabled
									class="form-input bg-gray-50 cursor-not-allowed"
								/>
								<p class="mt-2 text-sm text-gray-500">
									Email address cannot be changed at this time.
								</p>
							</div>

							<div class="col-span-6">
								<label for="member-since" class="form-label">Member since</label>
								<input
									type="text"
									name="member-since"
									id="member-since"
									value="Recently joined"
									disabled
									class="form-input bg-gray-50 cursor-not-allowed"
								/>
							</div>
						</div>
					</div>
				</div>
			</div>
		</div>

		<div class="hidden sm:block" aria-hidden="true">
			<div class="py-5">
				<div class="border-t border-gray-200"></div>
			</div>
		</div>

		<div class="mt-10 sm:mt-0">
			<div class="md:grid md:grid-cols-3 md:gap-6">
				<div class="md:col-span-1">
					<div class="px-4 sm:px-0">
						<h3 class="text-lg font-medium leading-6 text-gray-900">Account Actions</h3>
						<p class="mt-1 text-sm text-gray-600">
							Manage your account settings and data.
						</p>
					</div>
				</div>
				<div class="mt-5 md:mt-0 md:col-span-2">
					<div class="card">
						<div class="px-4 py-5 sm:p-6">
							<div class="space-y-6">
								<div>
									<h4 class="text-sm font-medium text-gray-900">Change Password</h4>
									<p class="mt-1 text-sm text-gray-500">
										Update your password to keep your account secure.
									</p>
									<div class="mt-3">
										<button
											type="button"
											class="btn-secondary"
											disabled
										>
											Change Password (Coming Soon)
										</button>
									</div>
								</div>

								<div class="border-t border-gray-200 pt-6">
									<h4 class="text-sm font-medium text-gray-900">Export Data</h4>
									<p class="mt-1 text-sm text-gray-500">
										Download all your screenplay analyses and data.
									</p>
									<div class="mt-3">
										<button
											type="button"
											class="btn-secondary"
											disabled
										>
											Export Data (Coming Soon)
										</button>
									</div>
								</div>

								<div class="border-t border-gray-200 pt-6">
									<h4 class="text-sm font-medium text-red-600">Delete Account</h4>
									<p class="mt-1 text-sm text-gray-500">
										Permanently delete your account and all associated data.
									</p>
									<div class="mt-3">
										<button
											type="button"
											class="btn-danger"
											disabled
										>
											Delete Account (Coming Soon)
										</button>
									</div>
								</div>
							</div>
						</div>
					</div>
				</div>
			</div>
		</div>
	</div>
{/if}
