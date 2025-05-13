from pyhanko.sign import signers
from pyhanko.sign.signers import PdfSigner, SignatureMetadata
from pyhanko.sign.general import load_cert_from_pemder
from pyhanko.sign.fields import SigFieldSpec
from pyhanko.sign.signers.pdf_signer import Signer
import os

# Paths
key_path = "certs/private_key.pem"
cert_path = "certs/certificate.pem"
input_pdf_path = "input.pdf"
output_pdf_path = "signed_output.pdf"

# Load signer
signer = signers.SimpleSigner.load(
    key_file=key_path,
    cert_file=cert_path,
    key_passphrase=None  # If your key is encrypted, provide passphrase here
)

# Set up PDF signer
pdf_signer = PdfSigner(
    signature_meta=SignatureMetadata(
        field_name="Signature1",
        certification_level=signers.CertificationLevel.CERTIFIED_NO_CHANGES_ALLOWED
    ),
    signer=signer,
)

# Sign the PDF
with open(input_pdf_path, "rb") as f_in, open(output_pdf_path, "wb") as f_out:
    pdf_signer.sign_pdf(f_in, output=f_out)

print("PDF signed successfully.")
