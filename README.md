# E-Commerce Backend API

RESTful e-commerce backend API built with Django REST Framework featuring product catalog, cart management, order processing, Razorpay payment integration, and inventory management.

## 🚀 Features

- **User Authentication**: JWT-based authentication with access and refresh tokens
- **Product Management**: Complete CRUD operations with categories, search, and filtering
- **Shopping Cart**: Support for both authenticated and anonymous users with session-based carts
- **Cart Migration**: Automatic cart merge on login/registration
- **Order Processing**: Full order lifecycle from cart to delivery with atomic transactions
- **Payment Integration**: Razorpay gateway integration with webhook support
- **Inventory Management**: Real-time stock tracking with race condition handling
- **Price Snapshots**: Historical price tracking in orders
- **Admin APIs**: Order management and product analytics

## 🛠️ Tech Stack

- **Backend**: Django 5.x, Django REST Framework
- **Database**: SQLite (Development) / PostgreSQL (Production)
- **Authentication**: JWT (djangorestframework-simplejwt)
- **Payment**: Razorpay Python SDK
- **Testing**: pytest, pytest-django

## 📊 Database Schema

![Database Schema](docs/database_schema.png)

### Models
- **User & Address**: Custom user model with shipping/billing addresses
- **Category & Product**: Nested categories with product catalog
- **Cart & CartItem**: Session-based and user-based shopping carts
- **Order & OrderItem**: Orders with price snapshots at purchase time
- **Payment**: Razorpay payment tracking with signature verification

## 🚦 API Endpoints

### Authentication (6 endpoints)
- `POST /api/auth/register/` - User registration with cart migration
- `POST /api/auth/login/` - User login with cart migration
- `POST /api/auth/logout/` - User logout with token blacklist
- `POST /api/auth/token/refresh/` - Refresh access token
- `GET /api/auth/profile/` - Get user profile
- `PATCH /api/auth/profile/` - Update user profile
- `POST /api/auth/change-password/` - Change password

### Categories (6 endpoints)
- `GET /api/categories/` - List root categories
- `GET /api/categories/all/` - List all categories (including nested)
- `GET /api/categories/{slug}/` - Category detail
- `POST /api/categories/` - Create category (admin only)
- `PUT /api/categories/{slug}/` - Update category (admin only)
- `DELETE /api/categories/{slug}/` - Delete category (admin only)

### Products (7 endpoints)
- `GET /api/products/` - List products (pagination, search, filters)
- `GET /api/products/{id}/` - Product detail
- `POST /api/products/` - Create product (admin only)
- `PUT /api/products/{id}/` - Update product (admin only)
- `DELETE /api/products/{id}/` - Delete product (admin only)
- `GET /api/products/featured/` - Get featured products (latest 10)
- `GET /api/products/low_stock/` - Get low stock products (admin only)

**Query Parameters for Product List:**
- `search` - Search in name/description
- `category` - Filter by category slug
- `min_price` - Minimum price filter
- `max_price` - Maximum price filter
- `in_stock` - Filter available items (true/false)
- `ordering` - Sort by price, created_at, name

### Cart (5 endpoints)
- `GET /api/cart/` - Get cart contents with totals
- `POST /api/cart/add/` - Add item to cart with stock validation
- `PATCH /api/cart/items/{id}/` - Update cart item quantity
- `DELETE /api/cart/items/{id}/` - Remove item from cart
- `DELETE /api/cart/clear/` - Clear entire cart

### Orders (5 endpoints)
- `POST /api/orders/create_order/` - Create order from cart (atomic)
- `GET /api/orders/` - List user orders (paginated)
- `GET /api/orders/{id}/` - Order detail with items
- `POST /api/orders/{id}/cancel/` - Cancel order and restore stock
- `PATCH /api/orders/{id}/update_status/` - Update order status (admin only)

### Payments (3 endpoints)
- `POST /api/payments/initiate/` - Initiate Razorpay payment
- `POST /api/payments/verify/` - Verify payment signature
- `POST /api/payments/webhook/` - Razorpay webhook handler

**Total: 31 API Endpoints**

## 📦 Installation

### Prerequisites
- Python 3.10+
- Git

### Setup

1. **Clone repository**
```bash
git clone https://github.com/Saiful07/ecommerce-backend-api.git
cd ecommerce-backend-api
```

2. **Create virtual environment**
```bash
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Mac/Linux:
source .venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure Razorpay keys**

Edit `ecommerce_backend/settings.py` and add your Razorpay test keys:
```python
RAZORPAY_KEY_ID = 'rzp_test_YOUR_KEY_ID'
RAZORPAY_KEY_SECRET = 'YOUR_KEY_SECRET'
```

Get test keys from: https://dashboard.razorpay.com/app/keys (Test Mode)

5. **Database setup**
```bash
python manage.py migrate
python manage.py createsuperuser
```

6. **Run development server**
```bash
python manage.py runserver
```

Server will start at: `http://127.0.0.1:8000`

## 🧪 Testing with Postman

### Quick Test Flow

1. **Register User**
```
POST http://127.0.0.1:8000/api/auth/register/
Body: {
  "username": "testuser",
  "email": "test@example.com",
  "password": "Test123!",
  "password2": "Test123!",
  "first_name": "Test",
  "last_name": "User",
  "phone": "1234567890"
}
```

2. **Login & Get Token**
```
POST http://127.0.0.1:8000/api/auth/login/
Body: {
  "username": "testuser",
  "password": "Test123!"
}
```
Save the `access` token for authenticated requests.

3. **Create Category (Admin)**
```
POST http://127.0.0.1:8000/api/categories/
Headers: Authorization: Bearer YOUR_ADMIN_TOKEN
Body: {
  "name": "Electronics",
  "description": "Electronic devices"
}
```

4. **Create Product (Admin)**
```
POST http://127.0.0.1:8000/api/products/
Headers: Authorization: Bearer YOUR_ADMIN_TOKEN
Body: {
  "name": "iPhone 15",
  "description": "Latest iPhone",
  "price": 99999.00,
  "stock": 50,
  "category": 1
}
```

5. **Add to Cart**
```
POST http://127.0.0.1:8000/api/cart/add/
Headers: Authorization: Bearer YOUR_TOKEN
Body: {
  "product_id": 1,
  "quantity": 2
}
```

6. **Create Order**
```
POST http://127.0.0.1:8000/api/orders/create_order/
Headers: Authorization: Bearer YOUR_TOKEN
Body: {
  "shipping_address": "123 Main St, City, State, 12345, Country"
}
```

7. **Initiate Payment**
```
POST http://127.0.0.1:8000/api/payments/initiate/
Headers: Authorization: Bearer YOUR_TOKEN
Body: {
  "order_id": 1
}
```

## 📝 Development Progress

Detailed daily progress tracking: [PROGRESS.md](PROGRESS.md)

**Current Status: 77.5% Complete**
- ✅ Authentication System
- ✅ Product Catalog with Search & Filtering
- ✅ Shopping Cart with Session Support
- ✅ Order Management
- ✅ Payment Integration (Razorpay)
- ⏳ Admin Analytics APIs
- ⏳ Testing Suite
- ⏳ Deployment

## 🏗️ Project Structure
```
ecommerce-backend-api/
├── accounts/              # User authentication & profiles
│   ├── models.py         # User, Address models
│   ├── serializers.py    # User serializers
│   ├── views.py          # Auth views with cart migration
│   └── urls.py
├── products/             # Product catalog
│   ├── models.py         # Category, Product models
│   ├── serializers.py    # Product serializers
│   ├── views.py          # Product CRUD with filtering
│   └── urls.py
├── carts/                # Shopping cart
│   ├── models.py         # Cart, CartItem models
│   ├── serializers.py    # Cart serializers
│   ├── views.py          # Cart operations
│   └── urls.py
├── orders/               # Order processing
│   ├── models.py         # Order, OrderItem models
│   ├── serializers.py    # Order serializers
│   ├── views.py          # Order creation with atomic transactions
│   └── urls.py
├── payments/             # Payment gateway
│   ├── models.py         # Payment model
│   ├── serializers.py    # Payment serializers
│   ├── views.py          # Razorpay integration
│   └── urls.py
├── ecommerce_backend/    # Project settings
│   ├── settings.py       # Django settings
│   └── urls.py           # Main URL configuration
├── docs/                 # Documentation
│   └── database_schema.png
├── manage.py
├── requirements.txt
├── PROGRESS.md           # Daily progress tracking
└── README.md
```

## 🔐 Security Features

- **JWT Authentication**: Secure token-based auth with refresh tokens
- **Token Blacklisting**: Logged out tokens are invalidated
- **Password Hashing**: Django's PBKDF2 algorithm
- **CSRF Protection**: Built-in Django CSRF middleware
- **SQL Injection Prevention**: Django ORM parameterized queries
- **Input Validation**: DRF serializer validation
- **Permission Classes**: Role-based access control (user/admin)
- **Atomic Transactions**: Data consistency for critical operations
- **Payment Signature Verification**: HMAC-SHA256 signature validation

## 🎯 Key Technical Features

### Atomic Transactions
- Order creation with stock deduction
- Cart migration on login
- Order cancellation with stock restoration

### Race Condition Handling
- `select_for_update()` for row-level locking
- Prevents overselling during concurrent orders

### Price Snapshot Pattern
- Stores product price at time of purchase
- Historical price accuracy for orders

### Session-Based Cart
- Works for anonymous users
- Automatically migrates to user account on login

### Query Optimization
- `select_related()` for foreign key optimization
- `prefetch_related()` for reverse relations
- Database indexes on frequently queried fields

## 🎯 Roadmap

- [x] Database schema design
- [x] Models implementation
- [x] Authentication APIs
- [x] Product catalog APIs
- [x] Cart management
- [x] Order processing
- [x] Payment integration
- [ ] Admin dashboard APIs
- [ ] API documentation (Swagger)
- [ ] Unit & integration tests
- [ ] Deployment to cloud platform

## 👤 Author

**Saiful Islam**
- GitHub: [@Saiful07](https://github.com/Saiful07)
- LinkedIn: [saifulislam07](https://linkedin.com/in/saifulislam07)
- Email: mdsaifults08@gmail.com
- Portfolio: [saifuldz.netlify.app](https://saifuldz.netlify.app)

## 📄 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

Built as part of internship at **The Developers Arena** (Jan 2026 - Present) to demonstrate backend development skills with Django REST Framework and e-commerce system architecture.

## 📧 Contact

For questions or collaboration opportunities, reach out via:
- Email: mdsaifults08@gmail.com
- LinkedIn: [saifulislam07](https://linkedin.com/in/saifulislam07)