from tkinter import *
from pymongo import MongoClient
from colecciones.Estudiantes import iniciar_interfaz_estudiantes
from colecciones.Docentes import iniciar_interfaz_docentes
from colecciones.Administrativos import iniciar_interfaz_administrativos
from colecciones.Asignatura import iniciar_interfaz_asignaturas
from colecciones.Horario import iniciar_interfaz_horario

client = MongoClient("mongodb://localhost:27017/")
db = client["UTSH"]
collection = db["Usuarios"]

navbar_abierto = False  

def home(rol_usuario, nombre_usuario):
    if rol_usuario == "admin":
        mostrar_usuarios()
    else:
        mostrar_mensaje_usuario(nombre_usuario)

def administrativos():
    root.withdraw()
    iniciar_interfaz_administrativos(root)

def asignaturas():
    root.withdraw()
    iniciar_interfaz_asignaturas(root)

def estudiantes():
    root.withdraw()  
    iniciar_interfaz_estudiantes(root)  

def docentes():
    root.withdraw()  
    iniciar_interfaz_docentes(root)  

def horario():
    root.withdraw()
    iniciar_interfaz_horario(root)

def mostrar_usuarios():
    ventana_usuarios = Toplevel(root)
    ventana_usuarios.title("Usuarios Registrados")
    ventana_usuarios.geometry("400x300")
    usuarios = collection.find()
    for usuario in usuarios:
        Label(ventana_usuarios, text=f"Nombre: {usuario['nombre']}, Correo: {usuario['correo']}, Rol: {usuario['rol']}").pack()

def mostrar_mensaje_usuario(nombre_usuario):
    ventana_mensaje = Toplevel(root)
    ventana_mensaje.title("Bienvenido")
    ventana_mensaje.geometry("300x200")
    Label(ventana_mensaje, text=f"Hola {nombre_usuario}", font=("Arial", 14)).pack(pady=50)

def exit_app():
    root.destroy()

def abrir_navbar(rol_usuario="usuario", nombre_usuario="Usuario"):
    global navbar_abierto
    if not navbar_abierto:
        global root
        root = Tk()
        root.title("Navbar con Menu")

        menu_bar = Menu(root)

        file_menu = Menu(menu_bar, tearoff=0)
        font_config = ("Arial", 14)
        file_menu.add_command(label="Inicio", command=lambda: home(rol_usuario, nombre_usuario), background="green", foreground="white", font=font_config)
        file_menu.add_separator()
        file_menu.add_command(label="Estudiantes", command=estudiantes, background="blue", foreground="white", font=font_config)
        file_menu.add_command(label="Administrativos", command=administrativos, background="blue", foreground="white", font=font_config)
        file_menu.add_command(label="Docentes", command=docentes, background="blue", foreground="white", font=font_config)
        file_menu.add_command(label="Asignaturas", command=asignaturas, background="blue", foreground="white", font=font_config)
        file_menu.add_command(label="Horario", command=horario, background="blue", foreground="white", font=font_config)
        if rol_usuario == "admin":  # Mostrar opción solo si el rol es admin
            file_menu.add_command(label="Mostrar Usuarios", command=mostrar_usuarios, background="purple", foreground="white", font=font_config)
        else:  # Mostrar mensaje de bienvenida si el rol es usuario
            file_menu.add_command(label="Mensaje", command=lambda: mostrar_mensaje_usuario(nombre_usuario), background="purple", foreground="white", font=font_config)
        file_menu.add_separator()
        file_menu.add_command(label="Salir", command=exit_app, background="red", foreground="white", font=font_config)

        menu_bar.add_cascade(label="Menú", menu=file_menu)

        root.config(menu=menu_bar)


        root.protocol("WM_DELETE_WINDOW", exit_app)
        root.deiconify()
        navbar_abierto = True
        
        root.update_idletasks()
        root.geometry("500x500")
        root.pack_propagate(False)
        
        root.mainloop()
    else:
        root.deiconify()

if __name__ == "__main__":
    # Cambiar los valores según el usuario que inició sesión
    abrir_navbar()
