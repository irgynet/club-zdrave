import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

export const collections = {
  articles: defineCollection({
    loader: glob({ pattern: '**/*.mdx', base: './src/content/articles' }),
    schema: ({ image }) =>
      z.object({
        title: z.string(),
        description: z.string(),
        date: z.coerce.date(),
        // Accept either a local image (resolved via Astro's image() helper —
        // returns ImageMetadata) or a full URL string for remote images.
        image: z.union([image(), z.string().url()]),
        author: z.string().default('Екип Клуб Здраве'),
        tags: z.array(z.string()).default([]),
        category: z.string(),
        featured: z.boolean().default(false),
      }),
  }),
  offers: defineCollection({
    loader: glob({ pattern: '**/*.md', base: './src/content/produkti' }),
    schema: ({ image }) =>
      z.object({
        title: z.string(),
        description: z.string(),
        image: z.union([image(), z.string().url()]),
        affiliateLink: z.string().url(),
        price: z.string(),
        brand: z.string(),
        featured: z.boolean().default(false),
        date: z.coerce.date(),
      }),
  }),
};
