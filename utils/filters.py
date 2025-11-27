def format_price(value):
    """Formatea un número como precio sin decimales con separador de miles"""
    try:
        return "{:,.0f}".format(float(value)).replace(",", ".")
    except (ValueError, TypeError):
        return "0"

def register_filters(app):
    """Registra todos los filtros personalizados"""
    app.template_filter('format_price')(format_price)