import { getCollection, type CollectionEntry } from 'astro:content';
import type { CategorySlug } from './categories';

export type MdPost = CollectionEntry<'articles'>;

export async function getAllPostsForCategory(category: CategorySlug): Promise<MdPost[]> {
  const all = await getCollection('articles');
  return all
    .filter((p) => p.data.category === category)
    .sort((a, b) => {
      const dateA = a.data.date instanceof Date ? a.data.date : new Date(a.data.date);
      const dateB = b.data.date instanceof Date ? b.data.date : new Date(b.data.date);
      return dateB.getTime() - dateA.getTime();
    });
}

export async function getFeaturedPosts(): Promise<MdPost[]> {
  const allCategories: CategorySlug[] = ['otslabvane', 'hranene-dieti', 'dalgoletie', 'sardechno-zdrave', 'trenirovki'];
  const allPosts: MdPost[] = [];
  for (const cat of allCategories) {
    const posts = await getAllPostsForCategory(cat);
    allPosts.push(...posts.filter((p) => p.data.featured));
  }
  return allPosts.sort((a, b) => {
    const dateA = a.data.date instanceof Date ? a.data.date : new Date(a.data.date);
    const dateB = b.data.date instanceof Date ? b.data.date : new Date(b.data.date);
    return dateB.getTime() - dateA.getTime();
  });
}

export async function getRecentPosts(limit = 6): Promise<MdPost[]> {
  const allCategories: CategorySlug[] = ['otslabvane', 'hranene-dieti', 'dalgoletie', 'sardechno-zdrave', 'trenirovki'];
  const allPosts: MdPost[] = [];
  for (const cat of allCategories) {
    const posts = await getAllPostsForCategory(cat);
    allPosts.push(...posts);
  }
  return allPosts
    .sort((a, b) => {
      const dateA = a.data.date instanceof Date ? a.data.date : new Date(a.data.date);
      const dateB = b.data.date instanceof Date ? b.data.date : new Date(b.data.date);
      return dateB.getTime() - dateA.getTime();
    })
    .slice(0, limit);
}

export function getPostUrl(post: MdPost): string {
  return `/${post.data.category}/${post.id}`;
}
