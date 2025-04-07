from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import pymongo
from bson.objectid import ObjectId
import re
from pydantic import BaseModel, ValidationError, constr

def iniciar_interfaz_horario(navbar_root):
    MONGO_HOST = 'localhost'
    MONGO_PUERTO = 27017
    MONGO_URI = f"mongodb://{MONGO_HOST}:{MONGO_PUERTO}/"
    MONGO_BASEDATOS = 'UTSH'
    MONGO_COLECCION = 'Horario'
    
    cliente = pymongo.MongoClient(MONGO_URI, serverSelectionTimeoutMS=1000)
    baseDatos = cliente[MONGO_BASEDATOS]
    coleccion = baseDatos[MONGO_COLECCION]
    
    global ID_HORARIO, id_horario, fecha, id_docente, id_asignatura, id_estudiante, crear, editar, borrar, tabla
    
    ID_HORARIO = ""
    
    # Modelo de validación para los datos de horarios
    class HorarioModel(BaseModel):
        id_horario: constr(strip_whitespace=True, min_length=1)
        fecha: constr(strip_whitespace=True, min_length=1)
        id_docente: constr(strip_whitespace=True, min_length=1)
        id_asignatura: constr(strip_whitespace=True, min_length=1)
        id_estudiante: constr(strip_whitespace=True, min_length=1)

    # Función para validar datos
    def validar_datos_horario(datos):
        try:
            return HorarioModel(**datos)
        except ValidationError as e:
            messagebox.showerror("Error de Validación", str(e))
            return None
    
    #funcion para mostrar los datos en la tabla horario
    def mostrarDatosHorario(tabla):
        try:
            tabla.delete(*tabla.get_children())
            for documento in coleccion.find():
                tabla.insert('', 'end', text=str(documento["_id"]), values=(
                    documento["id_horario"], 
                    documento["fecha"],
                    documento["id_docente"], 
                    documento["id_asignatura"], 
                    documento["id_estudiante"]))
        except pymongo.errors.ConnectionFailure as error:
            print("Error", "Error al mostrar los datos del horario", error)
            
    #funcion para crear un nuevo registro en la tabla horario
    def crearRegistroHorario():
        datos = {
            "id_horario": id_horario.get().strip(),
            "fecha": fecha.get().strip(),
            "id_docente": id_docente.get().strip(),
            "id_asignatura": id_asignatura.get().strip(),
            "id_estudiante": id_estudiante.get().strip()
        }
        horario = validar_datos_horario(datos)
        if horario:
            try:
                coleccion.insert_one(horario.dict())
                mostrarDatosHorario(tabla)
                limpiarCamposHorario()
            except pymongo.errors.ConnectionFailure as error:
                print("Error", "Error al insertar el registro", error)
            
    #funcion para doble clic en la tabla horario
    def dobleClickHorario(event):
        global ID_HORARIO, id_horario, fecha, id_docente, id_asignatura, id_estudiante, crear, editar, borrar
        
        try:
            ID_HORARIO = tabla.item(tabla.selection())["text"]
            documento = coleccion.find_one({"_id": ObjectId(ID_HORARIO)})
            
            if documento:
                id_horario.delete(0, END)
                id_horario.insert(0, documento["id_horario"])
                
                fecha.delete(0, END)
                fecha.insert(0, documento["fecha"])
                
                id_docente.delete(0, END)
                id_docente.insert(0, documento["id_docente"])
                
                id_asignatura.delete(0, END)
                id_asignatura.insert(0, documento["id_asignatura"])
                
                id_estudiante.delete(0, END)
                id_estudiante.insert(0, documento["id_estudiante"])
                
                crear.config(state="disabled")
                editar.config(state="normal")
                borrar.config(state="normal")
                
        except pymongo.errors.ConnectionFailure as error:
            print("Error", "Error al seleccionar el registro", error)
            
    #funcion para editar un registro en la tabla horario
    def editarRegistroHorario():
        global ID_HORARIO
        datos = {
            "id_horario": id_horario.get().strip(),
            "fecha": fecha.get().strip(),
            "id_docente": id_docente.get().strip(),
            "id_asignatura": id_asignatura.get().strip(),
            "id_estudiante": id_estudiante.get().strip()
        }
        horario = validar_datos_horario(datos)
        if horario:
            try:
                idBuscarHorario = {"_id": ObjectId(ID_HORARIO)}
                nuevosValoresHorario = {"$set": horario.dict()}
                coleccion.update_one(idBuscarHorario, nuevosValoresHorario)
                mostrarDatosHorario(tabla)
                limpiarCamposHorario()
            except pymongo.errors.ConnectionFailure as error:
                print("Error", "Error al actualizar el registro", error)
            
    #funcion para eliminar un registro en la tabla horario
    def borrarRegistroHorario():
        global ID_HORARIO, id_horario, fecha, id_docente, id_asignatura, id_estudiante, crear, editar, borrar
        
        try:
            idBuscarHorario = {"_id": ObjectId(ID_HORARIO)}
            coleccion.delete_one(idBuscarHorario)
            mostrarDatosHorario(tabla)
            limpiarCamposHorario()
        except pymongo.errors.ConnectionFailure as error:
            print("Error", "Error al eliminar el registro", error)
            
        crear.config(state="normal")
        editar.config(state="disabled")
        borrar.config(state="disabled")
        
    #funcion para limpiar los campos de la tabla horario
    def limpiarCamposHorario():
        id_horario.delete(0, END)
        fecha.delete(0, END)
        id_docente.delete(0, END)
        id_asignatura.delete(0, END)
        id_estudiante.delete(0, END)
        
        
    #funcion para volver al navbar
    def volver_navbar():
        ventana.destroy()
        navbar_root.deiconify()

    # Interfaz gráfica
    ventana = Tk()
    ventana.title("Gestión de Horarios")
    #ventana.attributes('-fullscreen', True) pantalla completa

    fuente_grande = ('Arial', 14)

    # Creación de la tabla
    tabla = ttk.Treeview(ventana, columns=("id_horario", "fecha", "id_docente", "id_asignatura", "id_estudiante"))
    tabla.grid(row=1, column=0, columnspan=2)
    tabla.heading("#0", text="ID")
    tabla.heading("#1", text="ID Horario")
    tabla.heading("#2", text="Fecha")
    tabla.heading("#3", text="ID Docente")
    tabla.heading("#4", text="ID Asignatura")
    tabla.heading("#5", text="ID Estudiante")

    # Mostrar datos al inicio
    mostrarDatosHorario(tabla)

    # Asociar evento de doble clic con la tabla
    tabla.bind("<Double-1>", dobleClickHorario)

    # Campos de entrada
    Label(ventana, text="ID Horario:", font=fuente_grande).grid(row=2, column=0, padx=5, pady=5)
    id_horario = Entry(ventana, font=fuente_grande)
    id_horario.grid(row=2, column=1, padx=5, pady=5)

    Label(ventana, text="Fecha:", font=fuente_grande).grid(row=3, column=0, padx=5, pady=5)
    fecha = Entry(ventana, font=fuente_grande)
    fecha.grid(row=3, column=1, padx=5, pady=5)

    Label(ventana, text="ID Docente:", font=fuente_grande).grid(row=4, column=0, padx=5, pady=5)
    id_docente = Entry(ventana, font=fuente_grande)
    id_docente.grid(row=4, column=1, padx=5, pady=5)

    Label(ventana, text="ID Asignatura:", font=fuente_grande).grid(row=5, column=0, padx=5, pady=5)
    id_asignatura = Entry(ventana, font=fuente_grande)
    id_asignatura.grid(row=5, column=1, padx=5, pady=5)

    Label(ventana, text="ID Estudiante:", font=fuente_grande).grid(row=6, column=0, padx=5, pady=5)
    id_estudiante = Entry(ventana, font=fuente_grande)
    id_estudiante.grid(row=6, column=1, padx=5, pady=5)

    # Botones
    crear = Button(ventana, text="Crear Horario", font=fuente_grande, command=crearRegistroHorario, bg="green", fg="white")
    crear.grid(row=7, column=0, padx=10, pady=10)

    editar = Button(ventana, text="Editar Horario", font=fuente_grande, command=editarRegistroHorario, bg="yellow", fg="white")
    editar.grid(row=7, column=1, padx=10, pady=10)
    editar.config(state="disabled")

    borrar = Button(ventana, text="Borrar Horario", font=fuente_grande, command=borrarRegistroHorario, bg="red", fg="white")
    borrar.grid(row=8, column=0, padx=10, pady=10)
    borrar.config(state="disabled")
    
    volverHorario = Button(ventana, text="Volver al Navbar", font=fuente_grande, command=volver_navbar, bg="orange", fg="white")
    volverHorario.grid(row=8, column=1, padx=10, pady=10)
    
    ventana.update_idletasks()
    ventana_ancho = ventana.winfo_width()
    ventana_alto = ventana.winfo_height()
    ventana.geometry(f"{ventana_ancho}x{ventana_alto}")

    ventana.mainloop()
