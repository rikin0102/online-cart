# Online Cart Web Application

A full-stack, production-ready online shopping cart web application built with **FastAPI**, **SQLAlchemy 2.0**, **Alembic**, **PostgreSQL**, **React 18**, and **Vite**.

---

## 1. Overview

Online Cart is an authenticated ecommerce shopping platform designed to provide a secure, reliable, and smooth shopping experience. The backend acts as the single source of truth for all business-critical operations including catalog pricing, real product imagery, user cart isolation, database migrations, and atomic order placements with transactional email confirmations.

### Primary User Flow

```text
Register / Login (Domain validation & bcrypt authentication)
   ↓
Product Dashboard (Responsive catalog grid with real product photography)
   ↓
Add Products to Cart / Live Stepper Quantity
   ↓
Shopping Cart (Responsive table / stacked mobile list with thumbnails)
   ↓
Place Order (Atomic transaction + snapshot line items + cart purge)
   ↓
Dispatch Confirmation Email (STARTTLS SMTP with HTML invoice)
   ↓
Order Success Page (Reference summary & email status banner)
```

---

## 2. Features

- **JWT Authentication & Authorization**: Secure password hashing with bcrypt, stateless JWT token issuance, email domain validation, and route protection.
- **Strict User Cart Scoping**: Every cart operation is strictly scoped to the authenticated user's JWT `sub` ID at the database level.
- **Accurate Financial Calculations**: Exact monetary computations using Python `Decimal` and SQL `Numeric(10, 2)`—eliminating binary floating-point inaccuracies.
- **Database Migrations with Alembic**: Fully automated schema versioning with safe, idempotent migrations for initial schemas and table alterations.
- **Real Product Photography**: Curated high-resolution product photos mapped to catalog items and categories with smooth hover zoom effects and fallback handling.
- **Atomic Order Submission**: Database transactions guarantee that Order creation, OrderItem snapshot recording, and Cart clearing succeed together or roll back completely.
- **Snapshot Data Integrity**: Historical orders store snapshots of product names and unit prices at the time of purchase, preserving data integrity even if catalog prices change later.
- **Resilient SMTP Email Service**: Sends HTML and plain-text fallback order bills via SMTP STARTTLS. If email delivery fails, the transaction is not rolled back, and the client receives an informative warning banner.
- **Clean Responsive UI**: Modern small-business design system with pure CSS (Inter typography, #FFFFFF cards, #F8FAFC visual containers, #2563EB primary, 4/2/1 responsive grid).

---

## 3. Tech Stack

### Backend
- **Python 3.11+**: Typed asynchronous backend runtime.
- **FastAPI**: High-performance REST framework with automatic OpenAPI/Swagger documentation.
- **SQLAlchemy 2.0**: Declarative ORM with explicit transactional integrity and relationship mapping.
- **Alembic**: Database migration tool for versioned schema tracking.
- **Pydantic v2 & Pydantic-Settings**: Strict request/response validation, email normalization, and typed settings.
- **psycopg2-binary & psycopg 3**: PostgreSQL database adapters.
- **python-jose & passlib[bcrypt]**: JWT generation, decoding, and bcrypt password hashing.
- **smtplib**: Standard library SMTP client for STARTTLS transactional email dispatch.

### Frontend
- **React 18**: Component-based user interface.
- **Vite**: Ultra-fast build tool and development server.
- **React Router v6**: Client-side routing with protected route guards.
- **Axios**: Centralized HTTP client configured with request/response interceptors for JWT injection and error handling.
- **Plain CSS**: Clean, modular styling without heavy external CSS frameworks.

### Database
- **PostgreSQL**: Enterprise-grade relational database.

---

## 4. Why PostgreSQL & Alembic?

1. **Relational Data Integrity**: Strict foreign key constraints (`ON DELETE CASCADE`) maintain relationships between Users, CartItems, Orders, and OrderItems.
2. **ACID Transactions**: Enables atomic order submission where order persistence and cart purging succeed as a single atomic unit.
3. **Exact Numeric Type (`Numeric(10, 2)`)**: Prevents IEEE 754 floating-point rounding errors in currency and financial totals.
4. **Unique Constraints**: Guarantees uniqueness for user emails and `(user_id, product_id)` cart entries at the database level.
5. **Automated Schema Evolution**: Alembic migrations track schema changes (e.g. adding `image_url` column) reliably across local and cloud environments.

---

## 5. Project Structure

```text
Online-Cart/
│
├── backend/
│   ├── alembic.ini              # Alembic configuration
│   ├── alembic/
│   │   ├── env.py               # Alembic environment with dynamic DATABASE_URL mapping
│   │   └── versions/
│   │       ├── 0001_initial_schema.py            # Baseline database tables
│   │       └── 0002_add_image_url_to_products.py # Migration for product image URLs
│   │
│   ├── app/
│   │   ├── __init__.py          # Package initialization
│   │   ├── main.py              # FastAPI application entry point, CORS & lifespan
│   │   ├── config.py            # Pydantic Settings & environment variable loader
│   │   ├── database.py          # SQLAlchemy engine, SessionLocal, and DB dependencies
│   │   ├── models.py            # SQLAlchemy models (User, Product, CartItem, Order, OrderItem)
│   │   ├── schemas.py           # Pydantic models for request/response validation
│   │   ├── security.py          # Password hashing and JWT token logic
│   │   ├── deps.py              # FastAPI authentication dependencies (get_current_user)
│   │   ├── email_service.py     # SMTP STARTTLS email sender with HTML template
│   │   ├── seed.py              # Idempotent catalog product seeder (10 items with images)
│   │   │
│   │   └── routers/
│   │       ├── __init__.py
│   │       ├── auth.py          # /auth/register, /auth/login, /auth/me
│   │       ├── products.py      # /products
│   │       ├── cart.py          # /cart, /cart/items, /cart/items/{product_id}
│   │       └── orders.py        # /orders/submit
│   │
│   ├── requirements.txt         # Python dependencies
│   ├── .env.example             # Backend environment template
│   └── Procfile                 # Process file for Render / cloud deployment
│
├── frontend/
│   ├── index.html               # Vite HTML entry point
│   ├── package.json             # Frontend dependencies & npm scripts
│   ├── vite.config.js           # Vite build configuration
│   ├── .env.example             # Frontend environment template
│   ├── .gitignore               # Frontend gitignore
│   │
│   ├── public/
│   │   └── images/
│   │       └── products/        # High-resolution product images
│   │           ├── wireless-mouse.jpg
│   │           ├── usb-keyboard.jpg
│   │           ├── laptop-stand.jpg
│   │           ├── hd-webcam.jpg
│   │           ├── phone-stand.jpg
│   │           ├── hdmi-cable.jpg
│   │           ├── mouse-pad.jpg
│   │           └── desk-lamp.jpg
│   │
│   └── src/
│       ├── main.jsx             # React entry point with providers
│       ├── App.jsx              # Route definitions and layout shell
│       │
│       ├── api/
│       │   ├── client.js        # Centralized Axios instance with auth interceptors
│       │   ├── auth.js          # Authentication API calls
│       │   ├── products.js      # Products API calls
│       │   ├── cart.js          # Cart & checkout API calls
│       │   └── errorHandler.js  # Standardized error extraction
│       │
│       ├── context/
│       │   └── AuthContext.jsx  # Global authentication and cart state management
│       │
│       ├── utils/
│       │   └── productImages.js # Product image resolution and fallback helper
│       │
│       ├── components/
│       │   ├── Navbar.jsx       # Global responsive navigation bar
│       │   ├── ProductCard.jsx  # Product catalog card with quantity stepper
│       │   ├── CartItemRow.jsx  # Table row (desktop) and stacked card (mobile)
│       │   ├── Toast.jsx        # Non-blocking notification toast provider
│       │   └── ProtectedRoute.jsx # Route guard for authenticated pages
│       │
│       ├── pages/
│       │   ├── Login.jsx        # User login page
│       │   ├── Register.jsx     # User registration page
│       │   ├── Dashboard.jsx    # Product catalog dashboard with filters
│       │   ├── Cart.jsx         # Cart summary and checkout page
│       │   └── OrderSuccess.jsx # Post-checkout receipt and status page
│       │
│       └── styles/
│           ├── global.css       # Core design tokens, typography, and base elements
│           ├── auth.css         # Styling for login & registration cards
│           ├── dashboard.css    # 4/2/1 column product grid and category chips
│           ├── cart.css         # Cart tables, summary cards, and order success
│           └── components.css   # Navbar, ProductCard, Toast, and Stepper styles
│
├── vercel.json                  # Single-Page Application rewrite rules for Vercel
├── README.md                    # Project documentation
└── .gitignore                   # Root gitignore
```

---

## 6. Environment Variables

### Backend (`backend/.env`)

| Variable | Description | Example |
| :--- | :--- | :--- |
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://postgres:postgres@localhost:5432/online_cart` |
| `JWT_SECRET_KEY` | Secret key for signing JWT tokens | `your_long_random_jwt_secret_key` |
| `JWT_ALGORITHM` | JWT signing algorithm | `HS256` |
| `JWT_EXPIRE_MINUTES` | Token lifetime in minutes | `60` |
| `SMTP_HOST` | SMTP server host | `smtp-relay.brevo.com` |
| `SMTP_PORT` | SMTP server port | `2525` / `587` |
| `SMTP_USER` | SMTP username or email | `your_smtp_login` |
| `SMTP_PASSWORD` | SMTP password / API master key | `your_smtp_key` |
| `SMTP_FROM` | Sender email address | `orders@yourdomain.com` |
| `ALLOWED_ORIGINS` | Comma-separated list of allowed CORS origins | `http://localhost:5173,https://your-app.vercel.app` |

### Frontend (`frontend/.env`)

| Variable | Description | Example |
| :--- | :--- | :--- |
| `VITE_API_URL` | Backend base URL for Axios calls | `http://localhost:8000` |

---

## 7. Local Setup & Execution

### Prerequisites
- Python 3.11+
- Node.js 18+ and npm
- PostgreSQL database instance

### Backend Setup

1. Navigate to the `backend` directory:
   ```bash
   cd backend
   ```

2. Create and activate a Python virtual environment:
   ```bash
   # Windows (PowerShell)
   python -m venv myenv
   .\myenv\Scripts\activate

   # macOS / Linux
   python3 -m venv myenv
   source myenv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment file:
   ```bash
   cp .env.example .env
   ```
   *Edit `.env` with your PostgreSQL connection URL and SMTP details.*

5. Run database migrations:
   ```bash
   alembic upgrade head
   ```

6. Seed the database with catalog products:
   ```bash
   python -m app.seed
   ```

7. Start the FastAPI development server:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

8. Verify backend:
   - Health Check: [http://localhost:8000/health](http://localhost:8000/health)
   - Interactive Swagger Docs: [http://localhost:8000/docs](http://localhost:8000/docs)
   - ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

### Frontend Setup

1. Open a second terminal and navigate to `frontend`:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Configure environment file:
   ```bash
   cp .env.example .env
   ```

4. Start the Vite development server:
   ```bash
   npm run dev
   ```

5. Open your browser:
   - Web App: [http://localhost:5173](http://localhost:5173)

---

## 8. API Endpoints Reference

| Method | Endpoint | Auth | Description |
| :--- | :--- | :--- | :--- |
| `GET` | `/health` | No | System health check |
| `POST` | `/auth/register` | No | Register a new user account with email validation |
| `POST` | `/auth/login` | No | Authenticate user and receive JWT access token |
| `GET` | `/auth/me` | Yes | Retrieve current authenticated user profile |
| `GET` | `/products` | Yes | List all catalog products with image URLs |
| `GET` | `/cart` | Yes | Retrieve user's cart and calculated grand total |
| `POST` | `/cart/items` | Yes | Add item or increment quantity (max 99) |
| `PATCH` | `/cart/items/{product_id}` | Yes | Update specific item quantity (1–99) |
| `DELETE`| `/cart/items/{product_id}` | Yes | Remove item from cart |
| `POST` | `/orders/submit` | Yes | Atomically place order, snapshot line items, clear cart & dispatch email |
| `GET` | `/smtp-test` | No | Diagnostic SMTP test endpoint for verification |

---

## 9. Deployment Guide

### Backend (Render)
1. Push repository to GitHub.
2. In Render, create a new **Web Service** connected to the repository.
3. Configure settings:
   - **Root Directory**: `backend`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Add environment variables: `DATABASE_URL`, `JWT_SECRET_KEY`, `ALLOWED_ORIGINS`, `SMTP_*`.

### Database (Render PostgreSQL / Supabase / Neon)
1. Provision a PostgreSQL instance.
2. Copy the connection URI into the backend `DATABASE_URL` environment variable.

### Frontend (Vercel)
1. Import the repository in Vercel.
2. Configure settings:
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
3. Add Environment Variable:
   - `VITE_API_URL`: Your deployed Render API URL (e.g. `https://your-backend.onrender.com`)

---

## 10. Catalog Products

| Product Name | Category | Unit Price | Image / Visual |
| :--- | :--- | :--- | :--- |
| **Wireless Mouse** | Accessories | Rs. 499.00 | Ergonomic wireless optical mouse |
| **USB Keyboard** | Accessories | Rs. 799.00 | Full-size desktop keyboard |
| **Laptop Stand** | Office | Rs. 1,200.00 | Aluminum adjustable laptop riser |
| **HD Webcam** | Peripherals | Rs. 1,899.00 | 1080p HD computer webcam |
| **Wireless Headphones** | Audio | Rs. 2,499.00 | Over-ear Bluetooth ANC headphones |
| **Power Bank** | Power | Rs. 1,299.00 | 10000mAh slim fast-charging battery |
| **Phone Stand** | Accessories | Rs. 299.00 | Desktop phone and tablet stand |
| **HDMI Cable** | Cables | Rs. 399.00 | High-speed 4K 60Hz braided cable |
| **Mouse Pad** | Accessories | Rs. 199.00 | Extended gaming desk mat |
| **Desk Lamp** | Lighting | Rs. 899.00 | Dimmable touch-control LED desk lamp |

---

## 11. What is Finished

- [x] Complete FastAPI backend with SQLAlchemy 2.0 and PostgreSQL integration.
- [x] Automated database migrations using Alembic with idempotent versioned scripts.
- [x] Secure JWT authentication with bcrypt hashing, lowercase normalization, and domain validation.
- [x] Strict user-isolated cart queries and mutation endpoints.
- [x] Atomic order submission with snapshot data persistence and cart clearing.
- [x] SMTP transactional email service with clean HTML receipts and plain-text fallback.
- [x] 10 seeded catalog items with real product photos and INR currency formatting.
- [x] React 18 frontend with React Router v6 and centralized Axios client.
- [x] Clean, small-business ecommerce design in pure CSS (no external UI libraries).
- [x] Dynamic cart count badge in navbar with live updates.
- [x] Responsive layout (desktop 4-col, tablet 2-col, mobile 1-col and mobile cart rows).
- [x] Non-blocking Toast notification system.
- [x] Single-Page Application routing configuration (`vercel.json`) for Vercel refresh resilience.
- [x] Production deployment configuration for Render and Vercel.

---

## 12. What I Would Improve Next

1. **Automated Test Suite**: Implement comprehensive unit and integration tests using `pytest` and `pytest-asyncio` for the backend, and Vitest + React Testing Library for frontend components.
2. **Background Task Queue**: Offload SMTP email delivery to Celery or ARQ backed by Redis for instantaneous API responses under heavy load.
3. **Payment Gateway Integration**: Integrate Razorpay or Stripe webhook verification for online payments.
4. **Order History Page**: Allow authenticated users to view a list of all their historical orders with timestamps and item breakdowns.
5. **Product Search & Sorting**: Add real-time text search and price sorting (low-to-high, high-to-low).
6. **Inventory & Stock Management**: Add quantity stock tracking on the `Product` table to prevent ordering out-of-stock products.
7. **Refresh Token Flow**: Implement HttpOnly refresh cookie rotation alongside short-lived access tokens.
