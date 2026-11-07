from fastapi import FastAPI, HTTPExceptionfrom db import get_connection
app = FastAPI(title="Tienda API", version="0.1.0")

@app.get("/salud")def salud():    with get_connection() as conn:        conn.execute("SELECT 1")    return {"ok": True, "db": "tienda"}

@app.get("/productos")def listar_productos():    with get_connection() as conn:        filas = conn.execute(            """            SELECT id, nombre, descripcion, precio, stock, activo, imagen_url            FROM productos            WHERE activo = TRUE            ORDER BY id            """        ).fetchall()    return [        {            "id": f["id"],            "nombre": f["nombre"],            "descripcion": f["descripcion"],            "precio": float(f["precio"]),            "stock": f["stock"],            "activo": f["activo"],            "imagen_url": f["imagen_url"],        }        for f in filas    ]

@app.get("/productos/{producto_id}")def obtener_producto(producto_id: int):    with get_connection() as conn:        fila = conn.execute(            """            SELECT id, nombre, descripcion, precio, stock, activo, imagen_url            FROM productos            WHERE id = %s            """,            (producto_id,),        ).fetchone()    if fila is None:        raise HTTPException(status_code=404, detail="Producto no encontrado")    return {        "id": fila["id"],        "nombre": fila["nombre"],        "descripcion": fila["descripcion"],        "precio": float(fila["precio"]),        "stock": fila["stock"],        "activo": fila["activo"],        "imagen_url": fila["imagen_url"],    }





