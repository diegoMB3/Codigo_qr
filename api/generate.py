from http.server import BaseHTTPRequestHandler
import io
import logging
import urllib.parse

import qrcode
from qrcode.exceptions import DataOverflowError


logger = logging.getLogger(__name__)


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            parsed_path = urllib.parse.urlparse(self.path)
            query_params = urllib.parse.parse_qs(parsed_path.query)
            text_to_encode = query_params.get('text', ['https://github.com'])[0]

            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_M,
                box_size=10,
                border=4,
            )
            try:
                qr.add_data(text_to_encode)
                qr.make(fit=True)
            except (DataOverflowError, ValueError):
                self._send_text_response(
                    400,
                    "El texto es demasiado largo para generar un código QR.",
                )
                return

            img = qr.make_image(fill_color="black", back_color="white")

            buffered = io.BytesIO()
            img.save(buffered, format="PNG")
            img_bytes = buffered.getvalue()

            self.send_response(200)
            self.send_header('Content-Type', 'image/png')
            self.send_header('Content-Length', str(len(img_bytes)))
            self.end_headers()
            self.wfile.write(img_bytes)
        except Exception:
            logger.exception("No se pudo generar el código QR")
            self._send_text_response(500, "Error interno al generar el código QR.")

    def _send_text_response(self, status_code, message):
        body = message.encode("utf-8")
        self.send_response(status_code)
        self.send_header('Content-Type', 'text/plain; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)
