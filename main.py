import os
import httpx
from typing import Optional
from fastapi import FastAPI, Request, Form, File, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse

app = FastAPI(title="SpokeStack - Autonomous 5-Tool Engine")

# Read Paystack Live Key from Render environment variables
PAYSTACK_SECRET_KEY = os.getenv("PAYSTACK_SECRET_KEY", "sk_live_placeholder")

# 5 High-Intent Utility Registry (Local KES & International USD)
TOOLS = {
    "mpesa-converter": {
        "name": "M-Pesa Statement PDF to CSV Converter",
        "price_kes": 150,
        "price_usd": 2,
        "desc": "Extract encrypted Safaricom M-Pesa PDFs into clean Excel sheets."
    },
    "etims-formatter": {
        "name": "KRA eTIMS Tax Receipt Formatter",
        "price_kes": 200,
        "price_usd": 3,
        "desc": "Format raw expense receipts into KRA eTIMS compliant invoice structures."
    },
    "phone-validator": {
        "name": "Bulk WhatsApp & Phone Line Cleaner",
        "price_kes": 250,
        "price_usd": 3.50,
        "desc": "Clean customer databases and verify active Safaricom lines before sending SMS blasts."
    },
    "kra-verifier": {
        "name": "KRA PIN & Tax Return Verification Parser",
        "price_kes": 150,
        "price_usd": 2,
        "desc": "Parse and structure data directly from official KRA iTax PDF certificates."
    },
    "bank-statement-parser": {
        "name": "Bank Statement & Payslip PDF Extractor",
        "price_kes": 200,
        "price_usd": 3,
        "desc": "Convert password-protected KCB, Equity, NCBA bank PDFs into structured CSV files."
    }
}

# 1. Google Search Console Verification Route
@app.get("/googleb6c685259aeb3a9f.html", response_class=PlainTextResponse)
def google_verify():
    return "google-site-verification: googleb6c685259aeb3a9f.html"

# 2. Complete 5-Tool Responsive Interface
@app.get("/", response_class=HTMLResponse)
def home():
    cards_html = ""
    for slug, tool in TOOLS.items():
        cards_html += f"""
        <div class="card">
            <h3>{tool['name']}</h3>
            <p class="desc">{tool['desc']}</p>
            <p class="price">Price: <strong>KES {tool['price_kes']}</strong> / <strong>USD ${tool['price_usd']}</strong></p>
            <form action="/pay/{slug}" method="POST" enctype="multipart/form-data">
                <label>Select Payment Method</label>
                <select name="currency">
                    <option value="KES">M-Pesa (KES {tool['price_kes']})</option>
                    <option value="USD">International Card (USD ${tool['price_usd']})</option>
                </select>
                <label>Your Phone / WhatsApp Number</label>
                <input type="text" name="phone" placeholder="07XX or +254XX" required>
                <label>Delivery Email Address</label>
                <input type="email" name="email" placeholder="name@example.com" required>
                <label>Upload File or Paste Data</label>
                <input type="file" name="file">
                <input type="text" name="raw_data" placeholder="Or paste text payload here...">
                <button type="submit" class="btn">Proceed & Pay via Paystack</button>
            </form>
        </div>
        """

    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>SpokeStack - Instant Business Utilities</title>
        <style>
            body {{ background: #07090e; color: #f1f5f9; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; padding: 16px; margin: 0; }}
            .container {{ max-width: 650px; margin: 0 auto; }}
            header {{ text-align: center; padding: 24px 0 16px 0; }}
            h1 {{ font-size: 1.6rem; color: #38bdf8; margin-bottom: 6px; }}
            p.sub {{ color: #94a3b8; font-size: 0.9rem; margin-top: 0; }}
            .card {{ background: #111827; border: 1px solid #1f2937; border-radius: 12px; padding: 20px; margin-bottom: 20px; box-shadow: 0 4px 10px rgba(0,0,0,0.4); }}
            h3 {{ margin-top: 0; color: #f8fafc; font-size: 1.15rem; }}
            .desc {{ color: #94a3b8; font-size: 0.85rem; margin-bottom: 8px; }}
            .price {{ color: #10b981; font-size: 0.9rem; margin-bottom: 12px; }}
            label {{ font-size: 0.8rem; color: #cbd5e1; display: block; margin-top: 10px; }}
            input, select {{ width: 100%; padding: 10px; margin-top: 4px; border-radius: 6px; border: 1px solid #374151; background: #1f2937; color: #fff; box-sizing: border-box; font-size: 0.9rem; }}
            .btn {{ background: #059669; color: #fff; padding: 12px; border: none; border-radius: 6px; font-weight: bold; width: 100%; margin-top: 16px; cursor: pointer; font-size: 0.95rem; }}
            .btn:hover {{ background: #047857; }}
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <h1>SpokeStack Business Engine</h1>
                <p class="sub">5 Automated Financial & Compliance Utilities for Kenya & Global Users</p>
            </header>
            {cards_html}
        </div>
    </body>
    </html>
    """

# 3. Paystack Live Payment Processor
@app.post("/pay/{slug}")
async def process_payment(
    slug: str, 
    currency: str = Form("KES"),
    phone: str = Form(...), 
    email: str = Form(...), 
    file: Optional[UploadFile] = File(None),
    raw_data: Optional[str] = Form(None)
):
    tool = TOOLS.get(slug)
    if not tool:
        return JSONResponse({"status": "error", "message": "Invalid utility tool selected."}, status_code=400)

    curr = currency.upper()
    amount = (tool["price_usd"] * 100) if curr == "USD" else (tool["price_kes"] * 100)

    payload = {
        "amount": int(amount),
        "email": email.strip(),
        "currency": curr
    }

    if curr == "KES":
        clean_phone = phone.strip().replace(" ", "").replace("-", "")
        if clean_phone.startswith("0"):
            clean_phone = "+254" + clean_phone[1:]
        elif not clean_phone.startswith("+"):
            clean_phone = "+" + clean_phone

        payload["mobile_money"] = {
            "phone": clean_phone,
            "provider": "mpesa"
        }
    else:
        payload["callback_url"] = "https://project-cench.onrender.com"

    headers = {
        "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient() as client:
        res = await client.post("https://api.paystack.co/charge", json=payload, headers=headers)
        data = res.json()

    if res.status_code == 200 and data.get("status"):
        return JSONResponse({
            "status": "success",
            "message": "Payment request initiated successfully! Complete prompt on your phone."
        })
    else:
        return JSONResponse({
            "status": "error",
            "message": data.get("message", "Payment initiation failed. Please check details.")
        }, status_code=400)
