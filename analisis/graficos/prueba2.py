cajas_por_segundo = 10
segundos_por_minutos = 60

productos_por_caja = []
total_productos = 0

for fila in range(cajas_por_segundo):
    cantidad = int(input(f"Ingrese la cantidad de productos para la caja: {fila }.  "))
    productos_por_caja.append(cantidad)
    total_productos = total_productos + cantidad

cajas_total_minutos = cajas_por_segundo * segundos_por_minutos

for fila in range(cajas_por_segundo):
    print(f"Caja { fila + 1}. {productos_por_caja[fila]}")

print("Cantidad de productos ingresados", total_productos)
print("Cantidad de cajas por minutos", cajas_total_minutos)
