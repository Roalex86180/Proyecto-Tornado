import streamlit as st
import pandas as pd
from datetime import date
import numpy as np
import os
from datetime import datetime
import io
import shutil



def vaciar_bases_de_datos(clave_usuario):
    CLAVE_SECRETA = "Ethan2024"

    if clave_usuario != CLAVE_SECRETA:
        st.error("❌ Clave incorrecta. No se realizó ninguna acción.")
        return

    archivos = ["animales.csv", "bajas.csv", "leche.csv", "rotacion_potreros.csv"]
    
    for archivo in archivos:
        if os.path.exists(archivo):
            df = pd.read_csv(archivo)
            columnas = df.columns
            df_vacio = pd.DataFrame(columns=columnas)
            df_vacio.to_csv(archivo, index=False)

    st.success("✅ Bases de datos vaciadas correctamente (archivos conservados con encabezados intactos).")

def main():
    st.title("⚙️Datos de la Finca")


    ARCHIVO = "animales.csv"
    BAJAS = "bajas.csv"
    LECHE = "leche.csv"
    ROTACIONES = "rotacion_potreros.csv"
    RESPALDO = "backup_bajas.csv"


    menu = st.sidebar.radio("Seleccione el tipo de registro:", ["Registro de animales", "Registro de bajas", "Produccion Leche", 
            "Rotacion de Potreros", "Edicion Tipo de Animales","Borrar base de datos"], key="form_menu_radio")
    # Cargar datos existentes, forzando ID como str y parseo fechas


# -----------------------------------
# Cargar archivo de animales
# -----------------------------------
    try:
        df = pd.read_csv(
            ARCHIVO,
            parse_dates=["Fecha", "Fecha Nacimiento", "Fecha Adquisición"],
            dtype={"ID": str}
        )
    except FileNotFoundError:
        df = pd.DataFrame(columns=[
            "Fecha", "Tipo", "Partos", "Cantidad", "Procedencia",
            "Peso Promedio", "Hierro", "ID", "Potrero", "Comentarios",
            "Fecha Nacimiento", "Fecha Adquisición"
        ])
        df.to_csv(ARCHIVO, index=False)
    except ValueError:
        df = pd.read_csv(ARCHIVO, dtype={"ID": str})
        for col in ["Fecha", "Fecha Nacimiento", "Fecha Adquisición"]:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')

    if "df_original" not in st.session_state:
        st.session_state.df_original = df.copy()

    df_original = df.copy()  # Para comparar luego o hacer respaldo
    animales = df.copy()     # Si prefieres seguir usando "animales"
    
    # -----------------------------------
    # Cargar archivo de rotaciones
    # -----------------------------------
    try:
        rotaciones = pd.read_csv(ROTACIONES)
    except FileNotFoundError:
        rotaciones = pd.DataFrame(columns=[
            "Fecha Rotacion", "Tipo", "Nombre",
            "Potrero_Anterior", "Potrero_Nuevo", "Comentario"
        ])

    # -----------------------------------
    # Cargar archivo de leche
    # -----------------------------------
    try:
        df_leche = pd.read_csv(LECHE, parse_dates=["Fecha"])
    except FileNotFoundError:
        df_leche = pd.DataFrame(columns=["Fecha", "Litros", "Precio"])

    # -----------------------------------
    # Cargar archivo de respaldo (bajas)
    # -----------------------------------
    try:
        df_respaldo = pd.read_csv(
            RESPALDO,
            dtype={"ID": str},
            parse_dates=["Fecha", "Fecha Nacimiento", "Fecha Adquisición", "Fecha_baja"]
        )
    except FileNotFoundError:
        df_respaldo = pd.DataFrame(columns=[
            "Fecha", "Tipo", "Partos", "Cantidad", "Procedencia",
            "Peso Promedio", "Hierro", "ID", "Potrero", "Comentarios",
            "Fecha Nacimiento", "Fecha Adquisición", "Fecha_baja"
        ])

    

    if menu == "Registro de animales":
            

            if "tipo" not in st.session_state:
                st.session_state["tipo"] = "Seleccione"

            if "id_input" not in st.session_state:
                st.session_state["id_input"] = ""

            if "comentarios_input" not in st.session_state:
                st.session_state["comentarios_input"] = ""

            if "peso_input" not in st.session_state or not isinstance(st.session_state["peso_input"], (int, float)):
                st.session_state["peso_input"] = 0.0
            
            
            st.title("Formulario de Registro de Animales")

            

            tipo_animal = st.selectbox("Tipo de Animal", ["Seleccione",
                "Becerro", "Becerra", "Maute", "Mauta", "Novilla",
                "Toro", "Vaca", "Vaca Preñada", "Vaca de ordeño"
            ],key="tipo")

            if tipo_animal == "Seleccione":
                st.warning("Debe seleccionar un Tipo de Animal")
                

            if tipo_animal in ["Vaca", "Vaca Preñada", "Vaca de ordeño"]:
                partos = st.number_input("Indique cuántos partos tiene", min_value=0, value=0, step=1, key="partos_input")
            else:
                partos = None


            procedencia = st.selectbox("Procedencia", ["Nacido en finca", "Adquirido"])

            st.markdown("### Fechas")

            fecha_nacimiento = None
            fecha_adquisicion = None

            if procedencia == "Nacido en finca":
                fecha_nacimiento = pd.to_datetime(st.date_input("Fecha de nacimiento", value=date.today())).normalize()
            else:
                fecha_adquisicion = pd.to_datetime(st.date_input("Fecha de adquisición", value=date.today())).normalize()

            
            peso_promedio = st.number_input("Peso promedio (kg)", min_value=0.0, step=0.1, key="peso_input")

            hierro = st.selectbox("¿Tiene hierro?", ["Seleccione", "Sí", "No"])
            if hierro == "Seleccione":
                st.warning("Debe seleccionar una opción para el campo 'Hierro'.")
                


            
            id_key = "id_input"
            id_unico = st.text_input("ID del animal (opcional)", key=id_key).strip()
            

            potrero = st.selectbox("Potrero", ["Seleccione", "Potrero 1","Potrero 2","Potrero 3",
            "Potrero 4","Potrero 5","Potrero 6","Potrero 7","Potrero 8","Potrero 9"])
            if potrero == "Seleccione":
                st.warning("Debe seleccionar un Potrero")
            
            comentarios = st.text_area("Comentarios", key="comentarios_input")

            # Validación de tipo y edad
            hoy = pd.Timestamp.today().normalize()
            tipo_final = tipo_animal
            if tipo_animal in ["Becerro", "Becerra"] and procedencia == "Nacido en finca":
                edad_dias = (hoy - fecha_nacimiento).days
                if edad_dias > 240:
                    tipo_final = "Maute" if tipo_animal == "Becerro" else "Mauta"
            elif tipo_animal in ["Maute", "Mauta"] and procedencia == "Nacido en finca":
                edad_dias = (hoy - fecha_nacimiento).days
                if edad_dias < 240:
                    st.warning("No se puede registrar Maute o Mauta con menos de 240 días.")
                    st.stop()

            if st.button("Guardar registro"):


                if id_unico:
                    df["ID"] = df["ID"].astype(str)  # Asegurar comparación correcta
                    if id_unico in df["ID"].values:
                        st.error("⚠️ Ya existe un animal con ese ID. Por favor, ingrese uno diferente.")
                        st.stop()


                nuevo_registro = {
                    "Fecha": hoy,
                    "Tipo": tipo_final,
                    "Partos": partos if partos is not None else np.nan,
                    "Cantidad": 1,
                    "Procedencia": procedencia,
                    "Peso Promedio": peso_promedio,
                    "Hierro": hierro,
                    "ID": id_unico if id_unico else np.nan,
                    "Potrero": potrero,
                    "Comentarios": comentarios,
                    "Fecha Nacimiento": fecha_nacimiento if procedencia == "Nacido en finca" else pd.NaT,
                    "Fecha Adquisición": fecha_adquisicion if procedencia == "Adquirido" else pd.NaT
                }

                # Para evitar FutureWarning, excluimos columnas vacías o NA del nuevo registro
                # Construimos DataFrame de nuevo registro con solo columnas que existen en df
                columnas_validas = [col for col in df.columns if col in nuevo_registro]
                df_nuevo = pd.DataFrame([{k: nuevo_registro[k] for k in columnas_validas}])

                df = pd.concat([df, df_nuevo], ignore_index=True)

                # Asegurar que ID sea string antes de guardar (para conservar ceros a la izquierda)
                df["ID"] = df["ID"].astype(str)

                df.to_csv(ARCHIVO, index=False)
                for key in ["id_input", "peso_input", "comentarios_input", "tipo"]:
                    if key in st.session_state:
                        del st.session_state[key]
                st.success("Registro guardado exitosamente.")
                st.rerun()

            if st.button("Deshacer último registro"):
                if not df.equals(st.session_state.df_original):
                    df = st.session_state.df_original.copy()
                    df.to_csv(ARCHIVO, index=False)
                    st.success("Último registro eliminado.")
                    for key in ["id_input", "peso_input", "comentarios_input", "tipo"]:
                        if key in st.session_state:
                            del st.session_state[key]
                    st.rerun()
                else:
                    st.warning("No hay registros nuevos para deshacer.")

            st.subheader("Animales registrados")
            st.dataframe(df)


            #---------------------------------------------------------#
            #------------Registro de Bajas----------------------------#
            #---------------------------------------------------------#

    if menu == "Registro de bajas":
            
        def registrar_bajas():

            if "seleccion_input" not in st.session_state or not isinstance(st.session_state["seleccion_input"], list):
                st.session_state["seleccion_input"] = []

            if "comentariosb_input" not in st.session_state:
                st.session_state["comentariosb_input"] = ""

            st.header("📉 Registro de Bajas de Animales")

            # Cargar archivos
            df_animales = pd.read_csv(ARCHIVO, parse_dates=["Fecha", "Fecha Nacimiento", "Fecha Adquisición"], dtype={"ID": str})
            df_bajas = pd.read_csv(BAJAS) if os.path.exists(BAJAS) else pd.DataFrame(columns=["Fecha_baja", "Tipo", "Motivo", "Comentarios"])
            df_bajas["Fecha_baja"] = pd.to_datetime(df_bajas["Fecha_baja"], errors="coerce")
            df_respaldo = pd.read_csv(RESPALDO) if os.path.exists(RESPALDO) else pd.DataFrame()

            modo = st.radio("Selecciona modo de baja", ["Por ID", "Por Tipo"])

            if modo == "Por ID":
                df_animales["ID"] = df_animales["ID"].astype(str)
                id_seleccionado = st.selectbox("Selecciona ID del animal a dar de baja", df_animales["ID"].unique())
                st.dataframe(df_animales)

                motivo = st.selectbox("Motivo de la baja", ["Venta", "Muerte", "Otros"])
                fecha = st.date_input("Fecha de la baja")
                comentario = st.text_area("Comentarios")

                if st.button("Registrar baja por ID"):
                    fila = df_animales[df_animales["ID"] == id_seleccionado]
                    if fila.empty:
                        st.error("ID no encontrado.")
                    else:
                        # Guardar respaldo
                        respaldo_actual = fila.assign(Fecha_baja=fecha.strftime("%Y-%m-%d"))

                        if os.path.exists(RESPALDO):
                            df_respaldo_existente = pd.read_csv(RESPALDO, dtype={"ID": str})
                            df_respaldo = pd.concat([df_respaldo_existente, respaldo_actual], ignore_index=True)
                        else:
                            df_respaldo = respaldo_actual

                        df_respaldo.to_csv(RESPALDO, index=False)

                        # Agregar a df_bajas
                        df_bajas = pd.concat([df_bajas, pd.DataFrame([{
                            "Fecha_baja": pd.to_datetime(fecha),
                            "Tipo": fila.iloc[0]["Tipo"],
                            "Motivo": motivo,
                            "Comentarios": comentario
                        }])], ignore_index=True)

                        # Eliminar del archivo principal
                        df_animales = df_animales[df_animales["ID"] != id_seleccionado]
                        df_animales.to_csv(ARCHIVO, index=False)
                        df_bajas.to_csv(BAJAS, index=False)

                        st.success("Baja registrada exitosamente.")
                        st.subheader("Registro actualizado (animales.csv)")
                        st.dataframe(df_animales)
                        st.subheader("Registro de bajas reciente")
                        st.dataframe(df_bajas.tail(5))

                # Sección para deshacer
                st.subheader("🔁 Deshacer última baja")

                if st.button("Deshacer última baja por ID"):

                    if os.path.exists(RESPALDO) and os.path.exists(ARCHIVO) and os.path.exists(BAJAS):
                        respaldo = pd.read_csv(RESPALDO, dtype={"ID": str})
                        df_animales = pd.read_csv(ARCHIVO, dtype={"ID": str})
                        df_bajas = pd.read_csv(BAJAS, dtype={"ID": str})

                        if respaldo.empty:
                            st.info("ℹ️ No hay registros en respaldo para deshacer.")
                        else:
                            # Detectar la fecha más reciente en respaldo (última tanda de bajas)
                            ultima_fecha = respaldo["Fecha_baja"].max()

                            # Filas que tienen esa última fecha (última tanda)
                            filas_restaurar = respaldo[respaldo["Fecha_baja"] == ultima_fecha].copy()

                            # Eliminar columna Fecha_baja para agregar a animales
                            filas_restaurar_sin_fecha = filas_restaurar.drop(columns=["Fecha_baja"], errors="ignore")

                            # Restaurar en animales.csv
                            df_animales = pd.concat([df_animales, filas_restaurar_sin_fecha], ignore_index=True)
                            df_animales.to_csv(ARCHIVO, index=False)

                            # Eliminar estas filas del respaldo
                            respaldo = respaldo[respaldo["Fecha_baja"] != ultima_fecha]
                            respaldo.to_csv(RESPALDO, index=False)

                            # Eliminar de bajas.csv las filas con esa fecha
                            df_bajas = df_bajas[df_bajas["Fecha_baja"] != ultima_fecha]
                            df_bajas.to_csv(BAJAS, index=False)

                            st.success(f"✅ Se deshizo la última baja por ID de fecha {ultima_fecha}.")
                            st.dataframe(df_animales)

                    else:
                        st.warning("⚠️ No existen archivos necesarios para deshacer.")


            else:  # Por Tipo
                st.subheader("Dar de baja por tipo de animal")

                tipo_baja = st.selectbox("Selecciona el tipo de animal", df_animales["Tipo"].unique())
                df_filtrado = df_animales[df_animales["Tipo"] == tipo_baja]

                st.info(f"Actualmente existen {len(df_filtrado)} animales del tipo '{tipo_baja}'.")

                cantidad_baja = st.number_input("Ingrese la cantidad a dar de baja", min_value=1, max_value=len(df_filtrado), step=1)
                motivo = st.selectbox("Motivo de la baja", ["Venta", "Muerte", "Otros"])
                comentario = st.text_input("Comentarios", key="comentariosb_input")
                fecha_baja = st.date_input("Fecha de la baja")

                st.write("Selecciona las filas a eliminar:")
                seleccion_indices = st.multiselect("Selecciona por índice", df_filtrado.index.tolist(), key="seleccion_input")
                st.dataframe(df_filtrado)

                if st.button("Registrar bajas por tipo"):
                    if len(seleccion_indices) != cantidad_baja:
                        st.warning("La cantidad seleccionada no coincide con la cantidad que ingresaste.")
                    else:
                        fecha_str = fecha_baja.strftime("%Y-%m-%d")

                        bajas_nuevas_full = df_animales.loc[seleccion_indices].copy()
                        bajas_nuevas = bajas_nuevas_full[["Tipo"]].copy()
                        bajas_nuevas["Fecha_baja"] = pd.to_datetime(fecha_str)
                        bajas_nuevas["Motivo"] = motivo
                        bajas_nuevas["Comentarios"] = comentario
                        bajas_nuevas = bajas_nuevas[["Fecha_baja", "Tipo", "Motivo", "Comentarios"]]

                        df_bajas = pd.concat([df_bajas, bajas_nuevas], ignore_index=True)
                        df_bajas.to_csv(BAJAS, index=False)

                        # Guardar respaldo
                        nuevo_respaldo = bajas_nuevas_full.copy()
                        nuevo_respaldo["Fecha_baja"] = fecha_str

                        if os.path.exists(RESPALDO):
                            respaldo_existente = pd.read_csv(RESPALDO, dtype={"ID": str})
                            respaldo = pd.concat([respaldo_existente, nuevo_respaldo], ignore_index=True)
                        else:
                            respaldo = nuevo_respaldo

                        respaldo.to_csv(RESPALDO, index=False)

                        # Eliminar animales dados de baja del archivo principal
                        df_animales = df_animales.drop(index=seleccion_indices)
                        df_animales.to_csv(ARCHIVO, index=False)

                        st.success("Baja registrada exitosamente.")
                        for key in ["seleccion_input", "comentariosb_input"]:
                            if key in st.session_state:
                                del st.session_state[key]

                        st.subheader("Registro actualizado (animales.csv)")
                        st.dataframe(df_animales)
                        st.subheader("Registro de bajas (bajas.csv)")
                        st.dataframe(df_bajas)

               # Bloque para deshacer el último cambio
                # Bloque para deshacer el último cambio
                if st.button("Deshacer última baja"):

                    if os.path.exists(RESPALDO) and os.path.exists(ARCHIVO) and os.path.exists(BAJAS):
                        respaldo = pd.read_csv(RESPALDO, dtype={"ID": str})
                        df_animales = pd.read_csv(ARCHIVO, dtype={"ID": str})
                        df_bajas = pd.read_csv(BAJAS, dtype={"ID": str})

                        if respaldo.empty:
                            st.info("ℹ️ No hay registros en respaldo para deshacer.")
                        else:
                            # Obtener la fecha de baja de la primera fila (última tanda dada de baja)
                            ultima_fecha = respaldo.iloc[0]["Fecha_baja"]

                            # Verificamos que esa fecha aún exista en bajas.csv
                            if ultima_fecha not in df_bajas["Fecha_baja"].values:
                                st.info("ℹ️ Esa baja ya fue deshecha previamente. No hay nada que restaurar.")
                            else:
                                # Filas que tienen esa última fecha (última tanda)
                                filas_restaurar = respaldo[respaldo["Fecha_baja"] == ultima_fecha].copy()

                                # Eliminar columna Fecha_baja para agregar a animales
                                filas_restaurar_sin_fecha = filas_restaurar.drop(columns=["Fecha_baja"], errors="ignore")

                                # Restaurar en animales.csv evitando duplicados exactos
                                df_animales = pd.concat([df_animales, filas_restaurar_sin_fecha], ignore_index=True)
                                df_animales = df_animales.drop_duplicates()
                                df_animales.to_csv(ARCHIVO, index=False)

                                # Eliminar estas filas del respaldo
                                respaldo = respaldo[respaldo["Fecha_baja"] != ultima_fecha]
                                respaldo.to_csv(RESPALDO, index=False)

                                # Eliminar de bajas.csv las filas con esa fecha
                                df_bajas = df_bajas[df_bajas["Fecha_baja"] != ultima_fecha]
                                df_bajas.to_csv(BAJAS, index=False)

                                st.success(f"✅ Se deshizo la última baja de fecha {ultima_fecha}.")
                                st.dataframe(df_animales)



        registrar_bajas()


    if menu == "Produccion Leche":


            st.subheader("🥛 Registro de Producción de Leche")

            df_leche["Fecha"] = pd.to_datetime(df_leche["Fecha"], format="%Y-%m-%d", errors="coerce")

            # Formulario de ingreso
            fecha = st.date_input("Fecha de producción", value=datetime.today())
            litros = st.number_input("Litros producidos en el día", min_value=0.0, step=1.0)
            precio = st.number_input("Precio por litro ($)", min_value=0.0, step=0.01)

            # Botón para guardar
            if st.button("Guardar producción"):
                fecha_str = pd.to_datetime(fecha).strftime("%Y-%m-%d")
                
                if fecha_str in df_leche["Fecha"].dt.strftime("%Y-%m-%d").values:
                    st.warning(f"Ya existe un registro de leche para el día {fecha_str}.")
                else:
                    nueva_fila = pd.DataFrame([{
                        "Fecha": fecha,
                        "Litros": litros,
                        "Precio": precio
                    }])
                    df_leche = pd.concat([df_leche, nueva_fila], ignore_index=True)
                    df_leche.to_csv(LECHE, index=False)
                    st.success(f"Registro guardado correctamente para el día {fecha_str}.")

            # Mostrar registros actuales
            st.subheader("📄 Registros de Producción de Leche")
            st.dataframe(df_leche.sort_values("Fecha", ascending=False).reset_index(drop=True))

        



    if menu == "Rotacion de Potreros":


            
        
            POTREROS = [f"Potrero {i}" for i in range(1, 10)]

            if os.path.exists(ARCHIVO):
                animales = pd.read_csv(ARCHIVO, dtype={"ID": str})
                animales["ID"] = animales["ID"].apply(lambda x: x.zfill(5) if pd.notnull(x) else "")
            else:
                st.error("No se encontró el archivo de animales.")

            # Cargar historial de rotaciones
            if os.path.exists(ROTACIONES):
                rotaciones = pd.read_csv(ROTACIONES)
            else:
                rotaciones = pd.DataFrame(columns=["Fecha Rotacion", "Tipo", "Potrero_Anterior", "Potrero_Nuevo", "Comentario", "Cantidad"])

            st.subheader("Rotación por tipo de animal")

            tipos_disponibles = animales["Tipo"].unique().tolist()
            tipo = st.selectbox("Selecciona el tipo de animal", tipos_disponibles)

            potreros_totales = [f"Potrero {i}" for i in range(1, 10)]  # Siempre muestra del 1 al 9
            potrero_anterior = st.selectbox("Selecciona el potrero actual", potreros_totales)
            potrero_nuevo = st.selectbox("Selecciona el potrero nuevo", [p for p in potreros_totales if p != potrero_anterior])

            fecha_rotacion = st.date_input("Fecha de rotación", value=date.today())
            comentario = st.text_area("Comentario", placeholder="Motivo de la rotación...")

            # Filtrar animales del tipo y potrero seleccionado
            animales_tipo = animales[(animales["Tipo"] == tipo) & (animales["Potrero"] == potrero_anterior)].copy()
            cantidad_actual = len(animales_tipo)
            st.info(f"Actualmente hay {cantidad_actual} animales tipo {tipo} en el {potrero_anterior}.")

            modo_rotacion = st.radio("¿Cómo deseas rotar?", ["Todos los animales", "Seleccionar filas específicas"])

            if modo_rotacion == "Todos los animales":
                if st.button("Rotar todos los animales de este tipo"):
                    if cantidad_actual == 0:
                        st.warning("No hay animales para rotar.")
                    else:
                        animales.loc[(animales["Tipo"] == tipo) & (animales["Potrero"] == potrero_anterior), "Potrero"] = potrero_nuevo

                        nueva_fila = {
                            "Fecha Rotacion": fecha_rotacion.strftime("%Y-%m-%d"),
                            "Tipo": tipo,
                            "Potrero_Anterior": potrero_anterior,
                            "Potrero_Nuevo": potrero_nuevo,
                            "Comentario": comentario,
                            "Cantidad": cantidad_actual
                        }
                        rotaciones = pd.concat([rotaciones, pd.DataFrame([nueva_fila])], ignore_index=True)

                        animales.to_csv(ARCHIVO, index=False)
                        rotaciones.to_csv(ROTACIONES, index=False)
                        st.success(f"Se rotaron {cantidad_actual} animales tipo {tipo} al {potrero_nuevo}.")

            else:
                indices_disponibles = animales_tipo.index.tolist()
                seleccion_indices = st.multiselect("Selecciona las filas (índices) a rotar:", indices_disponibles)

                if st.button("Rotar animales seleccionados"):
                    if not seleccion_indices:
                        st.warning("No seleccionaste ninguna fila.")
                    else:
                        animales.loc[seleccion_indices, "Potrero"] = potrero_nuevo

                        nueva_fila = {
                            "Fecha Rotacion": fecha_rotacion.strftime("%Y-%m-%d"),
                            "Tipo": tipo,
                            "Potrero_Anterior": potrero_anterior,
                            "Potrero_Nuevo": potrero_nuevo,
                            "Comentario": comentario,
                            "Cantidad": len(seleccion_indices)
                        }
                        rotaciones = pd.concat([rotaciones, pd.DataFrame([nueva_fila])], ignore_index=True)

                        animales.to_csv(ARCHIVO, index=False)
                        rotaciones.to_csv(ROTACIONES, index=False)
                        st.success(f"Se rotaron {len(seleccion_indices)} animales tipo {tipo} al {potrero_nuevo}.")

            st.subheader("⏪ Deshacer última rotación")
            if not rotaciones.empty:
                ultima = rotaciones.iloc[-1]
                st.write("Última rotación registrada:")
                st.dataframe(pd.DataFrame([ultima]))

                if st.button("Deshacer última rotación"):
                    tipo = ultima["Tipo"]
                    potrero_anterior = ultima["Potrero_Anterior"]
                    potrero_nuevo = ultima["Potrero_Nuevo"]

                    revertidos = (animales["Tipo"] == tipo) & (animales["Potrero"] == potrero_nuevo)
                    animales.loc[revertidos, "Potrero"] = potrero_anterior
                    animales["ID"] = animales["ID"].astype(str)

                    rotaciones = rotaciones.iloc[:-1]
                    animales.to_csv(ARCHIVO, index=False)
                    rotaciones.to_csv(ROTACIONES, index=False)
                    st.success("Última rotación deshecha exitosamente.")
            else:
                st.info("No hay rotaciones registradas para deshacer.")

            rotaciones = rotaciones.dropna(how="all")

            st.subheader("📜 Historial de rotaciones registradas")
            st.dataframe(rotaciones)

            st.subheader("📋 Estado actual del archivo animales.csv")
            st.dataframe(animales)



    if menu == "Edicion Tipo de Animales":
            



            ARCHIVO = "animales.csv"
            BACKUP_CAMBIOS_TIPO = "backup_cambios_tipo.csv"

            # Cargar animales
            animales = pd.read_csv(ARCHIVO, dtype={"ID": str})
            

            # Asegurar columna de fecha
            if "Fecha Cambio Tipo" not in animales.columns:
                animales["Fecha Cambio Tipo"] = ""

            st.subheader("🔁 Cambiar tipo de animal según evolución")

            # Tabla de transiciones


            # Diccionario de transiciones de tipo
            transiciones = {
                "Mauta": "Novilla",
                "Novilla": "Vaca Preñada",
                "Vaca Preñada": "Vaca de ordeño",
                "Vaca de ordeño": "Vaca",
                "Maute": "Toro"
            }

            st.subheader("🔄 Evolución de tipo de animal")

            # Selección por tipo de animal
            tipo_seleccionado = st.selectbox("Selecciona el tipo de animal a evolucionar", list(transiciones.keys()))

            # Mostrar mensaje de transición
            tipo_destino = transiciones.get(tipo_seleccionado, None)
            if tipo_destino:
                st.info(f"{tipo_seleccionado} ---- {tipo_destino}")

            # Filtrar animales de ese tipo
            animales_filtrados = animales[animales["Tipo"] == tipo_seleccionado].copy()
            #animales_filtrados.reset_index(inplace=True)

            # Mostrar DataFrame con índice para seleccionar
            st.dataframe(animales_filtrados, hide_index=True)

            # Selección por índice
            filas_a_cambiar = st.multiselect(
                "Selecciona las filas (índices) que deseas evolucionar",
                options=animales_filtrados.index.tolist()
            )

            # Botón para aplicar cambios
            if st.button("Guardar cambios de tipo"):
                animales["ID"] = animales["ID"].astype(str)
                animales.to_csv("backup_animales.csv", index=False)  # Backup
                fecha_actual = datetime.now().strftime("%Y-%m-%d")

                for idx in filas_a_cambiar:
                    animales.loc[idx, "Tipo"] = tipo_destino
                    animales.loc[idx, "Fecha Cambio Tipo"] = fecha_actual

                animales["ID"] = animales["ID"].astype(str)

                animales.to_csv(ARCHIVO, index=False)
                st.success("Cambios aplicados correctamente.")
                st.dataframe(animales.loc[filas_a_cambiar])

                # Deshacer cambio
                st.subheader("⏪ Deshacer último cambio de tipo")
                if os.path.exists("backup_animales.csv"):
                    if st.button("Deshacer último cambio"):
                        animales = pd.read_csv("backup_animales.csv", dtype={"ID": str})
                        
                        animales.to_csv(ARCHIVO, index=False)
                        st.success("Cambio deshecho. Datos restaurados.")
                        st.dataframe(animales)
                else:
                    st.info("No hay respaldo disponible para deshacer.")
            st.subheader("📋 Estado actual del archivo animales.csv")
            st.dataframe(animales)



            st.title("Gestión de Partos")

            RUTA_CSV = "animales.csv"  # Asegúrate de que el archivo esté en el mismo directorio o cambia la ruta

            # ------------------------------
            # Función para actualizar partos con respaldo
            # ------------------------------
            def actualizar_partos_con_respaldo(ruta_csv, id_vaca, nuevo_valor):
                respaldo_path = ruta_csv.replace(".csv", "_respaldo.csv")

                try:
                    df = pd.read_csv(ruta_csv, dtype={"ID": str})

                    if id_vaca not in df["ID"].values:
                        return "❌ No se encontró ninguna vaca con ese ID."

                    tipo = df.loc[df["ID"] == id_vaca, "Tipo"].values[0].lower()
                    if tipo not in ["vaca", "vaca preñada", "vaca de ordeño"]:
                        return "⚠️ El ID no corresponde a una vaca (tipo permitido: Vaca, Vaca Preñada, Vaca de Ordeño)."


                    # Guardar respaldo antes de modificar
                    shutil.copyfile(ruta_csv, respaldo_path)

                    # Actualizar partos
                    df.loc[df["ID"] == id_vaca, "Partos"] = nuevo_valor
                    df.to_csv(ruta_csv, index=False)

                    return "✅ Número de partos actualizado correctamente. Puedes deshacer si fue un error."
                
                except Exception as e:
                    return f"❌ Error al actualizar: {e}"

            # ------------------------------
            # Función para deshacer el último cambio
            # ------------------------------
            def deshacer_cambio_partos(ruta_csv):
                respaldo_path = ruta_csv.replace(".csv", "_respaldo.csv")

                if os.path.exists(respaldo_path):
                    shutil.copyfile(respaldo_path, ruta_csv)
                    os.remove(respaldo_path)
                    return "✅ Cambio deshecho. Se restauró la versión anterior."
                else:
                    return "⚠️ No se encontró respaldo para deshacer."

            # ------------------------------
            # Interfaz Streamlit
            # ------------------------------

            st.subheader("Actualizar número de partos")

            id_vaca = st.text_input("ID de la vaca")
            nuevo_parto = st.number_input("Nuevo número de partos", min_value=0, step=1)

            col1, col2 = st.columns(2)

            with col1:
                if st.button("Actualizar Partos"):
                    if id_vaca.strip() == "":
                        st.warning("⚠️ Ingresa un ID de vaca.")
                    else:
                        resultado = actualizar_partos_con_respaldo(RUTA_CSV, id_vaca.strip(), nuevo_parto)
                        st.info(resultado)

            with col2:
                if st.button("Deshacer Cambio"):
                    resultado = deshacer_cambio_partos(RUTA_CSV)
                    st.info(resultado)


    if menu == "Borrar base de datos":

        st.subheader("🧨 Vaciar base de datos")
        clave = st.text_input("Ingrese la clave secreta", type="password")
        if st.button("Vaciar bases"):
            vaciar_bases_de_datos(clave)


        

        

