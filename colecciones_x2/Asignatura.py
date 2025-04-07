from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import pymongo
from bson.objectid import ObjectId
from functools import wraps
from pydantic import BaseModel, ValidationError, constr

# Modelo de validación para los datos de asignaturas
class AsignaturaModel(BaseModel):
    id_asignatura: constr(strip_whitespace=True, min_length=1)
    nombre: constr(strip_whitespace=True, min_length=1)
    PE: constr(strip_whitespace=True, min_length=1)
    id_docente: constr(strip_whitespace=True, min_length=1)

# Función para validar datos
def validar_datos_asignatura(datos):
    try:
        return AsignaturaModel(**datos)
    except ValidationError as e:
        messagebox.showerror("Error de Validación", str(e))
        return None

def iniciar_interfaz_asignaturas(navbar_root):
    MONGO_HOST = 'mongodb://localhost/'
    MONGO_PORT = 27017
    MONGO_BASEDATOS = 'UTSH'
    MONGO_COLECCION = 'Asignatura'
    
    cliente = pymongo.MongoClient(MONGO_HOST, MONGO_PORT)
    base_datos = cliente[MONGO_BASEDATOS]
    coleccion = base_datos[MONGO_COLECCION]
    
    ID_ASIGNATURA = ""
    
    def mostrarDatosAsignaturas():
        try:
            tabla.delete(*tabla.get_children())
            for documento in coleccion.find():
                tabla.insert('', 'end', text=documento["_id"], values=(
                    documento["id_asignatura"], 
                    documento["nombre"], 
                    documento["PE"], 
                    documento["id_docente"]))
        except pymongo.errors.Connection as e:
            messagebox.showerror("Error", "Error al mostrar los datos de las asignaturas")
            
    def crearRegistroAsignatura():
        datos = {
            "id_asignatura": id_asignatura.get().strip(),
            "nombre": nombre.get().strip(),
            "PE": PE.get().strip(),
            "id_docente": id_docente.get().strip()
        }
        asignatura = validar_datos_asignatura(datos)
        if asignatura:
            try:
                coleccion.insert_one(asignatura.dict())
                mostrarDatosAsignaturas()
                limpiarCamposAsignatura()
            except pymongo.errors.PyMongoError as e:
                messagebox.showerror("Error", "Error al insertar el registro")
                
    def dobleClicAsignatura(event):
        global ID_ASIGNATURA
        
        try:
            ID_ASIGNATURA = tabla.item(tabla.selection())["text"]
            documento = coleccion.find_one({"_id": ObjectId(ID_ASIGNATURA)})
            
            if documento:
                id_asignatura.delete(0, END)
                id_asignatura.insert(0, documento["id_asignatura"])
                nombre.delete(0, END)
                nombre.insert(0, documento["nombre"])
                PE.delete(0, END)
                PE.insert(0, documento["PE"])
                id_docente.delete(0, END)
                id_docente.insert(0, documento["id_docente"])
                
                crear.config(state="disabled")
                editar.config(state="normal")
                borrar.config(state="normal")
            
        except pymongo.errors.PyMongoError as e:
            messagebox.showerror("Error", "Error al seleccionar el registro")
    
    def editarRegistroAsignatura():
        global ID_ASIGNATURA
        datos = {
            "id_asignatura": id_asignatura.get().strip(),
            "nombre": nombre.get().strip(),
            "PE": PE.get().strip(),
            "id_docente": id_docente.get().strip()
        }
        asignatura = validar_datos_asignatura(datos)
        if asignatura:
            try:
                idBuscarAsignatura = {"_id": ObjectId(ID_ASIGNATURA)}
                nuevosValoresAsignatura = {"$set": asignatura.dict()}
                coleccion.update_one(idBuscarAsignatura, nuevosValoresAsignatura)
                mostrarDatosAsignaturas()
                limpiarCamposAsignatura()
                ID_ASIGNATURA = ""
                crear.config(state="normal")
                editar.config(state="disabled")
                borrar.config(state="disabled")
            except pymongo.errors.ConnectionFailure as error:
                print("Error al editar el registro", error)                
    
    def borrarRegistroAsignatura():
        global ID_ASIGNATURA
        
        try:
            idBuscarAsignatura = {"_id": ObjectId(ID_ASIGNATURA)}
            coleccion.delete_one(idBuscarAsignatura)
            mostrarDatosAsignaturas()
            limpiarCamposAsignatura()
            ID_ASIGNATURA = ""
        except pymongo.errors.ConnectionFailure as e:
            print("Error al eliminar el registro", e)
            
        crear.config(state="normal")
        editar.config(state="disabled")
        borrar.config(state="disabled")
            
    def limpiarCamposAsignatura():
        id_asignatura.delete(0, END)
        nombre.delete(0, END)
        PE.delete(0, END)
        id_docente.delete(0, END)
        
    def volver_navbar():
        ventana.destroy()
        navbar_root.deiconify()
        
    ventana = Tk()
    ventana.title("Interfaz de Asignaturas")
    
    fuente_grande_asignatura = ('Arial', 14)
    
    Frame_tabla = Frame(ventana)
    Frame_tabla.grid(row=0, column=0, padx=10, pady=10)
    
    tabla = ttk.Treeview(Frame_tabla, columns=("id_asignatura", "nombre", "PE", "id_docente"))
    
    tabla.heading("#0", text="ID")
    tabla.heading("id_asignatura", text="ID Asignatura")
    tabla.heading("nombre", text="Nombre")
    tabla.heading("PE", text="PE")
    tabla.heading("id_docente", text="ID Docente")
    
    for col in ("#0", "id_asignatura", "nombre", "PE", "id_docente"):
        tabla.column(col, anchor=CENTER, width=100)
        
    scrollbar_x = Scrollbar(Frame_tabla, orient=HORIZONTAL, command=tabla.xview)
    scrollbar_x.pack(side=BOTTOM, fill=X)
    
    tabla.configure(xscrollcommand=scrollbar_x.set)
    
    tabla.pack(side=LEFT, fill=BOTH)
    
    mostrarDatosAsignaturas()
    
    tabla.bind("<Double-1>", dobleClicAsignatura)
    
    Label(ventana, text="ID Asignatura", font=fuente_grande_asignatura).grid(row=1, column=0, padx=10, pady=10)
    id_asignatura = Entry(ventana, font=fuente_grande_asignatura)
    id_asignatura.grid(row=1, column=1, padx=10, pady=10)
    
    Label(ventana, text="Nombre", font=fuente_grande_asignatura).grid(row=2, column=0, padx=10, pady=10)
    nombre = Entry(ventana, font=fuente_grande_asignatura)
    nombre.grid(row=2, column=1, padx=10, pady=10)
    
    Label(ventana, text="PE", font=fuente_grande_asignatura).grid(row=3, column=0, padx=10, pady=10)
    PE = Entry(ventana, font=fuente_grande_asignatura)
    PE.grid(row=3, column=1, padx=10, pady=10)
    
    Label(ventana, text="ID Docente", font=fuente_grande_asignatura).grid(row=4, column=0, padx=10, pady=10)
    id_docente = Entry(ventana, font=fuente_grande_asignatura)
    id_docente.grid(row=4, column=1, padx=10, pady=10)
    
    crear = Button(ventana, text="Crear", font=fuente_grande_asignatura, command=crearRegistroAsignatura, bg="green", fg="white")
    crear.grid(row=5, column=0, padx=10, pady=10)
    
    editar = Button(ventana, text="Editar", font=fuente_grande_asignatura, command=editarRegistroAsignatura, bg="blue", fg="white")
    editar.grid(row=5, column=1, padx=10, pady=10)
    editar.config(state="disabled")
    
    borrar = Button(ventana, text="Borrar", font=fuente_grande_asignatura, command=borrarRegistroAsignatura, bg="red", fg="white")
    borrar.grid(row=5, column=2, padx=10, pady=10)
    borrar.config(state="disabled")
    
    volver_navbar = Button(ventana, text="Volver", font=fuente_grande_asignatura, command=volver_navbar, bg="blue", fg="white")
    volver_navbar.grid(row=5, column=3, padx=10, pady=10)
    
    ventana.update_idletasks()
    ventana_ancho = ventana.winfo_width()
    ventana_alto = ventana.winfo_height()
    ventana.geometry(f"{ventana_ancho}x{ventana_alto}")
    
    ventana.mainloop()