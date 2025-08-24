<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';

	let user: { id: string; email: string } | null = null;
	let loading = true;
	let uploading = false;
	let uploadProgress = 0;
	let error = '';
	let success = '';
	
	let title = '';
	let budget: string = '';
	let file: File | null = null;
	let dragActive = false;
	
	// Budget validation and warnings
	$: budgetWarnings = (() => {
		if (!budget || isNaN(Number(budget)) || Number(budget) <= 0) return [];
		
		const budgetNum = Number(budget);
		const warnings = [];
		
		// Very high budget warnings
		if (budgetNum > 500_000_000) {
			warnings.push({
				type: 'error',
				message: 'Budget exceeds typical Hollywood tentpole films. Consider reviewing.',
				icon: '⚠️'
			});
		} else if (budgetNum > 200_000_000) {
			warnings.push({
				type: 'warning',
				message: 'Very high budget. Ensure story justifies massive investment.',
				icon: '💰'
			});
		}
		
		// Very low budget warnings
		if (budgetNum < 10000) {
			warnings.push({
				type: 'warning',
				message: 'Extremely low budget. Limited to single-location, minimal crew projects.',
				icon: '💡'
			});
		}
		
		// Helpful tips based on budget tier
		if (budgetNum >= 50_000_000) {
			warnings.push({
				type: 'info',
				message: 'Tentpole budget requires global appeal and franchise potential.',
				icon: '🌍'
			});
		} else if (budgetNum >= 20_000_000) {
			warnings.push({
				type: 'info',
				message: 'High budget enables A-list talent and wide theatrical release.',
				icon: '⭐'
			});
		} else if (budgetNum >= 5_000_000) {
			warnings.push({
				type: 'info',
				message: 'Mid budget allows professional production values and established talent.',
				icon: '🎬'
			});
		} else if (budgetNum >= 1_000_000) {
			warnings.push({
				type: 'info',
				message: 'Low budget focuses on character-driven stories and emerging talent.',
				icon: '🎭'
			});
		} else {
			warnings.push({
				type: 'info',
				message: 'Micro budget emphasizes strong writing and minimal production costs.',
				icon: '✍️'
			});
		}
		
		return warnings;
	})();
	
	// Enhanced progress tracking
	let analysisId = '';
	let progressData: {
		stage: string;
		progress: number;
		message: string;
		details: {
			model?: string;
			estimated_time?: string;
			file_size?: string;
			upload_speed?: string;
			upload_time?: string;
			score?: number;
			recommendation?: string;
			cost?: string;
		};
		timestamp: number;
	} = {
		stage: '',
		progress: 0,
		message: '',
		details: {},
		timestamp: 0
	};
	let eventSource: EventSource | null = null;
	let uploadStartTime = 0;
	let connectionRetries = 0;
	let maxRetries = 5;
	let pollInterval: ReturnType<typeof setInterval> | null = null;
	let lastProgressUpdate = 0;
	let progressTimeout: ReturnType<typeof setTimeout> | null = null;
	
	// Detailed stage tracking
	let stageHistory: Array<{stage: string, message: string, timestamp: number, progress: number}> = [];
	let currentStageStartTime = 0;

	onMount(async () => {
		try {
			const response = await fetch('/api/auth/me');
			const data = await response.json();
			
			if (data.success) {
				user = data.user;
			} else {
				goto('/auth/login?redirectTo=/screenplays/upload');
			}
		} catch (error) {
			console.error('Failed to fetch user:', error);
			goto('/auth/login?redirectTo=/screenplays/upload');
		} finally {
			loading = false;
		}
	});
	
	// Cleanup event source on component destroy
	onMount(() => {
		const cleanup = () => {
			if (eventSource) {
				eventSource.close();
				eventSource = null;
			}
			if (pollInterval) {
				clearInterval(pollInterval);
				pollInterval = null;
			}
			if (progressTimeout) {
				clearTimeout(progressTimeout);
				progressTimeout = null;
			}
		};
		
		// Add cleanup on page unload
		window.addEventListener('beforeunload', cleanup);
		
		// Return cleanup function for onMount
		return () => {
			window.removeEventListener('beforeunload', cleanup);
			cleanup();
		};
	});

	function startProgressStream(id: string) {
		if (eventSource) {
			eventSource.close();
			eventSource = null;
		}
		if (pollInterval) {
			clearInterval(pollInterval);
			pollInterval = null;
		}
		
		connectionRetries = 0;
		lastProgressUpdate = Date.now();
		connectToProgressStream(id);
		
		// Start a fallback polling mechanism
		startProgressPolling(id);
		
		// Set a timeout to detect stuck progress
		startProgressTimeout(id);
	}
	
	function connectToProgressStream(id: string) {
		try {
			eventSource = new EventSource(`/api/analysis/${id}/progress`);
			
			eventSource.onopen = () => {
				connectionRetries = 0;
				console.log('✅ Progress stream connected');
				
				// Update UI to show connection restored
				if (progressData.stage !== 'complete') {
					progressData = {
						...progressData,
						message: progressData.message.includes('Connection') 
							? 'Connection restored. Continuing analysis...' 
							: progressData.message
					};
				}
			};
			
			eventSource.onmessage = (event) => {
				try {
					const data = JSON.parse(event.data);
					
					// Skip heartbeat messages but update connection status
					if (data.heartbeat) {
						console.log('💓 Heartbeat received - connection alive');
						lastProgressUpdate = Date.now();
						return;
					}
					
					// Update last progress timestamp
					lastProgressUpdate = Date.now();
					
					// Track stage changes
					if (data.stage !== progressData.stage) {
						const now = Date.now();
						if (progressData.stage) {
							// Add previous stage to history
							stageHistory = [...stageHistory, {
								stage: progressData.stage,
								message: progressData.message,
								timestamp: currentStageStartTime,
								progress: progressData.progress
							}];
						}
						currentStageStartTime = now;
					}
					
					progressData = { ...data, timestamp: Date.now() };
					
					// Check if analysis is complete
					if (data.progress >= 100 || data.stage === 'complete' || data.stage === 'error') {
						cleanupConnections();
						
						if (data.stage === 'complete') {
							success = 'Analysis completed successfully! Redirecting to results...';
							// Add final stage to history
							stageHistory = [...stageHistory, {
								stage: data.stage,
								message: data.message,
								timestamp: currentStageStartTime,
								progress: data.progress
							}];
							setTimeout(() => {
								goto(`/screenplays/analysis/${id}`);
							}, 2000);
						} else if (data.stage === 'error') {
							error = data.message || 'Analysis failed. Please try again or check the screenplays page.';
							uploading = false;
						}
					}
				} catch (err) {
					console.error('❌ Error parsing progress data:', err, 'Raw data:', event.data);
					// Don't break the connection for parsing errors
				}
			};
			
			eventSource.onerror = (event) => {
				console.error('❌ EventSource error:', event);
				
				// Close the current connection
				if (eventSource) {
					eventSource.close();
					eventSource = null;
				}
				
				// Only retry if we haven't exceeded max retries
				if (connectionRetries < maxRetries) {
					connectionRetries++;
					console.log(`🔄 Retrying connection (${connectionRetries}/${maxRetries})...`);
					
					// Show retry message to user
					progressData = {
						...progressData,
						message: `Connection lost. Retrying (${connectionRetries}/${maxRetries})...`,
						timestamp: Date.now()
					};
					
					// Retry with exponential backoff
					const retryDelay = Math.min(2000 * Math.pow(2, connectionRetries - 1), 30000); // Max 30 seconds
					setTimeout(() => {
						if (uploading && analysisId) { // Only retry if still uploading
							connectToProgressStream(id);
						}
					}, retryDelay);
				} else {
					console.log('❌ Max retries exceeded, falling back to polling only');
					
					// Update user with helpful message
					progressData = {
						...progressData,
						message: 'Connection issues detected. Using backup monitoring - analysis continues in background.',
						timestamp: Date.now()
					};
					
					// Increase polling frequency when EventSource fails
					if (pollInterval) {
						clearInterval(pollInterval);
					}
					startEnhancedPolling(id);
				}
			};
		} catch (error) {
			console.error('❌ Failed to create EventSource:', error);
			
			// Fall back to polling immediately
			progressData = {
				...progressData,
				message: 'Using backup monitoring mode. Analysis continues in background.',
				timestamp: Date.now()
			};
			
			startEnhancedPolling(id);
		}
	}
	
	function cleanupConnections() {
		if (eventSource) {
			eventSource.close();
			eventSource = null;
		}
		if (pollInterval) {
			clearInterval(pollInterval);
			pollInterval = null;
		}
		if (progressTimeout) {
			clearTimeout(progressTimeout);
			progressTimeout = null;
		}
	}
	
	function startProgressPolling(id: string) {
		// Poll every 5 seconds as a fallback
		pollInterval = setInterval(async () => {
			try {
				const response = await fetch(`/api/screenplays/analysis/${id}`, {
					headers: {
						'Cache-Control': 'no-cache'
					}
				});
				
				if (response.ok) {
					const data = await response.json();
					
					if (data.result && data.result.status === 'completed') {
						cleanupConnections();
						success = 'Analysis completed successfully! Redirecting to results...';
						setTimeout(() => {
							goto(`/screenplays/analysis/${id}`);
						}, 1000);
					} else if (data.result && data.result.status === 'error') {
						cleanupConnections();
						error = data.result.error_message || 'Analysis failed';
						uploading = false;
					} else if (data.result && data.result.status === 'processing') {
						// Update progress if we have info
						progressData = {
							...progressData,
							message: 'Analysis in progress (backup monitoring)',
							timestamp: Date.now()
						};
					}
				} else if (response.status === 404) {
					// Analysis might not be saved yet, continue polling
					console.log('🔄 Analysis not found yet, continuing to poll...');
				} else {
					console.error('❌ Polling failed:', response.status);
				}
			} catch (err) {
				console.error('❌ Polling error:', err);
				// Don't stop polling on network errors
			}
		}, 5000);
	}

	function startEnhancedPolling(id: string) {
		// Enhanced polling with shorter intervals when EventSource fails
		pollInterval = setInterval(async () => {
			try {
				const response = await fetch(`/api/screenplays/analysis/${id}`, {
					headers: {
						'Cache-Control': 'no-cache'
					}
				});
				
				if (response.ok) {
					const data = await response.json();
					
					if (data.result) {
						const result = data.result;
						
						if (result.status === 'completed') {
							cleanupConnections();
							success = 'Analysis completed successfully! Redirecting to results...';
							setTimeout(() => {
								goto(`/screenplays/analysis/${id}`);
							}, 1000);
						} else if (result.status === 'error') {
							cleanupConnections();
							error = result.error_message || 'Analysis failed';
							uploading = false;
						} else {
							// Update progress with estimated completion
							const estimatedProgress = Math.min(
								progressData.progress + 5, // Increment slowly
								90 // Don't go past 90% without real data
							);
							
							progressData = {
								...progressData,
								progress: estimatedProgress,
								message: `Analysis in progress... (${estimatedProgress}% estimated)`,
								timestamp: Date.now()
							};
						}
					}
				} else if (response.status === 404) {
					console.log('🔄 Analysis not ready yet...');
				} else {
					console.error('❌ Enhanced polling failed:', response.status);
				}
			} catch (err) {
				console.error('❌ Enhanced polling error:', err);
			}
		}, 3000); // Poll every 3 seconds for enhanced monitoring
	}
	
	function startProgressTimeout(id: string) {
		// If no progress updates for 2 minutes, assume something is wrong
		progressTimeout = setTimeout(() => {
			const timeSinceLastUpdate = Date.now() - lastProgressUpdate;
			if (timeSinceLastUpdate > 120000) { // 2 minutes
				console.log('Progress timeout detected, checking final status');
				checkFinalStatus(id);
			}
		}, 120000);
	}
	
	async function checkFinalStatus(id: string) {
		try {
			const response = await fetch(`/api/screenplays/analysis/${id}`);
			if (response.ok) {
				const data = await response.json();
				
				if (data.result && data.result.status === 'completed') {
					cleanupConnections();
					success = 'Analysis completed successfully! Redirecting to results...';
					setTimeout(() => {
						goto(`/screenplays/analysis/${id}`);
					}, 1000);
				} else if (data.result && data.result.status === 'error') {
					cleanupConnections();
					error = data.result.error_message || 'Analysis failed';
					uploading = false;
				} else {
					// Still processing, show a message
					progressData = {
						...progressData,
						message: 'Analysis is taking longer than expected. Please wait or check the screenplays page.',
						timestamp: Date.now()
					};
				}
			} else {
				error = 'Unable to check analysis status. Please check the screenplays page.';
				uploading = false;
			}
		} catch (err) {
			console.error('Status check error:', err);
			error = 'Connection error. Please check the screenplays page for your analysis results.';
			uploading = false;
		}
	}

	function handleFileSelect(event: Event) {
		const target = event.target as HTMLInputElement;
		if (target.files && target.files[0]) {
			file = target.files[0];
			if (!title) {
				// Auto-populate title from filename
				title = file.name.replace(/\.[^/.]+$/, "");
			}
		}
	}

	function handleDrop(event: DragEvent) {
		event.preventDefault();
		dragActive = false;
		
		if (event.dataTransfer?.files && event.dataTransfer.files[0]) {
			file = event.dataTransfer.files[0];
			if (!title) {
				title = file.name.replace(/\.[^/.]+$/, "");
			}
		}
	}

	function handleDragOver(event: DragEvent) {
		event.preventDefault();
		dragActive = true;
	}

	function handleDragLeave(event: DragEvent) {
		event.preventDefault();
		dragActive = false;
	}

	async function handleUpload() {
		if (!title.trim()) {
			error = 'Please enter a title for your screenplay';
			return;
		}

		if (!file) {
			error = 'Please select a file to upload';
			return;
		}

		// Validate file type
		const allowedTypes = ['.pdf', '.txt', '.doc', '.docx', '.fountain', '.fdx'];
		const fileExtension = '.' + file.name.split('.').pop()?.toLowerCase();
		if (!allowedTypes.includes(fileExtension)) {
			error = 'Please upload a valid screenplay file (.pdf, .txt, .doc, .docx, .fountain, .fdx)';
			return;
		}

		// Validate file size (10MB limit)
		if (file.size > 10 * 1024 * 1024) {
			error = 'File size must be less than 10MB';
			return;
		}

		uploading = true;
		uploadProgress = 0;
		error = '';
		success = '';
		uploadStartTime = Date.now();
		stageHistory = [];
		currentStageStartTime = Date.now();

		try {
			const formData = new FormData();
			formData.append('title', title.trim());
			formData.append('file', file);
			formData.append('genre', ''); // Optional genre field
			formData.append('user_id', user?.id || '');
			if (budget && !isNaN(Number(budget)) && Number(budget) > 0) {
				formData.append('budget_estimate', String(Number(budget)));
			}

			// Create XMLHttpRequest for upload progress tracking
			const xhr = new XMLHttpRequest();
			
			// Track upload progress
			xhr.upload.addEventListener('progress', (event) => {
				if (event.lengthComputable) {
					uploadProgress = Math.round((event.loaded / event.total) * 100);
					progressData = {
						stage: 'uploading',
						progress: Math.min(uploadProgress * 0.1, 10), // Upload is 10% of total
						message: `Uploading file... ${uploadProgress}% (${(event.loaded / 1024 / 1024).toFixed(1)}MB / ${(event.total / 1024 / 1024).toFixed(1)}MB)`,
						details: {
							upload_speed: event.loaded > 0 ? `${((event.loaded / 1024 / 1024) / ((Date.now() - uploadStartTime) / 1000)).toFixed(1)} MB/s` : '0 MB/s',
							file_size: `${(event.total / 1024 / 1024).toFixed(1)} MB`
						},
						timestamp: Date.now()
					};
				}
			});

			// Handle upload completion
			xhr.addEventListener('load', () => {
				if (xhr.status === 200) {
					try {
						const data = JSON.parse(xhr.responseText);
						
						if (data.analysis_id) {
							analysisId = data.analysis_id;
							
							// Initialize analysis progress
							progressData = {
								stage: 'upload_complete',
								progress: 15,
								message: 'Upload complete! Initializing analysis...',
								details: {
									file_size: `${(file!.size / 1024 / 1024).toFixed(1)} MB`,
									upload_time: `${((Date.now() - uploadStartTime) / 1000).toFixed(1)}s`
								},
								timestamp: Date.now()
							};
							
							// Start streaming progress updates
							startProgressStream(data.analysis_id);
							
							// Also do an immediate status check in case analysis completes very quickly
							setTimeout(() => {
								if (uploading && progressData.progress < 100) {
									checkFinalStatus(data.analysis_id);
								}
							}, 3000);
							
							// Clear form
							title = '';
							file = null;
							const fileInput = document.getElementById('file-upload') as HTMLInputElement;
							if (fileInput) fileInput.value = '';
						} else {
							error = data.error || 'Upload successful but analysis initialization failed';
							uploading = false;
						}
					} catch (parseError) {
						error = 'Invalid response from server';
						uploading = false;
					}
				} else {
					error = `Upload failed: ${xhr.status} ${xhr.statusText}`;
					uploading = false;
				}
			});

			// Handle upload errors
			xhr.addEventListener('error', () => {
				error = 'Network error during upload. Please check your connection and try again.';
				uploading = false;
			});

			// Handle upload timeout
			xhr.addEventListener('timeout', () => {
				error = 'Upload timed out. Please try again with a smaller file or check your connection.';
				uploading = false;
			});

			// Set timeout to 5 minutes for large files
			xhr.timeout = 600000; // 10 minutes

			// Send the request
			xhr.open('POST', '/api/screenplays/analyze');
			xhr.send(formData);

		} catch (err) {
			error = 'Failed to start upload. Please try again.';
			uploading = false;
		}
	}

	function removeFile() {
		file = null;
		const fileInput = document.getElementById('file-upload') as HTMLInputElement;
		if (fileInput) fileInput.value = '';
	}
</script>

<svelte:head>
	<title>Upload Screenplay - Quilty</title>
</svelte:head>

{#if loading}
	<div class="flex items-center justify-center min-h-screen">
		<div class="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
	</div>
{:else if user}
	<div class="min-h-screen bg-gray-50 py-12">
		<div class="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8">
			<!-- Page header -->
			<div class="text-center mb-8">
				<div class="flex justify-center mb-4">
					<div class="w-12 h-12 bg-blue-600 rounded-lg flex items-center justify-center">
						<svg class="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
						</svg>
					</div>
				</div>
				<h1 class="text-3xl font-bold tracking-tight text-gray-900">Upload Your Screenplay</h1>
				<p class="mt-2 text-lg text-gray-600">
					Get professional analysis and detailed feedback on your script
				</p>
			</div>

			<!-- Upload Form -->
			<div class="bg-white shadow-xl rounded-lg border border-gray-200">
				<div class="px-6 py-8 sm:px-10">
					<form on:submit|preventDefault={handleUpload} class="space-y-8">
						<!-- Title Input -->
						<div>
							<label for="title" class="block text-sm font-medium text-gray-700 mb-2">
								Screenplay Title
							</label>
							<input
								type="text"
								id="title"
								bind:value={title}
								placeholder="Enter the title of your screenplay"
								class="block w-full px-3 py-3 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
								required
							/>
							<p class="mt-2 text-sm text-gray-500">
								This will be used to identify your screenplay in the system.
							</p>
						</div>

						<!-- Proposed Budget -->
						<div>
							<label for="budget" class="block text-sm font-medium text-gray-700 mb-2">
								Proposed budget (USD) — optional
							</label>
							
							<!-- Budget Preset Buttons -->
							<div class="mb-3">
								<div class="text-xs font-medium text-gray-500 mb-2">Quick select:</div>
								<div class="flex flex-wrap gap-2">
									<button
										type="button"
										on:click={() => budget = '500000'}
										class="px-3 py-1 text-xs font-medium bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-md transition-colors"
									>
										Micro ($500K)
									</button>
									<button
										type="button"
										on:click={() => budget = '3000000'}
										class="px-3 py-1 text-xs font-medium bg-blue-100 hover:bg-blue-200 text-blue-700 rounded-md transition-colors"
									>
										Low ($3M)
									</button>
									<button
										type="button"
										on:click={() => budget = '12000000'}
										class="px-3 py-1 text-xs font-medium bg-green-100 hover:bg-green-200 text-green-700 rounded-md transition-colors"
									>
										Mid ($12M)
									</button>
									<button
										type="button"
										on:click={() => budget = '35000000'}
										class="px-3 py-1 text-xs font-medium bg-orange-100 hover:bg-orange-200 text-orange-700 rounded-md transition-colors"
									>
										High ($35M)
									</button>
									<button
										type="button"
										on:click={() => budget = '75000000'}
										class="px-3 py-1 text-xs font-medium bg-purple-100 hover:bg-purple-200 text-purple-700 rounded-md transition-colors"
									>
										Tentpole ($75M)
									</button>
								</div>
							</div>
							
							<input
								type="number"
								id="budget"
								min="0"
								step="1000"
								bind:value={budget}
								placeholder="e.g., 5000000"
								class="block w-full px-3 py-3 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
							/>
							
							<!-- Budget Category Indicator -->
							{#if budget && !isNaN(Number(budget)) && Number(budget) > 0}
								{@const budgetNum = Number(budget)}
								{@const category = budgetNum < 1000000 ? 'Micro-budget' : budgetNum < 5000000 ? 'Low-budget' : budgetNum < 20000000 ? 'Mid-budget' : budgetNum < 50000000 ? 'High-budget' : 'Tentpole'}
								<div class="mt-2 flex items-center space-x-2">
									{#if budgetNum < 1000000}
										<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
											{category}
										</span>
									{:else if budgetNum < 5000000}
										<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
											{category}
										</span>
									{:else if budgetNum < 20000000}
										<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
											{category}
										</span>
									{:else if budgetNum < 50000000}
										<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-orange-100 text-orange-800">
											{category}
										</span>
									{:else}
										<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
											{category}
										</span>
									{/if}
									<span class="text-xs text-gray-500">
										${budgetNum.toLocaleString()}
									</span>
								</div>
							{/if}
							
							<!-- Budget Warnings and Tips -->
							{#if budgetWarnings.length > 0}
								<div class="mt-3 space-y-2">
									{#each budgetWarnings as warning}
										<div class="flex items-start space-x-2 p-2 rounded-md {warning.type === 'error' ? 'bg-red-50 border border-red-200' : warning.type === 'warning' ? 'bg-yellow-50 border border-yellow-200' : 'bg-blue-50 border border-blue-200'}">
											<span class="text-sm">{warning.icon}</span>
											<span class="text-xs {warning.type === 'error' ? 'text-red-700' : warning.type === 'warning' ? 'text-yellow-700' : 'text-blue-700'}">
												{warning.message}
											</span>
										</div>
									{/each}
								</div>
							{/if}
							
							<p class="mt-2 text-sm text-gray-600">
								This affects casting, director suggestions, and financial forecasts. If left blank, our system will infer a realistic budget range based on industry standards and the screenplay.
							</p>
						</div>

						<!-- File Upload -->
						<div>
							<label for="file-upload" class="block text-sm font-medium text-gray-700 mb-4">
								Upload Your Screenplay
							</label>
							
							{#if !file}
								<div
									class="relative border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-gray-400 transition-colors {dragActive ? 'border-blue-400 bg-blue-50' : ''}"
									role="button"
									tabindex="0"
									on:drop={handleDrop}
									on:dragover={handleDragOver}
									on:dragleave={handleDragLeave}
									on:keydown={(e) => e.key === 'Enter' && document.getElementById('file-upload')?.click()}
								>
									<div class="space-y-4">
										<div class="flex justify-center">
											<svg class="h-16 w-16 text-gray-400" stroke="currentColor" fill="none" viewBox="0 0 48 48">
												<path d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
											</svg>
										</div>
										<div>
											<label for="file-upload" class="cursor-pointer">
												<span class="text-lg font-medium text-blue-600 hover:text-blue-500">
													Choose a file
												</span>
												<span class="text-gray-600"> or drag and drop</span>
												<input
													id="file-upload"
													name="file-upload"
													type="file"
													class="sr-only"
													accept=".pdf,.txt,.doc,.docx,.fountain,.fdx"
													on:change={handleFileSelect}
												/>
											</label>
										</div>
										<p class="text-sm text-gray-500">
											PDF, TXT, DOC, DOCX, Fountain, or FDX up to 10MB
										</p>
									</div>
								</div>
							{:else}
								<div class="bg-gray-50 rounded-lg p-6 border border-gray-200">
									<div class="flex items-center justify-between">
										<div class="flex items-center space-x-4">
											<div class="flex-shrink-0">
												<svg class="h-10 w-10 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
													<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
												</svg>
											</div>
											<div>
												<p class="text-sm font-medium text-gray-900">{file?.name}</p>
												<p class="text-sm text-gray-500">{(file?.size || 0) / 1024 / 1024 | 0} MB</p>
											</div>
										</div>
										<button type="button" class="text-red-600 hover:text-red-700 text-sm" on:click={removeFile}>Remove</button>
									</div>
								</div>
							{/if}
						</div>

						<!-- Supported Formats Info -->
						<div class="mt-6 bg-blue-50 rounded-lg p-4 border border-blue-200">
							<h4 class="text-sm font-medium text-blue-900 mb-2">Supported Formats:</h4>
							<div class="grid grid-cols-1 sm:grid-cols-2 gap-2 text-sm text-blue-800">
								<div class="flex items-center">
									<svg class="h-4 w-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
										<path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
									</svg>
									<strong>PDF:</strong> Most common format
								</div>
								<div class="flex items-center">
									<svg class="h-4 w-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
										<path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
									</svg>
									<strong>TXT:</strong> Plain text format
								</div>
								<div class="flex items-center">
									<svg class="h-4 w-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
										<path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
									</svg>
									<strong>DOC/DOCX:</strong> Microsoft Word
								</div>
								<div class="flex items-center">
									<svg class="h-4 w-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
										<path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
									</svg>
									<strong>Fountain:</strong> Screenwriting markup
								</div>
								<div class="flex items-center">
									<svg class="h-4 w-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
										<path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
									</svg>
									<strong>FDX:</strong> Final Draft XML
								</div>
							</div>
						</div>

						{#if uploading && (progressData.progress > 0 || uploadProgress > 0)}
							<!-- Enhanced Progress Display -->
							<div class="rounded-lg bg-gradient-to-r from-blue-50 to-indigo-50 p-6 border border-blue-200 shadow-lg">
								<div class="space-y-6">
									<!-- Progress Header -->
									<div class="flex items-center justify-between">
										<h3 class="text-xl font-bold text-blue-900">
											{#if progressData.stage === 'uploading'}
												Uploading Your Screenplay
											{:else if progressData.stage === 'upload_complete'}
												Upload Complete - Starting Analysis
											{:else}
												Analyzing Your Screenplay
											{/if}
										</h3>
										<div class="text-right">
											<span class="text-lg font-bold text-blue-700">
												{Math.round(progressData.progress || 0)}%
											</span>
											{#if progressData.stage === 'uploading'}
												<div class="text-xs text-blue-600">
													Upload: {uploadProgress}%
												</div>
											{/if}
										</div>
									</div>
									
									<!-- Enhanced Progress Bar -->
									<div class="space-y-2">
										<div class="w-full bg-blue-200 rounded-full h-4 overflow-hidden">
											<div 
												class="bg-gradient-to-r from-blue-500 to-indigo-600 h-4 rounded-full transition-all duration-300 ease-out shadow-sm"
												style="width: {Math.max(progressData.progress || 0, uploadProgress * 0.1)}%"
											></div>
										</div>
										
										<!-- Stage indicators -->
										<div class="flex justify-between text-xs text-blue-600">
											<span class="{progressData.progress >= 0 ? 'font-medium' : ''}">Start</span>
											<span class="{progressData.progress >= 15 ? 'font-medium' : ''}">Upload</span>
											<span class="{progressData.progress >= 25 ? 'font-medium' : ''}">Process</span>
											<span class="{progressData.progress >= 50 ? 'font-medium' : ''}">Craft</span>
											<span class="{progressData.progress >= 75 ? 'font-medium' : ''}">Reality</span>
											<span class="{progressData.progress >= 85 ? 'font-medium' : ''}">Commercial</span>
											<span class="{progressData.progress >= 100 ? 'font-medium' : ''}">Complete</span>
										</div>
									</div>
									
									<!-- Current Stage with Enhanced Icons -->
									<div class="bg-white rounded-lg p-4 border border-blue-100 shadow-sm">
										<div class="flex items-center space-x-3">
											{#if progressData.stage === 'uploading'}
												<div class="animate-pulse">
													<svg class="h-6 w-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
														<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
													</svg>
												</div>
											{:else if progressData.stage === 'upload_complete'}
												<svg class="h-6 w-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
													<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
												</svg>
											{:else if progressData.stage === 'starting'}
												<div class="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
											{:else if progressData.stage === 'pdf_processing'}
												<div class="animate-bounce">
													<svg class="h-6 w-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
														<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
													</svg>
												</div>
											{:else if progressData.stage === 'claude_analysis'}
												<div class="animate-pulse">
													<svg class="h-6 w-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
														<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
													</svg>
												</div>
											{:else if progressData.stage === 'grok_analysis'}
												<div class="animate-pulse">
													<svg class="h-6 w-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
														<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
													</svg>
												</div>
											{:else if progressData.stage === 'openai_analysis'}
												<div class="animate-pulse">
													<svg class="h-6 w-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
														<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-4.05.5L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
													</svg>
												</div>
											{:else if progressData.stage === 'saving'}
												<div class="animate-bounce">
													<svg class="h-6 w-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
														<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-3m-1 4l-3 3m0 0l-3-3m3 3V4" />
													</svg>
												</div>
											{:else if progressData.stage === 'complete'}
												<svg class="h-6 w-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
													<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
												</svg>
											{:else}
												<div class="animate-pulse rounded-full h-6 w-6 bg-blue-600"></div>
											{/if}
											
											<div class="flex-1">
												<p class="text-sm font-medium text-blue-800">
													{progressData.message}
												</p>
												{#if progressData.timestamp}
													<p class="text-xs text-blue-600 mt-1">
														{new Date(progressData.timestamp).toLocaleTimeString()}
													</p>
												{/if}
											</div>
										</div>
									</div>
									
									<!-- Enhanced Stage Details -->
									{#if progressData.details && Object.keys(progressData.details).length > 0}
										<div class="bg-white rounded-lg p-4 border border-blue-100 shadow-sm">
											<h4 class="text-sm font-semibold text-gray-700 mb-3">Analysis Details</h4>
											<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 text-sm">
												{#if progressData.details.model}
													<div class="flex justify-between items-center">
														<span class="text-gray-600">Analysis Engine:</span>
														<span class="font-medium text-gray-900 bg-gray-100 px-2 py-1 rounded text-xs">{progressData.details.model}</span>
													</div>
												{/if}
												{#if progressData.details.estimated_time}
													<div class="flex justify-between items-center">
														<span class="text-gray-600">Est. Time:</span>
														<span class="font-medium text-gray-900">{progressData.details.estimated_time}</span>
													</div>
												{/if}
												{#if progressData.details.file_size}
													<div class="flex justify-between items-center">
														<span class="text-gray-600">File Size:</span>
														<span class="font-medium text-gray-900">{progressData.details.file_size}</span>
													</div>
												{/if}
												{#if progressData.details.upload_speed}
													<div class="flex justify-between items-center">
														<span class="text-gray-600">Upload Speed:</span>
														<span class="font-medium text-gray-900">{progressData.details.upload_speed}</span>
													</div>
												{/if}
												{#if progressData.details.upload_time}
													<div class="flex justify-between items-center">
														<span class="text-gray-600">Upload Time:</span>
														<span class="font-medium text-gray-900">{progressData.details.upload_time}</span>
													</div>
												{/if}
												{#if progressData.details.score}
													<div class="flex justify-between items-center">
														<span class="text-gray-600">Score:</span>
														<span class="font-bold text-blue-600">{progressData.details.score}/10</span>
													</div>
												{/if}
												{#if progressData.details.recommendation}
													<div class="flex justify-between items-center">
														<span class="text-gray-600">Recommendation:</span>
														<span class="font-medium text-green-600">{progressData.details.recommendation}</span>
													</div>
												{/if}
												{#if progressData.details.cost}
													<div class="flex justify-between items-center">
														<span class="text-gray-600">Cost:</span>
														<span class="font-medium text-gray-900">{progressData.details.cost}</span>
													</div>
												{/if}
											</div>
										</div>
									{/if}
									
									<!-- Stage History -->
									{#if stageHistory.length > 0}
										<div class="bg-white rounded-lg p-4 border border-blue-100 shadow-sm">
											<h4 class="text-sm font-semibold text-gray-700 mb-3">Progress History</h4>
											<div class="space-y-2 max-h-32 overflow-y-auto">
												{#each stageHistory as stage}
													<div class="flex items-center justify-between text-xs">
														<span class="text-gray-600">{stage.message}</span>
														<div class="flex items-center space-x-2">
															<span class="text-gray-500">{stage.progress}%</span>
															<span class="text-gray-400">{new Date(stage.timestamp).toLocaleTimeString()}</span>
														</div>
													</div>
												{/each}
											</div>
										</div>
									{/if}
								</div>
							</div>
						{/if}

						{#if error}
							<div class="rounded-md bg-red-50 p-4 border border-red-200">
								<div class="flex">
									<div class="flex-shrink-0">
										<svg class="h-5 w-5 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
											<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
										</svg>
									</div>
									<div class="ml-3">
										<p class="text-sm font-medium text-red-800">{error}</p>
									</div>
								</div>
							</div>
						{/if}

						{#if success}
							<div class="rounded-md bg-green-50 p-4 border border-green-200">
								<div class="flex">
									<div class="flex-shrink-0">
										<svg class="h-5 w-5 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
											<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
										</svg>
									</div>
									<div class="ml-3">
										<p class="text-sm font-medium text-green-800">{success}</p>
									</div>
								</div>
							</div>
						{/if}
						
						<!-- Manual status check button for stuck uploads -->
						{#if uploading && analysisId && progressData.progress > 10 && progressData.progress < 100}
							<div class="rounded-md bg-blue-50 p-4 border border-blue-200">
								<div class="flex items-center justify-between">
									<div class="flex items-center">
										<div class="flex-shrink-0">
											<svg class="h-5 w-5 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
												<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
											</svg>
										</div>
										<div class="ml-3">
											<p class="text-sm text-blue-700">Analysis taking longer than expected?</p>
										</div>
									</div>
									<button
										type="button"
										on:click={() => checkFinalStatus(analysisId)}
										class="inline-flex items-center px-3 py-2 border border-blue-300 shadow-sm text-sm leading-4 font-medium rounded-md text-blue-700 bg-white hover:bg-blue-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
									>
										Check Status
									</button>
								</div>
							</div>
						{/if}

						<!-- Submit Buttons -->
						<div class="flex flex-col sm:flex-row gap-3 pt-6 border-t border-gray-200">
							<button
								type="submit"
								disabled={uploading || !title.trim() || !file}
								class="flex-1 w-full flex justify-center py-3 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
							>
								{#if uploading}
									<svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
										<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
										<path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
									</svg>
									Uploading your screenplay...
								{:else}
									<svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
									</svg>
									Upload & Analyze Screenplay
								{/if}
							</button>
							<a
								href="/screenplays"
								class="w-full sm:w-auto flex justify-center py-3 px-4 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors"
							>
								Cancel
							</a>
						</div>
					</form>
				</div>
			</div>
		</div>
	</div>
{:else}
	<div class="flex items-center justify-center min-h-screen">
		<div class="text-center">
			<h1 class="text-2xl font-bold text-gray-900 mb-4">Access Denied</h1>
			<p class="text-gray-600 mb-6">Please log in to upload screenplays.</p>
			<a href="/auth/login" class="btn-primary">
				Sign In
			</a>
		</div>
	</div>
{/if}
