# Online Cart Web Application

A full-stack online shopping cart application built using **FastAPI, React, and PostgreSQL**.

Users can register, log in, browse products, add products to their cart, update quantities, and place orders.

---

## 🔗 Links & Test Account

Live app : https://online-cart-frontend.vercel.app/
GitHub : https://github.com/rikin0102/online-cart

### Test Login

Email: rikinbtech@gmail.com
Password: Rikin@123

You can also create a new account from the Website.

## 🔄 Website Flow

The application works in the following way:

Register / Login
↓
Browse Products
↓
Add Products to Cart
↓
Update / Remove Cart Items
↓
Review Cart & Total
↓
Place Order
↓
Save Order in Database
↓
Clear Cart
↓
Send Order Confirmation Email
↓
Order Success Page

### Order Flow

When the user places an order:

1. The order is saved in PostgreSQL.
2. Product name and price are saved with the order.
3. The user's cart is cleared.
4. An order confirmation email is sent.
5. The user is redirected to the order success page.

If the email cannot be sent, the order is still saved successfully and the user is shown a warning.

## 🛠️ Tech Stack

### Backend

- Python 3.11+
- FastAPI
- SQLAlchemy 2.0
- Alembic
- PostgreSQL
- Pydantic
- JWT Authentication
- bcrypt

### Frontend

- React 18
- Vite
- React Router
- Axios
- CSS

### Email

- SMTP
- Brevo

---

## 🗄️ Database

PostgreSQL is used to store the main application data.

Main tables:

Users
Products
Cart Items
Orders
Order Items

The cart is stored in the database, so items remain saved even after refreshing the page or logging in again.

Orders also store the product name and price at the time of purchase. This means an old order will still show the original price even if the product price changes later.

## 🔐 Authentication

The application uses:

- JWT tokens for user authentication
- bcrypt for password hashing
- Protected API routes
- User-based cart and order access

Each user's cart is linked to their account, so users cannot access another user's cart through the API.

## 📧 Order Confirmation Email

After an order is successfully placed, the backend sends an email containing the order details.

The email includes:

- Order reference
- Purchased products
- Quantity
- Unit price
- Total amount

The email is sent through **Brevo SMTP**.

# 📁 Project Structure

## Project Structure

```text
Online-Cart/
├── backend/
│   ├── alembic.ini
│   ├── alembic/
│   │   ├── env.py
│   │   └── versions/
│   │       ├── 0001_initial_schema.py
│   │       └── 0002_add_image_url_to_products.py
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── security.py
│   │   ├── deps.py
│   │   ├── email_service.py
│   │   ├── seed.py
│   │   └── routers/
│   │       ├── __init__.py
│   │       ├── auth.py
│   │       ├── products.py
│   │       ├── cart.py
│   │       └── orders.py
│   ├── requirements.txt
│   ├── .env.example
│   └── Procfile
│
├── frontend/
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   ├── vercel.json
│   ├── .env.example
│   ├── .gitignore
│   ├── public/
│   │   └── images/
│   │       └── products/
│   │           ├── wireless-mouse.jpg
│   │           ├── usb-keyboard.jpg
│   │           ├── laptop-stand.jpg
│   │           ├── hd-webcam.jpg
│   │           ├── phone-stand.jpg
│   │           ├── hdmi-cable.jpg
│   │           ├── mouse-pad.jpg
│   │           └── desk-lamp.jpg
│   └── src/
│       ├── main.jsx
│       ├── App.jsx
│       ├── api/
│       │   ├── client.js
│       │   ├── auth.js
│       │   ├── products.js
│       │   ├── cart.js
│       │   └── errorHandler.js
│       ├── context/
│       │   └── AuthContext.jsx
│       ├── utils/
│       │   └── productImages.js
│       ├── components/
│       │   ├── Navbar.jsx
│       │   ├── ProductCard.jsx
│       │   ├── CartItemRow.jsx
│       │   ├── Toast.jsx
│       │   └── ProtectedRoute.jsx
│       ├── pages/
│       │   ├── Login.jsx
│       │   ├── Register.jsx
│       │   ├── Dashboard.jsx
│       │   ├── Cart.jsx
│       │   └── OrderSuccess.jsx
│       └── styles/
│           ├── global.css
│           ├── auth.css
│           ├── dashboard.css
│           ├── cart.css
│           └── components.css
│
├── README.md
└── .gitignore
```

### Backend File Purpose

| File / Folder         | Purpose                                     |
| --------------------- | ------------------------------------------- |
| `main.py`             | FastAPI application entry point             |
| `config.py`           | Environment and application settings        |
| `database.py`         | PostgreSQL database connection              |
| `models.py`           | SQLAlchemy database models                  |
| `schemas.py`          | Request and response validation             |
| `security.py`         | Password hashing and JWT authentication     |
| `deps.py`             | Authentication dependencies                 |
| `email_service.py`    | Order confirmation email service            |
| `seed.py`             | Adds sample products to the database        |
| `routers/auth.py`     | Registration, login and user authentication |
| `routers/products.py` | Product APIs                                |
| `routers/cart.py`     | Cart management APIs                        |
| `routers/orders.py`   | Order submission API                        |
| `alembic/`            | Database migrations                         |

### Frontend File Purpose

| File / Folder        | Purpose                               |
| -------------------- | ------------------------------------- |
| `main.jsx`           | React application entry point         |
| `App.jsx`            | Application routes and layout         |
| `api/`               | Backend API communication using Axios |
| `AuthContext.jsx`    | Global authentication state           |
| `components/`        | Reusable UI components                |
| `pages/`             | Application screens                   |
| `styles/`            | CSS files for application styling     |
| `public/images/`     | Product images                        |
| `ProtectedRoute.jsx` | Restricts pages to logged-in users    |

# API Endpoints

| Method   | Endpoint                   | Auth | Purpose               |
| -------- | -------------------------- | ---- | --------------------- |
| `GET`    | `/health`                  | No   | Check backend status  |
| `POST`   | `/auth/register`           | No   | Create an account     |
| `POST`   | `/auth/login`              | No   | Login and receive JWT |
| `GET`    | `/auth/me`                 | Yes  | Get logged-in user    |
| `GET`    | `/products`                | Yes  | Get products          |
| `GET`    | `/cart`                    | Yes  | Get user's cart       |
| `POST`   | `/cart/items`              | Yes  | Add product to cart   |
| `PATCH`  | `/cart/items/{product_id}` | Yes  | Update quantity       |
| `DELETE` | `/cart/items/{product_id}` | Yes  | Remove product        |
| `POST`   | `/orders/submit`           | Yes  | Place an order        |

API documentation is available through FastAPI Swagger:

http://localhost:8000/docs

# ⚙️ Environment Variables

## Backend

Create `backend/.env`:

DATABASE_URL=your_postgresql_database_url
JWT_SECRET_KEY=your_secret_key
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=60

SMTP_HOST=smtp-relay.brevo.com
SMTP_PORT=587
SMTP_USER=your_smtp_user
SMTP_PASSWORD=your_smtp_password
SMTP_FROM=your_sender_email

ALLOWED_ORIGINS=http://localhost:5173

# 💻 Run Locally

## Backend

```bash
cd backend
```

Create a virtual environment:

### Windows

```bash
py -3.12 -m venv venv
venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create `.env` from `.env.example` and add your database and SMTP details.

Run migrations:

```bash
alembic upgrade head
```

Add sample products:

```bash
python -m app.seed
```

Start the backend:

```bash
uvicorn app.main:app --reload --port 8000
```

Backend:

```text
http://localhost:8000
```

Swagger:

```text
http://localhost:8000/docs
```

---

## Frontend

Open another terminal:

```bash
cd frontend
npm install
npm run dev
```

Frontend:

```text
http://localhost:5173
```

Make sure `VITE_API_URL` points to the backend.

---

# 🚀 Flow of project

                 ┌──────────────┐
                 │ React + Vite │   │
                 └──────┬───────┘
                        │
                     REST API
                        │
                 ┌──────▼───────┐
                 │    FastAPI   │    │
                 └──────┬───────┘
                        │
                 ┌──────▼───────┐
                 │  PostgreSQL  │
                 └──────────────┘

# 🔮 What I Would Improve Next

1. **Authentication Improvements**  
   Add forgot-password functionality with a secure email reset link and OTP verification for email/phone during registration.

2. **Order History**
   Add a page where users can view their previous orders and order details.

3. **Product Search & Sorting**
   Add search, price sorting, and more product filters.

4. **Inventory Management**
   Track product stock and prevent users from ordering unavailable products.

5. **Payment Integration**
   Add a payment gateway such as Razorpay or Stripe with proper webhook verification.
