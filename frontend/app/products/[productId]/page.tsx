"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import { ArrowLeft, ShoppingCart } from "lucide-react";
import { ApiError, apiRequest, formatCurrency, getAuthToken, type Product } from "../../../lib/api";
import { ProductImage } from "../../../components/product-image";

export default function ProductDetailsPage() {
  const params = useParams<{ productId: string }>();
  const [product, setProduct] = useState<Product | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    apiRequest<Product>(`/products/${encodeURIComponent(params.productId)}`)
      .then((result) => {
        if (!cancelled) setProduct(result);
      })
      .catch((requestError: unknown) => {
        if (!cancelled) setError(requestError instanceof Error ? requestError.message : "Could not load this product.");
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [params.productId]);

  async function addToCart() {
    if (!product) return;
    const token = getAuthToken();
    if (!token) {
      window.location.assign(`/account?next=${encodeURIComponent(`/products/${product.id}`)}`);
      return;
    }
    try {
      await apiRequest(
        "/cart/items",
        { method: "POST", body: JSON.stringify({ product_id: product.id, quantity: 1 }) },
        token,
      );
      setNotice("Added to your cart.");
    } catch (requestError) {
      if (requestError instanceof ApiError && requestError.status === 401) {
        window.localStorage.removeItem("berozgaar-token");
        window.location.assign(`/account?next=${encodeURIComponent(`/products/${product.id}`)}`);
      } else {
        setNotice(requestError instanceof Error ? requestError.message : "Could not add this product.");
      }
    }
  }

  return (
    <main className="page-shell detail-page">
      <Link href="/" className="back-link"><ArrowLeft size={16} /> Back to shopping</Link>
      {loading ? <p className="empty-state" role="status">Loading product…</p> : null}
      {!loading && error ? <p className="empty-state error-state" role="alert">Product could not be loaded: {error}</p> : null}
      {!loading && product ? (
        <article className="detail-card">
          <div className="detail-art">
            <ProductImage src={product.image_url} alt={product.name} className="product-photo" />
          </div>
          <div className="detail-copy">
            <span className="eyebrow">{product.category}</span>
            <h1>{product.name}</h1>
            <p>{product.description || "No additional description has been provided for this product."}</p>
            <p className="detail-sku">SKU: {product.sku}</p>
            <strong className="detail-price">{formatCurrency(product.price_paise)}</strong>
            <p className="product-stock">
              {product.sku.startsWith("DEMO-")
                ? `Demo listing — sample quantity: ${product.stock}; this is not live inventory.`
                : product.stock > 0 ? `${product.stock} available` : "Currently unavailable"}
            </p>
            <button type="button" className="primary-btn" disabled={product.stock <= 0} onClick={() => void addToCart()}>
              <ShoppingCart size={17} /> Add to cart
            </button>
            {notice ? <p className="notice-message" role="status">{notice}</p> : null}
          </div>
        </article>
      ) : null}
    </main>
  );
}
