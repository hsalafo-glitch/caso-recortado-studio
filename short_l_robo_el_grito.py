from lote14 import cargar
globals().update(cargar("robo-el-grito"))

if __name__ == "__main__":
    import generar_short as g
    configurar()
    g.main()
