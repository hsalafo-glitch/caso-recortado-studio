from lote14 import cargar
globals().update(cargar("esquema-ponzi"))

if __name__ == "__main__":
    import generar_short as g
    configurar()
    g.main()
