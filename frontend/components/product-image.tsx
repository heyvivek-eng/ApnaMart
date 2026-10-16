"use client";

import { useState } from "react";

type ProductImageProps = {
  src: string;
  alt: string;
  className: string;
};

const fallbackImage = "/images/demo-product-placeholder.svg";

export function ProductImage({ src, alt, className }: ProductImageProps) {
  const [failedSrc, setFailedSrc] = useState<string | null>(null);
  const imageSrc = src && failedSrc !== src ? src : fallbackImage;

  return (
    <img
      className={className}
      src={imageSrc}
      alt={alt}
      width={800}
      height={600}
      loading="lazy"
      decoding="async"
      onError={() => {
        if (src && failedSrc !== src) setFailedSrc(src);
      }}
    />
  );
}
