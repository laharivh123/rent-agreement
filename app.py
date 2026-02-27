from flask import Flask, request, send_file, render_template
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable, PageBreak
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.lib import colors
from datetime import datetime
from io import BytesIO

app = Flask(__name__)

# ---------- Watermark + Page Number ----------
def add_page_number_and_watermark(canvas_obj, doc):
    canvas_obj.saveState()
    canvas_obj.setFont("Helvetica", 60)
    canvas_obj.setFillColorRGB(0.92, 0.92, 0.92)
    canvas_obj.drawCentredString(A4[0]/2, A4[1]/2, "DRAFT COPY")
    canvas_obj.setFont("Helvetica", 9)
    canvas_obj.setFillColor(colors.black)
    canvas_obj.drawRightString(A4[0]-40, 20, f"Page {doc.page}")
    canvas_obj.restoreState()

# ---------- Helper to format addresses ----------
def format_address(address, style):
    lines = [line.strip() for line in address.split("\n") if line.strip()]
    return [Paragraph(line, style) for line in lines]

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/generate", methods=["POST"])
def generate():
    # -------- INPUTS --------
    agreement_type = request.form.get("agreement_type")
    duration = request.form.get("duration", "12")
    size = request.form.get("size", "N/A")
    place = request.form.get("place", "N/A")

    landlord = request.form.get("landlord", "Landlord Name")
    landlord_address = request.form.get("landlord_address", "")
    tenant = request.form.get("tenant", "Tenant Name")
    tenant_address = request.form.get("tenant_address", "")
    property_address = request.form.get("property_address", "")

    property_type = request.form.get("property_type", "")
    bhk = request.form.get("bhk", "")
    rent = request.form.get("rent", "0")
    deposit = request.form.get("deposit", "0")
    
    ancestor_list = request.form.getlist("ancestor[]")
    ancestor_list = [a.strip() for a in ancestor_list if a.strip()]

    heading = "RENT AGREEMENT" if agreement_type == "rent" else "LAND TRANSFER AGREEMENT"

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=50,
        leftMargin=50,
        topMargin=60,
        bottomMargin=40
    )

    elements = []
    styles = getSampleStyleSheet()
    legal_style = ParagraphStyle(
        'Legal',
        parent=styles['Normal'],
        fontSize=11,
        leading=18,
        alignment=4  # Justified
    )

    # -------- TITLE --------
    elements.append(Paragraph(f"<b>{heading}</b>", styles["Title"]))
    elements.append(Spacer(1, 0.3*inch))

    # -------- ADDRESSES --------
    landlord_paragraphs = format_address(landlord_address, legal_style)
    tenant_paragraphs = format_address(tenant_address, legal_style)
    property_paragraphs = format_address(property_address, legal_style)

    elements.append(Paragraph(f"This Agreement is executed on {datetime.today().strftime('%d-%m-%Y')} between:", legal_style))
    elements.append(Spacer(1, 0.1*inch))
    elements.append(Paragraph(f"<b>{landlord}</b> residing at:", legal_style))
    elements.extend(landlord_paragraphs)
    elements.append(Spacer(1, 0.1*inch))
    elements.append(Paragraph(f"(hereinafter referred to as the Transferor) and <b>{tenant}</b> residing at:", legal_style))
    elements.extend(tenant_paragraphs)
    elements.append(Paragraph("(hereinafter referred to as the Transferee).", legal_style))
    elements.append(Spacer(1, 0.2*inch))

    # -------- PROPERTY DESCRIPTION --------
    elements.append(Paragraph("WHEREAS the Transferor is the lawful owner of the immovable property measuring {} square feet situated at:".format(size), legal_style))
    elements.extend(property_paragraphs)
    elements.append(Paragraph("AND WHEREAS the Transferor has agreed to transfer/lease the said property to the Transferee, and the Transferee has agreed to accept the same, the parties hereby execute this Agreement as follows:", legal_style))
    elements.append(Spacer(1, 0.3*inch))

    # -------- LAND AGREEMENT --------
    if agreement_type == "land" and ancestor_list:
        elements.append(Paragraph("The Transferor declares that the property forms part of ancestral holdings.", legal_style))
        elements.append(Paragraph("The property is being transferred from the following family members:", legal_style))
        for i, ancestor in enumerate(ancestor_list, start=1):
            elements.append(Paragraph(f"{i}. {ancestor}", legal_style))
        elements.append(Paragraph("to the Transferee, with full consent of all the above-mentioned members.", legal_style))
        elements.append(Spacer(1, 0.3*inch))

    # -------- RENT AGREEMENT DETAILED CLAUSES --------
    if agreement_type == "rent":
        clauses = [
            f"The rent in respect of the 'Demised Premises' shall commence from (Starting Date of Agreement) and shall be valid till (Expiry Date of Agreement). Thereafter, it may be extended on mutual consent of both parties.",
            f"The Tenant shall pay to the Owner a monthly rent of Rs.({rent}), excluding electricity and water bills, payable on or before 7th day of each month.",
            "The Tenant shall pay a monthly maintenance charge towards Generator, Elevator, Guards, Common Areas, and lawn maintenance.",
            "The Tenant shall pay for the running costs of elevator and generator separately.",
            "During the Rent period, the Tenant shall pay for electricity and water as per bills. The Owner is responsible for dues until possession is handed over.",
            f"The Tenant will pay an interest-free refundable security deposit of Rs.({deposit}) vide cheque at the time of signing. The Owner shall refund it after adjusting dues or damages.",
            "All sanitary, electrical and other fittings in the premises shall be handed over in good working condition.",
            "The Tenant shall not sublet or assign the premises and it shall be used for bonafide residential purposes only.",
            "Day-to-day minor repairs are the Tenant's responsibility; structural or major repairs by the Owner.",
            "No structural additions without written consent of the Owner. Tenant can install ACs or electrical gadgets at their own cost and remove them later.",
            "The Owner can enter the premises for inspection or repairs, not exceeding once a month.",
            "The Tenant shall comply with all local authority rules applicable to the premises.",
            "The Owner shall pay all property taxes and other subscription fees.",
            "The Owner will keep the Tenant free from any claims regarding quiet possession.",
            "The Rent Agreement can be terminated before expiry by serving one month prior notice in writing.",
            "Tenant shall maintain the premises in good condition; minor repairs at Tenant's cost, natural wear & tear exempted.",
            "If Premises are not vacated, Tenant shall pay damages at two times the rent until possession is surrendered.",
            "Both parties shall observe and adhere to all terms and conditions herein.",
            "Both parties represent that they are fully empowered and competent to enter into this Agreement.",
            "Any disputes shall be settled in the jurisdiction of the civil courts of the city specified.",
            "The Rent Agreement will be registered in front of the Registrar; charges towards registration to be borne by the parties."
        ]
        for idx, clause in enumerate(clauses, start=1):
            elements.append(Paragraph(f"{idx}. {clause}", legal_style))
            elements.append(Spacer(1, 0.2*inch))

    # -------- PAGE BREAK for signatures --------
    elements.append(PageBreak())

    # -------- SIGNATURES --------
    elements.append(HRFlowable(width="100%"))
    elements.append(Spacer(1, 0.5*inch))
    elements.append(Paragraph("Signature of Transferor: _______________________________", styles["Normal"]))
    elements.append(Spacer(1, 0.8*inch))
    elements.append(Paragraph("Signature of Transferee: _________________________________", styles["Normal"]))
    elements.append(Spacer(1, 0.8*inch))
    elements.append(Paragraph(f"Place: {place}", styles["Normal"]))
    elements.append(Paragraph(f"Date: {datetime.today().strftime('%d-%m-%Y')}", styles["Normal"]))

    # Build PDF
    doc.build(
        elements,
        onFirstPage=add_page_number_and_watermark,
        onLaterPages=add_page_number_and_watermark
    )

    buffer.seek(0)
    return send_file(
        buffer,
        as_attachment=True,
        download_name=f"{heading.replace(' ','_')}_{tenant}.pdf",
        mimetype="application/pdf"
    )

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)