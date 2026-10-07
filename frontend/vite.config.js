import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// During development the API runs on :8000 (uvicorn); /api is proxied to it.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: { "/api": { target: process.env.VITE_API_TARGET || "http://localhost:8000", changeOrigin: true } },
  },
});
