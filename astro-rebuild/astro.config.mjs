// @ts-check
import { defineConfig } from 'astro/config';
import tailwindcss from '@tailwindcss/vite';

// https://astro.build/config
export default defineConfig({
  site: 'https://cvisiondesigns.github.io',
  base: '/wordpress-v1-backup',
  vite: {
    plugins: [tailwindcss()]
  }
});