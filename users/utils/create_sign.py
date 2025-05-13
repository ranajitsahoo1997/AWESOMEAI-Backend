from pyhanko.sign import signers
from pyhanko.sign.signers import PdfSigner, PdfSignatureMetadata
from pyhanko.sign.fields import SigSeedSubFilter
from pyhanko.pdf_utils.incremental_writer import IncrementalPdfFileWriter
from pyhanko.pdf_utils import text, images
from pyhanko.stamp import QRStampStyle, TextStampStyle
import qrcode
from pathlib import Path

def create_fully_locked_signed_pdf(input_pdf_path: str, output_pdf_path: str):
    """
    Creates a signed PDF with:
    - Highest certification level (no edits allowed)
    - Visible signature appearance
    - Page watermarks
    - QR code verification
    """
    # Certificate paths (update these)
    key_path = Path("/home/ranajit/Desktop/RedIntegro/Graphql/backend-graphql-django/cert/private_key.pem")
    cert_path = Path("/home/ranajit/Desktop/RedIntegro/Graphql/backend-graphql-django/cert/certificate.pem")
    
    # Security checks
    for f in [key_path, cert_path, Path(input_pdf_path)]:
        if not f.exists():
            raise FileNotFoundError(f"File not found: {f}")

    try:
        print("again")
        # 1. Initialize signer with credentials
        signer = signers.SimpleSigner.load(
            key_file=key_path,
            cert_file=cert_path,
            key_passphrase=None  # Remove if no passphrase
        )
        print("passed1")
        # 2. Prepare PDF with strict permissions
        with open(input_pdf_path, "rb") as f_in:
            writer = IncrementalPdfFileWriter(f_in)
            writer.set_root_edit_permission(allow=False)  # Blocks all edits
            print("passed2")
            # 3. Create advanced signature metadata
            meta = PdfSignatureMetadata(
                field_name="SecureSignature",
                certification_level=signers.CertificationLevel.CERTIFIED_NO_CHANGES_ALLOWED,
                subfilter=SigSeedSubFilter.PADES,
                reason="Legally Binding Document",
                location="Secure Signing Server",
                contact_info="verification@yourdomain.com",
                embed_validation_info=True,
                use_pades_lta=True,
                # Visible signature appearance settings
                appearance_text={
                    'signer': "AUTHORIZED SIGNATURE",
                    'date': "Date: %(signing_time)s",
                    'location': "Location: %(signing_location)s"
                }
            )
            print("passed3")
            # 4. Create custom stamp with QR code
            qr_img = qrcode.make("https://verify.yourdomain.com/doc123").get_image()
            qr_stamp = QRStampStyle(
                background=images.PdfImage(qr_img),
                stamp_text="Scan to verify\nDocument ID: DOC-123-456",
                text_color="red"
            )
            print("passed4")
            # 5. Configure page watermarks
            watermark = TextStampStyle(
                stamp_text="CONFIDENTIAL - DO NOT COPY",
                # background=StampStyle.Background.OPAQUE,
                text_color=(0.9, 0.1, 0.1),  # Red color
                font_size=18,
                border_width=2
            )
            print("passed5")
            # 6. Create PDF signer with all security features
            pdf_signer = PdfSigner(
                signature_meta=meta,
                signer=signer,
                stamp_style=qr_stamp,
                watermark=watermark,
                page_security=True  # Apply watermark to all pages
            )
            print("passed6")
            # 7. Perform signing
            with open(output_pdf_path, 'wb') as f_out:
                pdf_signer.sign_pdf(writer, output=f_out)

            print(f"Created fully locked PDF: {output_pdf_path}")
            return True
        
    except Exception as e:
        print(f"Signing failed: {str(e)}")
        return False

# # Example usage
# create_fully_locked_signed_pdf("input.pdf", "secured_output.pdf")