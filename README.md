# Fruity Flicks Invoice & Receipt Generator

A web-based invoice and receipt generator for **Fruity Flicks**, a fruit distribution company based in Dansoman, Accra. Built with Flask and MongoDB; PDFs are rendered server-side with WeasyPrint.

## Features

- **Invoice creation** — Fill in client details and add multiple line items with descriptions, quantities, and unit prices (GHS).
- **Receipt creation** — Issue paid-receipts with payment date, payment method (Cash / Bank Transfer / Mobile Money), reference / transaction ID, and amount paid. Outstanding balance is computed automatically; a green **PAID** stamp is added when the balance hits zero.
- **Auto-calculations** — Row amounts, subtotal, total, balance, and amount in words update live in the browser.
- **Save & Download** — Submitting the form persists the document to MongoDB and returns a freshly rendered PDF in the same response.
- **Dynamic line items** — Add or remove item rows as needed.
- **Single-page A4 PDF** — Server-rendered PDF that auto-fits everything onto a single A4 page no matter how many line items the document has.
- **Cross-form navigation** — One-click toggle between the invoice and receipt forms.
- **Clear form** — Reset all fields to start a new document.

## Tech Stack

- **Backend:** Python / Flask
- **Database:** MongoDB Atlas (via PyMongo)
- **Frontend:** HTML, CSS, vanilla JavaScript (calculations and UX only)
- **PDF generation:** WeasyPrint (server-side, HTML/CSS to PDF)
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
│   ├── index.html               # Editable invoice form
│   ├── invoice_pdf.html         # Server-rendered template used for the invoice PDF
│   ├── receipt.html             # Editable receipt form
│   └── receipt_pdf.html         # Server-rendered template used for the receipt PDF
└── static/
    ├── css/style.css            # Form styling
    ├── img/logo.jpg             # Company logo (used by both views)
    └── main.js                  # Row math, add/remove, clear form (shared)
```

## Routes

| Method | Path        | Purpose                                                    |
|--------|-------------|------------------------------------------------------------|
| GET    | `/`         | Renders the invoice form (alias for `/invoice`)            |
| GET    | `/invoice`  | Renders the invoice form                                   |
| POST   | `/invoice`  | Saves invoice to MongoDB and returns the PDF as a download |
| GET    | `/receipt`  | Renders the receipt form                                   |
| POST   | `/receipt`  | Saves receipt to MongoDB and returns the PDF as a download |

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

6. Open `http://localhost:5000/invoice` (or `/receipt`) in your browser.

## Usage

### Issuing an invoice

1. Open `/invoice`. Fill in **invoice number**, **client name**, **address**, **contact person**, and **delivery date**.
2. Add line items with the **+ Add Item** button — enter description, quantity, and unit price.
3. Totals and amount-in-words update as you type.
4. Click **Save & Download** — the form POSTs to `/invoice`; the server saves the record to MongoDB and streams back a PDF download (`FruityFlicks_Invoice_<number>.pdf`).
5. Use **Clear All** to reset the form.

### Issuing a receipt

1. From the invoice form, click **→ Switch to Receipt** (or open `/receipt` directly).
2. Fill in **receipt number**, the same client fields, and the **payment details**: payment date, payment method, reference / transaction ID.
3. Add line items the same way.
4. Enter the **Amount Paid** — the balance and amount-in-words recompute live.
5. Click **Save & Download** — the server saves the receipt to MongoDB and returns the PDF (`FruityFlicks_Receipt_<number>.pdf`). When the balance is zero, the PDF includes a green **PAID** stamp.

If the database is unreachable, PDF generation still succeeds — the save failure is logged but the user still gets their document.

## MongoDB Document Structure

Invoices live in the `invoices.invoices` collection, receipts in `invoices.receipts`.

### Invoice

```json
{
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

Render injects `PORT` automatically — `app.py` already reads it. In MongoDB Atlas, allow Render's egress IPs (or `0.0.0.0/0`) under **Network Access**.

## Company Details (Pre-filled)

- **Company:** Fruity Flicks
- **Tagline:** Eat Smart, Live Well
- **Location:** 10 Moole Street, Dansoman Exhibition Roundabout
- **Bank:** Stanbic Bank (Acc: 9040014197480)
- **Mobile Money:** 0243869554
