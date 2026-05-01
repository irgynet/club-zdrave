import type { ImageMetadata } from 'astro';

/**
 * An image value that may be either a local imported image (ImageMetadata,
 * produced by Astro's `image()` schema helper) or a remote URL string.
 */
export type FlexibleImage = ImageMetadata | string;

export function isLocalImage(value: FlexibleImage): value is ImageMetadata {
  return typeof value === 'object' && value !== null && 'src' in value;
}

export function getImageSrc(value: FlexibleImage): string {
  return isLocalImage(value) ? value.src : value;
}
