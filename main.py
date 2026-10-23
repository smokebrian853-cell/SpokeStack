import os
import httpx
from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

app = FastAPI(title="SpokeStack - Cench.io Engine")
templates = Jinja2Templates(directory="templates")

# Reads key securely from Render Environment Variables
PAYSTACK_SECRET_KEY = os.getenv("PAYSTACK_SECRET_KEY", "sk_test_placeholder")

# All 3 SpokeStack Tools Registered in One Place
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

@app.get("/", response_class=HTMLResponse)
async def home_river(request: Request):
    """Lists all 3 live tools on the homepage."""
    return templates.TemplateResponse(request, "index.html", {"tools": SPOKE_REGISTRY})

@app.get("/tool/{slug}", response_class=HTMLResponse)
async def render_spoke_page(request: Request, slug: str):
    """Renders the specific tool page dynamically."""
    tool = SPOKE_REGISTRY.get(slug)
    if not tool:
        raise HTTPException(status_code=404, detail="Spoke tool not found.")
    return templates.TemplateResponse(request, "spoke_tool.html", {"slug": slug, "tool": tool})

@app.post("/api/pay/{slug}")
async def initiate_paystack_stk(slug: str, phone_number: str = Form(...), email: str = Form(...)):
    """Triggers M-Pesa STK Push directly to customer phone via Paystack."""
    tool = SPOKE_REGISTRY.get(slug)
    if not tool:
        return JSONResponse({"status": "error", "message": "Invalid tool selection."}, status_code=400)

    # Format Kenyan Phone Number (+254...)
    clean_phone = phone_number.strip().replace("+", "")
    if clean_phone.startswith("0"):
        clean_phone = "254" + clean_phone[1:]

    payload = {
        "amount": tool["price_kes"] * 100,  # Convert KES to cents
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
            "message": "STK Push sent! Enter your M-Pesa PIN on your phone to unlock download.",
            "reference": res_data["data"]["reference"]
        })
    else:
        return JSONResponse({
            "status": "error",
            "message": res_data.get("message", "Failed to send STK Push. Try again.")
        }, status_code=400)
