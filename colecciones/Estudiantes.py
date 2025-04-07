from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import pymongo
from bson.objectid import ObjectId
import html
from pydantic import BaseModel, ValidationError, constr, conint


def iniciar_interfaz_estudiantes(navbar_root):
    # Configuración de MongoDB
    MONGO_HOST = "localhost"
    MONGO_PUERTO = "27017"
    MONGO_URI = f"mongodb://{MONGO_HOST}:{MONGO_PUERTO}/"
    MONGO_BASE_DATOS = "UTSH"
    MONGO_COLECCION = "Estudiantes"

    CERTH_PATH = r"C:\Certificados\certificado.pem"  # Ruta al certificado

    # Conexión de MongoDB con TLS (SSL)
    cliente = pymongo.MongoClient(
        MONGO_URI,
           # Especificar el certificado
        serverSelectionTimeoutMS=1000
    )
    baseDatos = cliente[MONGO_BASE_DATOS]
    coleccion = baseDatos[MONGO_COLECCION]


    ID_ESTUDIANTE = ""  # Variable global para almacenar el ID seleccionado

    # Modelo de validación para los datos de estudiantes
    class EstudianteModel(BaseModel):
        id_estudiante: constr(strip_whitespace=True, min_length=1)
        matricula: constr(strip_whitespace=True, min_length=1)
        nombre: constr(strip_whitespace=True, min_length=1)
        apellidos: constr(strip_whitespace=True, min_length=1)
        edad: conint(ge=1, le=120)
        telefono: constr(strip_whitespace=True, min_length=1)
        curp: constr(strip_whitespace=True, min_length=1)

    # Función para validar datos
    def validar_datos_estudiante(datos):
        try:
            return EstudianteModel(**datos)
        except ValidationError as e:
            messagebox.showerror("Error de Validación", str(e))
            return None

    # Función para mostrar datos en la tabla
    def mostrarDatos(tabla):
        try:
            tabla.delete(*tabla.get_children())  # Limpiar la tabla antes de actualizar
            for documento in coleccion.find():
                tabla.insert('', 'end', text=documento["_id"], values=(
                    documento["id_estudiante"],
                    documento["matricula"],
                    documento["nombre"],
                    documento["apellidos"],
                    documento["edad"],
                    documento["telefono"],
                    documento["curp"]))
        except pymongo.errors.ConnectionFailure as error:
            print("Error de conexion con MongoDB:", error)

    # Función para crear un nuevo registro
    def crearRegistro():
        datos = {
            "id_estudiante": id_estudiante.get().strip(),
            "matricula": matricula.get().strip(),
            "nombre": nombre.get().strip(),
            "apellidos": apellidos.get().strip(),
            "edad": edad.get().strip(),
            "telefono": telefono.get().strip(),
            "curp": curp.get().strip()
        }
        estudiante = validar_datos_estudiante(datos)
        if estudiante:
            try:
                coleccion.insert_one(estudiante.dict())
                mostrarDatos(tabla)
                limpiarCampos()
            except pymongo.errors.ConnectionFailure as error:
                print("Error de conexion con MongoDB:", error)

    # Función para manejar doble clic en la tabla
    def dobleClickTabla(event):
        global ID_ESTUDIANTE
        
        try:
            ID_ESTUDIANTE = tabla.item(tabla.selection())["text"]
            documento = coleccion.find_one({"_id": ObjectId(ID_ESTUDIANTE)})

            if documento:
                id_estudiante.delete(0, END)
                id_estudiante.insert(0, documento["id_estudiante"])
                matricula.delete(0, END)
                matricula.insert(0, documento["matricula"])
                nombre.delete(0, END)
                nombre.insert(0, documento["nombre"])
                apellidos.delete(0, END)
                apellidos.insert(0, documento["apellidos"])
                edad.delete(0, END)
                edad.insert(0, documento["edad"])
                telefono.delete(0, END)
                telefono.insert(0, documento["telefono"])
                curp.delete(0, END)
                curp.insert(0, documento["curp"])

                crear.config(state="disabled")
                editar.config(state="normal")
                borrar.config(state="normal")
        except pymongo.errors.ConnectionFailure as error:
            print("Error de conexion con MongoDB:", error)

    # Función para editar un registro
    def editarRegistro():
        global ID_ESTUDIANTE
        datos = {
            "id_estudiante": id_estudiante.get().strip(),
            "matricula": matricula.get().strip(),
            "nombre": nombre.get().strip(),
            "apellidos": apellidos.get().strip(),
            "edad": edad.get().strip(),
            "telefono": telefono.get().strip(),
            "curp": curp.get().strip()
        }
        estudiante = validar_datos_estudiante(datos)
        if estudiante:
            try:
                idBuscar = {"_id": ObjectId(ID_ESTUDIANTE)}
                nuevosValores = {"$set": estudiante.dict()}
                coleccion.update_one(idBuscar, nuevosValores)
                mostrarDatos(tabla)
                limpiarCampos()
            except pymongo.errors.ConnectionFailure as error:
                print("Error de conexion con MongoDB:", error)

    # Función para borrar un registro
    def borrarRegistro():
        global ID_ESTUDIANTE
        try:
            idBuscar = {"_id": ObjectId(ID_ESTUDIANTE)}
            coleccion.delete_one(idBuscar)
            mostrarDatos(tabla)
            limpiarCampos()
            ID_ESTUDIANTE = ""
        except pymongo.errors.ConnectionFailure as error:
            print("Error de conexion con MongoDB:", error)

        crear.config(state="normal")
        editar.config(state="disabled")
        borrar.config(state="disabled")

    # Función para limpiar los campos
    def limpiarCampos():
        id_estudiante.delete(0, END)
        matricula.delete(0, END)
        nombre.delete(0, END)
        apellidos.delete(0, END)
        edad.delete(0, END)
        telefono.delete(0, END)
        curp.delete(0, END)
    
    #funcion para volver al navbar
    def volver_navbar():
        ventana.destroy()
        navbar_root.deiconify()

    # Interfaz gráfica
    ventana = Tk()
    ventana.title("Gestión de Estudiantes")
    #ventana.attributes('-fullscreen', True) pantalla completa

    fuente_grande = ('Arial', 14)

    # Creación de la tabla
    tabla = ttk.Treeview(ventana, columns=("id_estudiante", "matricula", "nombre", "apellidos", "edad", "telefono", "curp"))
    tabla.grid(row=1, column=0, columnspan=2)
    tabla.heading("#0", text="ID")
    tabla.heading("#1", text="ID Estudiante")
    tabla.heading("#2", text="Matrícula")
    tabla.heading("#3", text="Nombre")
    tabla.heading("#4", text="Apellidos")
    tabla.heading("#5", text="Edad")
    tabla.heading("#6", text="Teléfono")
    tabla.heading("#7", text="CURP")

    # Mostrar datos al inicio
    mostrarDatos(tabla)

    # Asociar evento de doble clic con la tabla
    tabla.bind("<Double-1>", dobleClickTabla)

    # Campos de entrada
    Label(ventana, text="ID Estudiante:", font=fuente_grande).grid(row=2, column=0, padx=5, pady=5)
    id_estudiante = Entry(ventana, font=fuente_grande)
    id_estudiante.grid(row=2, column=1, padx=5, pady=5)

    Label(ventana, text="Matrícula:", font=fuente_grande).grid(row=3, column=0, padx=5, pady=5)
    matricula = Entry(ventana, font=fuente_grande)
    matricula.grid(row=3, column=1, padx=5, pady=5)

    Label(ventana, text="Nombre:", font=fuente_grande).grid(row=4, column=0, padx=5, pady=5)
    nombre = Entry(ventana, font=fuente_grande)
    nombre.grid(row=4, column=1, padx=5, pady=5)

    Label(ventana, text="Apellidos:", font=fuente_grande).grid(row=5, column=0, padx=5, pady=5)
    apellidos = Entry(ventana, font=fuente_grande)
    apellidos.grid(row=5, column=1, padx=5, pady=5)

    Label(ventana, text="Edad:", font=fuente_grande).grid(row=6, column=0, padx=5, pady=5)
    edad = Entry(ventana, font=fuente_grande)
    edad.grid(row=6, column=1, padx=5, pady=5)

    Label(ventana, text="Teléfono:", font=fuente_grande).grid(row=7, column=0, padx=5, pady=5)
    telefono = Entry(ventana, font=fuente_grande)
    telefono.grid(row=7, column=1, padx=5, pady=5)

    Label(ventana, text="CURP:", font=fuente_grande).grid(row=8, column=0, padx=5, pady=5)
    curp = Entry(ventana, font=fuente_grande)
    curp.grid(row=8, column=1, padx=5, pady=5)

    # Botones
    crear = Button(ventana, text="Crear Estudiante", font=fuente_grande, command=crearRegistro, bg="green", fg="white")
    crear.grid(row=9, column=0, padx=10, pady=10)

    editar = Button(ventana, text="Editar Estudiante", font=fuente_grande, command=editarRegistro, bg="yellow", fg="white")
    editar.grid(row=9, column=1, padx=10, pady=10)
    editar.config(state="disabled")

    borrar = Button(ventana, text="Borrar Estudiante", font=fuente_grande, command=borrarRegistro, bg="red", fg="white")
    borrar.grid(row=10, column=0, padx=10, pady=10)
    borrar.config(state="disabled")
    
    volverEstudiante = Button(ventana, text="Volver al Navbar", font=fuente_grande, command=volver_navbar, bg="orange", fg="white")
    volverEstudiante.grid(row=10, column=1, padx=10, pady=10)
    
    ventana.update_idletasks()  # Asegurarse de que todos los widgets se han dibujado
    ventana_ancho = ventana.winfo_width()
    ventana_alto = ventana.winfo_height()
    ventana.geometry(f"{ventana_ancho}x{ventana_alto}")  # Establecer el tamaño de la ventana

    ventana.mainloop()
