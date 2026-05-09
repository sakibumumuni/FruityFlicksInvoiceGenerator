# Fruity Flicks Invoice Generator

A web-based invoice generator for **Fruity Flicks**, a fruit distribution company based in Dansoman, Accra. Built with Flask and MongoDB; PDFs are rendered server-side with WeasyPrint.

## Features

- **Invoice creation** — Fill in client details and add multiple line items with descriptions, quantities, and unit prices (GHS).
- **Auto-calculations** — Row amounts, subtotal, total, and amount in words update live in the browser.
- **Save & Download** — Submitting the form persists the invoice to MongoDB and returns a freshly rendered PDF in the same response.
- **Dynamic line items** — Add or remove item rows as needed.
- **A4 PDF export** — Server-rendered PDF with company branding, fixed to a single A4 page.
- **Clear form** — Reset all fields to start a new invoice.

## Tech Stack

- **Backend:** Python / Flask
- **Database:** MongoDB Atlas (via PyMongo)
- **Frontend:** HTML, CSS, vanilla JavaScript (calculations and UX only)
- **PDF generation:** WeasyPrint (server-side, HTML/CSS to PDF)

## Project Structure

```
.
├── app.py                       # Flask app, routes, PDF generation
├── requirements.txt
├── .env                         # MongoDB URI (gitignored)
├── .gitignore
├── README.md
├── templates/
│   ├── index.html               # Editable invoice form
│   └── invoice_pdf.html         # Server-rendered template used for the PDF
└── static/
    ├── css/style.css            # Form styling
    ├── img/logo.jpg             # Company logo (used by both views)
    └── main.js                  # Row math, add/remove, clear form
```

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

6. Open `http://localhost:5000/invoice` in your browser.

## Usage

1. Fill in **invoice number**, **client name**, **address**, **contact person**, and **delivery date**.
2. Add line items with the **+ Add Item** button — enter description, quantity, and unit price.
3. Totals and amount-in-words update as you type.
4. Click **Save & Download** — the form POSTs to `/invoice`; the server saves the record to MongoDB and streams back a PDF download (`FruityFlicks_Invoice_<number>.pdf`).
5. Use **Clear All** to reset the form.

If the database is unreachable, PDF generation still succeeds — the save failure is logged but the user still gets their invoice.

## MongoDB Document Structure

Each invoice is stored in the `invoices.invoices` collection:

```json
{
  "invoice_number": "FF-001",
  "client_name": "Acme Ltd",
  "client_address": "123 Main St, Accra",
  "contact_person": "John Doe",
  "delivery_date": "2026-03-27",
  "items": [
    {
      "description": "Fruit Packs",
      "quantity": 10,
      "unit_price": 50.00,
      "amount": 500.00
    }
  ],
  "sub_total": 500.00,
  "total_amount": 500.00,
  "amount_words": "Five Hundred Ghana Cedis Only",
  "created_at": "2026-03-27T10:15:00Z"
}
```

## Company Details (Pre-filled)

- **Company:** Fruity Flicks
- **Tagline:** Eat Smart, Live Well
- **Location:** 10 Moole Street, Dansoman Exhibition Roundabout
- **Bank:** Stanbic Bank (Acc: 9040014197480)
- **Mobile Money:** 0243869554
