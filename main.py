import os
import httpx
from typing import Optional
from fastapi import FastAPI, Request, Form, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

# ==========================================
# 1. INITIALIZE APP FIRST (BEFORE ANY @app)
# ==========================================
app = FastAPI(title="SpokeStack - Cench.io Engine")

# 2. Setup templates
templates = Jinja2Templates(directory="templates")

# 3. Read environment variable
PAYSTACK_SECRET_KEY = os.getenv("PAYSTACK_SECRET_KEY", "sk_test_placeholder")

# 4. Spoke Registry
SPOKE_REGISTRY = {
    "cheap-mpesa-statement-converter": {
        "title": "Cheap & Fast Bulk M-Pesa PDF to CSV Converter",
        "category": "Financial Utility",
        "price_kes": 150,
        "description": "Convert password-protected Safaricom M-Pesa PDFs directly into clean Excel/CSV files in seconds."
    },
    "instant-etims-receipt-formatter": {
        "title": "Instant KRA eTIMS Compliant Tax Receipt Generator",
        "category": "Compliance Utility",
        "price_kes": 200,
        "description": "Format raw transaction payloads into KRA eTIMS compliant tax invoice receipts instantly."
    },
    "quick-phone-number-validator": {
        "title": "Quick Bulk Phone Number & WhatsApp Line Checker",
        "category": "Outreach Utility",
        "price_kes": 250,
        "description": "Clean bulk phone lists and verify active WhatsApp lines before running SMS/WhatsApp campaigns."
    }
}

# ==========================================
# 5. NOW PLACE ALL YOUR @app.get AND @app.post ROUTES BELOW HERE
# ==========================================

@app.get("/", response_class=HTMLResponse)
async def home_river(request: Request):
    return templates.TemplateResponse(request, "index.html", {"tools": SPOKE_REGISTRY})

@app.get("/tool/{slug}", response_class=HTMLResponse)
async def render_spoke_page(request: Request, slug: str):
    tool = SPOKE_REGISTRY.get(slug)
    if not tool:
        raise HTTPException(status_code=404, detail="Spoke tool not found.")
    return templates.TemplateResponse(request, "spoke_tool.html", {"slug": slug, "tool": tool})

@app.post("/api/pay/{slug}")
async def initiate_paystack_stk(
    slug: str, 
    phone_number: str = Form(...), 
    email: str = Form(...),
    raw_data: Optional[str] = Form(None),
    uploaded_file: Optional[UploadFile] = File(None)
):
    tool = SPOKE_REGISTRY.get(slug)
    if not tool:
        return JSONResponse({"status": "error", "message": "Invalid tool selection."}, status_code=400)

    if not raw_data and not (uploaded_file and uploaded_file.filename):
        return JSONResponse({"status": "error", "message": "Please paste data or upload a file first."}, status_code=400)

    # Format Kenyan Phone Number (+254...)
    raw_phone = phone_number.strip().replace(" ", "").replace("-", "")
    if raw_phone.startswith("0"):
        clean_phone = "+254" + raw_phone[1:]
    elif raw_phone.startswith("254"):
        clean_phone = "+" + raw_phone
    elif not raw_phone.startswith("+"):
        clean_phone = "+" + raw_phone
    else:
        clean_phone = raw_phone

    payload = {
        "amount": tool["price_kes"] * 100,
        "email": email.strip(),
        "currency": "KES",
        "mobile_money": {
            "phone": clean_phone,
            "provider": "mpesa"
        }
    }

    headers = {
        "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient() as client:
        response = await client.post("https://api.paystack.co/charge", json=payload, headers=headers)
        res_data = response.json()

    if response.status_code == 200 and res_data.get("status"):
        return JSONResponse({
            "status": "success",
            "message": "STK Push sent to your phone! Enter PIN to process.",
            "reference": res_data["data"]["reference"]
        })
    else:
        return JSONResponse({
            "status": "error",
            "message": res_data.get("message", "Payment failed. Please check phone number.")
        }, status_code=400)
