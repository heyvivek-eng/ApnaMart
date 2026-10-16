export type Product = {
  id: number;
  name: string;
  description: string;
  category: string;
  sku: string;
  price_paise: number;
  stock: number;
  image_url: string;
};

export type CartLine = {
  product: Product;
  quantity: number;
  line_total_paise: number;
};

export type Cart = {
  items: CartLine[];
  total_paise: number;
};

export type Order = {
  id: number;
  status: string;
  payment_method: string;
  payment_status: string;
  total_paise: number;
  items: Array<{
    product_name: string;
    sku: string;
    unit_price_paise: number;
    quantity: number;
  }>;
};

export class ApiError extends Error {
  constructor(
    message: string,
    readonly status: number,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

const apiBaseUrl = (process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1").replace(/\/$/, "");

export async function apiRequest<T>(
  path: string,
  options: RequestInit = {},
  token?: string,
): Promise<T> {
  const headers = new Headers(options.headers);
  if (options.body && !(options.body instanceof URLSearchParams)) {
    headers.set("Content-Type", "application/json");
  }
  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  const response = await fetch(`${apiBaseUrl}${path}`, { ...options, headers });
  if (!response.ok) {
    let message = `Request failed (${response.status})`;
    try {
      const body = (await response.json()) as { detail?: string };
      if (typeof body.detail === "string") message = body.detail;
    } catch {
      // Keep the HTTP status message when the server response is not JSON.
    }
    throw new ApiError(message, response.status);
  }

  return (await response.json()) as T;
}

export function getAuthToken(): string | null {
  return window.localStorage.getItem("berozgaar-token");
}

export function formatCurrency(paise: number): string {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0,
  }).format(paise / 100);
}
