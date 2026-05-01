export interface HtmlPost {
  id: string;
  slug: string;
  collection: string;
  contentType: 'html';
  data: {
    title: string;
    description: string;
    date: Date;
    image: string;
    author: string;
    tags: string[];
    category: string;
    featured: boolean;
  };
  rawHtml: string;
}

const HTML_FILES = import.meta.glob<string>('/src/content/articles/**/*.html', { query: '?raw', import: 'default' });

function parseFrontmatter(source: string): { meta: Record<string, unknown>; body: string } {
  const match = source.match(/^<!--FRONTMATTER\s*([\s\S]*?)\s*-->/);
  if (!match) return { meta: {}, body: source };
  try {
    const meta = JSON.parse(match[1]);
    const body = source.slice(match[0].length).trim();
    return { meta, body };
  } catch {
    return { meta: {}, body: source };
  }
}

export async function getAllHtmlPosts(): Promise<HtmlPost[]> {
  const posts: HtmlPost[] = [];
  for (const [path, loader] of Object.entries(HTML_FILES)) {
    const filename = path.split('/').pop()!;
    const slug = filename.replace(/\.html$/, '');
    const raw = await loader();
    const { meta, body } = parseFrontmatter(raw);
    const category = String(meta.category ?? 'uncategorized');
    posts.push({
      id: slug,
      slug,
      collection: 'articles',
      contentType: 'html',
      data: {
        title: String(meta.title ?? 'Untitled'),
        description: String(meta.description ?? ''),
        date: new Date(String(meta.date ?? new Date().toISOString())),
        image: String(meta.image ?? ''),
        author: String(meta.author ?? 'Top Trip Ideas Staff'),
        tags: Array.isArray(meta.tags) ? meta.tags.map(String) : [],
        category,
        featured: Boolean(meta.featured ?? false),
      },
      rawHtml: body,
    });
  }
  return posts.sort((a, b) => b.data.date.getTime() - a.data.date.getTime());
}

export async function getHtmlPostsByCategory(category: string): Promise<HtmlPost[]> {
  const all = await getAllHtmlPosts();
  return all.filter((p) => p.data.category === category);
}

export async function getHtmlPostBySlug(slug: string): Promise<HtmlPost | undefined> {
  const all = await getAllHtmlPosts();
  return all.find((p) => p.slug === slug);
}
