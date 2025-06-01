from pyhanko.sign import signers, fields, timestamps
from pyhanko.sign.fields import SigSeedSubFilter
from pyhanko.pdf_utils.incremental_writer import IncrementalPdfFileWriter
from pyhanko import stamp
from pyhanko.pdf_utils import images
from cryptography.hazmat.primitives.serialization import pkcs12
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from asn1crypto import x509
from io import BytesIO
import os
from PyPDF2 import PdfMerger
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PDFSigner:
    def __init__(self):
        self.pfx_path = "/home/ranajit/Desktop/RedIntegro/Graphql/backend-graphql-django/AwesomeAI/certs2222/signer.pfx"
        self.passphrase = b'@rR64410007751'
        self.signer = None
        self._load_certificate()

    def _load_certificate(self):
        """Load the PKCS#12 certificate and initialize the signer"""
        if not os.path.exists(self.pfx_path):
            raise FileNotFoundError(f"Certificate PFX file not found at: {self.pfx_path}")

        try:
            with open(self.pfx_path, 'rb') as f:
                pfx_data = f.read()
                private_key, cert, additional_certs = pkcs12.load_key_and_certificates(
                    pfx_data, self.passphrase, backend=default_backend()
                )
                
            # Convert certificates to ASN1 format
            additional_certs_asn1 = [self._convert_cert(c) for c in additional_certs] if additional_certs else []
            cert_asn1 = self._convert_cert(cert)

            self.signer = signers.SimpleSigner.load_pkcs12(
                pfx_file=self.pfx_path,
                passphrase=self.passphrase,
                other_certs=additional_certs_asn1,
            )
            
            logger.info(f"✅ Successfully loaded certificate: {cert.subject}")
            logger.info(f"✅ Signing certificate: {self.signer.signing_cert.subject.human_friendly}")

        except Exception as e:
            logger.error(f"❌ Failed to load PKCS#12 certificate: {e}")
            raise

    @staticmethod
    def _convert_cert(cert_crypto):
        """Convert cryptography certificate to ASN1 format"""
        return x509.Certificate.load(cert_crypto.public_bytes(serialization.Encoding.DER))
    
    def add_signed_pdf(self,input_pdf_path):
        singed_pdf_path = "/home/ranajit/Desktop/RedIntegro/Graphql/backend-graphql-django/media/resource_files/signed_3.pdf"
        if os.path.exists(singed_pdf_path):
            merger = PdfMerger()
            merger.append(singed_pdf_path)
            merger.append(input_pdf_path)
            merger.write(input_pdf_path)
            merger.close()
        return input_pdf_path

    def sign_pdf(self, input_pdf_path, output_pdf_path=None):
        """
        Sign a PDF document with a digital signature
        
        Args:
            input_pdf_path (str): Path to input PDF file
            output_pdf_path (str, optional): Path to save signed PDF. If None, returns BytesIO object
            
        Returns:
            BytesIO or None: Signed PDF as BytesIO if output_pdf_path is None, otherwise None
        """
        if not os.path.exists(input_pdf_path):
            raise FileNotFoundError(f"Input PDF file not found: {input_pdf_path}")

        try:
            # Set up timestamping
            timestamper = timestamps.HTTPTimeStamper(
                url='http://timestamp.digicert.com'
            )

            # Configure signature metadata
            signature_meta = signers.PdfSignatureMetadata(
                field_name='Signature1',
                md_algorithm='sha256',
                # subfilter=SigSeedSubFilter.PADES,
                # use_pades_lta=True,
                # signer_name="Ranajit Sahoo",
                reason="Document Approval",
                location="Online",
                contact_info="support@redintegro.com",
            )

            # Set up signature appearance
            stamp_style = stamp.TextStampStyle(
                border_width=0,
                stamp_text="",
                # stamp_text='Digitally signed by Redintegro Consulting Solutions LLP\n'
                #           'Signed by: %(signer)s\n'
                #           'Date: %(ts)s',
                background=images.PdfImage("/home/ranajit/Desktop/RedIntegro/Graphql/backend-graphql-django/media/images/job logo.png"),
                background_opacity=0,
                # text_align='left',
                # font_size=8
            )

            # Read input PDF
            # input_pdf_path = self.add_signed_pdf(input_pdf_path)
            with open(input_pdf_path, 'rb') as inf:
                writer = IncrementalPdfFileWriter(inf)
                
                # Add signature field (positioned at bottom right)
                page_width = 595  # A4 width in points
                box_width = 200
                box_height = 50
                margin = 20
                
                sig_box = (
                    page_width - box_width - margin,  # x1
                    margin,                          # y1
                    page_width - margin,             # x2
                    margin + box_height              # y2
                )
                
                fields.append_signature_field(
                    writer,
                    sig_field_spec=fields.SigFieldSpec(
                        "Signature1",
                        box=(59.5, 10, 535.5, 252.6),
                    )
                )

                # Initialize PDF signer
                pdf_signer = signers.PdfSigner(
                    signature_meta=signature_meta,
                    signer=self.signer,
                    timestamper=timestamper,
                    stamp_style=stamp_style
                )

                # Sign the PDF
                output_buffer = BytesIO()
                pdf_signer.sign_pdf(writer, output=output_buffer)
                
                
                return output_buffer

        except Exception as e:
            logger.error(f"❌ Failed to sign PDF: {e}")
            raise


