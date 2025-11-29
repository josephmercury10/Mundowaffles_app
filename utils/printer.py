import win32print
import win32api
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class ThermalPrinter:
    def __init__(self, printer_name=None):
        """
        Inicializa la impresora térmica usando Windows Print Spooler
        printer_name: nombre de la impresora en Windows (ej: "EPSON TM-T88V Receipt5")
        Si es None, usa la impresora predeterminada
        """
        self.printer_name = printer_name
        self.printer = None
        
        try:
            if not printer_name:
                # Usar impresora predeterminada
                self.printer = win32print.GetDefaultPrinter()
                logger.info(f"Usando impresora predeterminada: {self.printer}")
            else:
                self.printer = printer_name
                logger.info(f"Impresora seleccionada: {self.printer}")
                
        except Exception as e:
            logger.error(f"Error al inicializar impresora: {str(e)}")
            self.printer = None
    
    def imprimir_pedido(self, pedido, cliente, items, total_con_envio):
        """
        Imprime el detalle completo del pedido en formato de recibo
        """
        if not self.printer:
            logger.error("Impresora no disponible")
            return False
        
        try:
            # Crear contenido de impresión
            contenido = self._generar_recibo(pedido, cliente, items, total_con_envio)
            
            # Imprimir usando Windows Print Spooler
            hprinter = win32print.OpenPrinter(self.printer)
            
            try:
                # Enviar contenido a la impresora
                win32print.StartDocPrinter(hprinter, 1, ("Recibo Pedido", None, "RAW"))
                win32print.StartPagePrinter(hprinter)
                
                # Convertir contenido a bytes y enviar
                contenido_bytes = contenido.encode('utf-8', errors='replace')
                win32print.WritePrinter(hprinter, contenido_bytes)
                
                win32print.EndPagePrinter(hprinter)
                win32print.EndDocPrinter(hprinter)
                
                logger.info(f"Pedido {pedido.id} impreso exitosamente")
                return True
                
            finally:
                win32print.ClosePrinter(hprinter)
                
        except Exception as e:
            logger.error(f"Error al imprimir: {str(e)}")
            return False
    
    def _generar_recibo(self, pedido, cliente, items, total_con_envio):
        """Genera el contenido del recibo en formato texto"""
        
        lineas = []
        ancho = 42  # Ancho estándar para 80mm
        
        # Encabezado
        lineas.append(self._centrar("MUNDO WAFFLES", ancho))
        lineas.append(self._centrar("Delivery", ancho))
        lineas.append(self._centrar("=" * ancho, ancho))
        lineas.append("")
        
        # Información del pedido
        lineas.append(f"Pedido #: {pedido.id}")
        lineas.append(f"Fecha: {pedido.fecha_hora.strftime('%d/%m/%Y %H:%M')}")
        lineas.append("")
        
        # Información del cliente
        lineas.append("CLIENTE:")
        if cliente and cliente.persona:
            lineas.append(f"  {cliente.persona.razon_social}")
            lineas.append(f"  Tel: {cliente.persona.telefono}")
            lineas.append(f"  Dir: {cliente.persona.direccion}")
        lineas.append("")
        
        lineas.append(self._centrar("=" * ancho, ancho))
        lineas.append("")
        
        # Items
        lineas.append("ITEMS:")
        lineas.append("")
        
        for item in items:
            cantidad = item.cantidad
            producto = item.producto.nombre[:30]  # Limitar longitud
            precio_venta = float(item.precio_venta)
            subtotal = cantidad * precio_venta
            
            lineas.append(f"{producto}")
            lineas.append(f"  x{cantidad} @ ${precio_venta:.2f} = ${subtotal:.2f}")
            
            # Atributos si existen
            if item.atributos_seleccionados:
                import json
                try:
                    atributos = json.loads(item.atributos_seleccionados)
                    for key, value in atributos.items():
                        lineas.append(f"    - {key}: {value}")
                except:
                    pass
            
            lineas.append("")
        
        # Resumen
        lineas.append(self._centrar("=" * ancho, ancho))
        lineas.append("")
        
        subtotal = float(pedido.total)
        costo_envio = float(pedido.costo_envio) if pedido.costo_envio else 0
        total = subtotal + costo_envio
        
        lineas.append(f"Subtotal:              ${subtotal:>8.2f}")
        lineas.append(f"Envío:                 ${costo_envio:>8.2f}")
        lineas.append("-" * ancho)
        lineas.append(f"TOTAL:                 ${total:>8.2f}")
        lineas.append("")
        lineas.append("")
        
        # Estado
        estado_texto = {
            1: "EN PREPARACION",
            2: "EN CAMINO",
            3: "ENTREGADO"
        }.get(pedido.estado_delivery, "DESCONOCIDO")
        
        lineas.append(self._centrar(f"Estado: {estado_texto}", ancho))
        lineas.append("")
        lineas.append(self._centrar("Gracias por su compra!", ancho))
        lineas.append("")
        lineas.append("")
        lineas.append("")
        
        return "\n".join(lineas)
    
    def imprimir_pedido_mostrador(self, pedido, items):
        """
        Imprime el detalle de un pedido de mostrador
        """
        if not self.printer:
            logger.error("Impresora no disponible")
            return False
        
        try:
            contenido = self._generar_recibo_mostrador(pedido, items)
            
            hprinter = win32print.OpenPrinter(self.printer)
            
            try:
                win32print.StartDocPrinter(hprinter, 1, ("Recibo Mostrador", None, "RAW"))
                win32print.StartPagePrinter(hprinter)
                contenido_bytes = contenido.encode('utf-8', errors='replace')
                win32print.WritePrinter(hprinter, contenido_bytes)
                win32print.EndPagePrinter(hprinter)
                win32print.EndDocPrinter(hprinter)
                
                logger.info(f"Pedido mostrador {pedido.id} impreso exitosamente")
                return True
                
            finally:
                win32print.ClosePrinter(hprinter)
                
        except Exception as e:
            logger.error(f"Error al imprimir: {str(e)}")
            return False
    
    def _generar_recibo_mostrador(self, pedido, items):
        """Genera el contenido del recibo de mostrador"""
        
        lineas = []
        ancho = 42
        
        # Encabezado
        lineas.append(self._centrar("MUNDO WAFFLES", ancho))
        lineas.append(self._centrar("Mostrador", ancho))
        lineas.append(self._centrar("=" * ancho, ancho))
        lineas.append("")
        
        # Información del pedido
        lineas.append(f"Pedido #: {pedido.id}")
        lineas.append(f"Fecha: {pedido.fecha_hora.strftime('%d/%m/%Y %H:%M')}")
        if pedido.comentarios:
            lineas.append(f"Cliente: {pedido.comentarios}")
        lineas.append("")
        
        lineas.append(self._centrar("=" * ancho, ancho))
        lineas.append("")
        
        # Items
        lineas.append("ITEMS:")
        lineas.append("")
        
        for item in items:
            cantidad = item.cantidad
            producto = item.producto.nombre[:30]
            precio_venta = float(item.precio_venta)
            subtotal = cantidad * precio_venta
            
            lineas.append(f"{producto}")
            lineas.append(f"  x{cantidad} @ ${precio_venta:.2f} = ${subtotal:.2f}")
            lineas.append("")
        
        # Resumen
        lineas.append(self._centrar("=" * ancho, ancho))
        lineas.append("")
        
        total = float(pedido.total)
        lineas.append("-" * ancho)
        lineas.append(f"TOTAL:                 ${total:>8.2f}")
        lineas.append("")
        lineas.append("")
        
        lineas.append(self._centrar("Gracias por su compra!", ancho))
        lineas.append("")
        lineas.append("")
        lineas.append("")
        
        return "\n".join(lineas)
    
    def _centrar(self, texto, ancho):
        """Centra texto en el ancho especificado"""
        if len(texto) >= ancho:
            return texto[:ancho]
        espacios = (ancho - len(texto)) // 2
        return " " * espacios + texto
    
    def cerrar(self):
        """Cierra la conexión con la impresora"""
        pass  # Windows Print Spooler se cierra automáticamente


def get_printer(app=None):
    """
    Obtiene instancia de impresora según configuración
    Configurar en config.py:
    PRINTER_NAME = 'EPSON TM-T88V Receipt5'
    """
    if app is None:
        from flask import current_app
        app = current_app
    
    printer_name = app.config.get('PRINTER_NAME', None)
    return ThermalPrinter(printer_name)