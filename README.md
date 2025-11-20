# 🛒 Online Auction & E-Commerce Shopping System

Lightweight online auction and e-commerce web application built with Django. Users can browse products, place bids in auctions, add items to a cart, and checkout. Admins can manage products, listings, and users via the Django admin.

**This repository contains a complete Django project with apps such as** `auctions`, `catalog`, `cart`, `orders`, `accounts`, and `core`.

**Key features**
- User registration, login, and account management
- Product catalog with categories and detail pages
- Auction listings with bidding and expiration handling
- Shopping cart and checkout flow
- Admin site for managing products/listings/users

**Tech stack (local development)**
- Backend: Django (Python)
- Database: SQLite (file: `db.sqlite3`) — suitable for development
- Frontend: HTML, CSS, Bootstrap
- Dependencies: see `requirements.txt`

---

## Quickstart (development)
These commands assume a Bash shell on Linux/macOS.

1. Clone and enter the repo

```bash
git clone https://github.com/Dinath2002/auction_shop.git
cd auction_shop
```

2. Create and activate a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

3. Install Python dependencies

```bash
pip install -r requirements.txt
```

4. Apply migrations and create a superuser

```bash
python manage.py migrate
python manage.py createsuperuser
```

5. (Optional) Seed demo data

```bash
python manage.py seed
```

6. Run the development server

```bash
python manage.py runserver
```

Open `http://127.0.0.1:8000/` in your browser.

Note: If you see "Couldn't import Django" when running `manage.py`, activate your virtualenv and install dependencies (`pip install -r requirements.txt`).

---

## Management commands & useful tasks
- Run periodic cleanup: `python manage.py close_expired_listings` (closes auctions past their expiration)
- Seed sample data: `python manage.py seed` (provided in `core/management/commands/seed.py`)
- Run tests: `python manage.py test`

## Project layout (high level)
- `auctions/` — auction listing logic, templates, and management commands
- `catalog/` — product listing and detail views
- `cart/` — shopping cart models and views
- `orders/` — checkout and order models
- `accounts/` — authentication templates and views
- `core/` — site-wide templates and utilities
- `config/` — project settings, URLs, WSGI/ASGI

---

## Development notes
- Database: this project ships with `SQLite` for ease of development (file `db.sqlite3`). For production, switch `DATABASES` in `config/settings.py` and update `requirements.txt` accordingly.
- Static files: during development `runserver` serves static files. For production, collect static files with `python manage.py collectstatic` and serve them with your web server / CDN.
- Media: product images are stored under `media/` — ensure your webserver serves that directory in production.

## Contributing
- Fork the repo, create a feature branch, add tests for new behavior, and open a pull request.

## License
This repository does not include an explicit license file. Add `LICENSE` if you want to define reuse terms.

---

If you'd like, I can also:
- add a `CONTRIBUTING.md` with development and PR guidelines
- add a simple `Makefile` or `scripts/` for common tasks (`venv`, `run`, `test`)
## ⚙️ Setup
```bash
git clone https://github.com/Dinath2002/auction_shop.git
cd auction_shop
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
