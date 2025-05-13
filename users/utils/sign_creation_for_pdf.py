from pyhanko.sign import signers,fields
from pyhanko_certvalidator import ValidationContext
from pyhanko_certvalidator.fetchers.aiohttp_fetchers import AIOHttpFetcherBackend
from pyhanko.sign.timestamps.aiohttp_client import AIOHttpTimeStamper
from pyhanko.sign.fields import SigSeedSubFilter
from pyhanko.pdf_utils.incremental_writer import IncrementalPdfFileWriter
import aiohttp
import asyncio
from cryptography.hazmat.primitives.serialization import pkcs12
from cryptography.hazmat.backends import default_backend


import os
pfx_path = "/home/ranajit/Desktop/RedIntegro/Graphql/backend-graphql-django/cert2/certificate.pfx"
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
async def sign_create_for_pdf(input_pdf_path: str,output_pdf_path: str):
    async with aiohttp.ClientSession() as session:
    
        key_path = "/home/ranajit/Desktop/RedIntegro/Graphql/backend-graphql-django/cert/private_key.pem"
        cert_path = "/home/ranajit/Desktop/RedIntegro/Graphql/backend-graphql-django/cert/certificate.pem"
       
        
        if not os.path.exists(key_path):
            raise FileNotFoundError(f"private key file not found on this path: {key_path}")
        if not os.path.exists(cert_path):
            raise FileNotFoundError(f"Certificate file not found: {cert_path}")

        print("XXXXXX-1")
        signature_meta = signers.PdfSignatureMetadata(field_name="Redintegro")
        
        print("XXXXXX-2")
    
        
        validation_context = ValidationContext(
            fetcher_backend=AIOHttpFetcherBackend(session),
            allow_fetching=True, 
        )
        print("XXXXXX-3")
        # Similarly, we choose an RFC 3161 client implementation
        # that uses AIOHttp under the hood
        timestamper = AIOHttpTimeStamper(
            'http://timestamp.digicert.com',
            session=session
        )
        print("XXXXXX-4")
        #The signing config is otherwise the same
        settings = signers.PdfSignatureMetadata(
            field_name='AsyncSignatureExample',
            validation_context=validation_context,
            subfilter=SigSeedSubFilter.PADES,
            embed_validation_info=True
            
        )
        print("XXXXXX-5")
        with open(input_pdf_path, 'rb') as inf:
            w = IncrementalPdfFileWriter(inf)
            fields.append_signature_field(
            w, sig_field_spec=fields.SigFieldSpec(
                'AsyncSignatureExample', box=(200, 600, 400, 660)
                )
            )
            with open(output_pdf_path, 'wb') as outf:
                await signers.async_sign_pdf(
                    w, 
                    signer=signer, 
                    timestamper=timestamper,
                    signature_meta=settings,
                    output=outf
                )
            print("singed_pdf")
        