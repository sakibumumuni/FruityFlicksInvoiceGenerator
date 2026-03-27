# Fruity Flicks Invoice Generator

A web-based invoice generator for **Fruity Flicks**, a fruit distribution company based in Dansoman, Accra. Built with Flask and MongoDB.

## Features

- **Invoice creation** — Fill in client details, add multiple line items with descriptions, quantities, and unit prices (GHS)
- **Auto-calculations** — Row amounts, subtotal, total, and amount in words (e.g. "Fifty Ghana Cedis Only") are calculated automatically
- **Save & Download** — A single button saves the invoice to MongoDB and downloads it as a PDF simultaneously
- **Dynamic line items** — Add or remove item rows as needed
- **PDF export** — Clean A4-formatted PDF with company branding (powered by html2pdf.js)
- **Clear form** — Reset all fields to start a new invoice

## Tech Stack

- **Backend:** Python / Flask
- **Database:** MongoDB Atlas (via PyMongo)
- **Frontend:** HTML, CSS, Vanilla JavaScript
- **PDF Generation:** html2pdf.js (client-side)

## Project Structure

```
├── app.py                  # Flask application and routes
├── .env                    # MongoDB connection string (not tracked in git)
├── .gitignore
├── templates/
│   └── index.html          # Invoice form template
└── static/
    ├── css/
    │   └── style.css       # Invoice styling
    └── main.js             # Client-side logic (calculations, PDF, AJAX save)
```

## Setup

### Prerequisites

- Python 3.x
- A MongoDB Atlas cluster (or local MongoDB instance)

### Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd MVP
   ```

2. Install dependencies:
   ```bash
   pip install flask pymongo python-dotenv dnspython
   ```

3. Create a `.env` file in the project root:
   ```
   MONGODB_URL='mongodb+srv://<username>:<password>@<cluster>.mongodb.net/?appName=<appName>'
   ```

4. Run the application:
   ```bash
   python app.py
   ```

5. Open `http://localhost:5000` in your browser.

## Usage

1. Fill in the **client name**, **address**, **contact person**, and **delivery date**
2. Add line items using the **+ Add Item** button — enter description, quantity, and unit price
3. Totals update automatically as you type
4. Click **Save & Download** to save the invoice to the database and download it as a PDF
5. Click **Clear All** to reset the form for a new invoice

## MongoDB Document Structure

Each invoice is stored in the `fruityflicks.invoices` collection with this structure:

```json
{
  "client_name": "Acme Ltd",
  "client_address": "123 Main St",
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
  "sub_total": "500.00",
  "total_amount": "500.00",
  "amount_words": "Five Hundred Ghana Cedis Only"
}
```

## Company Details (Pre-filled)

- **Company:** Fruity Flicks
- **Tagline:** Eat Smart, Live Well
- **Location:** 10 Moole Street, Dansoman Exhibition Roundabout
- **Bank:** Stanbic Bank (Acc: 9040014197480)
- **Mobile Money:** 0243869554
