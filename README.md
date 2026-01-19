# E-Commerce Backend API

RESTful e-commerce backend API built with Django REST Framework featuring product catalog, cart management, order processing, Razorpay payment integration, and inventory management.

## 🚀 Features

- **User Authentication**: JWT-based authentication with access and refresh tokens
- **Product Management**: Complete CRUD operations with categories, search, and filtering
- **Shopping Cart**: Support for both authenticated and anonymous users
- **Order Processing**: Full order lifecycle from cart to delivery
- **Payment Integration**: Razorpay gateway integration with webhook support
- **Inventory Management**: Real-time stock tracking with race condition handling
- **Admin APIs**: Dashboard analytics and bulk operations

## 🛠️ Tech Stack

- **Backend**: Django 5.x, Django REST Framework
- **Database**: PostgreSQL
- **Cache**: Redis
- **Task Queue**: Celery
- **Payment**: Razorpay
- **Authentication**: JWT (Simple JWT)
- **Testing**: pytest, pytest-django

## 📊 Database Schema

![Database Schema](docs/database_schema.png)

### Models
- **User & Address**: Custom user model with shipping/billing addresses
- **Category & Product**: Nested categories with product catalog
- **Cart & CartItem**: Session-based and user-based shopping carts
- **Order & OrderItem**: Orders with price snapshots
- **Payment**: Razorpay payment tracking

## 🚦 API Endpoints

### Authentication
- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - User login
- `POST /api/auth/logout/` - User logout
- `POST /api/auth/token/refresh/` - Refresh access token

### Products
- `GET /api/products/` - List products (with pagination, search, filters)
- `GET /api/products/{id}/` - Product detail
- `POST /api/products/` - Create product (admin)
- `PUT /api/products/{id}/` - Update product (admin)
- `DELETE /api/products/{id}/` - Delete product (admin)

### Cart
- `GET /api/cart/` - Get cart contents
- `POST /api/cart/items/` - Add item to cart
- `PATCH /api/cart/items/{id}/` - Update cart item quantity
- `DELETE /api/cart/items/{id}/` - Remove item from cart

### Orders
- `POST /api/orders/` - Create order from cart
- `GET /api/orders/` - List user orders
- `GET /api/orders/{id}/` - Order detail
- `POST /api/orders/{id}/cancel/` - Cancel order

### Payments
- `POST /api/payments/initiate/` - Initiate payment
- `POST /api/payments/verify/` - Verify payment
- `POST /api/payments/webhook/` - Razorpay webhook

## 📦 Installation

### Prerequisites
- Python 3.10+
- PostgreSQL
- Redis

### Setup

1. **Clone repository**
```bash
git clone https://github.com/Saiful07/ecommerce-backend-api.git
cd ecommerce-backend-api
```

2. **Create virtual environment**
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Environment variables**

Create `.env` file in project root:
```env
SECRET_KEY=your-secret-key-here
DEBUG=True
DATABASE_URL=postgresql://user:password@localhost:5432/ecommerce_db
REDIS_URL=redis://localhost:6379/0
RAZORPAY_KEY_ID=your-razorpay-key-id
RAZORPAY_KEY_SECRET=your-razorpay-key-secret
```

5. **Database setup**
```bash
python manage.py migrate
python manage.py createsuperuser
```

6. **Run development server**
```bash
python manage.py runserver
```

7. **Run Celery worker** (separate terminal)
```bash
celery -A ecommerce_backend worker -l info
```

## 🧪 Testing
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=.

# Run specific test file
pytest tests/test_orders.py
```

## 📝 Development Progress

Track daily progress in [PROGRESS.md](PROGRESS.md)

## 🏗️ Project Structure
```
ecommerce-backend-api/
├── accounts/           # User authentication and profiles
├── products/           # Product catalog and categories
├── carts/             # Shopping cart management
├── orders/            # Order processing
├── payments/          # Payment gateway integration
├── ecommerce_backend/ # Project settings
├── docs/              # Documentation and diagrams
├── tests/             # Test suite
├── manage.py
├── requirements.txt
└── README.md
```

## 🔐 Security Features

- JWT token authentication
- Password hashing with Django's default hasher
- CSRF protection
- SQL injection prevention via ORM
- Rate limiting (planned)
- Input validation with DRF serializers

## 🎯 Roadmap

- [x] Database schema design
- [x] Models implementation
- [ ] Authentication APIs
- [ ] Product catalog APIs
- [ ] Cart management
- [ ] Order processing
- [ ] Payment integration
- [ ] Admin dashboard APIs
- [ ] API documentation (Swagger)
- [ ] Unit & integration tests
- [ ] Deployment

## 👤 Author

**Saiful Islam**
- GitHub: [@Saiful07](https://github.com/Saiful07)
- LinkedIn: [saifulislam07](https://linkedin.com/in/saifulislam07)
- Email: mdsaifults08@gmail.com

## 📄 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

Built as part of internship at The Developers Arena to demonstrate backend development skills with Django and REST APIs.