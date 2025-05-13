from pyhanko.sign import signers
from pyhanko.sign.signers import PdfSigner, PdfSignatureMetadata
from pyhanko_certvalidator import ValidationContext
from pyhanko.pdf_utils.incremental_writer import IncrementalPdfFileWriter
from pyhanko.sign.fields import SigFieldSpec,SigSeedSubFilter
import os

def sign_pdf_with_self_cert(input_pdf_path: str, output_pdf_path: str):
    print("entered")
    """
    Digitally sign a PDF using a self-signed certificate and private key.

    Args:
        input_pdf_path (str): Path to the input PDF file.
        output_pdf_path (str): Path where the signed PDF will be saved.

    Raises:
        FileNotFoundError: If input PDF or certificate files don't exist
        ValueError: If there are issues with the signing process
    """
    # Validate input paths
    if not os.path.exists(input_pdf_path):
        raise FileNotFoundError(f"Input PDF file not found: {input_pdf_path}")
    print("entered2")
    key_path = "/home/ranajit/Desktop/RedIntegro/Graphql/backend-graphql-django/cert/private_key.pem"
    cert_path = "/home/ranajit/Desktop/RedIntegro/Graphql/backend-graphql-django/cert/certificate.pem"
    print("entered3")

    if not os.path.exists(key_path):
        raise FileNotFoundError(f"Private key file not found: {key_path}")
    if not os.path.exists(cert_path):
        raise FileNotFoundError(f"Certificate file not found: {cert_path}")

    try:
        # Load the signer from your private key and certificate
        signer = signers.SimpleSigner.load(
            key_file=key_path,
            cert_file=cert_path,  # Provide passphrase if your key is encrypted
            
        )
        print("entered4",signer)

        # Configure validation context (optional but recommended)
        validation_context = ValidationContext(allow_fetching=False)

        # Configure PDF signer
        pdf_signer = PdfSigner(
            
            signature_meta=PdfSignatureMetadata(
                field_name="Signature1",
                # Reason for signing (optional but good practice)
                # reason="Document approval",
                # Location (optional)
                # location="Company HQ",
                # Set signing time (optional)
                # signer_name="Document Signer",
                # You can uncomment this for stricter certification
                certify=True,
                # certification_level=
                # signer_key_usage=
                # docmdp_permissions=
                md_algorithm='sha256',
                # subfilter=SigSeedSubFilter.PADES,
                # validation_context=ValidationContext(allow_fetching=True),
                # embed_validation_info=True,
                # use_pades_lta=True
            ),
            signer=signer,
            # validation_context=validation_context
            # new_field_spec=SigFieldSpec(sig_field_name="Signature1")
        )
        print("entered5",pdf_signer)
        

        with open(input_pdf_path, "rb") as f_in:
            writer = IncrementalPdfFileWriter(f_in)
            with open(output_pdf_path, "wb") as f_out:
                pdf_signer.sign_pdf(writer, output=f_out)

        print(f"Signed PDF saved to {output_pdf_path}")
        return True

    except Exception as e:
        print(f"Error signing PDF: {str(e)}")
        raise ValueError(f"PDF signing failed: {str(e)}")

# Example usage:
# sign_pdf_with_self_cert("input.pdf", "output_signed.pdf")