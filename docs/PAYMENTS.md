# Payment boundaries

The current checkout supports COD only. New COD orders are recorded as `unpaid`; this code does not mark payment collected, reconcile collections or transfer money to sellers.

Razorpay is not configured. A production Razorpay integration must create provider orders on the server, keep keys server-only, verify signatures and webhooks, query provider state when appropriate, process duplicate events idempotently, and test failure/timeout/retry behavior. Standard checkout alone does not provide marketplace seller settlement. Obtain the appropriate approved marketplace/linked-account product and complete seller onboarding/KYC/compliance before implementing actual transfers.

No credentials are included and no live payment is claimed to have been tested.
