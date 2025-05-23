from pyhanko.sign import signers,fields,timestamps
from pyhanko_certvalidator import ValidationContext
from pyhanko_certvalidator.fetchers.aiohttp_fetchers import AIOHttpFetcherBackend
from pyhanko.sign.timestamps.aiohttp_client import AIOHttpTimeStamper
from pyhanko.sign.fields import SigSeedSubFilter
from pyhanko.pdf_utils.incremental_writer import IncrementalPdfFileWriter
import aiohttp
import asyncio
from cryptography.hazmat.primitives.serialization import pkcs12
from cryptography.hazmat.backends import default_backend
from asn1crypto import x509, pem
from io import BytesIO
from pyhanko import stamp
from pyhanko.pdf_utils import text, images
from PyPDF2 import PdfMerger

import os
pfx_path = "/home/ranajit/Desktop/RedIntegro/Graphql/backend-graphql-django/certs/user.pfx"
if not os.path.exists(pfx_path):
    raise FileNotFoundError(f"certificate pfx file no found on this location: {pfx_path}")

try:
    with open(pfx_path, 'rb') as f:
        pfx_data = f.read()
        private_key, cert, additional_certs = pkcs12.load_key_and_certificates(
            pfx_data, b'@rR64410007751', default_backend()
        )
        print("✅ PKCS#12 loaded successfully!")
        print(f"Certificate Subject: {cert.subject}")
        
except Exception as e:
    print(f"❌ Failed to load PKCS#12: {e}")
    raise
signer = signers.SimpleSigner.load_pkcs12(
    
            pfx_file= pfx_path,
            passphrase=b'@rR64410007751',
            
        ) 
print(f"✅ Signing certificate: {signer.signing_cert.subject.human_friendly}")


def add_signed_pdf(input_pdf_path):
    singed_pdf_path = "/home/ranajit/Desktop/RedIntegro/Graphql/backend-graphql-django/media/resource_files/signed_3.pdf"
    if os.path.exists(singed_pdf_path):
        merger = PdfMerger()
        merger.append(singed_pdf_path)
        merger.append(input_pdf_path)
        merger.write(input_pdf_path)
        merger.close()
    return input_pdf_path
    



def sign_create_for_pdf(input_pdf_path: str,output_pdf_path: str):
    # Set up a timestamping client to fetch timestamps tokens
    timestamper = timestamps.HTTPTimeStamper(
        url='http://timestamp.digicert.com'
    
        )
    # Load the root CA certificate properly
    with open("/home/ranajit/Desktop/RedIntegro/Graphql/backend-graphql-django/certs/rootCA.pem", "rb") as f:
        pem_data = f.read()
        if pem.detect(pem_data):
            _, _, der_bytes = pem.unarmor(pem_data)
        else:
            der_bytes = pem_data  # fallback if already DER

        root_cert = x509.Certificate.load(der_bytes)
    signature_meta = signers.PdfSignatureMetadata(
    field_name='Signature1', md_algorithm='sha256',
    # Mark the signature as a PAdES signature
    subfilter=SigSeedSubFilter.PADES,
    # We'll also need a validation context
    # to fetch & embed revocation info.
    # validation_context=ValidationContext(allow_fetching=True,trust_roots=[root_cert]),
    # Embed relevant OCSP responses / CRLs (PAdES-LT)
    # embed_validation_info=True,
    # Tell pyHanko to put in an extra DocumentTimeStamp
    # to kick off the PAdES-LTA timestamp chain.
    use_pades_lta=True
    
    )
    # with open(input_pdf_path, 'rb') as inf:
    #     w = IncrementalPdfFileWriter(inf)
    #     fields.append_signature_field(
    #         w, sig_field_spec=fields.SigFieldSpec(
    #             'Signature1', box=(200, 600, 400, 660)
    #             )
    #         )
    #     output_buffer = BytesIO()
    #     signers.sign_pdf(
    #         w, signature_meta=signature_meta, signer=signer,
    #         timestamper=timestamper, output=output_buffer,
    #     )
    #     output_buffer.seek(0)
    #     return output_buffer
    
    page_width = 595  # for A4 in points
    box_width = 100
    box_height = 30
    margin = 20

    x1 = page_width - box_width - margin
    y1 = margin
    x2 = x1 + box_width
    y2 = y1 + box_height

    sig_box = (x1, y1, x2, y2)
    input_pdf_path = add_signed_pdf(input_pdf_path)
    with open(input_pdf_path,'rb') as inf:
        w = IncrementalPdfFileWriter(inf)
        fields.append_signature_field(
            w,sig_field_spec=fields.SigFieldSpec(
                "Signature1",box=(59.5, 10, 535.5, 252.6),
            )
        )
        pdf_signer = signers.PdfSigner(
            signature_meta= signature_meta,
            signer=signer,
            stamp_style= stamp.TextStampStyle(
                border_width= 1,
                stamp_text= 'Digital Signature!!\nPrepared by: Redintegro Consulting Solutions LLP\nSigned by: %(signer)s\nTime: %(ts)s',
                # stamp_text= 'Digital Signature!!\nPrepared by: Redintegro Consulting Solutions LLP\nSigned by: Ranajit Thomson <ranajitsahoo@redintegro.com>\nTime: %(ts)s',
                
                background= images.PdfImage("/home/ranajit/Desktop/RedIntegro/Graphql/backend-graphql-django/media/images/job logo.png"),
                background_opacity=0.4
            )   
        )  
        output_buffer = BytesIO()
        pdf_signer.sign_pdf(
            w,
            output= output_buffer
        ) 
        return output_buffer