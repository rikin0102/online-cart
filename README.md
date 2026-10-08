# Online Cart Web Application

A full-stack, production-ready online shopping cart web application built with **FastAPI**, **SQLAlchemy 2.0**, **PostgreSQL**, **React 18**, and **Vite**.

---

## 1. Overview

Online Cart is an authenticated ecommerce shopping platform designed to provide a secure and robust shopping experience. The backend acts as the single source of truth for all business-critical operations including pricing, inventory calculations, cart isolation, and atomic order placements.

### Primary User Flow

```text
Register
   ↓
Login
   ↓
Product Dashboard (Catalog Grid)
   ↓
Add Products to Cart / Stepper Quantity
   ↓
View Cart (Responsive Table / Stacked Mobile View)
   ↓
Place Order (Atomic Transaction + Snapshot Retention)
   ↓
Clear Cart & Dispatch Order Confirmation Email (SMTP STARTTLS)
   ↓
Order Success Page (Line Totals, Snapshots & Email Status)
```

---

## 2. Features

- **JWT Authentication & Authorization**: Secure password hashing with bcrypt, stateless token issuance, and authenticated route protection.
- **Strict User Cart Scoping**: Every cart operation is strictly scoped to the authenticated user's JWT `sub` ID. User A cannot access, modify, or delete User B's cart.
- **Accurate Financial Calculations**: Exact monetary computations using Python `Decimal` and SQL `Numeric(10, 2)`—eliminating binary floating-point inaccuracies.
- **Atomic Order Submission**: Database transactions guarantee that Order creation, OrderItem snapshot recording, and Cart clearing succeed together or roll back completely.
- **Snapshot Data Integrity**: Historical orders store snapshots of product names and prices at time of purchase, preserving data integrity even if catalog prices change later.
- **Resilient SMTP Email Service**: Sends HTML and plain-text fallback order bills via SMTP STARTTLS with a 10-second timeout. If the email fails, the transaction is not rolled back, and the client receives the order receipt with an informative warning banner.
- **Clean Responsive UI**: Designed with clean small-business aesthetic (Inter typography, #FFFFFF bg, #F5F6F8 sections, #1D4ED8 primary, 8px spacing system, responsive 4/2/1 column grid).

---

## 3. Tech Stack

### Backend
- **Python 3.11+**: Modern typed backend runtime.
- **FastAPI**: High-performance asynchronous web framework with automatic OpenAPI documentation.
- **SQLAlchemy 2.0**: Declarative ORM with explicit transactional integrity and relationship mapping.
- **Pydantic v2**: Strict schema validation and data sanitization (email normalization, length bounds).
- **psycopg2-binary**: PostgreSQL database adapter.
- **python-jose & passlib[bcrypt]**: JWT generation, decoding, and bcrypt password hashing.
- **smtplib**: Standard library SMTP client for STARTTLS transactional email dispatch.

### Frontend
- **React 18**: Component-based user interface.
- **Vite**: Ultra-fast build tool and development server.
- **React Router v6**: Declarative client-side routing with protected route guards.
- **Axios**: Centralized HTTP client configured with request/response interceptors for token attachment and 401 handling.
- **Plain CSS**: Clean, modular styling without heavy external CSS frameworks.

### Database
- **PostgreSQL**: Enterprise-grade relational database.

---

## 4. Why PostgreSQL?

1. **Relational Data Integrity**: Strict foreign key constraints (`ON DELETE CASCADE`) maintain relationships between Users, CartItems, Orders, and OrderItems.
2. **ACID Transactions**: Enables atomic order submission where order persistence and cart purging succeed as a single atomic unit.
3. **Exact Numeric Type (`Numeric(10, 2)`)**: Prevents IEEE 754 floating-point rounding errors in currency and financial totals.
4. **Unique Constraints**: Guarantees uniqueness for user emails and `(user_id, product_id)` cart entries at the database level.
5. **High Concurrency & Indexing**: B-tree indexing on `email`, `user_id`, and `product_id` ensures fast lookups under load.

---

## 5. Project Structure

```text
Online-Cart/
│
├── backend/
│   ├── app/
│   │   ├── __init__.py          # Package initialization
│   │   ├── main.py              # FastAPI application entry point & CORS configuration
│   │   ├── config.py            # Pydantic Settings & environment variable loader
│   │   ├── database.py          # SQLAlchemy engine, SessionLocal, and DB dependencies
│   │   ├── models.py            # SQLAlchemy models (User, Product, CartItem, Order, OrderItem)
│   │   ├── schemas.py           # Pydantic models for request/response validation
│   │   ├── security.py          # Password hashing and JWT token logic
│   │   ├── deps.py              # FastAPI authentication dependencies (get_current_user)
│   │   ├── email_service.py     # SMTP STARTTLS email sender with fallback
│   │   ├── seed.py              # Idempotent catalog product seeder (10 items)
│   │   │
│   │   └── routers/
│   │       ├── __init__.py
│   │       ├── auth.py          # /auth/register, /auth/login, /auth/me
│   │       ├── products.py      # /products
│   │       ├── cart.py          # /cart, /cart/items, /cart/items/{id}
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
│   └── src/
│       ├── main.jsx             # React entry point with providers
│       ├── App.jsx              # Route definitions and layout shell
│       │
│       ├── api/
│       │   └── client.js        # Centralized Axios instance with auth interceptors
│       │
│       ├── context/
│       │   └── AuthContext.jsx  # Global authentication and cart state management
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
| `SMTP_HOST` | SMTP server host | `smtp.gmail.com` |
| `SMTP_PORT` | SMTP server port | `587` |
| `SMTP_USER` | SMTP username or email | `your_email@gmail.com` |
| `SMTP_PASSWORD` | SMTP password or app-specific password | `your_app_password` |
| `SMTP_FROM` | Sender email address | `your_email@gmail.com` |
| `ALLOWED_ORIGINS` | Comma-separated list of allowed CORS origins | `http://localhost:5173` |

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
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # macOS / Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create configuration file:
   ```bash
   cp .env.example .env
   ```
   *Edit `.env` with your PostgreSQL database credentials and SMTP details.*

5. Seed the database with catalog products:
   ```bash
   python -m app.seed
   ```

6. Start the FastAPI development server:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

7. Verify backend:
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

3. Create environment configuration:
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
| `POST` | `/auth/register` | No | Register a new user account |
| `POST` | `/auth/login` | No | Authenticate user and receive JWT |
| `GET` | `/auth/me` | Yes | Retrieve current user profile |
| `GET` | `/products` | Yes | List all catalog products |
| `GET` | `/cart` | Yes | Retrieve user's cart and calculated grand total |
| `POST` | `/cart/items` | Yes | Add item or increment quantity (max 99) |
| `PATCH` | `/cart/items/{product_id}` | Yes | Update specific item quantity (1–99) |
| `DELETE`| `/cart/items/{product_id}` | Yes | Remove item from cart |
| `POST` | `/orders/submit` | Yes | Atomically place order, clear cart & dispatch email |

---

## 9. Deployment Guide

### Backend (Render / Railway / Heroku)
1. Push repository to GitHub.
2. Create a new **Web Service** pointing to the `backend/` directory.
3. Set environment to **Python 3.11+**.
4. Build Command: `pip install -r requirements.txt`
5. Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
6. Add environment variables: `DATABASE_URL`, `JWT_SECRET_KEY`, `ALLOWED_ORIGINS`, `SMTP_*`.

### Database (Render PostgreSQL / Supabase / Neon)
1. Provision a PostgreSQL instance.
2. Copy the external connection URI into `DATABASE_URL`.

### Frontend (Vercel / Netlify)
1. Import repository and set root directory to `frontend/`.
2. Build Command: `npm run build`
3. Output Directory: `dist`
4. Set Environment Variable: `VITE_API_URL=https://your-backend-api.onrender.com`

---

## 10. Screenshots

| Screen | Description |
| :--- | :--- |
| **Login & Register** | *Clean card-based authentication with live validation* |
| **Product Dashboard** | *4-column responsive grid with category filters and quantity steppers* |
| **Cart View** | *Full table breakdown with line totals and real-time total recalculations* |
| **Order Confirmation** | *Complete breakdown of purchased snapshots and SMTP status banner* |

*(Place screenshot images in `docs/screenshots/`)*

---

## 11. What is Finished

- [x] Complete FastAPI backend with SQLAlchemy 2.0 and PostgreSQL integration.
- [x] Secure JWT authentication with bcrypt hashing and lowercase email normalization.
- [x] Strict user-isolated cart queries and mutation endpoints.
- [x] Atomic order submission with snapshot data persistence and cart clearing.
- [x] SMTP email service with STARTTLS, HTML templates, plain-text fallback, and non-blocking failure tolerance.
- [x] 10 realistic seeded catalog items priced in Indian Rupees (idempotent seeder).
- [x] React 18 frontend with React Router v6 and centralized Axios client.
- [x] Clean, small-business ecommerce design in pure CSS (no component libraries).
- [x] Dynamic cart count badge in navbar with live updates.
- [x] Responsive layout (desktop 4-col, tablet 2-col, mobile 1-col and mobile cart rows).
- [x] Non-blocking Toast notification system.
- [x] Complete production deployment configuration (Procfile, .env templates, .gitignore).

---

## 12. What I Would Improve Next

1. **Automated Test Suite**: Implement comprehensive unit and integration tests using `pytest` and `pytest-asyncio` for the backend, and Vitest + React Testing Library for frontend components.
2. **Background Task Queue**: Offload SMTP email delivery to Celery or ARQ backed by Redis to achieve sub-millisecond API response times.
3. **Payment Gateway Integration**: Integrate Razorpay or Stripe webhook verification for online payments.
4. **Order History Page**: Allow authenticated users to view a list of all their historical orders with timestamps and item breakdowns.
5. **Product Search & Sorting**: Add real-time text search and price sorting (low-to-high, high-to-low).
6. **Inventory & Stock Management**: Add quantity stock tracking on the `Product` table to prevent ordering out-of-stock products.
7. **Refresh Token Flow**: Implement HttpOnly refresh cookie rotation alongside short-lived access tokens.

---

## 13. Git Commit Plan

```text
1. Initialize Online Cart project structure and root configuration
2. Set up FastAPI backend architecture with Pydantic settings
3. Configure PostgreSQL database connection and declarative models
4. Implement JWT authentication and bcrypt password hashing
5. Create catalog products API with idempotent seed script
6. Implement user-isolated cart endpoints with Decimal calculations
7. Add atomic order processing and snapshot retention
8. Implement resilient SMTP email service with HTML and fallback
9. Set up React 18 frontend with Vite and React Router
10. Build centralized Axios client and AuthContext provider
11. Implement responsive Navbar, Toast notification, and ProtectedRoute
12. Build authentication UI for Login and Register pages
13. Create responsive product dashboard with category filters
14. Implement shopping cart page with desktop table and mobile view
15. Build order success receipt page with email status reporting
16. Add comprehensive documentation and deployment configuration
```
