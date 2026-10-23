import os
import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(
    title="SpokeStack Kenya - SME Automated Tool Suite",
    description="M-Pesa Statement Converter, KRA eTIMS Formatter, and Bulk Phone Validator",
    version="1.0.0"
)

# CORS Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files if present
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# -------------------------------------------------------------------
# Core Routes
# -------------------------------------------------------------------

@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>SpokeStack Kenya | Automated SME Tools</title>
        <style>
            body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 800px; margin: 40px auto; padding: 0 20px; line-height: 1.6; color: #111827; }
            h1 { color: #059669; }
            .tool-card { border: 1px solid #E5E7EB; padding: 20px; border-radius: 8px; margin-bottom: 20px; background: #F9FAFB; }
            .price { font-weight: bold; color: #059669; }
            a { color: #2563EB; text-decoration: none; font-weight: 600; }
            a:hover { text-decoration: underline; }
        </style>
    </head>
    <body>
        <h1>SpokeStack Kenya</h1>
        <p>Instant browser-based utilities for accountants, cyber cafes, and small businesses.</p>
        
        <div class="tool-card">
            <h3>1. M-Pesa Statement Converter <span class="price">(KES 150)</span></h3>
            <p>Convert Safaricom M-Pesa PDF statements to clean Excel (.xlsx) / CSV spreadsheets instantly.</p>
            <a href="/tool/cheap-mpesa-statement-converter">Launch Tool &rarr;</a>
        </div>

        <div class="tool-card">
            <h3>2. Instant eTIMS Receipt Formatter <span class="price">(KES 200)</span></h3>
            <p>Format line items and vendor receipts into KRA-compliant eTIMS expense summaries.</p>
            <a href="/tool/instant-etims-receipt-formatter">Launch Tool &rarr;</a>
        </div>

        <div class="tool-card">
            <h3>3. Quick Phone Number Validator <span class="price">(KES 250)</span></h3>
            <p>Clean bulk customer contact lists (0712 vs 2547) for M-Pesa STK payouts and WhatsApp campaigns.</p>
            <a href="/tool/quick-phone-number-validator">Launch Tool &rarr;</a>
        </div>
    </body>
    </html>
    """

# Tool Path Handlers
@app.get("/tool/cheap-mpesa-statement-converter", response_class=HTMLResponse)
async def mpesa_tool():
    return "<h1>M-Pesa Statement Converter (KES 150)</h1><p>Upload your PDF statement to convert to Excel.</p>"

@app.get("/tool/instant-etims-receipt-formatter", response_class=HTMLResponse)
async def etims_tool():
    return "<h1>Instant eTIMS Formatter (KES 200)</h1><p>Format transaction lines for KRA compliance.</p>"

@app.get("/tool/quick-phone-number-validator", response_class=HTMLResponse)
async def phone_tool():
    return "<h1>Phone Number Validator (KES 250)</h1><p>Validate and clean bulk contact lists.</p>"

# Health Check
@app.get("/health")
async def health():
    return {"status": "ok", "app": "SpokeStack"}

# -------------------------------------------------------------------
# Google Search Console Verification Route
# -------------------------------------------------------------------

@app.get("/googleb6c685259aeb3a9f.html", response_class=PlainTextResponse)
def google_verification():
    return "google-site-verification: googleb6c685259aeb3a9f.html"
