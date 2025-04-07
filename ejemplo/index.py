from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import pymongo
from bson.objectid import ObjectId

# Configuración de MongoDB
MONGO_HOST = "localhost"
MONGO_PUERTO = "27017"
MONGO_URI = f"mongodb://{MONGO_HOST}:{MONGO_PUERTO}/"
MONGO_BASE_DATOS = "escuela"
MONGO_COLECCION = "alumnos"

# Conexión con MongoDB
cliente = pymongo.MongoClient(MONGO_URI, serverSelectionTimeoutMS=1000)
baseDatos = cliente[MONGO_BASE_DATOS]
coleccion = baseDatos[MONGO_COLECCION]

ID_ALUMNO = ""  # Variable global para almacenar el ID seleccionado

# Función para mostrar datos en la tabla
def mostrarDatos(tabla):
    try:
        tabla.delete(*tabla.get_children())  # Limpiar la tabla antes de actualizar
        for documento in coleccion.find(): 
            tabla.insert('', 'end', text=documento["_id"], values=(documento["nombre"], documento["sexo"], documento["calificacion"]))
    except pymongo.errors.ConnectionFailure as error:
        print("Error de conexión con MongoDB:", error)

# Función para crear un nuevo registro
def crearRegistro():
    nombre_val = nombre.get().strip()
    sexo_val = sexo.get().strip()
    calificacion_val = calificacion.get().strip()

    if nombre_val and sexo_val and calificacion_val:
        try:
            documento = {"nombre": nombre_val, "sexo": sexo_val, "calificacion": calificacion_val}
            coleccion.insert_one(documento)
            mostrarDatos(tabla)  
            limpiarCampos()
        except pymongo.errors.ConnectionFailure as error:
            print("Error de conexión con MongoDB:", error)
    else:
        messagebox.showwarning("Advertencia", "Todos los campos son obligatorios")

# Función para manejar doble clic en la tabla
def dobleClickTabla(event):
    global ID_ALUMNO
    try:
        ID_ALUMNO = tabla.item(tabla.selection())["text"]
        documento = coleccion.find_one({"_id": ObjectId(ID_ALUMNO)})

        if documento:
            nombre.delete(0, END)
            nombre.insert(0, documento["nombre"])
            sexo.delete(0, END)
            sexo.insert(0, documento["sexo"])
            calificacion.delete(0, END)
            calificacion.insert(0, documento["calificacion"])

            crear.config(state="disabled")
            editar.config(state="normal")
            borrar.config(state="normal")
    except Exception as e:
        print("Error al seleccionar elemento:", e)

# Función para editar un registro
def editarRegistro():
    global ID_ALUMNO
    nombre_val = nombre.get().strip()
    sexo_val = sexo.get().strip()
    calificacion_val = calificacion.get().strip()

    if nombre_val and sexo_val and calificacion_val:
        try:
            idBuscar = {"_id": ObjectId(ID_ALUMNO)}
            nuevosValores = {"$set": {"nombre": nombre_val, "sexo": sexo_val, "calificacion": calificacion_val}}
            coleccion.update_one(idBuscar, nuevosValores)
            mostrarDatos(tabla)
            limpiarCampos()
        except pymongo.errors.ConnectionFailure as error:
            print("Error de conexión con MongoDB:", error)
    else:
        messagebox.showwarning("Advertencia", "Todos los campos son obligatorios")
    
    crear.config(state="normal")
    editar.config(state="disabled")
    borrar.config(state="disabled")

# Función para borrar un registro
def borrarRegistro():
    global ID_ALUMNO
    try:
        idBuscar = {"_id": ObjectId(ID_ALUMNO)}
        coleccion.delete_one(idBuscar)
        mostrarDatos(tabla)
        limpiarCampos()
        ID_ALUMNO = ""  # Reiniciar variable global después de borrar
    except pymongo.errors.ConnectionFailure as error:
        print("Error de conexión con MongoDB:", error)

    crear.config(state="normal")
    editar.config(state="disabled")
    borrar.config(state="disabled")

# Función para limpiar los campos
def limpiarCampos():
    nombre.delete(0, END)
    sexo.delete(0, END)
    calificacion.delete(0, END)

# Interfaz gráfica con Tkinter
ventana = Tk()
ventana.title("Gestión de Alumnos")
ventana.geometry("400x300")

# Tabla para mostrar los datos
tabla = ttk.Treeview(ventana, columns=("Nombre", "Sexo", "Calificación"))
tabla.grid(row=1, column=0, columnspan=2, padx=10, pady=10)
tabla.heading("#0", text="ID")
tabla.heading("Nombre", text="Nombre")
tabla.heading("Sexo", text="Sexo")
tabla.heading("Calificación", text="Calificación")
tabla.bind("<Double-1>", dobleClickTabla)

# Mostrar datos al inicio
mostrarDatos(tabla)

# Campos de entrada
Label(ventana, text="Nombre:").grid(row=2, column=0, padx=5, pady=5)
nombre = Entry(ventana)
nombre.grid(row=2, column=1, padx=5, pady=5)

Label(ventana, text="Sexo:").grid(row=3, column=0, padx=5, pady=5)
sexo = Entry(ventana)
sexo.grid(row=3, column=1, padx=5, pady=5)

Label(ventana, text="Calificación:").grid(row=4, column=0, padx=5, pady=5)
calificacion = Entry(ventana)
calificacion.grid(row=4, column=1, padx=5, pady=5)

# Botones
crear = Button(ventana, text="Crear", command=crearRegistro, bg="green", fg="white")
crear.grid(row=5, columnspan=2, padx=10, pady=10)

editar = Button(ventana, text="Editar", command=editarRegistro, bg="yellow", fg="black")
editar.grid(row=6, columnspan=2)
editar.config(state="disabled")

borrar = Button(ventana, text="Borrar", command=borrarRegistro, bg="red", fg="white")
borrar.grid(row=7, columnspan=2)
borrar.config(state="disabled")

ventana.mainloop()
