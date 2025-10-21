import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';

export default ({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '');
  const proxyTarget = env.MCP_PROXY_TARGET || 'http://localhost:8000';

  return defineConfig({
    plugins: [react()],
    server: {
      proxy: {
        '/mcp/': {
          target: proxyTarget,
          changeOrigin: true,
        },
      },
    },
    build: {
      outDir: 'dist',
      emptyOutDir: true,
    },
  });
};
