import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

const backend = "http://127.0.0.1:8000";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/auth": backend,
      "/users": backend,
      "/organizations": backend,
      "/projects": backend,
      "/invitations": backend,
      "/health": backend,
      "/ready": backend,
    },
  },
});
