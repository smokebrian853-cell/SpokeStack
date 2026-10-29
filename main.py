import os
import httpx
from typing import Optional
from fastapi import FastAPI, Request, Form, File, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse

app = FastAPI(title="SpokeStack - Autonomous 24/7 Engine")

# Fetch your Paystack Live Secret Key securely from Render environment variables
PAYSTACK_SECRET_KEY = os.getenv("PAYSTACK_SECRET_KEY", "sk_live_placeholder")

# Tool Registry with Local (KES) and International (USD) Layers
TOOLS = {
    "mpesa-converter": {
        "name": "M-Pesa Statement PDF to CSV Converter",
        "price_kes": 150,
        "price_usd": 2,
        "desc": "Extract password-protected Safaricom PDFs into clean Excel files instantly."
    },
    "etims-formatter": {
        "name": "KRA eTIMS Tax Receipt Formatter",
        "price_kes": 200,
        "price_usd": 3,
        "desc": "Format raw expenses into KRA-compliant digital invoice payloads."
    },
    "phone-validator": {
        "name": "Bulk WhatsApp & Phone Line Cleaner",
        "price_kes": 250,
        "price_usd": 3.50,
        "desc": "Verify active Safaricom lines and clean phone lists for marketing."
    }
}

# 1. Google Search Console Verification (Hardcoded, never drops)
@app.get("/googleb6c685259aeb3a9f.html", response_class=PlainTextResponse)
def google_verify():
    return "google-site-verification: googleb6c685259aeb3a9f.html"

# 2. Autonomous 24/7 Responsive UI (Zero Lag, Zero Auto-Reloads)
@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>SpokeStack - Instant Business & Tax Utilities</title>
        <style>
            body { background: #07090e; color: #f1f5f9; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; padding: 16px; margin: 0; }
            .container { max-width: 600px; margin: 0 auto; }
            header { text-align: center; padding: 20px 0; }
            h1 { font-size: 1.5rem; color: #38bdf8; margin-bottom: 5px; }
            p.sub { color: #94a3b8; font-size: 0.9rem; }
            .card { background: #111827; border: 1px: #1f2937; border-radius: 12px; padding: 20px; margin-bottom: 16px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
            h3 { margin-top: 0; color: #f8fafc; font-size: 1.1rem; }
            .desc { color: #94a3b8; font-size: 0.85rem; margin-bottom: 15px; }
            label { font-size: 0.8rem; color: #cbd5e1; display: block; margin-top: 8px; }
            input, select { width: 100%; padding: 10px; margin-top: 4px; border-radius: 6px; border: 1px solid #374151; background: #1f2937; color: #fff; box-sizing: border-box; font-size: 0.9rem; }
            .btn { background: #059669; color: #fff; padding: 12px; border: none; border-radius: 6px; font-weight: bold; width: 100%; margin-top: 15px; cursor: pointer; font-size: 0.95ln; }
            .btn:hover { background: #047857; }
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <h1>SpokeStack Cloud Utilities</h1>
                <p class="sub">Automated financial document formatting & validation</p>
            </header>

            <div class="card">
                <h3>M-Pesa Statement to CSV</h3>
                <p class="desc">KES 150 / USD 2 — Converts locked Safaricom statements into Excel.</p>
                <form action="/pay/mpesa-converter" method="POST" enctype="multipart/form-data">
                    <label>Currency & Payment Method</label>
                    <select name="currency">
                        <option value="KES">M-Pesa (KES 150)</option>
                        <option value="USD">International Card (USD $2)</option>
                    </select>
                    <label>Your Phone / WhatsApp (for M-Pesa STK push)</label>
                    <input type="text" name="phone" placeholder="07XX or +254XX" required>
                    <label>Email Address</label>
                    <input type="email" name="email" placeholder="name@example.com" required>
                    <label>Upload Protected PDF Statement</label>
                    <input type="file" name="file" required>
                    <button type="submit" class="btn">Proceed & Pay via Paystack</button>
                </form>
            </div>

            <div class="card">
                <h3>KRA eTIMS Receipt Formatter</h3>
                <p class="desc">KES 200 / USD 3 — Instant expense payload structuring.</p>
                <form action="/pay/etims-formatter" method="POST">
                    <label>Currency & Payment Method</label>
                    <select name="currency">
                        <option value="KES">M-Pesa (KES 200)</option>
                        <option value="USD">International Card (USD $3)</option>
                    </select>
                    <label>Your Phone / WhatsApp</label>
                    <input type="text" name="phone" placeholder="07XX or +254XX" required>
                    <label>Email Address</label>
                    <input type="email" name="email" placeholder="name@example.com" required>
                    <label>Paste Raw Transaction Text</label>
                    <input type="text" name="raw_data" placeholder="Paste line items here..." required>
                    <button type="submit" class="btn">Proceed & Pay via Paystack</button>
                </form>
            </div>
        </div>
    </body>
    </html>
    """

# 3. Secure Backend Payment Gateway Processor
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
        "amount": amount,
        "email": email.strip(),
        "currency": curr
    }

    if curr == "KES":
        clean_phone = phone.strip().replace(" ", "")
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
            "message": "Payment request initiated successfully! Check your phone prompt or card flow."
        })
    else:
        return JSONResponse({
            "status": "error",
            "message": data.get("message", "Payment gateway error. Please verify input details.")
        }, status_code=400)
