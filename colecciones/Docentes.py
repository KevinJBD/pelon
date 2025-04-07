from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import pymongo
from bson.objectid import ObjectId
from cryptography.fernet import Fernet
from pydantic import BaseModel, ValidationError, constr, conint
import os

def iniciar_interfaz_docentes(navbar_root):
    MONGO_HOST = "localhost"
    MONGO_PUERTO = "27017"
    MONGO_URI = f"mongodb://{MONGO_HOST}:{MONGO_PUERTO}/"
    MONGO_BASE_DATOS = "UTSH"
    MONGO_COLECCION = "Docentes"

    try:
        cliente = pymongo.MongoClient(MONGO_URI, serverSelectionTimeoutMS=1000)
        baseDatos = cliente[MONGO_BASE_DATOS]
        coleccion = baseDatos[MONGO_COLECCION]
    except pymongo.errors.ConnectionFailure as error:
        messagebox.showerror("Error de conexión", f"No se pudo conectar a MongoDB: {error}")
        return  # Salir de la función si no hay conexión

    ID_DOCENTE = ""  # Variable global para almacenar el ID seleccionado de los docentes

    # Cargar la clave desde un archivo llamado clave.key o generar una nueva si no existe.
    def cargar_clave():
        clave_file = 'clave.key'
        if os.path.exists(clave_file):
            with open(clave_file, 'rb') as f:
                return f.read()  # Lee la clave existente
        else:
            clave = Fernet.generate_key()
            with open(clave_file, 'wb') as f:
                f.write(clave)  # Guarda la nueva clave en el archivo
            return clave

    clave = cargar_clave()
    cifrador = Fernet(clave)

    def cifrar_dato(dato):
        return cifrador.encrypt(dato.encode()).decode()

    def descifrar_dato(dato_cifrado):
        try:
            if dato_cifrado:
                # Asegurar que dato_cifrado sea una cadena
                if not isinstance(dato_cifrado, str):
                    return str(dato_cifrado)  # o lanza una excepción, dependiendo de tus necesidades

                # Calcula el padding necesario
                padding_needed = len(dato_cifrado) % 4
                if padding_needed != 0:
                    dato_cifrado += '=' * (4 - padding_needed)  # Añade el padding necesario
                return cifrador.decrypt(dato_cifrado.encode()).decode()
            else:
                return ""  # o None, dependiendo de cómo quieras manejar los valores vacíos
        except Exception as e:
            print("Error al descifrar:", e)
            return None  # O maneja el error como consideres adecuado

    # Modelo de validación para los datos de docentes
    class DocenteModel(BaseModel):
        id_docente: constr(strip_whitespace=True, min_length=1)
        nombre: constr(strip_whitespace=True, min_length=1)
        apellidos: constr(strip_whitespace=True, min_length=1)
        PE: constr(strip_whitespace=True, min_length=1)
        NEmp: constr(strip_whitespace=True, min_length=1)
        edad: conint(ge=1, le=120)
        telefono: constr(strip_whitespace=True, min_length=1)
        curp: constr(strip_whitespace=True, min_length=1)

    # Función para validar datos
    def validar_datos_docente(datos):
        try:
            return DocenteModel(**datos)
        except ValidationError as e:
            messagebox.showerror("Error de Validación", str(e))
            return None

    # Función para mostrar los datos en la tabla
    def mostrarDatosDocente(tabla):
        try:
            tabla.delete(*tabla.get_children())
            for documento in coleccion.find():
                tabla.insert('', 'end', text=documento["_id"], values=(
                    documento["id_docente"],
                    documento["nombre"],
                    documento["apellidos"],
                    documento["PE"],
                    documento["NEmp"],
                    documento["edad"],
                    documento["telefono"],
                    descifrar_dato(documento["curp"])))
        except pymongo.errors.ConnectionFailure as error:
            print("Error de conexión con MongoDB:", error)

    # Función para crear un nuevo registro
    def crearRegistroDocente():
        datos = {
            "id_docente": id_docente.get().strip(),
            "nombre": nombre.get().strip(),
            "apellidos": apellidos.get().strip(),
            "PE": PE.get().strip(),
            "NEmp": NEmp.get().strip(),
            "edad": edad.get().strip(),
            "telefono": telefono.get().strip(),
            "curp": curp.get().strip()
        }
        docente = validar_datos_docente(datos)
        if docente:
            try:
                docente_dict = docente.dict()
                docente_dict["curp"] = cifrar_dato(docente_dict["curp"])
                coleccion.insert_one(docente_dict)
                mostrarDatosDocente(tabla)
                limpiarCamposDocente()
            except pymongo.errors.ConnectionFailure as error:
                print("Error de conexión con MongoDB:", error)

    # Función para manejar doble clic en la tabla
    def dobleClickTablaDocente(event):
        global ID_DOCENTE
        try:
            ID_DOCENTE = tabla.item(tabla.selection())["text"]
            documento = coleccion.find_one({"_id": ObjectId(ID_DOCENTE)})

            if documento:
                id_docente.delete(0, END)
                id_docente.insert(0, documento["id_docente"])

                nombre.delete(0, END)
                nombre.insert(0, documento["nombre"])

                apellidos.delete(0, END)
                apellidos.insert(0, documento["apellidos"])

                PE.delete(0, END)
                PE.insert(0, documento["PE"])

                NEmp.delete(0, END)
                NEmp.insert(0, documento["NEmp"])

                edad.delete(0, END)
                edad.insert(0, documento["edad"])

                telefono.delete(0, END)
                telefono.insert(0, documento["telefono"])

                curp.delete(0, END)
                curp.insert(0, descifrar_dato(documento["curp"]))

                crear.config(state="disabled")
                editar.config(state="normal")
                borrar.config(state="normal")
        except pymongo.errors.ConnectionFailure as error:
            print("Error de conexión con MongoDB:", error)

    # Función para editar un registro de docente
    def editarRegistroDocente():
        global ID_DOCENTE
        datos = {
            "id_docente": id_docente.get().strip(),
            "nombre": nombre.get().strip(),
            "apellidos": apellidos.get().strip(),
            "PE": PE.get().strip(),
            "NEmp": NEmp.get().strip(),
            "edad": edad.get().strip(),
            "telefono": telefono.get().strip(),
            "curp": curp.get().strip()
        }
        docente = validar_datos_docente(datos)
        if docente:
            try:
                docente_dict = docente.dict()
                docente_dict["curp"] = cifrar_dato(docente_dict["curp"])
                idBuscarDocente = {"_id": ObjectId(ID_DOCENTE)}
                nuevosValoresDocente = {"$set": docente_dict}
                coleccion.update_one(idBuscarDocente, nuevosValoresDocente)
                mostrarDatosDocente(tabla)
                limpiarCamposDocente()
            except pymongo.errors.ConnectionFailure as error:
                print("Error de conexión con MongoDB:", error)

        crear.config(state="normal")
        editar.config(state="disabled")
        borrar.config(state="disabled")

    # Función para borrar un registro de docente
    def borrarRegistroDocente():
        global ID_DOCENTE
        try:
            idBuscarDocente = {"_id": ObjectId(ID_DOCENTE)}
            coleccion.delete_one(idBuscarDocente)
            mostrarDatosDocente(tabla)
            limpiarCamposDocente()
            ID_DOCENTE = ""

        except pymongo.errors.ConnectionFailure as error:
            print("Error de conexión con MongoDB:", error)

        crear.config(state="normal")
        editar.config(state="disabled")
        borrar.config(state="disabled")

    # Función para limpiar los campos de docente
    def limpiarCamposDocente():
        id_docente.delete(0, END)
        nombre.delete(0, END)
        apellidos.delete(0, END)
        PE.delete(0, END)
        NEmp.delete(0, END)
        edad.delete(0, END)
        telefono.delete(0, END)
        curp.delete(0, END)

    # Función para volver al navbar
    def volver_navbar():
        ventana.destroy()
        navbar_root.deiconify()

    # Interfaz gráfica docentes
    ventana = Tk()
    ventana.title("Gestión de Docentes")
    #ventana.attributes('-fullscreen', True) # Eliminar la pantalla completa

    fuente_grande_docente = ('Arial', 14)

    # Crear un Frame para la tabla y el scrollbar
    frame_tabla = Frame(ventana)
    frame_tabla.grid(row=1, column=0, columnspan=2)

    # Crear la tabla dentro del Frame
    tabla = ttk.Treeview(frame_tabla, columns=("id_docente", "nombre", "apellidos", "PE", "NEmp", "edad", "telefono", "curp"))
    
    # Configurar encabezados y columnas
    tabla.heading("#0", text="ID")
    tabla.heading("#1", text="ID Docente")
    tabla.heading("#2", text="Nombre")
    tabla.heading("#3", text="Apellidos")
    tabla.heading("#4", text="PE")
    tabla.heading("#5", text="NEmp")
    tabla.heading("#6", text="Edad")
    tabla.heading("#7", text="Telefono")
    tabla.heading("#8", text="CURP")

    for col in ("#0", "#1", "#2", "#3", "#4", "#5", "#6", "#7", "#8"):
        tabla.column(col, width=120)  # Ajustar ancho fijo para cada columna

    # Configurar Scrollbar horizontal
    scrollbar_x = Scrollbar(frame_tabla, orient=HORIZONTAL, command=tabla.xview)
    scrollbar_x.pack(side=BOTTOM, fill=X)

    # Asociar el Scrollbar al Treeview
    tabla.configure(xscrollcommand=scrollbar_x.set)
    
    tabla.pack(side=LEFT, fill=BOTH)

    # Mostrar datos al inicio
    mostrarDatosDocente(tabla)

    # Asociar evento de doble clic con la tabla
    tabla.bind("<Double-1>", dobleClickTablaDocente)

    # campos de entrada
    Label(ventana, text="ID Docente:", font=fuente_grande_docente).grid(row=2, column=0, padx=5, pady=5)
    id_docente = Entry(ventana, font=fuente_grande_docente)
    id_docente.grid(row=2, column=1, padx=5, pady=5)
    
    Label(ventana, text="Nombre:", font=fuente_grande_docente).grid(row=3, column=0, padx=5, pady=5)
    nombre = Entry(ventana, font=fuente_grande_docente)
    nombre.grid(row=3, column=1, padx=5, pady=5)
    
    Label(ventana, text="Apellidos:", font=fuente_grande_docente).grid(row=4, column=0, padx=5, pady=5)
    apellidos = Entry(ventana, font=fuente_grande_docente)
    apellidos.grid(row=4, column=1, padx=5, pady=5)
    
    Label(ventana, text="PE:", font=fuente_grande_docente).grid(row=5, column=0, padx=5, pady=5)
    PE = Entry(ventana, font=fuente_grande_docente)
    PE.grid(row=5, column=1, padx=5, pady=5)
    
    Label(ventana, text="NEmp:", font=fuente_grande_docente).grid(row=6, column=0, padx=5, pady=5)
    NEmp = Entry(ventana, font=fuente_grande_docente)
    NEmp.grid(row=6, column=1, padx=5, pady=5)
    
    Label(ventana, text="Edad:", font=fuente_grande_docente).grid(row=7, column=0, padx=5, pady=5)
    edad = Entry(ventana, font=fuente_grande_docente)
    edad.grid(row=7, column=1, padx=5, pady=5)
    
    Label(ventana, text="Telefono:", font=fuente_grande_docente).grid(row=8, column=0, padx=5, pady=5)
    telefono = Entry(ventana, font=fuente_grande_docente)
    telefono.grid(row=8, column=1, padx=5, pady=5)
    
    Label(ventana, text="CURP:", font=fuente_grande_docente).grid(row=9, column=0, padx=5, pady=5)
    curp = Entry(ventana, font=fuente_grande_docente)
    curp.grid(row=9, column=1, padx=5, pady=5)
    
    #botones
    crear = Button(ventana, text="Crear Docente", font=fuente_grande_docente, command=crearRegistroDocente, bg="green", fg="white")
    crear.grid(row=10, column=0, padx=10, pady=10)
    
    editar = Button(ventana, text="Editar Docente", font=fuente_grande_docente, command=editarRegistroDocente, bg="yellow", fg="black")
    editar.grid(row=10, column=1, padx=10, pady=10)
    editar.config(state="disabled")
    
    borrar = Button(ventana, text="Borrar Docente", font=fuente_grande_docente, command=borrarRegistroDocente, bg="red", fg="white")
    borrar.grid(row=11, column=0, padx=10, pady=10)
    borrar.config(state="disabled")
    
    volverDocente = Button(ventana, text="Volver al Navbar", font=fuente_grande_docente,command=volver_navbar, bg="blue", fg="white")
    volverDocente.grid(row=11, column=1, padx=10, pady=10)
    
    ventana.update_idletasks()  # Asegurarse de que todos los widgets se han dibujado
    ventana_ancho = ventana.winfo_width()
    ventana_alto = ventana.winfo_height()
    ventana.geometry(f"{ventana_ancho}x{ventana_alto}")  # Establecer el tamaño de la ventana
    
    ventana.mainloop()
