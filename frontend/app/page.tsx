"use client";

import Link from "next/link";
import { useEffect, useMemo, useState, type FormEvent } from "react";
import {
  BookOpen,
  CarFront,
  Dumbbell,
  Gamepad2,
  Headset,
  Heart,
  HeartPulse,
  House,
  Menu,
  Monitor,
  MoonStar,
  PackageCheck,
  Search,
  ShieldCheck,
  Shirt,
  ShoppingCart,
  Sparkles,
  SunMedium,
  Truck,
  UserRound,
  type LucideIcon,
} from "lucide-react";
import { ApiError, apiRequest, formatCurrency, getAuthToken, type Cart, type Product } from "../lib/api";
import { ProductImage } from "../components/product-image";
import { useTheme } from "./theme-provider";

const categoryIcons: Record<string, LucideIcon> = {
  electronics: Monitor,
  "electronics & accessories": Monitor,
  clothing: Shirt,
  fashion: Shirt,
  "fashion & footwear": Shirt,
  "home & kitchen": House,
  "home & living": House,
  beauty: Sparkles,
  sports: Dumbbell,
  automotive: CarFront,
  books: BookOpen,
  "toys & games": Gamepad2,
  "health & wellness": HeartPulse,
  "sports, toys & lifestyle": Dumbbell,
};

const categoryImages: Record<string, string> = {
  electronics: "https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=800&q=80",
  "electronics & accessories": "https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=800&q=80",
  fashion: "https://images.unsplash.com/photo-1521572267360-ee0c2909d518?auto=format&fit=crop&w=800&q=80",
  "fashion & footwear": "https://images.unsplash.com/photo-1521572267360-ee0c2909d518?auto=format&fit=crop&w=800&q=80",
  clothing: "https://images.unsplash.com/photo-1521572267360-ee0c2909d518?auto=format&fit=crop&w=800&q=80",
  "home & living": "https://images.unsplash.com/photo-1505693416388-ac5ce068fe85?auto=format&fit=crop&w=800&q=80",
  "home & kitchen": "https://images.unsplash.com/photo-1505693416388-ac5ce068fe85?auto=format&fit=crop&w=800&q=80",
  beauty: "https://images.unsplash.com/photo-1522335789203-aabd1fc54bc9?auto=format&fit=crop&w=800&q=80",
  sports: "https://images.unsplash.com/photo-1542291026-7eec264c27ff?auto=format&fit=crop&w=800&q=80",
  "toys & games": "https://images.unsplash.com/photo-1600185365483-26d7a4cc7519?auto=format&fit=crop&w=800&q=80",
  automotive: "https://images.unsplash.com/photo-1492144534655-ae79c964c9d7?auto=format&fit=crop&w=800&q=80",
  books: "https://images.unsplash.com/photo-1512820790803-83ca734da794?auto=format&fit=crop&w=800&q=80",
  "books & stationery": "https://images.unsplash.com/photo-1512820790803-83ca734da794?auto=format&fit=crop&w=800&q=80",
  "beauty & personal care": "https://images.unsplash.com/photo-1522335789203-aabd1fc54bc9?auto=format&fit=crop&w=800&q=80",
  "sports, toys & lifestyle": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?auto=format&fit=crop&w=800&q=80",
};

const benefits = [
  { title: "Free Shipping", detail: "On orders over ₹999", icon: Truck },
  { title: "Secure Payments", detail: "100% protected", icon: ShieldCheck },
  { title: "Easy Returns", detail: "30-day return policy", icon: PackageCheck },
  { title: "24/7 Support", detail: "Always here to help", icon: Headset },
];

const PAGE_SIZE = 24;
const catalogCategories = [
  "Electronics & Accessories",
  "Fashion & Footwear",
  "Home & Kitchen",
  "Beauty & Personal Care",
  "Books & Stationery",
  "Sports, Toys & Lifestyle",
  "Clothing",
  "Electronics",
];

export default function Home() {
  const { theme, ready: themeReady, toggleTheme } = useTheme();
  const [products, setProducts] = useState<Product[]>([]);
  const [query, setQuery] = useState("");
  const [category, setCategory] = useState("");
  const [sort, setSort] = useState("newest");
  const [page, setPage] = useState(0);
  const [hasMore, setHasMore] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [cartCount, setCartCount] = useState(0);
  const [notice, setNotice] = useState("");
  const [mobileCategoriesOpen, setMobileCategoriesOpen] = useState(false);

  useEffect(() => {
    let cancelled = false;
    const timer = window.setTimeout(async () => {
      setLoading(true);
      setError("");
      const params = new URLSearchParams({ limit: String(PAGE_SIZE), offset: String(page * PAGE_SIZE), sort });
      if (query.trim()) params.set("q", query.trim());
      if (category) params.set("category", category);

      try {
        const result = await apiRequest<Product[]>(`/products?${params.toString()}`);
        if (!cancelled) {
          setProducts((current) => page === 0 ? result : [...current, ...result]);
          setHasMore(result.length === PAGE_SIZE);
        }
      } catch (requestError) {
        if (!cancelled) {
          if (page === 0) setProducts([]);
          setError(requestError instanceof Error ? requestError.message : "Could not load products.");
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }, 200);
    return () => {
      cancelled = true;
      window.clearTimeout(timer);
    };
  }, [query, category, sort, page]);

  useEffect(() => {
    const token = getAuthToken();
    if (!token) return;
    apiRequest<Cart>("/cart", {}, token)
      .then((cart) => setCartCount(cart.items.reduce((count, item) => count + item.quantity, 0)))
      .catch((requestError: unknown) => {
        if (requestError instanceof ApiError && requestError.status === 401) {
          window.localStorage.removeItem("berozgaar-token");
        }
      });
  }, []);

  const categories = useMemo(() => catalogCategories, []);

  async function addToCart(product: Product) {
    const token = getAuthToken();
    if (!token) {
      window.location.assign("/account?next=/cart");
      return;
    }
    try {
      const cart = await apiRequest<Cart>(
        "/cart/items",
        { method: "POST", body: JSON.stringify({ product_id: product.id, quantity: 1 }) },
        token,
      );
      setCartCount(cart.items.reduce((count, item) => count + item.quantity, 0));
      setNotice(`${product.name} added to your cart.`);
    } catch (requestError) {
      if (requestError instanceof ApiError && requestError.status === 401) {
        window.localStorage.removeItem("berozgaar-token");
        window.location.assign("/account?next=/cart");
      } else {
        setNotice(requestError instanceof Error ? requestError.message : "Could not add this product.");
      }
    }
  }

  function handleSearch(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    document.getElementById("products")?.scrollIntoView({ behavior: "smooth" });
  }

  function selectCategory(value: string) {
    setCategory((selected) => (selected === value ? "" : value));
    setProducts([]);
    setPage(0);
    setMobileCategoriesOpen(false);
    document.getElementById("products")?.scrollIntoView({ behavior: "smooth" });
  }

  return (
    <>
      <div className="topbar">Thoughtful finds. Fair prices. Delivered across India.</div>
      <header className="site-header">
        <div className="header-inner">
          <Link className="brand-block" href="/" aria-label="ApnaMart home">
            <span className="brand-mark" aria-hidden="true">A</span>
            <span className="brand-word">ApnaMart</span>
          </Link>
          <form className="search-wrap" onSubmit={handleSearch} role="search">
            <input
              type="search"
              placeholder="Search for products..."
              aria-label="Search for products"
              value={query}
              onChange={(event) => {
                setQuery(event.target.value);
                setProducts([]);
                setPage(0);
              }}
            />
            <button className="search-icon" type="submit" aria-label="Search">
              <Search size={16} />
            </button>
          </form>
          <div className="header-actions">
            <Link className="header-action" href="/account">
              <span className="action-icon" aria-hidden="true"><UserRound size={16} /></span>
              <span>Account</span>
            </Link>
            <button className="header-action unavailable-action" type="button" disabled title="Wishlist is not available in this version">
              <span className="action-icon" aria-hidden="true"><Heart size={16} /></span>
              <span>Wishlist</span>
            </button>
            <Link className="header-action cart-action" href="/cart" aria-label={`Cart, ${cartCount} items`}>
              <span className="action-icon" aria-hidden="true"><ShoppingCart size={16} /></span>
              <span>Cart</span>
              <span className="cart-badge">{cartCount}</span>
            </Link>
            <button
              type="button"
              className="theme-toggle"
              aria-label={`Switch to ${theme === "light" ? "dark" : "light"} mode`}
              disabled={!themeReady}
              onClick={toggleTheme}
            >
              {theme === "light" ? <SunMedium size={16} /> : <MoonStar size={16} />}
            </button>
          </div>
        </div>
        <div className="nav-row">
          <button
            type="button"
            className="browse-btn"
            aria-expanded={mobileCategoriesOpen}
            onClick={() => setMobileCategoriesOpen((open) => !open)}
          >
            <span className="menu-icon" aria-hidden="true"><Menu size={15} /></span>
            Browse Categories
          </button>
          <nav className="nav-links" aria-label="Main navigation">
            <Link className="active" href="/">Home</Link>
            <a href="#products">Shop</a>
            <a href="#products">Deals</a>
            <a href="#products">New Arrivals</a>
            <a href="#products">Best Sellers</a>
            <Link href="/account#orders">Track Order</Link>
            <Link href="/account#support">Contact Us</Link>
          </nav>
        </div>
      </header>

      {notice ? (
        <div className="notice page-shell" role="status">
          <span>{notice}</span>
          <button type="button" aria-label="Dismiss message" onClick={() => setNotice("")}>×</button>
        </div>
      ) : null}

      <main className="page-shell">
        <div className="content-grid">
          <aside className={`category-sidebar${mobileCategoriesOpen ? " mobile-open" : ""}`} aria-label="Product categories">
            <ul>
              {categories.length ? categories.map((item) => {
                const Icon = categoryIcons[item.toLowerCase()] ?? PackageCheck;
                return (
                  <li key={item}>
                    <button className={category === item ? "selected-category" : ""} type="button" onClick={() => selectCategory(item)}>
                      <span className="side-icon" aria-hidden="true"><Icon size={17} /></span>
                      <span>{item}</span>
                    </button>
                  </li>
                );
              }) : <li className="category-empty">Categories appear when the catalog is available.</li>}
            </ul>
            {category ? <button type="button" className="clear-category" onClick={() => setCategory("")}>Clear category filter</button> : null}
          </aside>

          <div className="main-column">
            <section className="hero-banner" aria-label="Promotional banner">
              <div className="hero-copy">
                <span className="eyebrow">WELCOME TO APNAMART</span>
                <h1>Discover. Shop. Enjoy.</h1>
                <p>Find the best products at the best prices. Fast delivery. Easy returns.</p>
                <a className="primary-btn" href="#products">Shop Now</a>
              </div>
              <div className="hero-visual" aria-hidden="true">
                <img
                  src="https://images.unsplash.com/photo-1546435770-a3e426bf472b?auto=format&fit=crop&w=800&q=80"
                  alt=""
                  className="hero-product hero-headphones"
                />
                <img
                  src="https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?auto=format&fit=crop&w=800&q=80"
                  alt=""
                  className="hero-product hero-phone"
                />
                <img
                  src="https://images.unsplash.com/photo-1523275335684-37898b6baf30?auto=format&fit=crop&w=800&q=80"
                  alt=""
                  className="hero-product hero-watch"
                />
                <div className="promo-pill">New</div>
              </div>
              <div className="slider-dots" aria-hidden="true">
                <span className="dot active" /><span className="dot" /><span className="dot" />
              </div>
            </section>

            <div className="benefit-strip" aria-label="Customer benefits">
              {benefits.map(({ title, detail, icon: Icon }) => (
                <div key={title} className="benefit-item">
                  <span className="benefit-icon" aria-hidden="true"><Icon size={18} /></span>
                  <div><strong>{title}</strong><small>{detail}</small></div>
                </div>
              ))}
            </div>

            <section className="catalog-section" id="categories">
              <div className="section-head"><h2>Shop by Category</h2></div>
              {categories.length ? (
                <div className="category-grid">
                  {categories.map((item, index) => {
                    const Icon = categoryIcons[item.toLowerCase()] ?? PackageCheck;
                    return (
                      <button
                        key={item}
                        type="button"
                        className={`category-card category-tint-${index % 4}`}
                        aria-pressed={category === item}
                        onClick={() => selectCategory(item)}
                      >
                        <span className="category-media">
                          {categoryImages[item.toLowerCase()] ? <img src={categoryImages[item.toLowerCase()]} alt="" /> : <Icon size={38} aria-hidden="true" />}
                        </span>
                        <span className="category-body"><span className="category-icon"><Icon size={16} /></span>{item}</span>
                      </button>
                    );
                  })}
                </div>
              ) : <p className="empty-state">No categories are available until products have been added to the catalog.</p>}
            </section>

            <section className="catalog-section" id="products">
              <div className="section-head">
                <h2>{category || "Shop Products"}</h2>
                <div className="catalog-controls">
                  <label className="sort-control">
                    <span>Sort by</span>
                    <select value={sort} onChange={(event) => { setSort(event.target.value); setProducts([]); setPage(0); }}>
                      <option value="newest">Newest</option>
                      <option value="price_asc">Price: low to high</option>
                      <option value="price_desc">Price: high to low</option>
                    </select>
                  </label>
                  {category ? <button className="text-button" type="button" onClick={() => { setCategory(""); setProducts([]); setPage(0); }}>Show all products</button> : null}
                </div>
              </div>
              {loading ? <p className="empty-state" role="status">Loading products…</p> : null}
              {!loading && error ? (
                <div className="empty-state error-state" role="alert">
                  <p>Products could not be loaded: {error}</p>
                  <p>Check that the API is running at {process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1"}.</p>
                </div>
              ) : null}
              {!loading && !error && products.length === 0 ? (
                <div className="empty-state">
                  {query || category ? <p>No products match your search or category.</p> : <p>The catalog is empty. Add catalog products to see them here.</p>}
                </div>
              ) : null}
              {!loading && !error && products.length > 0 ? (
                <div className="product-grid">
                  {products.map((product) => (
                    <article key={product.id} className="product-card">
                      <Link className="product-detail-link" href={`/products/${product.id}`} aria-label={`View ${product.name}`}>
                        <div className="product-art">
                          <ProductImage src={product.image_url} alt={product.name} className="product-photo" />
                          <span className="product-tag">
                            {product.sku.startsWith("DEMO-")
                              ? `Demo · ${product.category}`
                              : product.stock > 0 ? product.category : "Out of stock"}
                          </span>
                        </div>
                        <div className="product-body">
                          <h3>{product.name}</h3>
                          <span className="product-stock">
                            {product.sku.startsWith("DEMO-")
                              ? `Sample quantity: ${product.stock}`
                              : product.stock > 0 ? `${product.stock} available` : "Currently unavailable"}
                          </span>
                          <div className="price-row"><strong>{formatCurrency(product.price_paise)}</strong></div>
                        </div>
                      </Link>
                      <div className="product-card-action">
                        <button type="button" className="mini-cart-btn" aria-label={`Add ${product.name} to cart`} disabled={product.stock <= 0} onClick={() => void addToCart(product)}>
                          <ShoppingCart size={14} />
                        </button>
                      </div>
                    </article>
                  ))}
                </div>
              ) : null}
              {!loading && !error && products.length > 0 && hasMore ? (
                <div className="load-more-wrap">
                  <button className="primary-btn" type="button" onClick={() => setPage((current) => current + 1)}>Load more products</button>
                </div>
              ) : null}
            </section>
          </div>
        </div>
      </main>
    </>
  );
}
