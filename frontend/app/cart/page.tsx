"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { ApiError, apiRequest, formatCurrency, getAuthToken, type Cart, type Order } from "../../lib/api";

export default function CartPage() {
  const [cart, setCart] = useState<Cart | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [confirmation, setConfirmation] = useState("");

  useEffect(() => {
    const token = getAuthToken();
    if (!token) {
      window.location.replace(`/account?next=${encodeURIComponent("/cart")}`);
      return;
    }
    apiRequest<Cart>("/cart", {}, token)
      .then(setCart)
      .catch((requestError: unknown) => {
        if (requestError instanceof ApiError && requestError.status === 401) {
          window.localStorage.removeItem("berozgaar-token");
          window.location.replace(`/account?next=${encodeURIComponent("/cart")}`);
        } else {
          setError(requestError instanceof Error ? requestError.message : "Could not load your cart.");
        }
      })
      .finally(() => setLoading(false));
  }, []);

  async function updateQuantity(productId: number, quantity: number) {
    const token = getAuthToken();
    if (!token) return;
    setBusy(true);
    setError("");
    try {
      const updated = quantity === 0
        ? await apiRequest<Cart>(`/cart/items/${productId}`, { method: "DELETE" }, token)
        : await apiRequest<Cart>(`/cart/items/${productId}`, {
            method: "PUT",
            body: JSON.stringify({ product_id: productId, quantity }),
          }, token);
      setCart(updated);
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Could not update your cart.");
    } finally {
      setBusy(false);
    }
  }

  async function checkout() {
    const token = getAuthToken();
    if (!token) return;
    setBusy(true);
    setError("");
    try {
      const order = await apiRequest<Order>("/orders/checkout", {
        method: "POST",
        body: JSON.stringify({ payment_method: "cod" }),
      }, token);
      setCart({ items: [], total_paise: 0 });
      setConfirmation(`Order #${order.id} placed. Cash on delivery is unpaid until collected.`);
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Checkout could not be completed.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="page-shell utility-page">
      <Link href="/" className="back-link">← Back to shopping</Link>
      <section className="utility-card">
        <h1>Your cart</h1>
        {loading ? <p className="empty-state" role="status">Loading your cart…</p> : null}
        {error ? <p className="error-state" role="alert">{error}</p> : null}
        {confirmation ? <p className="success-state" role="status">{confirmation} <Link href="/account#orders">View orders</Link></p> : null}
        {!loading && !error && cart?.items.length === 0 ? <p className="empty-state">Your cart is empty. <Link href="/">Browse products</Link></p> : null}
        {cart?.items.length ? (
          <>
            <div className="cart-lines">
              {cart.items.map(({ product, quantity, line_total_paise }) => (
                <article className="cart-line" key={product.id}>
                  <div className="cart-line-info">
                    <Link href={`/products/${product.id}`}><strong>{product.name}</strong></Link>
                    <small>{formatCurrency(product.price_paise)} each</small>
                  </div>
                  <div className="quantity-control" aria-label={`Quantity for ${product.name}`}>
                    <button type="button" aria-label={`Decrease ${product.name} quantity`} disabled={busy || quantity <= 1} onClick={() => void updateQuantity(product.id, quantity - 1)}>−</button>
                    <span>{quantity}</span>
                    <button type="button" aria-label={`Increase ${product.name} quantity`} disabled={busy || quantity >= 50} onClick={() => void updateQuantity(product.id, quantity + 1)}>+</button>
                  </div>
                  <strong>{formatCurrency(line_total_paise)}</strong>
                  <button type="button" className="text-button remove-button" disabled={busy} onClick={() => void updateQuantity(product.id, 0)}>Remove</button>
                </article>
              ))}
            </div>
            <div className="cart-summary">
              <div><span>Total</span><strong>{formatCurrency(cart.total_paise)}</strong></div>
              <p>Payment method: Cash on delivery. Payment remains due on delivery.</p>
              <button className="primary-btn" type="button" disabled={busy} onClick={() => void checkout()}>{busy ? "Please wait…" : "Place COD order"}</button>
            </div>
          </>
        ) : null}
      </section>
    </main>
  );
}
