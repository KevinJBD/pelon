from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import pymongo
from bson.objectid import ObjectId
import re
from pydantic import BaseModel, ValidationError, constr
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

def iniciar_interfaz_horario(navbar_root):
    MONGO_HOST = 'localhost'
    MONGO_PUERTO = 27017
    MONGO_URI = f"mongodb://{MONGO_HOST}:{MONGO_PUERTO}/"
    MONGO_BASEDATOS = 'UTSH'
    MONGO_COLECCION = 'Horario'
    
    cliente = pymongo.MongoClient(MONGO_URI, serverSelectionTimeoutMS=1000)
    baseDatos = cliente[MONGO_BASEDATOS]
    coleccion = baseDatos[MONGO_COLECCION]
    
    global ID_HORARIO, hora_inicio_cb, hora_fin_cb, cb_docente, cb_asignatura, cb_estudiante, crear, editar, borrar, tabla_lunes, tabla_martes, tabla_miercoles, tabla_jueves, tabla_viernes

    ID_HORARIO = ""
    
    # Modelo de validación
    class HorarioModel(BaseModel):
        hora_inicio: constr(strip_whitespace=True, min_length=5, max_length=5)
        hora_fin: constr(strip_whitespace=True, min_length=5, max_length=5)
        id_docente: constr(strip_whitespace=True, min_length=1)
        id_asignatura: constr(strip_whitespace=True, min_length=1)
        id_estudiante: constr(strip_whitespace=True, min_length=1)
        dia_semana: constr(strip_whitespace=True, min_length=1)

    # Función para obtener nombres de docentes, asignaturas y estudiantes
    def obtener_nombres(coleccion):
        return {str(doc['_id']): doc['nombre'] for doc in baseDatos[coleccion].find()}

    # Generar PDF
    def generar_pdf():
        try:
            doc = SimpleDocTemplate("horario.pdf", pagesize=letter)
            elements = []
            styles = getSampleStyleSheet()

            dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"]
            for dia in dias:
                # Agregar el encabezado del día

                # Encabezados de la tabla
                data = [["Hora Inicio", "Hora Fin", "Docente", "Asignatura", "Estudiante"]]

                # Recorrer los datos de la colección y agregarlos a la tabla
                for horario in coleccion.find({"dia_semana": dia}):
                    # Obtener los nombres correspondientes a los IDs
                    docente = baseDatos['Docentes'].find_one({"_id": ObjectId(horario['id_docente'])})
                    asignatura = baseDatos['Asignaturas'].find_one({"_id": ObjectId(horario['id_asignatura'])})
                    estudiante = baseDatos['Estudiantes'].find_one({"_id": ObjectId(horario['id_estudiante'])})

                    docente_nombre = docente['nombre'] if docente else "Desconocido"
                    asignatura_nombre = asignatura['nombre'] if asignatura else "Desconocido"
                    estudiante_nombre = estudiante['nombre'] if estudiante else "Desconocido"

                    data.append([
                        horario["hora_inicio"],
                        horario["hora_fin"],
                        docente_nombre,
                        asignatura_nombre,
                        estudiante_nombre
                    ])

                # Crear la tabla con los datos
                table = Table(data, colWidths=[doc.width/5.0]*5) 
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))

                # Agregar la tabla a los elementos del documento
                elements.append(table)

            # Construir el PDF
            doc.build(elements)
            messagebox.showinfo("PDF Generado", "Archivo guardado como horario.pdf")
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar PDF: {str(e)}")

    # Validación de datos
    def validar_datos_horario(datos):
        try:
            # Validar formato de hora
            if not re.match(r'^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$', datos['hora_inicio']):
                raise ValueError("Formato de hora inicio inválido (HH:MM)")
            if not re.match(r'^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$', datos['hora_fin']):
                raise ValueError("Formato de hora fin inválido (HH:MM)")

            return HorarioModel(**datos)
        except ValidationError as e:
            messagebox.showerror("Error de Validación", str(e))
            return None
        except ValueError as e:
            messagebox.showerror("Error de Formato", str(e))
            return None

    # Mostrar datos en tabla
    def mostrarDatosHorario(tabla, dia_semana):
        try:
            tabla.delete(*tabla.get_children())

            # Obtener nombres para mostrar en lugar de IDs
            nombres_docentes = obtener_nombres('Docentes')
            nombres_asignaturas = obtener_nombres('Asignaturas')
            nombres_estudiantes = obtener_nombres('Estudiantes')

            for documento in coleccion.find({"dia_semana": dia_semana}):
                # Obtener nombres correspondientes a los IDs
                nombre_docente = nombres_docentes.get(documento['id_docente'], "Desconocido")
                nombre_asignatura = nombres_asignaturas.get(documento['id_asignatura'], "Desconocido")
                nombre_estudiante = nombres_estudiantes.get(documento['id_estudiante'], "Desconocido")

                tabla.insert('', 'end', text=str(documento["_id"]), values=(
                    documento["hora_inicio"],
                    documento["hora_fin"],
                    nombre_docente,
                    nombre_asignatura,
                    nombre_estudiante))
        except Exception as error:
            messagebox.showerror("Error", f"Error al mostrar datos: {str(error)}")

    # Crear registro
    def crearRegistroHorario():
        datos = {
            "hora_inicio": hora_inicio_cb.get().strip(),
            "hora_fin": hora_fin_cb.get().strip(),
            "id_docente": cb_docente.get().strip(),
            "id_asignatura": cb_asignatura.get().strip(),
            "id_estudiante": cb_estudiante.get().strip(),
            "dia_semana": cb_dia.get().strip()
        }

        if validar_datos_horario(datos):
            try:
                coleccion.insert_one(datos)

                # Actualizar la tabla correspondiente al día
                dia_semana = cb_dia.get().strip()
                if dia_semana == "Lunes":
                    mostrarDatosHorario(tabla_lunes, dia_semana)
                elif dia_semana == "Martes":
                    mostrarDatosHorario(tabla_martes, dia_semana)
                elif dia_semana == "Miércoles":
                    mostrarDatosHorario(tabla_miercoles, dia_semana)
                elif dia_semana == "Jueves":
                    mostrarDatosHorario(tabla_jueves, dia_semana)
                elif dia_semana == "Viernes":
                    mostrarDatosHorario(tabla_viernes, dia_semana)

                limpiarCamposHorario()
            except Exception as error:
                messagebox.showerror("Error", f"Error al crear registro: {str(error)}")

    # Doble click en tabla
    def dobleClickHorario(event, tabla):
        global ID_HORARIO
        try:
            ID_HORARIO = tabla.item(tabla.selection())["text"]
            documento = coleccion.find_one({"_id": ObjectId(ID_HORARIO)})

            if documento:
                hora_inicio_cb.set(documento["hora_inicio"])
                hora_fin_cb.set(documento["hora_fin"])
                cb_docente.set(documento["id_docente"])
                cb_asignatura.set(documento["id_asignatura"])
                cb_estudiante.set(documento["id_estudiante"])
                cb_dia.set(documento["dia_semana"])

                crear.config(state="disabled")
                editar.config(state="normal")
                borrar.config(state="normal")

        except Exception as error:
            messagebox.showerror("Error", f"Error al seleccionar registro: {str(error)}")

    # Editar registro
    def editarRegistroHorario():
        global ID_HORARIO
        datos = {
            "hora_inicio": hora_inicio_cb.get().strip(),
            "hora_fin": hora_fin_cb.get().strip(),
            "id_docente": cb_docente.get().strip(),
            "id_asignatura": cb_asignatura.get().strip(),
            "id_estudiante": cb_estudiante.get().strip(),
            "dia_semana": cb_dia.get().strip()
        }

        if validar_datos_horario(datos):
            try:
                coleccion.update_one(
                    {"_id": ObjectId(ID_HORARIO)},
                    {"$set": datos}
                )

                # Actualizar la tabla correspondiente al día
                dia_semana = cb_dia.get().strip()
                if dia_semana == "Lunes":
                    mostrarDatosHorario(tabla_lunes, dia_semana)
                elif dia_semana == "Martes":
                    mostrarDatosHorario(tabla_martes, dia_semana)
                elif dia_semana == "Miércoles":
                    mostrarDatosHorario(tabla_miercoles, dia_semana)
                elif dia_semana == "Jueves":
                    mostrarDatosHorario(tabla_jueves, dia_semana)
                elif dia_semana == "Viernes":
                    mostrarDatosHorario(tabla_viernes, dia_semana)

                limpiarCamposHorario()
            except Exception as error:
                messagebox.showerror("Error", f"Error al actualizar registro: {str(error)}")

    # Borrar registro
    def borrarRegistroHorario():
        global ID_HORARIO
        try:
            # Obtener el documento antes de borrarlo para actualizar la tabla correcta
            documento = coleccion.find_one({"_id": ObjectId(ID_HORARIO)})
            if documento:
                dia_semana = documento["dia_semana"]

                coleccion.delete_one({"_id": ObjectId(ID_HORARIO)})

                # Actualizar la tabla correspondiente al día
                if dia_semana == "Lunes":
                    mostrarDatosHorario(tabla_lunes, dia_semana)
                elif dia_semana == "Martes":
                    mostrarDatosHorario(tabla_martes, dia_semana)
                elif dia_semana == "Miércoles":
                    mostrarDatosHorario(tabla_miercoles, dia_semana)
                elif dia_semana == "Jueves":
                    mostrarDatosHorario(tabla_jueves, dia_semana)
                elif dia_semana == "Viernes":
                    mostrarDatosHorario(tabla_viernes, dia_semana)

                limpiarCamposHorario()
        except Exception as error:
            messagebox.showerror("Error", f"Error al eliminar registro: {str(error)}")

    # Limpiar campos
    def limpiarCamposHorario():
        hora_inicio_cb.set('')
        hora_fin_cb.set('')
        cb_docente.set('')
        cb_asignatura.set('')
        cb_estudiante.set('')
        cb_dia.set('')
        crear.config(state="normal")
        editar.config(state="disabled")
        borrar.config(state="disabled")

    # Volver al navbar
    def volver_navbar():
        ventana.destroy()
        navbar_root.deiconify()

    # Obtener los nombres para los comboboxes
    nombres_docentes = obtener_nombres('Docentes')
    nombres_asignaturas = obtener_nombres('Asignaturas')
    nombres_estudiantes = obtener_nombres('Estudiantes')

    # Interfaz gráfica
    ventana = Tk()
    ventana.title("Gestión de Horarios")

    # Configuración de estilo
    fuente_grande = ('Arial', 12)
    padding = 5

    # Frame principal
    main_frame = Frame(ventana)
    main_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)

    # Frame para los campos de entrada y botones
    input_frame = Frame(main_frame)
    input_frame.pack(side=TOP, fill=X)

    # Horas disponibles
    horas = [f"{hora:02d}:{minuto:02d}" for hora in range(8, 22) for minuto in (0, 30)]

    # Combobox para Hora Inicio
    Label(input_frame, text="Hora Inicio:", font=fuente_grande).grid(row=0, column=0, sticky="w", padx=padding, pady=padding)
    hora_inicio_cb = ttk.Combobox(input_frame, values=horas, state="readonly", font=fuente_grande)
    hora_inicio_cb.grid(row=0, column=1, padx=padding, pady=padding)

    # Combobox para Hora Fin
    Label(input_frame, text="Hora Fin:", font=fuente_grande).grid(row=0, column=2, sticky="w", padx=padding, pady=padding)
    hora_fin_cb = ttk.Combobox(input_frame, values=horas, state="readonly", font=fuente_grande)
    hora_fin_cb.grid(row=0, column=3, padx=padding, pady=padding)

    # Comboboxes con datos existentes
    docentes_ids = list(nombres_docentes.keys())
    asignaturas_ids = list(nombres_asignaturas.keys())
    estudiantes_ids = list(nombres_estudiantes.keys())
    dias_semana = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"]

    Label(input_frame, text="Docente:", font=fuente_grande).grid(row=1, column=0, sticky="w", padx=padding, pady=padding)
    cb_docente = ttk.Combobox(input_frame, values=docentes_ids, state="readonly", font=fuente_grande)
    cb_docente.grid(row=1, column=1, padx=padding, pady=padding)

    Label(input_frame, text="Asignatura:", font=fuente_grande).grid(row=1, column=2, sticky="w", padx=padding, pady=padding)
    cb_asignatura = ttk.Combobox(input_frame, values=asignaturas_ids, state="readonly", font=fuente_grande)
    cb_asignatura.grid(row=1, column=3, padx=padding, pady=padding)

    Label(input_frame, text="Estudiante:", font=fuente_grande).grid(row=2, column=0, sticky="w", padx=padding, pady=padding)
    cb_estudiante = ttk.Combobox(input_frame, values=estudiantes_ids, state="readonly", font=fuente_grande)
    cb_estudiante.grid(row=2, column=1, padx=padding, pady=padding)

    Label(input_frame, text="Día:", font=fuente_grande).grid(row=2, column=2, sticky="w", padx=padding, pady=padding)
    cb_dia = ttk.Combobox(input_frame, values=dias_semana, state="readonly", font=fuente_grande)
    cb_dia.grid(row=2, column=3, padx=padding, pady=padding)

    # Botones
    btn_frame = Frame(input_frame)
    btn_frame.grid(row=3, column=0, columnspan=4, pady=padding)

    crear = Button(btn_frame, text="Crear", command=crearRegistroHorario, bg="#4CAF50", fg="white", font=fuente_grande)
    crear.pack(side=LEFT, padx=padding)

    editar = Button(btn_frame, text="Editar", command=editarRegistroHorario, bg="#2196F3", fg="white", font=fuente_grande)
    editar.pack(side=LEFT, padx=padding)
    editar.config(state="disabled")

    borrar = Button(btn_frame, text="Borrar", command=borrarRegistroHorario, bg="#f44336", fg="white", font=fuente_grande)
    borrar.pack(side=LEFT, padx=padding)
    borrar.config(state="disabled")

    btn_pdf = Button(btn_frame, text="Generar PDF", command=generar_pdf, bg="#9C27B0", fg="white", font=fuente_grande)
    btn_pdf.pack(side=LEFT, padx=padding)

    volver = Button(btn_frame, text="Volver", command=volver_navbar, bg="#FF9800", fg="white", font=fuente_grande)
    volver.pack(side=LEFT, padx=padding)

    # Frame para las tablas de cada día
    tablas_frame = Frame(main_frame)
    tablas_frame.pack(side=BOTTOM, fill=BOTH, expand=True)

    # Crear un notebook para las tablas de cada día
    notebook = ttk.Notebook(tablas_frame)
    notebook.pack(fill=BOTH, expand=True)

    # Función para crear la tabla de un día específico
    def crear_tabla_dia(dia_semana):
        frame_dia = Frame(notebook)
        notebook.add(frame_dia, text=dia_semana)

        tabla_dia = ttk.Treeview(frame_dia, columns=("hora_inicio", "hora_fin", "docente", "asignatura", "estudiante"))
        tabla_dia.heading("#0", text="ID")
        tabla_dia.heading("hora_inicio", text="Hora Inicio")
        tabla_dia.heading("hora_fin", text="Hora Fin")
        tabla_dia.heading("docente", text="Docente")
        tabla_dia.heading("asignatura", text="Asignatura")
        tabla_dia.heading("estudiante", text="Estudiante")
        tabla_dia.pack(fill=BOTH, expand=True)

        # Asociar evento de doble clic a la tabla
        tabla_dia.bind("<Double-1>", lambda event: dobleClickHorario(event, tabla_dia))

        return tabla_dia

    # Crear las tablas para cada día
    tabla_lunes = crear_tabla_dia("Lunes")
    tabla_martes = crear_tabla_dia("Martes")
    tabla_miercoles = crear_tabla_dia("Miércoles")
    tabla_jueves = crear_tabla_dia("Jueves")
    tabla_viernes = crear_tabla_dia("Viernes")

    # Mostrar datos iniciales
    mostrarDatosHorario(tabla_lunes, "Lunes")
    mostrarDatosHorario(tabla_martes, "Martes")
    mostrarDatosHorario(tabla_miercoles, "Miércoles")
    mostrarDatosHorario(tabla_jueves, "Jueves")
    mostrarDatosHorario(tabla_viernes, "Viernes")

    ventana.mainloop()
