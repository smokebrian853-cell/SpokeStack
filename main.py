from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

app = FastAPI(title="Project Cench - Spoke Engine")
templates = Jinja2Templates(directory="templates")

BANNED_ZERO_INTENT = ["free", "crack", "open source", "diy", "github", "torrent", "pirate"]

SPOKE_REGISTRY = {
    "cheap-mpesa-statement-converter": {
        "title": "Cheap & Fast Bulk M-Pesa PDF to CSV Converter",
        "category": "Financial Utility",
        "description": "Convert messy M-Pesa till/paybill PDF statements into clean Excel spreadsheets instantly.",
        "price_kes": 150,
        "input_label": "Paste Raw M-Pesa Text or Upload Data"
    },
    "instant-etims-receipt-formatter": {
        "title": "Instant KRA eTIMS Compliant Tax Receipt Generator",
        "category": "Compliance Utility",
        "description": "Format clean, tax-compliant invoice payloads for local businesses in seconds.",
        "price_kes": 200,
        "input_label": "Enter Transaction Details"
    },
    "quick-phone-number-validator": {
        "title": "Quick Bulk Phone Number & WhatsApp Line Checker",
        "category": "Outreach Utility",
        "description": "Filter out dead numbers and verify active WhatsApp business lines instantly.",
        "price_kes": 250,
        "input_label": "Paste Phone Numbers (One per line)"
    }
}

@app.get("/", response_class=HTMLResponse)
async def home_river(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "tools": SPOKE_REGISTRY})

@app.get("/tool/{slug}", response_class=HTMLResponse)
async def render_spoke_page(request: Request, slug: str):
    tool = SPOKE_REGISTRY.get(slug)
    if not tool:
        raise HTTPException(status_code=404, detail="Spoke tool not found.")
    return templates.TemplateResponse("spoke_tool.html", {"request": request, "slug": slug, "tool": tool})

@app.post("/api/process/{slug}")
async def process_user_data(slug: str, raw_input: str = Form(...)):
    tool = SPOKE_REGISTRY.get(slug)
    if not tool:
        return JSONResponse({"status": "error", "message": "Invalid tool spoke."}, status_code=400)
    if not raw_input.strip():
        return JSONResponse({"status": "error", "message": "Input cannot be empty."}, status_code=400)

    lines = raw_input.strip().split("\n")
    preview_snippet = f"Successfully processed {len(lines)} rows.\nPreview item 1: {lines[0][:40]}...\n[FULL FILE LOCKED]"

    return {
        "status": "success",
        "preview": preview_snippet,
        "price_kes": tool["price_kes"],
        "payment_prompt": f"Pay {tool['price_kes']} KES via M-Pesa / Airtel / Card to download full clean file."
    }
