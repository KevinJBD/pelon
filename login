import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from pymongo import MongoClient
import bcrypt
import re
from navbar import abrir_navbar

client = MongoClient("mongodb://localhost:27017/")
db = client["UTSH"]
collection = db["Usuarios"]

def validar_correo(correo):
    return re.match(r"[^@]+@[^@]+\.[^@]+", correo)

def validar_campos(correo, contraseña):
    if not correo or not contraseña:
        return False
    return True

def validar_login():
    global rol_usuario  # Variable global para almacenar el rol del usuario
    correo = entrada_correo.get()
    contraseña = entrada_contraseña.get()

    if not validar_campos(correo, contraseña):
        messagebox.showerror("Error", "Todos los campos son obligatorios")
        return
    if not validar_correo(correo):
        messagebox.showerror("Error", "Formato de correo inválido")
        return

    usuario = collection.find_one({"correo": correo})

    if usuario:
        if bcrypt.checkpw(contraseña.encode("utf-8"), usuario["contraseña"]):
            rol_usuario = usuario["rol"]  
            messagebox.showinfo("Login", f"Bienvenido, {usuario['nombre']}!")
            ventana.destroy() 
            abrir_navbar(rol_usuario)  # Pasar el rol al navbar
        else:
            messagebox.showerror("Error", "Contraseña incorrecta")
    else:
        messagebox.showerror("Error", "Usuario no encontrado")

def abrir_registro():
    ventana_registro = tk.Toplevel(ventana)
    ventana_registro.title("Registro")
    ventana_registro.geometry("400x300")
    ventana_registro.configure(bg="#2c3e50")

    card_registro = ttk.Frame(ventana_registro, style="Card.TFrame")
    card_registro.place(relx=0.5, rely=0.5, anchor="center")

    ttk.Label(card_registro, text="Nombre:", style="TLabel").pack(pady=5)
    entrada_nombre = ttk.Entry(card_registro, font=("Arial", 12), width=25)
    entrada_nombre.pack(pady=5)

    ttk.Label(card_registro, text="Correo:", style="TLabel").pack(pady=5)
    entrada_correo_registro = ttk.Entry(card_registro, font=("Arial", 12), width=25)
    entrada_correo_registro.pack(pady=5)

    ttk.Label(card_registro, text="Contraseña:", style="TLabel").pack(pady=5)
    entrada_contraseña_registro = ttk.Entry(card_registro, font=("Arial", 12), show="*", width=25)
    entrada_contraseña_registro.pack(pady=10)

    tk.Button(
        card_registro,
        text="Registrarse",
        font=("Arial", 12, "bold"),
        bg="#3498db",
        fg="#ffffff",
        activebackground="#2980b9",
        activeforeground="#ffffff",
        relief="flat",
        padx=20,
        pady=10,
        command=lambda: registrar_usuario(
            entrada_nombre.get(),
            entrada_correo_registro.get(),
            entrada_contraseña_registro.get(),
            ventana_registro
        )
    ).pack(pady=20)

def registrar_usuario(nombre, correo, contraseña, ventana_registro):
    if not nombre or not correo or not contraseña:
        messagebox.showerror("Error", "Todos los campos son obligatorios")
        return
    if not validar_correo(correo):
        messagebox.showerror("Error", "Formato de correo inválido")
        return

    if collection.find_one({"correo": correo}):
        messagebox.showerror("Error", "El correo ya está registrado")
        return

    contraseña_encriptada = bcrypt.hashpw(contraseña.encode("utf-8"), bcrypt.gensalt())

    nuevo_usuario = {
        "nombre": nombre,
        "correo": correo,
        "contraseña": contraseña_encriptada,
        "rol": "usuario"  
    }
    collection.insert_one(nuevo_usuario)

    messagebox.showinfo("Registro", "Usuario registrado exitosamente")
    ventana_registro.destroy()

ventana = tk.Tk()
ventana.title("Login")
ventana.geometry("500x400")
ventana.configure(bg="#2c3e50") 

estilo = ttk.Style()
estilo.configure("Card.TFrame", background="#ffffff", borderwidth=2, relief="raised", padding=20)
estilo.configure("TLabel", font=("Arial", 12), background="#ffffff", foreground="#2c3e50")

card = ttk.Frame(ventana, style="Card.TFrame")
card.place(relx=0.5, rely=0.5, anchor="center")

ttk.Label(card, text="Iniciar sesión", font=("Helvetica", 18, "bold"), background="#ffffff", foreground="#3498db").pack(pady=10)

ttk.Label(card, text="Correo:", style="TLabel").pack(pady=5)
entrada_correo = ttk.Entry(card, font=("Arial", 12), width=25)
entrada_correo.pack(pady=5)

ttk.Label(card, text="Contraseña:", style="TLabel").pack(pady=5)
entrada_contraseña = ttk.Entry(card, font=("Arial", 12), show="*", width=25)
entrada_contraseña.pack(pady=10)

tk.Button(
    card,
    text="Iniciar sesión",
    font=("Arial", 12, "bold"),
    bg="#3498db",
    fg="#ffffff",
    activebackground="#2980b9",
    activeforeground="#ffffff",
    relief="flat",
    padx=20,
    pady=10,
    command=validar_login
).pack(pady=10)

tk.Button(
    card,
    text="Registrarse",
    font=("Arial", 12, "bold"),
    bg="#2ecc71",
    fg="#ffffff",
    activebackground="#27ae60",
    activeforeground="#ffffff",
    relief="flat",
    padx=20,
    pady=10,
    command=abrir_registro
).pack(pady=10)

ventana.mainloop()
 