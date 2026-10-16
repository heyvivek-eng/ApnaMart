"use client";

import Link from "next/link";
import { useEffect, useState, type FormEvent } from "react";
import { ApiError, apiRequest, formatCurrency, getAuthToken, type Order } from "../../lib/api";

type AuthResponse = { access_token: string };

export default function AccountPage() {
  const [registering, setRegistering] = useState(false);
  const [token, setToken] = useState<string | null>(null);
  const [orders, setOrders] = useState<Order[]>([]);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    const savedToken = getAuthToken();
    setToken(savedToken);
    if (!savedToken) return;

    apiRequest<Order[]>("/orders", {}, savedToken)
      .then(setOrders)
      .catch((requestError: unknown) => {
        if (requestError instanceof ApiError && requestError.status === 401) {
          window.localStorage.removeItem("berozgaar-token");
          setToken(null);
          setError("Your session expired. Sign in again to view your orders.");
        } else {
          setError(requestError instanceof Error ? requestError.message : "Could not load your orders.");
        }
      });
  }, []);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true);
    setError("");
    try {
      if (registering) {
        await apiRequest("/auth/register", {
          method: "POST",
          body: JSON.stringify({ email, full_name: fullName, password }),
        });
      }
      const login = await apiRequest<AuthResponse>("/auth/login", {
        method: "POST",
        body: new URLSearchParams({ username: email, password }),
      });
      window.localStorage.setItem("berozgaar-token", login.access_token);
      const next = new URLSearchParams(window.location.search).get("next");
      const destination = next?.startsWith("/") && !next.startsWith("//") ? next : "/account";
      window.location.assign(destination);
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Could not sign in.");
    } finally {
      setBusy(false);
    }
  }

  function signOut() {
    window.localStorage.removeItem("berozgaar-token");
    setToken(null);
    setOrders([]);
    setError("");
  }

  return (
    <main className="page-shell utility-page">
      <Link href="/" className="back-link">← Back to shopping</Link>
      {token ? (
        <section className="utility-card">
          <div className="section-head">
            <h1>Your account</h1>
            <button type="button" className="text-button" onClick={signOut}>Sign out</button>
          </div>
          <section id="orders">
            <h2>Your orders</h2>
            {error ? <p className="error-state" role="alert">{error}</p> : null}
            {!error && orders.length === 0 ? <p className="empty-state">You have no orders yet.</p> : null}
            {orders.map((order) => (
              <article className="order-row" key={order.id}>
                <div><strong>Order #{order.id}</strong><small>{order.items.map((item) => `${item.product_name} × ${item.quantity}`).join(", ")}</small></div>
                <div><strong>{formatCurrency(order.total_paise)}</strong><small>{order.status} · {order.payment_status}</small></div>
              </article>
            ))}
          </section>
          <section id="support" className="support-note">
            <h2>Contact Us</h2>
            <p>Direct support contact is not configured in this MVP. Please use the project owner&apos;s published support channel.</p>
          </section>
        </section>
      ) : (
        <section className="utility-card auth-card">
          <h1>{registering ? "Create your account" : "Sign in to your account"}</h1>
          <p>Sign in to manage your orders and use your cart.</p>
          <form className="utility-form" onSubmit={(event) => void submit(event)}>
            {registering ? (
              <label>
                Full name
                <input required minLength={2} maxLength={120} autoComplete="name" value={fullName} onChange={(event) => setFullName(event.target.value)} />
              </label>
            ) : null}
            <label>
              Email
              <input required type="email" autoComplete="email" value={email} onChange={(event) => setEmail(event.target.value)} />
            </label>
            <label>
              Password
              <input required type="password" minLength={registering ? 10 : 1} maxLength={128} autoComplete={registering ? "new-password" : "current-password"} value={password} onChange={(event) => setPassword(event.target.value)} />
              {registering ? <small>Use at least 10 characters.</small> : null}
            </label>
            {error ? <p className="error-state" role="alert">{error}</p> : null}
            <button className="primary-btn" type="submit" disabled={busy}>{busy ? "Please wait…" : registering ? "Create account" : "Sign in"}</button>
          </form>
          <p className="auth-switch">
            {registering ? "Already have an account?" : "New to ApnaMart?"}{" "}
            <button type="button" className="text-button" onClick={() => { setRegistering((value) => !value); setError(""); }}>
              {registering ? "Sign in" : "Create an account"}
            </button>
          </p>
        </section>
      )}
    </main>
  );
}
