from flask import Flask, request, jsonify
from flask_cors import CORS
import win32print

app = Flask(__name__)
CORS(app)


@app.get('/health')
def health():
    return jsonify({'status': 'ok', 'version': '1.0.0'})


@app.post('/print/raw')
def print_raw():
    data = request.get_json(force=True, silent=True) or {}
    driver = data.get('driver')
    content = data.get('content', '')
    feed = int(data.get('feed', 3))
    cut = bool(data.get('cut', True))
    if not driver or not content:
        return jsonify({'ok': False, 'error': 'driver y content requeridos'}), 400

    try:
        hprinter = win32print.OpenPrinter(driver)
        try:
            win32print.StartDocPrinter(hprinter, 1, ("RAW", None, "RAW"))
            win32print.StartPagePrinter(hprinter)
            win32print.WritePrinter(hprinter, content.encode('utf-8', errors='replace'))
            # Opcional: no tenemos util FEED_LINES aquí; simple avance con saltos
            win32print.WritePrinter(hprinter, ("\n" * feed).encode('utf-8'))
            if cut:
                # GS V 1 (corte parcial)
                win32print.WritePrinter(hprinter, b"\x1dV\x01")
            win32print.EndPagePrinter(hprinter)
            win32print.EndDocPrinter(hprinter)
        finally:
            win32print.ClosePrinter(hprinter)
        return jsonify({'ok': True})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8765)
