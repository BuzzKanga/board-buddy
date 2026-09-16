/**
 * Plain Vite config for building the frontend as a client-side SPA.
 *
 * Used by the Docker build (`vite build --config vite.spa.config.ts`) to
 * produce a static bundle (dist/) that FastAPI can serve.  This deliberately
 * does NOT use @lovable.dev/vite-tanstack-config or TanStack Start / Nitro,
 * since the SSR server is replaced by FastAPI in the production container.
 */

import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tsconfigPaths from "vite-tsconfig-paths";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
  plugins: [react(), tsconfigPaths(), tailwindcss()],
  build: {
    outDir: "dist",
    emptyOutDir: true,
  },
});
