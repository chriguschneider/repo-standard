import { getCollection, type CollectionEntry } from 'astro:content';
import { PREVIEW } from '../config';
import { localeRoot, type Locale } from '../i18n';

export type Post = CollectionEntry<'posts'>;

/** Drafts show in `npm run dev` and on previews, never in production. */
export const SHOW_DRAFTS = import.meta.env.DEV || PREVIEW;

/** Every visible post, newest first. Pass a locale to get only that language. */
export async function posts(locale?: Locale): Promise<Post[]> {
  const all = await getCollection('posts', ({ data }) => (SHOW_DRAFTS || !data.draft) && (!locale || data.lang === locale));
  return all.sort((a, b) => b.data.date.getTime() - a.data.date.getTime());
}

/** A post lives under the root of its own language: `/posts/<id>/` or `/en/posts/<id>/`. */
export const postUrl = (post: Post): string => `${localeRoot(post.data.lang)}posts/${post.id}/`;
