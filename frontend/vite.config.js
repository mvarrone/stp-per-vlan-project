import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  server: {
    host: '0.0.0.0', // Escucha en todas las interfaces de red
    port: 3000, // Cambia al puerto que desees, asegúrate de que el puerto esté permitido en el cortafuegos
    strictPort: true, // Si el puerto está en uso, lanzará un error
    cors: true, // Habilita CORS
  }
})
