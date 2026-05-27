# Sales Planning

Scalable ERP-style master management module built with Django, Django REST Framework, PostgreSQL, and Bootstrap 5.

## Features

- **Multi-role parties**: One business partner can be Vendor, Customer, Broker, Transporter, or Manufacturer
- **Normalized ERP architecture**: Party → PartyRole → role-specific profiles
- **Rich master data**: Commercial, statutory, bank, contacts, documents, trucks, drivers
- **Tabbed ERP UI**: Bootstrap 5 interface with dynamic inline formsets
- **REST API**: ViewSets with nested serializers, pagination, filtering, and search
- **Validations**: GST, PAN, IFSC, phone, Aadhar, duplicate account/truck checks
- **Admin panel**: Full Django admin with inlines and optimized list views

## Project Structure

```
ritik-sales/
├── config/                 # Django project settings
├── apps/
│   ├── core/               # Abstract base models
│   ├── accounts/           # Auth & dashboard redirect
│   ├── masters/            # Lookup masters & choices
│   ├── parties/            # Party, roles, shared profiles
│   ├── vendors/            # VendorProfile
│   ├── transporters/       # TransporterProfile & truck driver UI
│   ├── logistics/          # Truck, TruckDriver
│   ├── common/             # Validators, mixins, services
│   └── api/                # DRF ViewSets & serializers
├── templates/
├── static/
├── media/
└── requirements/
```

## Quick Start

### 1. Start PostgreSQL

```bash
docker compose up -d
```

### 2. Create virtual environment & install dependencies

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements/requirements.txt
```

### 3. Configure environment

```bash
copy .env.example .env
```

### 4. Run migrations & seed data

```bash
python manage.py migrate
python manage.py seed_erp_data
.\run_dev.ps1
```

> **Port:** `python manage.py runserver` now defaults to **8004** (set `DEV_PORT` in `.env` to change).
>
> **Windows tip:** Use `.\run_dev.ps1` for request logs in the terminal (`[WEB]` / `[API]` tags).

### 5. Access the application (port **8004**)

| URL | Description |
|-----|-------------|
| http://127.0.0.1:8004/ | Login (admin / admin123 after seed) |
| http://127.0.0.1:8004/parties/ | Business Partner list |
| http://127.0.0.1:8004/parties/create/ | Create new partner |
| http://127.0.0.1:8004/admin/ | Django Admin |
| http://127.0.0.1:8004/api/v1/ | REST API root |

**Run the app (one command):** `.\start.ps1` — migrate, seed, and start on port 8004.

**First-time only** (no venv yet): `.\setup.ps1` is optional; `.\start.ps1` creates the venv automatically.

**Create partner:** Name is required. Phone and Mobile are optional.

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET/POST /api/v1/parties/` | List/create parties |
| `GET/PUT/PATCH/DELETE /api/v1/parties/{id}/` | Party detail |
| `GET/POST /api/v1/vendors/` | Vendor profiles |
| `GET/POST /api/v1/transporters/` | Transporter profiles |
| `GET/POST /api/v1/trucks/` | Trucks |
| `GET/POST /api/v1/drivers/` | Truck drivers |

**Query params**: `?search=`, `?role=`, `?is_active=`, `?ordering=`, `?page=`

## Architecture

```
Party
  └── PartyRole (Vendor | Customer | Broker | Transporter | Manufacturer)
        ├── CommercialProfile
        ├── StatutoryDetail
        ├── BankDetail (multiple)
        ├── ContactPerson (multiple)
        ├── PartyDocument (multiple)
        ├── VendorProfile
        ├── TransporterProfile
        │     └── Truck (multiple)
        │           └── TruckDriver (multiple)
        ├── BrokerProfile
        └── CustomerProfile
```

## Vendor masters (Admin)

Manage dynamic masters at http://127.0.0.1:8004/admin/:

| Master | Model | Notes |
|--------|--------|--------|
| Vendor Type | `VendorType` | Registered, Unregistered, etc. |
| Vendor Category | `VendorCategory` | Top-level category |
| Vendor Sub Category | `VendorSubCategory` | Linked to category |
| Office Status | — | **Static** dropdown: Active / Inactive only |

Seed default masters:

```bash
python manage.py seed_vendor_masters
```

## Development Notes

- Abstract models: `TimeStampedModel`, `SoftDeleteModel`, `AuditModel`, `BaseERPModel`
- Optimized querysets use `select_related` / `prefetch_related`
- Soft delete via `Party.soft_delete()` — sets `is_deleted=True`, `is_active=False`
- Role management UI: `/parties/{id}/roles/{role_id}/manage/`

## License

Proprietary — Sales Planning
