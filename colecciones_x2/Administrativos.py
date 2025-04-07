from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import pymongo
from bson.objectid import ObjectId
import logging
from pydantic import BaseModel, ValidationError, constr

# Configurar el registro de actividades
logging.basicConfig(filename="actividades.log", level=logging.INFO, format="%(asctime)s - %(message)s")

def registrar_actividad(mensaje):
    logging.info(mensaje)

# Modelo de validación para los datos de administrativos
class AdministrativoModel(BaseModel):
    id_m: constr(strip_whitespace=True, min_length=1)

# Función para validar datos
def validar_datos_administrativo(datos):
    try:
        return AdministrativoModel(**datos)
    except ValidationError as e:
        messagebox.showerror("Error de Validación", str(e))
        return None

def iniciar_interfaz_administrativos(navbar_root):
    
    MONGO_HOST = "localhost"
    MONGO_PUERTO = "27017"
    MONGO_URI = f"mongodb://{MONGO_HOST}:{MONGO_PUERTO}/"
    MONGO_BASE_DATOS = "UTSH"
    MONGO_COLECCION = "Administrativos"
    
    # Conexión de MongoDB
    cliente = pymongo.MongoClient(MONGO_URI, serverSelectionTimeoutMS=1000)
    baseDatos = cliente[MONGO_BASE_DATOS]
    coleccion = baseDatos[MONGO_COLECCION]
    
    ID_ADMINISTRATIVO = "" 
    
    # Función para mostrar datos en la tabla DE ADMINISTRATIVOS
    def mostrarDatosAdministrativo(tabla):
        try:
            tabla.delete(*tabla.get_children())  
            for documento in coleccion.find():
                tabla.insert('', 'end', text=documento["_id"], values=(
                    documento["id_m"]))
                
        except pymongo.errors.ConnectionFailure as error:
            print("Error de conexion con MongoDB:", error)
            
    # Función para crear un nuevo registro
    def crearRegistroAdministrativo():
        datos = {"id_m": id_m.get().strip()}
        administrativo = validar_datos_administrativo(datos)
        if administrativo:
            try:
                coleccion.insert_one(administrativo.dict())
                mostrarDatosAdministrativo(tabla)
                limpiarCamposAdministrativo()
                registrar_actividad(f"Registro creado: {administrativo.id_m}")
            except pymongo.errors.ConnectionFailure as error:
                print("Error de conexion con MongoDB:", error)
                registrar_actividad(f"Error al crear registro: {str(error)}")
        else:
            messagebox.showwarning("Advertencia", "Todos los campos son obligatorios")
            
    # Función para manejar doble clic en la tabla
    def dobleClickTablaAdministrativo(event):
        
        global ID_ADMINISTRATIVO
        
        try:
            ID_ADMINISTRATIVO = tabla.item(tabla.selection())["text"]
            documento = coleccion.find_one({"_id": ObjectId(ID_ADMINISTRATIVO)})
            
            if documento:
                id_m.delete(0, END)
                id_m.insert(0, documento["id_m"])
                
                crear.config(state="disabled")
                editar.config(state="normal")
                borrar.config(state="normal")
            
        except pymongo.errors.ConnectionFailure as error:
            print("Error de conexion con MongoDB:", error)
            
    # Función para editar un registro de administrativo
    def editarRegistroAdministrativo():
        
        global ID_ADMINISTRATIVO
        
        datos = {"id_m": id_m.get().strip()}
        administrativo = validar_datos_administrativo(datos)
        if administrativo:
            try:
                idBuscar = {"_id": ObjectId(ID_ADMINISTRATIVO)}
                nuevosValoresAdministrativo = {"$set": administrativo.dict()}
                coleccion.update_one(idBuscar, nuevosValoresAdministrativo)
                mostrarDatosAdministrativo(tabla)
                limpiarCamposAdministrativo()
                registrar_actividad(f"Registro editado: {administrativo.id_m}")
            except pymongo.errors.ConnectionFailure as error:
                print("Error de conexion con MongoDB:", error)
                registrar_actividad(f"Error al editar registro: {str(error)}")
                
        else:
            messagebox.showwarning("Advertencia", "Todos los campos son obligatorios")
            crear.config(state="normal")
            editar.config(state="disabled")
            borrar.config(state="disabled")
    
    # Función para borrar un registro de administrativo
    def borrarRegistroAdministrativo():
        
        global ID_ADMINISTRATIVO
        
        try:
            idBuscar = {"_id": ObjectId(ID_ADMINISTRATIVO)}
            coleccion.delete_one(idBuscar)
            mostrarDatosAdministrativo(tabla)
            limpiarCamposAdministrativo()
            
            id_administrativo = ""
            registrar_actividad(f"Registro borrado: {ID_ADMINISTRATIVO}")
            
        except pymongo.errors.ConnectionFailure as error:
            print("Error de conexion con MongoDB:", error)
            registrar_actividad(f"Error al borrar registro: {str(error)}")
            
        crear.config(state="normal")
        editar.config(state="disabled")
        borrar.config(state="disabled")
        
    # Función para limpiar campos de administrativo
    def limpiarCamposAdministrativo():
        id_m.delete(0, END)
        
    #funcion para volver al navbar
    def volver_navbar():
        ventana.destroy()
        navbar_root.deiconify()
        
    #interfaz de administrativos
    ventana = Tk()
    ventana.title("Administrativos")
    
    fuente_grande = ('Arial', 14)
    
    #creacion de la tabla
    tabla = ttk.Treeview(ventana, columns=("id_m"))
    tabla.grid(row=1, column=0, columnspan=2)
    tabla.heading("#0", text="ID")
    
    mostrarDatosAdministrativo(tabla)
    
    #evento del doble click
    tabla.bind("<Double-1>", dobleClickTablaAdministrativo)
    
    
    #campos de entrada
    Label(ventana, text="ID:").grid(row=2, column=0, padx=5, pady=5)
    id_m = Entry(ventana, font=fuente_grande)
    id_m.grid(row=2, column=1)
    
    #botones    
    crear = Button(ventana, text="Crear", font=fuente_grande, command=crearRegistroAdministrativo, bg="green", fg="white")
    crear.grid(row=3, column=0, padx=10, pady=10)
    
    editar = Button(ventana, text="Editar", font=fuente_grande, state="disabled", command=editarRegistroAdministrativo, bg="yellow", fg="white")
    editar.grid(row=3, column=1, padx=10, pady=10)
    editar.config(state="disabled")
    
    borrar = Button(ventana, text="Borrar", font=fuente_grande, state="disabled", command=borrarRegistroAdministrativo, bg="red", fg="white")
    borrar.grid(row=4, column=0, padx=10, pady=10)
    borrar.config(state="disabled")
    
    volverAdministrativo = Button(ventana, text="Volver al navbar", font=fuente_grande, command=volver_navbar, bg="orange", fg="white")
    volverAdministrativo.grid(row=4, column=1, padx=10, pady=10)
    
    
    ventana.update_idletasks()
    ventana_ancho = ventana.winfo_width()
    ventana_alto = ventana.winfo_height()
    ventana.geometry(f"{ventana_ancho}x{ventana_alto}")
    
    ventana.mainloop()