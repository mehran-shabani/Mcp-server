import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';

export default ({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '');
  const proxyTarget = env.MCP_PROXY_TARGET || 'http://localhost:8000';
  const host = env.MCP_DEVSERVER_HOST || '0.0.0.0';
  const port = parseInt(env.MCP_DEVSERVER_PORT || '5173', 10);

  return defineConfig({
    plugins: [react()],
    server: {
      host,
      port,
      strictPort: true,
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
