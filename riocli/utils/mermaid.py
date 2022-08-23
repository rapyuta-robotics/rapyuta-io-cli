from urllib.parse import quote, unquote
import base64
import zlib
import json

def js_encode_uri_component(data):
    return quote(data)

def js_string_to_byte(data):
    return bytes(data, 'iso-8859-1')


def js_bytes_to_string(data):
    return data.decode('iso-8859-1')


def js_btoa(data):
    return base64.b64encode(data)


def js_atob(data):
    return base64.b64decode(data)


def pako_inflate_raw(data):
    decompress = zlib.decompressobj(-15)
    decompressed_data = decompress.decompress(data)
    decompressed_data += decompress.flush()
    return decompressed_data



def pako_deflate_raw(data):
    compress = zlib.compressobj(
        zlib.Z_DEFAULT_COMPRESSION, zlib.DEFLATED, -15, 8,
        zlib.Z_DEFAULT_STRATEGY)
    compressed_data = compress.compress(js_string_to_byte(js_encode_uri_component(data)))
    compressed_data += compress.flush()
    return compressed_data


data_main = """
flowchart LR
    disk:small-pvc-4[disk:small-pvc-4]
    secret:sootballs[secret:sootballs]
    network:sootballs[network:sootballs]
    package:Sootballs_SUI2[package:Sootballs SUI2] --> secret:sootballs[secret:sootballs]
    package:Sootballs_SUI2[package:Sootballs SUI2] --> secret:sootballs[secret:sootballs]
    package:Sootballs_SUI2[package:Sootballs SUI2]
    package:Sootballs_Edge2[package:Sootballs Edge2] --> secret:sootballs[secret:sootballs]
    package:Sootballs_Edge2[package:Sootballs Edge2] --> secret:sootballs[secret:sootballs]
    package:Sootballs_Edge2[package:Sootballs Edge2]
    package:Sootballs_Robot2[package:Sootballs Robot2] --> secret:sootballs[secret:sootballs]
    package:Sootballs_Robot2[package:Sootballs Robot2] --> secret:sootballs[secret:sootballs]
    package:Sootballs_Robot2[package:Sootballs Robot2]
    package:sootballs_ims[package:sootballs_ims] --> secret:sootballs[secret:sootballs]
    package:sootballs_ims[package:sootballs_ims] --> secret:sootballs[secret:sootballs]
    package:sootballs_ims[package:sootballs_ims]
    package:sootballs_db[package:sootballs_db]
    package:MinIO_File_Server[package:MinIO File Server]
    package:sootballs_wcs[package:sootballs_wcs] --> secret:sootballs[secret:sootballs]
    package:sootballs_wcs[package:sootballs_wcs] --> secret:sootballs[secret:sootballs]
    package:sootballs_wcs[package:sootballs_wcs]
    staticroute:ims-kibarobots-apply[staticroute:ims-kibarobots-apply]
    staticroute:minio-kibarobots-apply[staticroute:minio-kibarobots-apply]
    deployment:sootballs_minio[deployment:sootballs_minio] --> package:MinIO_File_Server[package:MinIO File Server]
    deployment:sootballs_minio[deployment:sootballs_minio] --> staticroute:minio-kibarobots-apply[staticroute:minio-kibarobots-apply]
    deployment:sootballs_minio[deployment:sootballs_minio] --> disk:minio-pvc[disk:minio-pvc]
    deployment:sootballs_minio[deployment:sootballs_minio]
    deployment:sootballs_db[deployment:sootballs_db] --> package:sootballs_db[package:sootballs_db]
    deployment:sootballs_db[deployment:sootballs_db] --> disk:postgres-pvc[disk:postgres-pvc]
    deployment:sootballs_db[deployment:sootballs_db]
    deployment:sootballs_ims[deployment:sootballs_ims] --> package:sootballs_ims[package:sootballs_ims]
    deployment:sootballs_ims[deployment:sootballs_ims] --> deployment:sootballs_db[deployment:sootballs_db]
    deployment:sootballs_ims[deployment:sootballs_ims] --> deployment:sootballs_minio[deployment:sootballs_minio]
    deployment:sootballs_ims[deployment:sootballs_ims] --> staticroute:ims-kibarobots-apply[staticroute:ims-kibarobots-apply]
    deployment:sootballs_ims[deployment:sootballs_ims]
    disk:postgres-pvc[disk:postgres-pvc]
    disk:minio-pvc[disk:minio-pvc]
    staticroute:wcs-kibarobots-apply[staticroute:wcs-kibarobots-apply]
    deployment:sootballs_wcs[deployment:sootballs_wcs] --> package:sootballs_wcs[package:sootballs_wcs]
    deployment:sootballs_wcs[deployment:sootballs_wcs] --> deployment:sootballs_db[deployment:sootballs_db]
    deployment:sootballs_wcs[deployment:sootballs_wcs] --> deployment:sootballs_ims[deployment:sootballs_ims]
    deployment:sootballs_wcs[deployment:sootballs_wcs]
    deployment:sootballs_db[deployment:sootballs_db] --> package:sootballs_db[package:sootballs_db]
    deployment:sootballs_db[deployment:sootballs_db] --> disk:postgres-pvc[disk:postgres-pvc]
    deployment:sootballs_db[deployment:sootballs_db]

"""

def mermaid_link(diagram):
    obj = {
        "code": diagram,
        "mermaid": {
             "theme": "default"
        },
        "updateEditor": False,
        "autoSync": True,
        "updateDiagram": False
    }
    json_str = json.dumps(obj)
    json_bytes = js_string_to_byte(json_str)
    encoded_uri =  js_btoa( json_bytes )
    return  "https://mermaid.live/view#base64:{}".format(js_bytes_to_string(encoded_uri))



 