import { defineConfig } from 'astro/config';
import mdx from '@astrojs/mdx';
import vercel from '@astrojs/vercel';
import react from '@astrojs/react';

export default defineConfig({
  site: 'https://purlpressure.com',
  output: 'static',
  adapter: vercel(),
  integrations: [mdx(), react()],
  markdown: {
    shikiConfig: { theme: 'css-variables' },
  },
});
