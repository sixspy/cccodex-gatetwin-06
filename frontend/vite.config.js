import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
export default defineConfig({
  plugins: [react()],
  build: { outDir: "../backend/app/static", emptyOutDir: false },
  server: { port: 6500, proxy: { "/api": "http://127.0.0.1:11500" } },
});
