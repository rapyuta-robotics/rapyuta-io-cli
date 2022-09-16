from urllib.parse import quote, unquote
import base64
import zlib
import json



def mermaid_safe(s: str):
    return s.replace(" ", "_")


def js_string_to_byte(data):
    return bytes(data, 'iso-8859-1')


def js_bytes_to_string(data):
    return data.decode('iso-8859-1')


def js_btoa(data):
    return base64.b64encode(data)



# def js_encode_uri_component(data):
#     return quote(data)


# def js_atob(data):
#     return base64.b64decode(data)

# def pako_inflate_raw(data):
#     decompress = zlib.decompressobj(-15)
#     decompressed_data = decompress.decompress(data)
#     decompressed_data += decompress.flush()
#     return decompressed_data


# def pako_deflate_raw(data):
#     compress = zlib.compressobj(
#         zlib.Z_DEFAULT_COMPRESSION, zlib.DEFLATED, -15, 8,
#         zlib.Z_DEFAULT_STRATEGY)
#     compressed_data = compress.compress(js_string_to_byte(js_encode_uri_component(data)))
#     compressed_data += compress.flush()
#     return compressed_data


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



 