import streamlit as st
import pandas as pd
from datetime import datetime
import base64
import formulario
from streamlit_option_menu import option_menu
import plotly.express as px
import altair as alt
import os


st.set_page_config(page_title="Finca El Tornado", layout="wide")


def get_image_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


def load_data():
    animales_df = pd.read_csv("animales.csv", parse_dates=["Fecha Nacimiento", "Fecha Adquisición", "Fecha"], dtype={"ID": str})
    animales_df["Fecha Nacimiento"] = pd.to_datetime(animales_df["Fecha Nacimiento"], errors='coerce')
    animales_df["Fecha Adquisición"] = pd.to_datetime(animales_df["Fecha Adquisición"], errors='coerce')
    animales_df["Fecha"] = pd.to_datetime(animales_df["Fecha"], errors='coerce')
    
    

    leche_df = pd.read_csv("leche.csv", parse_dates=["Fecha"])
    leche_df["Fecha"] = pd.to_datetime(leche_df["Fecha"], errors='coerce')

    bajas_df = pd.read_csv("bajas.csv", parse_dates=["Fecha_baja"])
    bajas_df["Fecha_baja"] = pd.to_datetime(bajas_df["Fecha_baja"], errors='coerce')

    rotaciones_df = pd.read_csv("rotacion_potreros.csv", parse_dates=["Fecha Rotacion"])
    rotaciones_df["Fecha Rotacion"] = pd.to_datetime(rotaciones_df["Fecha Rotacion"], errors='coerce')

    return animales_df, leche_df, bajas_df, rotaciones_df


# Sidebar
with st.sidebar:
    opcion = option_menu(
        "Menú Principal",
        ["Dashboard", "Formulario"],
        icons=["bar-chart", "clipboard-check"],
        menu_icon="cast",
        default_index=0,
    )

if opcion == "Dashboard":
    img_izquierda = get_image_base64("encabezado1.jpeg")
    img_derecha = get_image_base64("encabezado2.jpeg")

    st.markdown(f"""
    <style>
    .header-container {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        background-color: #99ccff;
        padding: 20px 30px;
        border-radius: 15px;
        box-shadow: 0px 4px 12px rgba(0,0,0,0.15);
        margin-bottom: 25px;
    }}
    .header-image {{
        height: 120px;
        border-radius: 12px;
    }}
    .header-title {{
        font-size: 32px;
        font-weight: bold;
        color: #002244;
        text-align: center;
        flex-grow: 1;
    }}
    </style>

    <div class="header-container">
        <img src="data:image/jpeg;base64,{img_izquierda}" class="header-image">
        <div class="header-title"> Finca El Tornado</div>
        <img src="data:image/jpeg;base64,{img_derecha}" class="header-image">
    </div>
    """, unsafe_allow_html=True)

    animales_df, leche_df, bajas_df, rotaciones_df = load_data()

    tab1, tab2, tab3 = st.tabs(["📋 Información de Animales", "🥛 Análisis Producción Lechera", "Consulta Histórica Precio Leche"])

    with tab1:
        cantidad_disponibles = len(animales_df)

        st.header("Resumen General")

        st.markdown(
            f"""
            <div style='
                background: linear-gradient(135deg, #4FC3F7, #0288D1);
                padding: 30px;
                border-radius: 12px;
                text-align: center;
                color: white;
                font-size: 22px;
                box-shadow: 0px 4px 10px rgba(0,0,0,0.1);
            '>
                <h2 style='margin-bottom:10px;'>🐮 Total Animales</h2>
                <div style='font-size: 44px; font-weight: bold;'>{cantidad_disponibles}</div>
            </div>
            """,
            unsafe_allow_html=True
        )



        st.markdown("---")
    

        df = pd.read_csv("animales.csv")

        # Elimina espacios y valores nulos en 'Tipo'
        df["Tipo"] = df["Tipo"].astype(str).str.strip()

        # Filtra filas sin tipo válido
        df = df[df["Tipo"] != ""]

        # Agrupar por 'Tipo' y contar
        conteo_por_tipo = df.groupby("Tipo").size().reset_index(name="Cantidad")


        # Mostrar los KPIs en columnas de 3
        st.subheader("Cantidad de animales por tipo")

        

        # Convertir en lista de diccionarios para facilitar el acceso
        # Mostrar KPIs
        num_columnas = 3
        filas = (len(conteo_por_tipo) + num_columnas - 1) // num_columnas

        for fila in range(filas):
            columnas = st.columns(num_columnas)
            for col_index in range(num_columnas):
                index = fila * num_columnas + col_index
                if index < len(conteo_por_tipo):
                    tipo = conteo_por_tipo.iloc[index]["Tipo"]
                    cantidad = int(conteo_por_tipo.iloc[index]["Cantidad"])
                    columnas[col_index].markdown(
                        f"""
                        <div style='
                            background: linear-gradient(135deg, #BBDEFB, #64B5F6);
                            padding: 20px;
                            border-radius: 12px;
                            text-align: center;
                            color: #0D47A1;
                            font-size: 20px;
                            box-shadow: 0px 4px 10px rgba(0,0,0,0.1);
                            margin-bottom: 15px;
                        '>
                            <h3 style='margin-bottom:10px;'>{tipo}</h3>
                            <div style='font-size: 36px; font-weight: bold;'>{cantidad}</div> 
                        </div>
                        """,
                        unsafe_allow_html=True
                    )


        

        # cantidad de animales #
        st.markdown("---")
        # Crear gráfica

        import altair as alt

        # Asegurarse de que "Cantidad" es numérica
        animales_df["Cantidad"] = pd.to_numeric(animales_df["Cantidad"], errors="coerce")

        # Eliminar filas sin Tipo o Cantidad
        animales_df = animales_df.dropna(subset=["Tipo", "Cantidad"])

        # Agrupar por tipo y sumar cantidades
        tipos = animales_df.groupby("Tipo")["Cantidad"].sum().reset_index()

        # Colores personalizados (puedes ajustar la lista si hay más tipos)
        colores = ['#4FC3F7', '#81D4FA', '#FF6347', '#32CD32', '#FFD700', '#8A2BE2', '#FF4500', '#00BFFF'][:len(tipos)]

        # Gráfico de barras
        barras = alt.Chart(tipos).mark_bar().encode(
            x=alt.X('Tipo:N', title='Tipo de Animal'),
            y=alt.Y('Cantidad:Q', title='Cantidad'),
            color=alt.Color('Tipo:N', scale=alt.Scale(domain=tipos['Tipo'].tolist(), range=colores))
        )

        # Etiquetas encima de las barras
        etiquetas = alt.Chart(tipos).mark_text(
            align='center',
            baseline='bottom',
            dy=-5,
            color='black'
        ).encode(
            x='Tipo:N',
            y='Cantidad:Q',
            text=alt.Text('Cantidad:Q', format='.0f')
        )

        # Mostrar ambos
        st.altair_chart(barras + etiquetas, use_container_width=True)

        
        

        st.markdown("---")
        st.subheader("Distribución de Animales por Potreros")

        # Asegurarse de que Cantidad es numérica
        animales_df["Cantidad"] = pd.to_numeric(animales_df["Cantidad"], errors="coerce")

        # Eliminar filas con valores nulos en columnas clave
        animales_df = animales_df.dropna(subset=["Potrero", "Tipo", "Cantidad"])

        # Agrupar por Potrero y Tipo y sumar la columna Cantidad
        df_potrero_tipo = animales_df.groupby(['Potrero', 'Tipo'])["Cantidad"].sum().reset_index()

        # Calcular total de animales por potrero para las etiquetas
        total_por_potrero = df_potrero_tipo.groupby('Potrero')['Cantidad'].sum().reset_index(name='Total')

        # Paleta de colores
        colores = ['#FF6347', '#32CD32', '#FFD700', '#8A2BE2', '#FF4500', '#00BFFF', '#039BE5', '#0277BD', '#01579B']
        tipos_unicos = df_potrero_tipo['Tipo'].unique().tolist()
        colores = colores[:len(tipos_unicos)]

        # Gráfico de barras apiladas
        barras_apiladas = alt.Chart(df_potrero_tipo).mark_bar().encode(
            x=alt.X('Potrero:N', title='Potrero'),
            y=alt.Y('Cantidad:Q', title='Cantidad de Animales'),
            color=alt.Color('Tipo:N', scale=alt.Scale(domain=tipos_unicos, range=colores), title='Tipo de Animal'),
            tooltip=['Potrero:N', 'Tipo:N', 'Cantidad:Q']
        ).properties(
            width=700,
            height=400,
            title="Cantidad de Animales por Potrero y Tipo"
        )

        # Etiquetas con el total de animales por potrero
        etiquetas_totales = alt.Chart(total_por_potrero).mark_text(
            dy=-5,
            color='black',
            fontWeight='bold'
        ).encode(
            x='Potrero:N',
            y='Total:Q',
            text=alt.Text('Total:Q', format='.0f')
        )

        # Mostrar gráfico
        st.altair_chart(barras_apiladas + etiquetas_totales, use_container_width=True)


        
        # cantidad de partos por vacas#
        st.markdown("---")
        # Filtrar tipos relevantes
        tipos_vaca = ['Vaca', 'Vaca de ordeño', 'Vaca Preñada']
        vacas_df = animales_df[animales_df['Tipo'].isin(tipos_vaca)].copy()

        # Asegurar que ID sea string para mantener ceros a la izquierda
        vacas_df['ID'] = vacas_df['ID'].astype(str)

        # Asegurarse de que Partos sea numérica
        vacas_df['Partos'] = pd.to_numeric(vacas_df['Partos'], errors='coerce')

        # Ordenar por número de partos descendente
        ranking_partos = vacas_df.sort_values(by='Partos', ascending=False)

        # Seleccionar columnas clave (sin Potrero)
        tabla_ranking = ranking_partos[['ID', 'Tipo', 'Partos', 'Procedencia', 'Comentarios']]

        # Mostrar en Streamlit
        st.subheader("🐮 Ranking de Vacas con Mayor Número de Partos")
        st.dataframe(tabla_ranking, use_container_width=True)

        # Filtrar solo los tipos de vacas
        tipos_vaca = ["Vaca", "Vaca de ordeño", "Vaca Preñada"]
        vacas_df = animales_df[animales_df["Tipo"].isin(tipos_vaca)]

        # Contar por procedencia
        nacidas = vacas_df[vacas_df["Procedencia"] == "Nacido en finca"].shape[0]
        adquiridas = vacas_df[vacas_df["Procedencia"] == "Adquirido"].shape[0]

        st.markdown("---")
        # Mostrar el KPI textual estilizado
        st.markdown(f"""
        <div style='
            background: linear-gradient(135deg, #e3f2fd, #bbdefb);
            padding: 15px 25px;
            border-radius: 10px;
            color: #0d47a1;
            font-size: 18px;
            font-weight: 500;
            margin-top: 20px;
            box-shadow: 2px 2px 6px rgba(0,0,0,0.1);
        '>
            🐮 Se tienen <strong>{nacidas}</strong> Vacas nacidas en la finca<br>
            🐄 Se tienen <strong>{adquiridas}</strong> Vacas adquiridas
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")
        # Leer el CSV con ID como string
        # Leer el CSV asegurando que ID sea string
        animales_df = pd.read_csv("animales.csv", dtype={"ID": str})

        # Convertir fecha de nacimiento a datetime
        animales_df['Fecha Nacimiento'] = pd.to_datetime(animales_df['Fecha Nacimiento'], errors='coerce')

        # Filtrar solo nacidos en finca
        nacidos_df = animales_df[animales_df['Procedencia'] == 'Nacido en finca'].copy()

        # Tipos disponibles
        tipos_animales = sorted(nacidos_df["Tipo"].unique())

        # Selección de tipo
        tipo_seleccionado = st.selectbox("Selecciona el tipo de animal", ["Todos"] + tipos_animales)

        if tipo_seleccionado != "Todos":
            nacidos_df = nacidos_df[nacidos_df["Tipo"] == tipo_seleccionado]

        # Calcular edad como texto
        def calcular_edad(fecha_nac):
            hoy = datetime.today()
            delta = hoy - fecha_nac
            años = delta.days // 365
            meses = (delta.days % 365) // 30
            dias = (delta.days % 365) % 30
            return f"{años} años con {meses} meses y {dias} días"

        nacidos_df["Edad de Animal"] = nacidos_df["Fecha Nacimiento"].apply(calcular_edad)

        # Reordenar columnas
        resultado_df = nacidos_df[["Fecha Nacimiento", "Tipo", "ID", "Procedencia", "Comentarios", "Edad de Animal"]].copy()
        resultado_df = resultado_df.sort_values("Fecha Nacimiento")

        # Estilo CSS para encabezado
        st.markdown("""
            <style>
            .styled-table thead tr {
                background: linear-gradient(135deg, #4FC3F7, #0288D1);
                color: white;
                text-align: left;
            }
            .styled-table {
                border-collapse: collapse;
                font-size: 15px;
                min-width: 100%;
            }
            .styled-table th, .styled-table td {
                padding: 10px 12px;
                border: 1px solid #ddd;
            }
            </style>
        """, unsafe_allow_html=True)

        # Mostrar primeros 8 con opción de expandir
        st.markdown("### 🐮 Edades de Animales nacidos en la finca")
        st.markdown(
            resultado_df.head(8).to_html(classes='styled-table', index=False, justify='left', escape=False),
            unsafe_allow_html=True
        )

        with st.expander("🔍 Ver tabla completa"):
            st.markdown(
                resultado_df.to_html(classes='styled-table', index=False, justify='left', escape=False),
                unsafe_allow_html=True
            )


            # Filtrar nacidos en finca
        vacas_finca = nacidos_df[
            nacidos_df['Tipo'].str.lower().isin(['vaca', 'vaca de ordeño', 'vaca preñada'])
        ]
        toros_finca = nacidos_df[nacidos_df['Tipo'].str.lower().str.contains('toro')]

        # Obtener la vaca más antigua
        vaca_antigua = vacas_finca.sort_values("Fecha Nacimiento").iloc[0] if not vacas_finca.empty else None

        # Obtener el toro más antiguo
        toro_antiguo = toros_finca.sort_values("Fecha Nacimiento").iloc[0] if not toros_finca.empty else None

        # Mostrar KPI en texto con estilo
        kpi_texto = ""

        if vaca_antigua is not None:
            kpi_texto += f"🐄 La vaca más antigua es **ID {vaca_antigua['ID']}** {calcular_edad(vaca_antigua['Fecha Nacimiento'])}<br>"

        if toro_antiguo is not None:
            kpi_texto += f"🐃 El toro más antiguo es **ID {toro_antiguo['ID']}** {calcular_edad(toro_antiguo['Fecha Nacimiento'])}"

        st.markdown(f"""
        <div style='
            background: linear-gradient(135deg, #4FC3F7, #0288D1);
            padding: 25px;
            border-radius: 10px;
            color: white;
            font-size: 20px;
            text-align: center;
            box-shadow: 0px 3px 8px rgba(0,0,0,0.1);
        '>
            {kpi_texto}
        </div>
        """, unsafe_allow_html=True)


        st.markdown("---")
        # Agrupar becerros y becerras nacidos en la finca
        crias = nacidos_df[nacidos_df['Tipo'].str.lower().isin(['becerro', 'becerra'])].copy()
        crias['Mes Nacimiento'] = pd.to_datetime(crias['Fecha Nacimiento']).dt.month_name()

        # Calcular porcentajes por mes
        por_mes = crias['Mes Nacimiento'].value_counts(normalize=True).sort_values(ascending=False) * 100
        por_mes = por_mes.round(2)

        # Construir el texto
        kpi_meses = "📅 **Distribución de nacimientos de crías por mes:**  \n\n"
        for mes, porcentaje in por_mes.items():
            kpi_meses += f"- {porcentaje}% nacen en **{mes}**  \n"

        # Mostrar en azul oscuro
        st.markdown(f"""
        <div style='color: #0D47A1; font-size: 18px; font-weight: 500;'>
            {kpi_meses}
        
        """, unsafe_allow_html=True)

   

        # Filtrar crías (Becerro y Becerra nacidos en la finca)
        crias = animales_df[
            (animales_df['Tipo'].str.lower().isin(['becerro', 'becerra'])) &
            (animales_df['Procedencia'] == 'Nacido en finca')
        ].copy()

        # Extraer mes de nacimiento
        crias['Mes'] = pd.to_datetime(crias['Fecha Nacimiento']).dt.month_name()

        # Calcular porcentaje de nacimientos por mes
        por_mes = crias['Mes'].value_counts(normalize=True).reset_index()
        por_mes.columns = ['Mes', 'Porcentaje']
        por_mes['Porcentaje'] = por_mes['Porcentaje'] * 100
        por_mes['Porcentaje'] = por_mes['Porcentaje'].round(2)

        # Para que se ordenen meses cronológicamente, si quieres:
        meses_orden = ['January', 'February', 'March', 'April', 'May', 'June', 'July',
                    'August', 'September', 'October', 'November', 'December']
        por_mes['Mes'] = pd.Categorical(por_mes['Mes'], categories=meses_orden, ordered=True)
        por_mes = por_mes.sort_values('Mes')

        # Gráfico barras horizontales
        barras = alt.Chart(por_mes).mark_bar().encode(
            y=alt.Y('Mes:N', sort='-x', title='Mes'),
            x=alt.X('Porcentaje:Q', title='Porcentaje (%)'),
            color=alt.Color('Mes:N', legend=None)  # color distinto por mes
        )

        # Etiquetas de porcentaje
        etiquetas = alt.Chart(por_mes).mark_text(
            align='left',
            baseline='middle',
            dx=3,  # separación a la derecha de la barra
            color='black',
            fontWeight='bold'
        ).encode(
            y=alt.Y('Mes:N', sort='-x'),
            x='Porcentaje:Q',
            text=alt.Text('Porcentaje:Q', format='.1f')
        )

        st.altair_chart(barras + etiquetas, use_container_width=True)


 
        

        st.markdown("---")
        # --- Alerta de Marcaje de Animales ---
        st.subheader("🔔 Alerta de Marcaje: Becerras y Becerros listos para marcar")

        # Cargar datos
        animales_df = pd.read_csv("animales.csv", dtype={"ID": str})
        animales_df['Fecha Nacimiento'] = pd.to_datetime(animales_df['Fecha Nacimiento'], errors='coerce')

        # Calcular edad en días
        hoy = pd.Timestamp.now().normalize()
        animales_df["Edad (días)"] = (hoy - animales_df["Fecha Nacimiento"]).dt.days

        # Filtrar animales listos para marcar
        condicion_marcaje = (
            (animales_df["Tipo"].isin(["Becerra", "Becerro"])) &
            (animales_df["Edad (días)"] >= 180) &
            (animales_df["Hierro"].astype(str).str.strip().str.lower() != "sí")
        )

        a_marcar_df = animales_df[condicion_marcaje].copy()

        if a_marcar_df.empty:
            st.info("✅ No hay becerras ni becerros listos para marcar.")
        else:
            st.markdown(f"**{len(a_marcar_df)} animales listos para marcar:**")
            st.dataframe(a_marcar_df[["Tipo", "ID", "Fecha Nacimiento", "Edad (días)", "Potrero"]])

            # Selección múltiple
            indices_seleccionados = st.multiselect(
                "Selecciona los animales a marcar:",
                options=a_marcar_df.index,
                format_func=lambda i: f"{a_marcar_df.loc[i, 'Tipo']} - {a_marcar_df.loc[i, 'Fecha Nacimiento'].date()} (Potrero: {a_marcar_df.loc[i, 'Potrero']})"
            )

            # Entrada de IDs según tipo
            nuevos_ids = {}
            for i in indices_seleccionados:
                tipo = a_marcar_df.loc[i, "Tipo"]
                label = f"Ingresar nuevo ID {'(obligatorio)' if tipo == 'Becerra' else '(opcional)'} para {tipo} (índice {i}):"
                nuevos_ids[i] = st.text_input(label, key=f"id_animal_{i}")

            # Botón para confirmar
            if st.button("✅ Confirmar marcaje"):
                errores = False
                usados = set(animales_df["ID"].dropna().astype(str).values)

                for i in indices_seleccionados:
                    tipo = a_marcar_df.loc[i, "Tipo"]
                    nuevo_id = nuevos_ids[i].strip()

                    if tipo == "Becerra":
                        if not nuevo_id:
                            st.error(f"⚠️ Debes ingresar un ID para la Becerra (índice {i}).")
                            errores = True
                        elif not nuevo_id.isdigit():
                            st.error(f"⚠️ El ID '{nuevo_id}' debe ser numérico.")
                            errores = True
                        elif nuevo_id in usados:
                            st.error(f"⚠️ El ID '{nuevo_id}' ya existe en la base de datos.")
                            errores = True

                    elif tipo == "Becerro" and nuevo_id:
                        if not nuevo_id.isdigit():
                            st.error(f"⚠️ El ID '{nuevo_id}' debe ser numérico.")
                            errores = True
                        elif nuevo_id in usados:
                            st.error(f"⚠️ El ID '{nuevo_id}' ya existe en la base de datos.")
                            errores = True

                # Aplicar cambios si no hay errores
                if not errores:
                    for i in indices_seleccionados:
                        animales_df.loc[i, "Hierro"] = "Sí"
                        nuevo_id = nuevos_ids[i].strip()
                        if nuevo_id:
                            animales_df.loc[i, "ID"] = str(nuevo_id)

                    animales_df.drop(columns=["Edad (días)"], inplace=True)
                    animales_df.to_csv("animales.csv", index=False)

                    st.success(f"✅ Se marcaron {len(indices_seleccionados)} animales correctamente.")
                    st.rerun()




        st.markdown("---")
        animales_df = pd.read_csv("animales.csv", dtype={"ID": str})
        animales_df["ID"] = animales_df["ID"].fillna("").astype(str).str.strip()
        animales_df["Hierro"] = animales_df["Hierro"].fillna("").astype(str).str.strip().str.lower()

        # Función auxiliar para mostrar conteo por tipo
        def mostrar_conteo(df, titulo):
            tipos = df["Tipo"].unique()
            conteo = df["Tipo"].value_counts()
            st.markdown(f"### {titulo}")
            for tipo in sorted(tipos):
                cantidad = conteo.get(tipo, 0)
                st.markdown(f"- **{cantidad} {tipo + ('s' if not tipo.endswith('s') else '')}**")

        # --- KPI 1: Animales sin marcar ---
        sin_marcar_df = animales_df[animales_df["Hierro"] != "sí"]
        mostrar_conteo(sin_marcar_df, "📌 Actualmente se tienen **{}** animales sin marcar".format(len(sin_marcar_df)))

        # --- KPI 2: Animales marcados con Hierro ---
        marcados_df = animales_df[animales_df["Hierro"] == "sí"]
        mostrar_conteo(marcados_df, "📌 Actualmente se tienen **{}** animales marcados con hierro".format(len(marcados_df)))

        # --- KPI 3: Animales marcados con Hierro + ID ---
        marcados_con_id_df = animales_df[
            (animales_df["Hierro"] == "sí") & (animales_df["ID"].str.strip() != "")
        ]
        mostrar_conteo(marcados_con_id_df, "📌 Actualmente se tienen **{}** animales marcados con hierro + ID".format(len(marcados_con_id_df)))



        st.markdown("---")
        # Cargar bajas.csv
        
        # Cargar archivo de bajas
        bajas_df = pd.read_csv("bajas.csv", parse_dates=["Fecha_baja"])
        bajas_df["Motivo"] = bajas_df["Motivo"].str.strip().str.title()
        bajas_df["Comentarios"] = bajas_df["Comentarios"].fillna("")
        bajas_df["Fecha_baja"] = pd.to_datetime(bajas_df["Fecha_baja"], errors="coerce")
        bajas_df["Año"] = bajas_df["Fecha_baja"].dt.year
        
        # Filtro por año
        años_disponibles = sorted(bajas_df["Año"].dropna().unique())
        año_seleccionado = st.selectbox("Selecciona un año", options=["Todos"] + años_disponibles, index=0)

        if año_seleccionado != "Todos":
            bajas_filtradas = bajas_df[bajas_df["Año"] == año_seleccionado]
        else:
            bajas_filtradas = bajas_df

        # Gráfico de cantidad de bajas por año
        st.subheader("📉 Bajas por Año")
        grafico = (
            alt.Chart(bajas_df if año_seleccionado == "Todos" else bajas_filtradas)
            .mark_bar()
            .encode(
                x=alt.X("Año:O", title="Año"),
                y=alt.Y("count():Q", title="Cantidad de bajas"),
                tooltip=["Año", "count()"]
            )
            .properties(width=600, height=400)
            .mark_bar(color="blue")
        )

        etiquetas = (
            alt.Chart(bajas_df if año_seleccionado == "Todos" else bajas_filtradas)
            .mark_text(
                align='center',
                baseline='bottom',
                dy=-5,
                color='black'
            )
            .encode(
                x="Año:O",
                y="count():Q",
                text="count():Q"
            )
        )

        st.altair_chart(grafico + etiquetas, use_container_width=True)

        # Etiquetas por motivo
        st.subheader("📋 Detalle de Bajas por Motivo")

        motivos_posibles = ["Venta", "Muerte", "Otros"]
        cols = st.columns(len(motivos_posibles))
        bajas_filtradas["Motivo"] = bajas_filtradas["Motivo"].fillna("Otros")

        for i, motivo in enumerate(motivos_posibles):
            with cols[i]:
                if not bajas_filtradas.empty:
                    # Aseguramos que Motivo no tenga NaN y que sea string para aplicar lower()
                    motivo_df = bajas_filtradas[
                        bajas_filtradas["Motivo"].fillna("").str.lower() == motivo.lower()
                    ]
                else:
                    motivo_df = pd.DataFrame(columns=bajas_filtradas.columns)  # vacío pero con columnas

                total = len(motivo_df)
                icon = "💰" if motivo.lower() == "venta" else "☠️" if motivo.lower() == "muerte" else "🚚"
                st.markdown(f"### {icon} {motivo}")
                st.markdown(f"**{total} animales**")

                if total > 0:
                    # Crear resumen por tipo y comentario
                    motivo_df["Resumen"] = motivo_df["Tipo"].str.title() + " – " + motivo_df["Comentarios"].fillna("").str.strip()
                    resumen = motivo_df["Resumen"].value_counts()

                    for linea, veces in resumen.items():
                        st.markdown(f"- {linea} – **{veces} veces**")
                else:
                    st.markdown("*Sin registros*")

        
        # Botón para ver historial completo
        # Convertimos las fechas a datetime para asegurarnos del merge correct

        # Cargar datos
        bajas_df = pd.read_csv("bajas.csv", dtype={"ID": str})
        backup_df = pd.read_csv("backup_bajas.csv", dtype={"ID": str})

        # Convertir fechas a datetime
        bajas_df["Fecha_baja"] = pd.to_datetime(bajas_df["Fecha_baja"], format="%Y-%m-%d", errors="coerce")
        backup_df["Fecha_baja"] = pd.to_datetime(backup_df["Fecha_baja"], format="%Y-%m-%d", errors="coerce")

        # Añadir columna año para filtro
        bajas_df["Año"] = bajas_df["Fecha_baja"].dt.year

        # Filtrado año
        año_seleccionado = st.selectbox("Seleccionar año", ["Todos"] + sorted(bajas_df["Año"].dropna().unique(), reverse=True))

        if año_seleccionado == "Todos":
            bajas_filtradas = bajas_df.copy()
        else:
            bajas_filtradas = bajas_df[bajas_df["Año"] == int(año_seleccionado)].copy()

        # Ordenar ambos datasets por Fecha y Tipo para que el emparejamiento sea correcto
        bajas_filtradas = bajas_filtradas.sort_values(["Fecha_baja", "Tipo"]).reset_index(drop=True)
        backup_df = backup_df.sort_values(["Fecha_baja", "Tipo"]).reset_index(drop=True)

        # Crear índice único para merge: contar ocurrencias dentro de cada grupo Fecha+Tipo
        bajas_filtradas["idx"] = bajas_filtradas.groupby(["Fecha_baja", "Tipo"]).cumcount()
        backup_df["idx"] = backup_df.groupby(["Fecha_baja", "Tipo"]).cumcount()

        # Merge con la clave compuesta de Fecha, Tipo e índice para emparejar filas una a una
        bajas_merged = pd.merge(
            bajas_filtradas,
            backup_df,
            on=["Fecha_baja", "Tipo", "idx"],
            how="left",
            suffixes=("_baja", "_animal")
        )

        # Renombrar columnas para presentación
        bajas_merged = bajas_merged.rename(columns={
            "Fecha_baja": "Fecha de Baja",
            "Motivo": "Motivo",
            "Comentarios_baja": "Comentario de Baja",
            "ID": "ID",
            "Potrero": "Potrero",
            "Procedencia": "Procedencia",
            "Fecha Nacimiento": "Fecha Nacimiento",
            "Fecha Adquisición": "Fecha Adquisición"
        })

        # Columnas para mostrar
        columnas_mostrar = [
            "Tipo", "Fecha de Baja", "Motivo", "Comentario de Baja",
            "ID", "Potrero", "Procedencia",
            "Fecha Nacimiento", "Fecha Adquisición"
        ]

        # Mostrar en streamlit
        with st.expander("📄 Ver historial completo de bajas"):
            st.dataframe(bajas_merged[columnas_mostrar], use_container_width=True)


    with tab2:
        
        def kpi_produccion_leche(leche_df):
            # Asegurar que Fecha es datetime
            leche_df["Fecha"] = pd.to_datetime(leche_df["Fecha"], errors="coerce")

            # Agregar columnas de año y mes
            leche_df["Mes"] = leche_df["Fecha"].dt.month
            leche_df["Año"] = leche_df["Fecha"].dt.year

            # Producción mensual
            produccion_mensual = leche_df.groupby(["Año", "Mes"])["Litros"].sum().reset_index()

        
            # Gráfico mensual
            fig = px.bar(
                produccion_mensual,
                x="Mes",
                y="Litros",
                color="Año",
                barmode="group",
                text="Litros",
                title="Producción de Leche por Mes",
                labels={"Litros": "Litros", "Mes": "Mes"}
            )

            # Personalizar etiquetas
            fig.update_traces(texttemplate='%{text:.0f}', textposition='outside')
            fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')

            st.plotly_chart(fig, use_container_width=True)

        kpi_produccion_leche(leche_df)

        
        def kpi_mensual_anual(leche_df):
            # Asegurar formato de fecha correcto
            leche_df["Fecha"] = pd.to_datetime(leche_df["Fecha"], errors="coerce")

            # Extraer mes y año
            leche_df["Mes"] = leche_df["Fecha"].dt.month
            leche_df["Año"] = leche_df["Fecha"].dt.year

            # Agrupaciones
            litros_mensuales = leche_df.groupby(["Año", "Mes"])["Litros"].sum().reset_index()
            litros_anuales = leche_df.groupby("Año")["Litros"].sum().reset_index()

            # Cálculos
            promedio_mensual_total = litros_mensuales["Litros"].mean()
            promedio_anual_total = litros_anuales["Litros"].mean()

            # Mostrar en cajas con diseño
            st.markdown("---")
            st.markdown("### 📊 Producción Promedio")
            col1, col2 = st.columns(2)

            with col1:
                st.markdown(
                    f"""
                    <div style='background-color:#DFF0D8; padding:20px; border-radius:10px; text-align:center'>
                        <h4 style='color:#3C763D;'>Promedio mensual total</h4>
                        <p style='font-size:24px; font-weight:bold'>{promedio_mensual_total:,.0f} litros</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            with col2:
                st.markdown(
                    f"""
                    <div style='background-color:#D9EDF7; padding:20px; border-radius:10px; text-align:center'>
                        <h4 style='color:#31708F;'>Promedio anual producido</h4>
                        <p style='font-size:24px; font-weight:bold'>{promedio_anual_total:,.0f} litros</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

       
        kpi_mensual_anual(leche_df)


        st.markdown("---")
        def kpi_ingresos(leche_df):
            # Asegurar que Fecha es datetime
            leche_df["Fecha"] = pd.to_datetime(leche_df["Fecha"], errors="coerce")

            # Extraer mes y año
            leche_df["Mes"] = leche_df["Fecha"].dt.month
            leche_df["Año"] = leche_df["Fecha"].dt.year

            # Calcular ingresos diarios
            leche_df["Ingreso"] = leche_df["Litros"] * leche_df["Precio"]

            # Ingresos mensuales y anuales
            ingresos_mensuales = leche_df.groupby(["Año", "Mes"])["Ingreso"].sum().reset_index()
            ingresos_anuales = leche_df.groupby("Año")["Ingreso"].sum().reset_index()

            # Promedios
            promedio_mensual_ingreso = ingresos_mensuales["Ingreso"].mean()
            promedio_anual_ingreso = ingresos_anuales["Ingreso"].mean()

            # Mostrar en cajas con estilo
            st.markdown("---")
            st.markdown("### 💰 Ingresos por Producción Lechera")
            col1, col2 = st.columns(2)

            with col1:
                st.markdown(
                    f"""
                    <div style='background-color:#FCF8E3; padding:20px; border-radius:10px; text-align:center'>
                        <h4 style='color:#8A6D3B;'>Promedio mensual de ingresos</h4>
                        <p style='font-size:24px; font-weight:bold'>${promedio_mensual_ingreso:,.2f}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            with col2:
                st.markdown(
                    f"""
                    <div style='background-color:#F2DEDE; padding:20px; border-radius:10px; text-align:center'>
                        <h4 style='color:#A94442;'>Promedio anual de ingresos</h4>
                        <p style='font-size:24px; font-weight:bold'>${promedio_anual_ingreso:,.2f}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            # Gráfico de ingresos mensuales
            fig = px.bar(
                ingresos_mensuales,
                x="Mes",
                y="Ingreso",
                color="Año",
                barmode="group",
                text="Ingreso",
                title="Ingresos por Mes",
                labels={"Ingreso": "Ingresos ($)", "Mes": "Mes"}
            )
            fig.update_traces(texttemplate='%{text:.0f}', textposition='outside')
            fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')

            st.plotly_chart(fig, use_container_width=True)

        kpi_ingresos(leche_df)



        ROTACIONES = "rotacion_potreros.csv"

        # ---------------------------
        # KPI: Historial de rotaciones de potreros
        # ---------------------------
        st.markdown("---")
        st.subheader("📋 Historial de Rotaciones de Potreros")

        
        if os.path.exists(ROTACIONES):
            df_rotaciones = pd.read_csv(ROTACIONES)
            df_rotaciones = df_rotaciones.dropna(how="all")
        else:
            df_rotaciones = pd.DataFrame(columns=["Fecha Rotacion", "Tipo", "Potrero_Anterior", "Potrero_Nuevo", "Comentario", "Cantidad"])

        # Mostrar DataFrame limpio
        st.dataframe(df_rotaciones)

        


        # Ruta al archivo de animales
        ARCHIVO = "animales.csv"
        
        st.markdown("---")
        st.subheader("📍 Distribución Actual de Animales en Potreros")

        def mostrar_distribucion_animales(ruta_csv):
            try:
                df = pd.read_csv(ruta_csv)
                df = df.dropna(subset=["Potrero", "Tipo"])

                # Agrupar por potrero y tipo de animal
                conteo = df.groupby(["Potrero", "Tipo"]).size().reset_index(name="Cantidad")

                # Reordenar por potrero para visualización
                conteo = conteo.sort_values(by=["Potrero", "Tipo"])

                # Construir el texto por potrero
                resultado = ""
                potreros = conteo["Potrero"].unique()

                for potrero in potreros:
                    datos = conteo[conteo["Potrero"] == potrero]
                    lista = [f'{row["Cantidad"]} {row["Tipo"]}' for _, row in datos.iterrows()]
                    resultado += f"**{potrero}** — " + ", ".join(lista) + "\n\n"

                st.markdown(resultado)

            except Exception as e:
                st.error(f"❌ Error al procesar la distribución: {e}")

        # Mostrar el KPI
        mostrar_distribucion_animales(ARCHIVO)



    with tab3:
        st.markdown("### 🔍 Consulta de Precio de Leche en un Día Específico")

        # Cargar datos y asegurar que la fecha esté bien formateada
        leche_df["Fecha"] = pd.to_datetime(leche_df["Fecha"], errors="coerce")

        # Selector de fecha
        fecha_consulta = st.date_input("Selecciona la fecha que deseas consultar")

        # Buscar ese día en el dataframe
        resultado = leche_df[leche_df["Fecha"] == pd.to_datetime(fecha_consulta)]

        if not resultado.empty:
            precio = resultado["Precio"].values[0]
            litros = resultado["Litros"].values[0]
            ingreso = litros * precio

            st.success(f"📅 El {fecha_consulta.strftime('%d/%m/%Y')} el precio fue de **${precio:.2f}** por litro.")
            st.info(f"Se produjeron **{litros:.2f} litros**, generando **${ingreso:.2f}** en ingresos ese día.")
        else:
            st.warning("⚠️ No se encontró información para esa fecha.")

        # Opción para mostrar el DataFrame completo
        if st.checkbox("Mostrar todos los registros de leche"):
            st.dataframe(leche_df.sort_values("Fecha", ascending=False))



        st.markdown("---")
        st.markdown("### 📄 ¿Necesita ver el listado completo de animales?")
        st.info("Use los filtros y presione el botón para mostrar los registros que desea visualizar.")

        # Filtros dinámicos basados en los datos actuales
        potreros_unicos = animales_df["Potrero"].dropna().unique().tolist()
        tipos_unicos = animales_df["Tipo"].dropna().unique().tolist()
        comentarios_unicos = animales_df["Comentarios"].dropna().unique().tolist()
        ID_unicos = animales_df["ID"].dropna().unique().tolist()

        # Filtros seleccionables
        filtro_potrero = st.multiselect("📍 Filtrar por Potrero", sorted(potreros_unicos))
        filtro_tipo = st.multiselect("🐄 Filtrar por Tipo de animal", sorted(tipos_unicos))
        filtro_comentarios = st.multiselect("🗒️ Filtrar por Comentarios", sorted(comentarios_unicos))
        filtro_ID = st.multiselect("🗒️ Filtrar por ID", sorted(ID_unicos))

        # Botón para mostrar resultados filtrados
        if st.button("🔍 Mostrar animales filtrados"):
            df_filtrado = animales_df.copy()

            # Aplicar filtros si están seleccionados
            if filtro_potrero:
                df_filtrado = df_filtrado[df_filtrado["Potrero"].isin(filtro_potrero)]
            if filtro_tipo:
                df_filtrado = df_filtrado[df_filtrado["Tipo"].isin(filtro_tipo)]
            if filtro_comentarios:
                df_filtrado = df_filtrado[df_filtrado["Comentarios"].isin(filtro_comentarios)]
            if filtro_ID:
                df_filtrado = df_filtrado[df_filtrado["ID"].isin(filtro_ID)]

            if df_filtrado.empty:
                st.warning("⚠️ No se encontraron animales con los filtros seleccionados.")
            else:
                st.success(f"✅ Se encontraron {len(df_filtrado)} registros:")
                st.dataframe(df_filtrado.reset_index(drop=True))


elif opcion == "Formulario":
    
    formulario.main()


    # ---- HIDE STREAMLIT STYLE ----
    hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
    st.markdown(hide_st_style, unsafe_allow_html=True)
