import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '');
  const apiUrl = process.env.VITE_API_BASE_URL || env.VITE_API_BASE_URL;

  // Build-time safety: Staging and Production deployment builds MUST supply a valid non-localhost API URL.
  // When building in strict deployment mode (STRICT_API_URL=true or mode === 'staging'),
  // fail immediately if VITE_API_BASE_URL is missing or defaults to localhost.
  const isStrictDeployment = process.env.STRICT_API_URL === 'true' || mode === 'staging';
  if (isStrictDeployment) {
    if (!apiUrl || apiUrl.trim() === '' || apiUrl.includes('localhost') || apiUrl.includes('127.0.0.1')) {
      throw new Error(
        'BUILD FAILURE: VITE_API_BASE_URL is required and must not point to localhost for staging/production deployment builds.'
      );
    }
  }

  return {
    base: './',
    plugins: [react()],
    server: {
      port: 5173,
      host: true,
    },
  };
});
