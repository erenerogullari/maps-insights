# MapInsights Frontend — Claude Code Context

## **Project Overview (Frontend Focus)**

MapInsights is an AI-powered SaaS tool for local business owners to get detailed feedback on their Google Maps presence. This document covers **frontend architecture only** — the Next.js application that provides the user interface for input, payment, and results visualization.

---

## **Frontend Technology Stack**

- **Framework**: Next.js 14+ (React, file-based routing, serverless API routes)
- **Language**: TypeScript (type safety, IDE support)
- **Styling**: Tailwind CSS (utility-first, rapid development)
- **HTTP Client**: Axios or Fetch API (API communication)
- **Payments**: Stripe.js (client-side payment handling)
- **State Management**: React hooks + Context API (simple, no Redux needed)
- **Testing**: Vitest + React Testing Library (component tests)
- **Package Manager**: npm or pnpm

---

## **Frontend Architecture**

### **Data Flow**

```
User Input (Google Maps URL)
    ↓
MapInputForm Component
    ↓
POST /api/checkout (Stripe session)
    ↓
Stripe Payment Modal
    ↓
Payment Success Webhook
    ↓
POST /api/analyze (Backend analysis)
    ↓
Results Display (ScoreCard, MediaFeedback, etc.)
```

### **Folder Structure**

```
frontend/
├── src/
│   ├── pages/
│   │   ├── index.tsx           # Landing page
│   │   ├── dashboard.tsx       # Analysis input page
│   │   ├── pricing.tsx         # Pricing/features page
│   │   ├── results/[id].tsx    # Analysis result detail page
│   │   ├── 404.tsx             # Not found
│   │   └── api/
│   │       ├── checkout.ts     # POST: Create Stripe checkout session
│   │       ├── analyze.ts      # POST: Trigger backend analysis
│   │       ├── webhook/stripe.ts # POST: Stripe webhook handler
│   │       └── health.ts       # GET: API health check
│   ├── components/
│   │   ├── Header.tsx
│   │   ├── Footer.tsx
│   │   ├── Navbar.tsx
│   │   ├── forms/
│   │   │   └── MapInputForm.tsx       # URL input + submit
│   │   ├── results/
│   │   │   ├── ScoreCard.tsx          # Overall score display
│   │   │   ├── MediaFeedback.tsx      # Photos/videos analysis
│   │   │   ├── InfoFeedback.tsx       # Info availability feedback
│   │   │   ├── ReviewFeedback.tsx     # Review sentiment & patterns
│   │   │   └── FeedbackGrid.tsx       # Layout wrapper
│   │   ├── payment/
│   │   │   ├── StripeCheckout.tsx     # Stripe embedded form
│   │   │   └── PaymentStatus.tsx      # Payment result display
│   │   └── shared/
│   │       ├── LoadingSpinner.tsx
│   │       ├── ErrorBoundary.tsx
│   │       ├── Button.tsx
│   │       └── Card.tsx
│   ├── hooks/
│   │   ├── useAnalysis.ts      # Hook for analysis API calls
│   │   ├── usePayment.ts       # Hook for Stripe payment flow
│   │   ├── useLocalStorage.ts  # Persist analysis history (optional)
│   │   └── useFetch.ts         # Generic fetch hook with loading/error
│   ├── lib/
│   │   ├── api.ts              # Axios/Fetch client, API base setup
│   │   ├── stripe.ts           # Stripe client initialization
│   │   ├── validators.ts       # URL validation, form validation
│   │   └── constants.ts        # App constants (prices, API URLs)
│   ├── types/
│   │   ├── analysis.ts         # FeedbackResponse, ScoreCard types
│   │   ├── payment.ts          # PaymentRequest, PaymentResponse types
│   │   ├── api.ts              # Generic API response types
│   │   └── index.ts            # Central type exports
│   ├── styles/
│   │   ├── globals.css         # Global styles + Tailwind imports
│   │   ├── variables.css       # CSS variables for theming
│   │   └── tailwind.css        # Tailwind config (if not in config file)
│   └── App.tsx (or _app.tsx)   # Root component / layout
├── public/
│   ├── favicon.ico
│   ├── logo.svg
│   └── images/
├── .env.local.example          # Env vars template
├── .gitignore                  # Node-specific ignores
├── next.config.js              # Next.js configuration
├── tailwind.config.js          # Tailwind CSS configuration
├── tsconfig.json               # TypeScript configuration
├── package.json                # Node dependencies
├── package-lock.json           # Dependency lock file
└── README.md                   # Frontend setup & component docs
```

---

## **Environment Variables (Frontend)**

**File**: `frontend/.env.local`

```
# Stripe (Public Key)
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_live_or_pk_test_key_here

# Backend API
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000  # Dev: local backend
                                                 # Prod: https://api.mapinsights.com

# App Configuration
NEXT_PUBLIC_APP_NAME=MapInsights
NEXT_PUBLIC_PRICE_USD=9.99
```

**Note**: Variables prefixed with `NEXT_PUBLIC_` are exposed to browser; never put secrets here.

---

## **Page Structure**

### **Landing Page** (`pages/index.tsx`)
- Hero section with value proposition
- CTA button → `/dashboard`
- Features overview
- Social proof (optional)

### **Dashboard** (`pages/dashboard.tsx`)
- MapInputForm component
- Input Google Maps URL
- Submit button
- Loading state during analysis
- Error handling

### **Results Page** (`pages/results/[id].tsx`)
- Dynamic route based on analysis ID
- ScoreCard (overall metrics)
- MediaFeedback (photo/video breakdown)
- InfoFeedback (contact/website/hours completeness)
- ReviewFeedback (sentiment & themes)
- CTA: "Run another analysis" or "Share results"

### **API Routes**

#### **`pages/api/checkout.ts`** — Create Stripe Session
```typescript
export default async function handler(req, res) {
  if (req.method !== "POST") return res.status(405).end();
  
  const { email } = req.body;
  
  // Call Stripe API to create checkout session
  // Return session ID
}
```

#### **`pages/api/analyze.ts`** — Trigger Backend Analysis
```typescript
export default async function handler(req, res) {
  if (req.method !== "POST") return res.status(405).end();
  
  const { googleMapsUrl, paymentId } = req.body;
  
  // Verify payment with backend
  // Call backend /analyze endpoint
  // Return analysis results
}
```

#### **`pages/api/webhook/stripe.ts`** — Stripe Webhook Handler
```typescript
export default async function handler(req, res) {
  // Verify webhook signature
  // Handle payment_intent.succeeded event
  // Mark order as paid
  // Return 200 OK
}
```

---

## **Key Components**

### **MapInputForm.tsx**
```typescript
interface MapInputFormProps {
  onSubmit: (url: string) => Promise<void>;
  isLoading?: boolean;
}

export default function MapInputForm({ onSubmit, isLoading }: MapInputFormProps) {
  const [url, setUrl] = useState("");
  const [error, setError] = useState("");
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validate URL
    // Call onSubmit callback
    // Handle errors
  };
  
  return (
    // Form UI
  );
}
```

### **ScoreCard.tsx**
```typescript
interface ScoreCardProps {
  overall_score: number;
  media_score: number;
  info_score: number;
  review_score: number;
}

export default function ScoreCard({ overall_score, ...scores }: ScoreCardProps) {
  return (
    // Display scores with progress bars / visualizations
  );
}
```

### **usePayment Hook**
```typescript
export function usePayment() {
  const [status, setStatus] = useState<"idle" | "processing" | "success" | "error">("idle");
  
  const checkout = async (email: string) => {
    // Call /api/checkout
    // Redirect to Stripe checkout
  };
  
  return { status, checkout };
}
```

### **useAnalysis Hook**
```typescript
export function useAnalysis() {
  const [data, setData] = useState<AnalysisResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const analyze = async (googleMapsUrl: string) => {
    // Call /api/analyze
    // Handle response
    // Handle errors
  };
  
  return { data, loading, error, analyze };
}
```

---

## **Type Definitions** (`types/`)

### **`types/analysis.ts`**
```typescript
export interface ScoreCard {
  overall_score: number;
  media_score: number;
  info_score: number;
  review_score: number;
}

export interface MediaFeedback {
  photo_count: number;
  video_count: number;
  quality_assessment: string;
  recommendations: string[];
}

export interface InfoFeedback {
  completeness_score: number;
  missing_fields: string[];
  recommendations: string[];
}

export interface ReviewFeedback {
  average_rating: number;
  total_reviews: number;
  common_positives: string[];
  common_negatives: string[];
}

export interface AnalysisResponse {
  id: string;
  scores: ScoreCard;
  media: MediaFeedback;
  info: InfoFeedback;
  reviews: ReviewFeedback;
  created_at: string;
}
```

### **`types/payment.ts`**
```typescript
export interface PaymentRequest {
  email: string;
  google_maps_url: string;
}

export interface PaymentResponse {
  session_id: string;
  checkout_url: string;
}

export interface WebhookEvent {
  type: string;
  data: {
    object: {
      id: string;
      status: string;
      email: string;
    };
  };
}
```

---

## **Styling Strategy**

### **Tailwind CSS Configuration**
```javascript
// tailwind.config.js
module.exports = {
  content: ["./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        primary: "#2563eb",      // MapInsights brand color
        secondary: "#64748b",
      },
      spacing: {
        // Custom spacing if needed
      },
    },
  },
  plugins: [],
};
```

### **Global Styles** (`styles/globals.css`)
```css
@tailwind base;
@tailwind components;
@tailwind utilities;

/* Custom components */
@layer components {
  .btn-primary {
    @apply px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary-dark;
  }
  .card {
    @apply p-6 bg-white rounded-lg shadow-md;
  }
}
```

---

## **API Client Setup** (`lib/api.ts`)

```typescript
import axios from "axios";

const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_BASE_URL,
  timeout: 30000,
});

export const api = {
  scraper: {
    analyze: (url: string) => apiClient.post("/analyze", { url }),
  },
  payment: {
    checkout: (email: string) => apiClient.post("/api/checkout", { email }),
  },
};

export default apiClient;
```

---

## **Deployment**

### **Local Development**
```bash
npm install
npm run dev
# App on http://localhost:3000
```

### **Build & Export**
```bash
npm run build
npm start  # Production server
```

### **Vercel Deployment**
- Push to GitHub
- Vercel auto-detects Next.js
- Set env vars in Vercel project settings
- Auto-deploy on push

---

## **Current Status**

🔄 **Phase**: Task 1 (Backend Apify) — Frontend setup deferred

- [ ] Next.js project initialized
- [ ] TypeScript configured
- [ ] Tailwind CSS set up
- [ ] Basic pages created (landing, dashboard)
- [ ] API routes stubbed
- [ ] Components stubbed

**Next**: Once backend Task 1 is complete, start frontend integration.

---

## **References**

- [Next.js Docs](https://nextjs.org/docs)
- [React Docs](https://react.dev/)
- [TypeScript Docs](https://www.typescriptlang.org/docs/)
- [Tailwind CSS](https://tailwindcss.com/docs)
- [Stripe.js Docs](https://stripe.com/docs/js)
- [Axios Docs](https://axios-http.com/docs/intro)