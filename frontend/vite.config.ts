import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig, loadEnv } from 'vite';

export default defineConfig(({ mode }) => {
	const env = loadEnv(mode, process.cwd());

	return {
		plugins: [sveltekit()],
		server: {
			host: true,
			port: 5173,
			proxy: {
				'/ws': {
					target: 'ws://api:8000',
					changeOrigin: true,
					ws: true,
				},
			},
		},
	};
});
