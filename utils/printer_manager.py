import win32print
from typing import Optional, List, Dict

from src.models.Printer_model import Printer
from utils.db import db


def listar_impresoras_windows() -> List[str]:
    try:
        printers = [p[2] for p in win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS)]
        return printers
    except Exception:
        return []


def obtener_por_perfil(perfil: str, tipo: Optional[str] = None) -> Optional[Printer]:
    import json
    printers = Printer.query.filter_by(estado=1).all()
    for p in printers:
        try:
            perfiles = json.loads(p.perfil) if isinstance(p.perfil, str) else p.perfil
            tipos = json.loads(p.tipo) if isinstance(p.tipo, str) else p.tipo
            if perfil in perfiles:
                if tipo is None or tipo in tipos:
                    return p
        except:
            continue
    return None


def guardar_driver(printer_id: int, driver_name: str) -> bool:
    pr = Printer.query.get(printer_id)
    if not pr:
        return False
    pr.driver_name = driver_name
    db.session.commit()
    return True


def mapear_perfiles() -> Dict[str, Dict[str, Optional[Printer]]]:
    perfiles = ['general', 'delivery', 'mostrador', 'cocina']
    tipos = ['ticket', 'comanda', 'factura', 'cocina']
    result: Dict[str, Dict[str, Optional[Printer]]] = {}
    for perfil in perfiles:
        result[perfil] = {}
        for tipo in tipos:
            result[perfil][tipo] = obtener_por_perfil(perfil, tipo)
    return result
