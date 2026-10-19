import { defineCollection } from 'astro:content';
import { glob } from 'astro/loaders';
import { z } from 'astro/zod';
import { DEFAULT_LOCALE, LOCALES } from './i18n/types';

/**
 * Posts: one Markdown file per post in `src/content/posts/`. Adding a post
 * needs no code change. The schema is the contract: a post with a missing
 * or wrongly typed field fails `astro build` with the file name, instead of
 * rendering an empty title or a wrong date.
 *
 * Files starting with `_` are skipped, so notes for authors can live next
 * to the posts.
 */
const posts = defineCollection({
  loader: glob({ base: './src/content/posts', pattern: '**/[^_]*.md' }),
  schema: z.object({
    title: z.string().min(1),
    /** One sentence for the post list and the meta description. */
    description: z.string().min(1),
    date: z.coerce.date(),
    /** Visible in `npm run dev` and on previews only, never in production. */
    draft: z.boolean().default(false),
    /** The post's language. A post exists in one language; translate by adding another file. */
    lang: z.enum(LOCALES).default(DEFAULT_LOCALE),
  }),
});

export const collections = { posts };
