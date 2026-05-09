import { defineCollection, z } from 'astro:content';

const obsessions = defineCollection({
  type: 'content',
  schema: z.object({
    title: z.string(),
    date: z.coerce.date(),
    excerpt: z.string(),
    color: z.string().default('#BF6B4A'),
    accent: z.string().default('#8C9471'),
    vibe: z.string().optional(),
    patterns: z
      .array(
        z.object({
          name: z.string(),
          designer: z.string(),
          ravelry: z.string().url().optional(),
          notes: z.string().optional(),
          image: z.number().int().optional(),
        })
      )
      .default([]),
    instagramPost: z.string().url().optional(),
    draft: z.boolean().default(false),
  }),
});

export const collections = { obsessions };
