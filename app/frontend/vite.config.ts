import path from "path";
import react from "@vitejs/plugin-react";
import { defineConfig, loadEnv } from "vite";

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
    // Load environment variables based on the mode
    const env = loadEnv(mode, process.cwd());

    return {
        plugins: [react()],
        build: {
            outDir: "../backend/static",
            emptyOutDir: true,
            sourcemap: false
        },
        resolve: {
            alias: {
                "@": path.resolve(__dirname, "./src")
            }
        },
        server: {
            proxy: {
                "/realtime": {
                    target: "ws://localhost:8765",
                    ws: true,
                    rewriteWsOrigin: true
                }
            }
        },
        define: {
            "process.env.VITE_AZURE_API_ENDPOINT": JSON.stringify(env.VITE_AZURE_API_ENDPOINT)
        }
    };
});
