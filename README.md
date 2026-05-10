# Fruity Flicks Invoice & Receipt Manager

A web-based invoice and receipt **management system** for **Fruity Flicks**, a fruit distribution company based in Dansoman, Accra. Built with Flask and MongoDB; PDFs are rendered server-side with WeasyPrint. Installable as a Progressive Web App on phones and desktops.

## Features

- **Dashboard** — Landing page lists every issued invoice and receipt with summary cards (counts, GHS totals), client-side search, and per-row actions.
- **Per-row actions** — From the dashboard, each saved doc supports: **View** (read-only HTML render), **PDF** (re-download the original PDF), **Duplicate** (open the create form pre-filled), **Delete** (confirm-prompted).
- **Invoice creation** — Fill in client details and add multiple line items with descriptions, quantities, and unit prices (GHS).
- **Receipt creation** — Issue paid-receipts with payment date, payment method (Cash / Bank Transfer / Mobile Money), reference / transaction ID, and amount paid. Outstanding balance is computed automatically; a green **PAID** stamp is added when the balance hits zero.
- **Auto-calculations** — Row amounts, subtotal, total, balance, and amount in words update live in the browser.
- **Save & Download** — Submitting the form persists the document to MongoDB and returns a freshly rendered PDF in the same response.
- **Single-page A4 PDF** — Server-rendered PDF that auto-fits everything onto a single A4 page no matter how many line items the document has.
- **Installable PWA** — A web app manifest and service worker make the dashboard installable on iOS/Android home screens and as a desktop app, with the company logo as the launcher icon.
- **Resilient dashboard** — Friendly error banner if MongoDB is unreachable; missing/None fields on legacy records won't break the page.

## Tech Stack

- **Backend:** Python / Flask
- **Database:** MongoDB Atlas (via PyMongo)
- **Frontend:** HTML, CSS, vanilla JavaScript (calculations, search, service-worker)
- **PDF generation:** WeasyPrint (server-side, HTML/CSS to PDF)
- **PWA:** Web App Manifest + Service Worker
- **Production server:** Gunicorn

## Project Structure

```
.
├── app.py                       # Flask app, routes, shared helpers, PDF generation
├── requirements.txt
├── .env                         # MongoDB URI (gitignored)
├── .gitignore
├── README.md
├── templates/
│   ├── dashboard.html           # Management dashboard (landing page)
│   ├── index.html               # Editable invoice form
│   ├── invoice_pdf.html         # Server-rendered template used for the invoice PDF
│   ├── receipt.html             # Editable receipt form
│   └── receipt_pdf.html         # Server-rendered template used for the receipt PDF
└── static/
    ├── css/style.css            # Form + dashboard styling
    ├── img/
    │   ├── logo.jpg             # Company logo
    │   ├── icon-192.png         # PWA icon (192x192)
    │   ├── icon-512.png         # PWA icon (512x512)
    │   └── apple-touch-icon.png # iOS home-screen icon (180x180)
    ├── manifest.json            # PWA manifest
    ├── service-worker.js        # PWA service worker (cache-first for assets)
    └── main.js                  # Row math, add/remove, clear form (shared)
```

## Routes

### Pages

| Method | Path                            | Purpose                                                |
|--------|---------------------------------|--------------------------------------------------------|
| GET    | `/`                             | **Dashboard** (landing page) — lists everything saved  |
| GET    | `/dashboard`                    | Dashboard (same view as `/`)                           |
| GET    | `/invoice`                      | Renders the invoice form                               |
| GET    | `/invoice?duplicate=<id>`       | Invoice form pre-filled from an existing record        |
| POST   | `/invoice`                      | Saves invoice to MongoDB, returns PDF as download      |
| GET    | `/receipt`                      | Renders the receipt form                               |
| GET    | `/receipt?duplicate=<id>`       | Receipt form pre-filled from an existing record        |
| POST   | `/receipt`                      | Saves receipt to MongoDB, returns PDF as download      |

### Doc-specific actions

| Method | Path                            | Purpose                                                |
|--------|---------------------------------|--------------------------------------------------------|
| GET    | `/invoice/<id>`                 | Read-only HTML render of a saved invoice               |
| GET    | `/invoice/<id>/pdf`             | Re-download the saved invoice as PDF                   |
| POST   | `/invoice/<id>/delete`          | Delete invoice (with confirm prompt in UI)             |
| GET    | `/receipt/<id>`                 | Read-only HTML render of a saved receipt               |
| GET    | `/receipt/<id>/pdf`             | Re-download the saved receipt as PDF                   |
| POST   | `/receipt/<id>/delete`          | Delete receipt                                         |

### PWA / static

| Method | Path                            | Purpose                                                |
|--------|---------------------------------|--------------------------------------------------------|
| GET    | `/service-worker.js`            | Service worker (served from root scope)                |
| GET    | `/static/manifest.json`         | PWA manifest                                           |

## Setup

### Prerequisites

- Python 3.10+
- A MongoDB Atlas cluster (or local MongoDB instance)
- WeasyPrint system dependencies (Pango, Cairo, GDK-PixBuf). On Debian/Ubuntu:
  ```bash
  sudo apt install libpango-1.0-0 libpangoft2-1.0-0
  ```
  See https://doc.courtbouillon.org/weasyprint/stable/first_steps.html for other platforms.

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/sakibumumuni/FruityFlicksInvoiceGenerator.git
   cd FruityFlicksInvoiceGenerator
   ```

2. Create and activate a virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the project root:
   ```
   mongodb_uri=mongodb+srv://<username>:<password>@<cluster>.mongodb.net/?appName=<appName>
   ```

5. Run the application:
   ```bash
   python app.py
   ```

6. Open `http://localhost:5000/` in your browser — the dashboard is the landing page.

## Usage

### Dashboard

Open `/` (or `/dashboard`). Two summary cards show the count and total GHS for issued invoices and receipts. Two tables list the records, newest first. Use the search box to filter both tables by document number or client name. Each row has:

- **View** — opens the saved doc as a read-only HTML render in a new tab
- **PDF** — re-downloads the original PDF
- **Duplicate** — opens the create form with all fields pre-filled (number cleared, ready for a new one)
- **Delete** — confirm-prompted, removes the record from MongoDB

### Issuing an invoice

1. From the dashboard click **+ New Invoice** (or open `/invoice`).
2. Fill in **invoice number**, **client name**, **address**, **contact person**, and **delivery date**.
3. Add line items with the **+ Add Item** button — enter description, quantity, and unit price.
4. Totals and amount-in-words update as you type.
5. Click **Save & Download** — the form POSTs to `/invoice`; the server saves the record to MongoDB and streams back a PDF download (`FruityFlicks_Invoice_<number>.pdf`).

### Issuing a receipt

1. From the dashboard click **+ New Receipt**, or from the invoice form click **→ Switch to Receipt**.
2. Fill in **receipt number**, the client fields, and the **payment details**: payment date, payment method, reference / transaction ID.
3. Add line items the same way.
4. Enter the **Amount Paid** — the balance and amount-in-words recompute live.
5. Click **Save & Download** — the server saves the receipt to MongoDB and returns the PDF (`FruityFlicks_Receipt_<number>.pdf`). When the balance is zero, the PDF includes a green **PAID** stamp.

If the database is unreachable, PDF generation still succeeds — the save failure is logged but the user still gets their document. The dashboard will show an error banner if it cannot read records.

### Installing as an app (PWA)

The deployed site is installable as a standalone app with the Fruity Flicks logo on your home screen / app drawer / dock.

- **Android (Chrome / Edge)** — open the dashboard, then three-dot menu → **Install app**.
- **iOS / iPadOS (Safari)** — open the dashboard, tap **Share** → **Add to Home Screen**.
- **Desktop (Chrome / Edge)** — click the install icon (⊕) in the address bar, or three-dot menu → **Install Fruity Flicks**.

Service workers require HTTPS — the deployed Render URL is HTTPS by default; locally you can install over `localhost`.

## MongoDB Document Structure

Invoices live in the `invoices.invoices` collection, receipts in `invoices.receipts`.

### Invoice

```json
{
  "_id": "ObjectId(…)",
  "invoice_number": "FF-001",
  "client_name": "Acme Ltd",
  "client_address": "123 Main St, Accra",
  "contact_person": "John Doe",
  "delivery_date": "2026-03-27",
  "items": [
    { "description": "Fruit Packs", "quantity": 10, "unit_price": 50.00, "amount": 500.00 }
  ],
  "sub_total": 500.00,
  "total_amount": 500.00,
  "amount_words": "Five Hundred Ghana Cedis Only",
  "created_at": "2026-03-27T10:15:00Z"
}
```

### Receipt

```json
{
  "_id": "ObjectId(…)",
  "receipt_number": "FFR-001",
  "client_name": "Acme Ltd",
  "client_address": "123 Main St, Accra",
  "contact_person": "John Doe",
  "payment_date": "2026-05-10",
  "payment_method": "Bank Transfer",
  "reference": "TXN-987654",
  "items": [
    { "description": "Mango Pack", "quantity": 5, "unit_price": 20.00, "amount": 100.00 }
  ],
  "sub_total": 100.00,
  "total_amount": 100.00,
  "amount_paid": 100.00,
  "balance": 0.00,
  "amount_words": "One Hundred Ghana Cedis Only",
  "created_at": "2026-05-10T10:15:00Z"
}
```

## Deployment (Render)

The app runs on Render's standard Python runtime out of the box.

| Setting        | Value                                |
|----------------|--------------------------------------|
| Build command  | `pip install -r requirements.txt`    |
| Start command  | `gunicorn app:app`                   |
| Environment var| `mongodb_uri` = your Atlas URI       |
| Python version | set `PYTHON_VERSION` (e.g. `3.11.9`) |

Render injects `PORT` automatically — `app.py` already reads it. In MongoDB Atlas, allow Render's egress IPs (or `0.0.0.0/0`) under **Network Access**. After redeploy, visit the Render URL once on each device you want to install the app on, then use the browser's *Install* / *Add to Home Screen* option.

## Company Details (Pre-filled)

- **Company:** Fruity Flicks
- **Tagline:** Eat Smart, Live Well
- **Location:** 10 Moole Street, Dansoman Exhibition Roundabout
- **Bank:** Stanbic Bank (Acc: 9040014197480)
- **Mobile Money:** 0243869554
