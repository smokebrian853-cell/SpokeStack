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

    # 1. Clean and format Kenyan Phone Number (+254...)
    raw_phone = phone_number.strip().replace(" ", "").replace("-", "")
    if raw_phone.startswith("0"):
        clean_phone = "+254" + raw_phone[1:]
    elif raw_phone.startswith("254"):
        clean_phone = "+" + raw_phone
    elif not raw_phone.startswith("+"):
        clean_phone = "+" + raw_phone
    else:
        clean_phone = raw_phone

    # 2. Build Paystack Charge Payload
    payload = {
        "amount": tool["price_kes"] * 100,  # KES to cents
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
            "message": res_data.get("message", "Payment failed. Please check your phone number.")
        }, status_code=400)
