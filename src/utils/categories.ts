export type CategorySlug = 'otslabvane' | 'hranene-dieti' | 'dalgoletie' | 'sardechno-zdrave' | 'trenirovki';

export interface CategoryMeta {
  slug: CategorySlug;
  label: string;
  description: string;
  heroImage: string;
  color: string;
}

export const categories: CategoryMeta[] = [
  {
    slug: 'otslabvane',
    label: 'Отслабване',
    description: 'Практични и научно подкрепени стратегии за отслабване: хранене, навици, мотивация и устойчиви резултати за по-здраво тяло.',
    heroImage: '/images/categories/otslabvane.webp',
    color: 'teal',
  },
  {
    slug: 'hranene-dieti',
    label: 'Хранене и Диети',
    description: 'Съвети за здравословно хранене, популярни диети, балансирани менюта и научни насоки за по-добър и активен начин на живот.',
    heroImage: '/images/categories/hranene-dieti.webp',
    color: 'sky',
  },
  {
    slug: 'dalgoletie',
    label: 'Дълголетие',
    description: 'Научно обосновани подходи за дълголетие: хранене, движение, навици и грижа за тялото и ума за по-дълъг и качествен живот.',
    heroImage: '/images/categories/dalgoletie.webp',
    color: 'amber',
  },
  {
    slug: 'sardechno-zdrave',
    label: 'Сърдечно Здраве',
    description: 'Информация и съвети за поддържане на здраво сърце: хранене, активност, превенция и намаляване на рисковите фактори.',
    heroImage: '/images/categories/sardechno-zdrave.webp',
    color: 'rose',
  },
  {
    slug: 'trenirovki',
    label: 'Тренировки',
    description: 'Тренировъчни програми, упражнения и експертни насоки за сила, издръжливост, тонус и по-добра физическа форма.',
    heroImage: '/images/categories/trenirovki.webp',
    color: 'emerald',
  },
];

export function getCategoryMeta(slug: CategorySlug): CategoryMeta {
  return categories.find((c) => c.slug === slug)!;
}
