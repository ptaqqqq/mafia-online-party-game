import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig, loadEnv } from 'vite';

export default defineConfig(({ mode }) => {
	const env = loadEnv(mode, process.cwd());

	return {
		plugins: [sveltekit()],
		server: {
			host: true,
			port: 3000,
			proxy: {
				'/ws': {
					target: env.VITE_WEBSOCKET_URL,
					changeOrigin: true,
					ws: true,
					// rewrite: (path) => path.replace(/^\/ws/, ''),
				},
			},
		},
	};
});
