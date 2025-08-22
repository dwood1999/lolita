import { sveltekit } from '@sveltejs/kit/vite';
import tailwindcss from '@tailwindcss/vite';
import { defineConfig } from 'vite';

export default defineConfig({
	plugins: [sveltekit(), tailwindcss()],
	server: {
		host: '0.0.0.0',
		port: 5174,
		allowedHosts: ['devtask.online', 'localhost', '127.0.0.1'],
		hmr: {
			port: 5174,
			clientPort: 5174,
			host: 'devtask.online'
		}
	},
	build: {
		// Optimize build performance
		target: 'esnext',
		minify: 'esbuild',
		cssMinify: true,
		rollupOptions: {
			output: {
				// Code splitting for better caching
				manualChunks: {
					vendor: ['svelte', '@sveltejs/kit'],
					ui: ['tailwindcss']
				}
			}
		}
	},
	optimizeDeps: {
		// Pre-bundle dependencies for faster dev server
		include: ['svelte', '@sveltejs/kit', 'tailwindcss']
	},
	css: {
		// Optimize CSS processing
		devSourcemap: false
	}
});
