import os
import streamlit as st
import pandas as pd
import pyodbc
from dotenv import load_dotenv
from datetime import date


# -------------------------------------------------------------------------
# Configuración base de datos
# -------------------------------------------------------------------------

load_dotenv()
CONN_STR = os.getenv("DB_CONN")  # Driver=ODBC Driver 17 for SQL Server;Server=...;Database=...;UID=...;PWD=...;TrustServerCertificate=yes

@st.cache_resource  # mantiene una sola conexión por sesión
def get_conn():
    return pyodbc.connect(CONN_STR, autocommit=True)

# ----------------------- Helpers genéricos -------------------------------

def fetch_df(sql: str, params=()):
    """Ejecuta un SELECT y devuelve un DataFrame."""
    return pd.read_sql(sql, get_conn(), params=params)

def exec_sql(sql: str, params=()):
    """Ejecuta una instrucción DML sin retorno de filas."""
    with get_conn().cursor() as cur:
        cur.execute(sql, params)

# -------------------------------------------------------------------------
# Helpers de negocio – CIUDAD
# -------------------------------------------------------------------------

def insert_ciudad(nombre: str) -> str:
    sql = """
        DECLARE @newId CHAR(3);
        EXEC dbo.CiudadInsert @NomCiudad = ?, @IdCiudad = @newId OUTPUT;
        SELECT @newId AS IdCiudad;
    """
    return fetch_df(sql, (nombre,)).iloc[0, 0]

def list_ciudades() -> pd.DataFrame:
    return fetch_df("SELECT IdCiudad, NomCiudad FROM dbo.Ciudad ORDER BY IdCiudad")

def update_ciudad(id_ciudad: str, nuevo_nombre: str):
    exec_sql(
        "UPDATE dbo.Ciudad SET NomCiudad = ? WHERE IdCiudad = ?",
        (nuevo_nombre, id_ciudad),
    )

def delete_ciudad(id_ciudad: str):
    exec_sql(
        "DELETE FROM dbo.Ciudad WHERE IdCiudad = ?",
        (id_ciudad,),
    )

# -------------------------------------------------------------------------
# Helpers de negocio – ESTADÍSTICA
# -------------------------------------------------------------------------

def insert_estadistica(descripcion: str, valor: int) -> str:
    sql = """
        DECLARE @newId CHAR(2);
        EXEC dbo.EstadisticaInsert @DescripcionEstadistica = ?,
                                   @Valor = ?,
                                   @IdEstadistica = @newId OUTPUT;
        SELECT @newId AS IdEstadistica;
    """
    return fetch_df(sql, (descripcion, valor)).iloc[0, 0]

def list_estadisticas() -> pd.DataFrame:
    return fetch_df(
        "SELECT IdEstadistica, DescripcionEstadistica, Valor FROM dbo.Estadistica ORDER BY IdEstadistica"
    )

def update_estadistica(id_est: str, nueva_desc: str, nuevo_valor: int):
    exec_sql(
        "UPDATE dbo.Estadistica SET DescripcionEstadistica = ?, Valor = ? WHERE IdEstadistica = ?",
        (nueva_desc, nuevo_valor, id_est),
    )

def delete_estadistica(id_est: str):
    exec_sql(
        "DELETE FROM dbo.Estadistica WHERE IdEstadistica = ?",
        (id_est,),
    )
# -------------------------------------------------------------------------
# Helpers de negocio – EQUIPO
# -------------------------------------------------------------------------

def insert_equipo(nom_equipo: str, id_ciudad: str) -> str:
    sql = """
        DECLARE @newId CHAR(3);
        EXEC dbo.EquipoInsert @NomEquipo = ?, @IdCiudad = ?, @IdEquipo = @newId OUTPUT;
        SELECT @newId AS IdEquipo;
    """
    return fetch_df(sql, (nom_equipo, id_ciudad)).iloc[0, 0]

def list_equipos() -> pd.DataFrame:
    return fetch_df(
        """
        SELECT e.IdEquipo, e.NomEquipo, c.NomCiudad AS Ciudad
        FROM dbo.Equipo e
        JOIN dbo.Ciudad c ON e.IdCiudad = c.IdCiudad
        ORDER BY e.IdEquipo
        """
    )
def update_equipo(id_equipo: str, nom_equipo: str, id_ciudad: str):
    exec_sql(
        "UPDATE dbo.Equipo SET NomEquipo = ?, IdCiudad = ? WHERE IdEquipo = ?",
        (nom_equipo, id_ciudad, id_equipo),
    )

def delete_equipo(id_equipo: str):
    exec_sql(
        "DELETE FROM dbo.Equipo WHERE IdEquipo = ?",
        (id_equipo,),
    )

# -------------------------------------------------------------------------
# Helpers de negocio – JUGADOR
# -------------------------------------------------------------------------

def list_jugadores() -> pd.DataFrame:
    return fetch_df(
        """
        SELECT j.IdJugador, j.NomJugador, j.IdCiudad, c.NomCiudad AS Ciudad,
               j.FechaNacimiento, j.NumJugador, j.IdEquipo, e.NomEquipo AS Equipo
        FROM dbo.Jugador j
        JOIN dbo.Ciudad c ON j.IdCiudad=c.IdCiudad
        JOIN dbo.Equipo e ON j.IdEquipo=e.IdEquipo
        ORDER BY j.IdJugador
        """
    )

def insert_jugador(nom_jugador: str, id_ciudad: str, fecha_nac, num_jugador: int, id_equipo: str) -> str:
    sql = """
        DECLARE @newId CHAR(5);
        EXEC dbo.JugadorInsert
            @NomJugador = ?,
            @IdCiudad = ?,
            @FechaNacimiento = ?,
            @NumJugador = ?,
            @IdEquipo = ?,
            @IdJugador = @newId OUTPUT;
        SELECT @newId AS IdJugador;
    """
    return fetch_df(sql, (nom_jugador, id_ciudad, fecha_nac, num_jugador, id_equipo)).iloc[0, 0]

def update_jugador(id_jugador: str, nom_jugador: str, id_ciudad: str, fecha_nac, num_jugador: int, id_equipo: str):
    exec_sql(
        "UPDATE dbo.Jugador SET NomJugador = ?, IdCiudad = ?, FechaNacimiento = ?, NumJugador = ?, IdEquipo = ? WHERE IdJugador = ?",
        (nom_jugador, id_ciudad, fecha_nac, num_jugador, id_equipo, id_jugador)
    )

def delete_jugador(id_jugador: str):
    exec_sql("DELETE FROM dbo.Jugador WHERE IdJugador = ?", (id_jugador,))

# -------------------------------------------------------------------------
# Helpers de negocio – JUEGO
# -------------------------------------------------------------------------

def list_juegos() -> pd.DataFrame:
    return fetch_df(
        """
        SELECT IdJuego, DescripcionJuego, IdEquipoA, IdEquipoB, FechaYHoraJuego
        FROM dbo.Juego
        ORDER BY IdJuego
        """
    )

def insert_juego(id_equipoA: str, id_equipoB: str, fecha_hora) -> str:
    sql = """
        DECLARE @newId CHAR(5);
        EXEC dbo.JuegoInsert
            @IdEquipoA       = ?,
            @IdEquipoB       = ?,
            @FechaYHoraJuego = ?,
            @IdJuego         = @newId OUTPUT;
        SELECT @newId AS IdJuego;
    """
    return fetch_df(sql, (id_equipoA, id_equipoB, fecha_hora)).iloc[0, 0]

def update_juego(id_juego: str, id_equipoA: str, id_equipoB: str, fecha_hora) -> None:
    sql = """
        UPDATE dbo.Juego
        SET 
            IdEquipoA       = ?,
            IdEquipoB       = ?,
            FechaYHoraJuego = ?,
            DescripcionJuego = (
                SELECT RTRIM(a.NomEquipo) + ' vs ' + RTRIM(b.NomEquipo)
                FROM dbo.Equipo a
                JOIN dbo.Equipo b 
                  ON a.IdEquipo = ? 
                 AND b.IdEquipo = ?
            )
        WHERE IdJuego = ?;
    """
    exec_sql(sql, (
        id_equipoA,
        id_equipoB,
        fecha_hora,
        id_equipoA,
        id_equipoB,
        id_juego,
    ))

def delete_juego(id_juego: str):
    exec_sql(
        "DELETE FROM dbo.Juego WHERE IdJuego = ?",
        (id_juego,),
    )

# -------------------------------------------------------------------------
# Helpers de negocio – JUEGO (SP Estadísticas)
# -------------------------------------------------------------------------

def get_estadisticas_juego(id_juego: str):
    """
    Ejecuta el sp_EstadisticasDelJuego y devuelve dos DataFrames:
     - df_local: detalle (jugadores + total) del equipo local
     - df_visit: detalle (jugadores + total) del equipo visitante
    """
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("EXEC dbo.sp_EstadisticasDelJuego ?", id_juego)

    # Primer resultset → stats del equipo local
    cols = [col[0] for col in cur.description]
    rows = cur.fetchall()
    df_local = pd.DataFrame.from_records(rows, columns=cols)

    # Segundo resultset → stats del equipo visitante
    if cur.nextset():
        cols = [col[0] for col in cur.description]
        rows = cur.fetchall()
        df_visit = pd.DataFrame.from_records(rows, columns=cols)
    else:
        df_visit = pd.DataFrame(columns=cols)

    return df_local, df_visit

# -------------------------------------------------------------------------
# Helpers de negocio – ESTADÍSTICA_JUEGO (INSERT)
# -------------------------------------------------------------------------
def insert_estadistica_juego(id_juego: str, id_estadistica: str, id_jugador: str, cantidad: int):
    exec_sql(
        """
        INSERT INTO dbo.EstadisticaJuego
            (IdJuego, IdEstadistica, IdJugador, CantEstadisticaRegistrada)
        VALUES (?, ?, ?, ?)
        """,
        (id_juego, id_estadistica, id_jugador, cantidad),
    )


# -------------------------------------------------------------------------
# Configuración Streamlit
# -------------------------------------------------------------------------

st.set_page_config(page_title="Gestión de Liga", layout="centered")

# -------------------------------------------------------------------------
# Main App
# -------------------------------------------------------------------------

def main():
    st.title("Sistema de Gestión de Liga")

    menu = [
        "🏙️ CRUD Ciudad",
        "📊 CRUD Estadística",
        "⚽ CRUD Equipo",
        "🎮 CRUD Jugador",
        "🎲 CRUD Juego",
        "📈 Estadísticas Juego",
        "➕ Agregar Estadística Juego"     
    ]
    choice = st.sidebar.radio("Menú principal", menu)

    # ============================= CIUDAD =============================
    if choice == "🏙️ CRUD Ciudad":
        st.subheader("CRUD Ciudad")

        # Inicializar estados
        for key in ("show_ciudad_insert", "show_ciudad_update", "show_ciudad_delete"):
            st.session_state.setdefault(key, False)

        # Botones de acción
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("➕ Insertar Ciudad"):
                st.session_state.show_ciudad_insert ^= True
                st.session_state.show_ciudad_update = False
                st.session_state.show_ciudad_delete = False
        with col2:
            if st.button("✏️ Modificar Ciudad"):
                st.session_state.show_ciudad_update ^= True
                st.session_state.show_ciudad_insert = False
                st.session_state.show_ciudad_delete = False
        with col3:
            if st.button("🗑️ Eliminar Ciudad"):
                st.session_state.show_ciudad_delete ^= True
                st.session_state.show_ciudad_insert = False
                st.session_state.show_ciudad_update = False

        # Insertar Ciudad
        if st.session_state.show_ciudad_insert:
            st.markdown("### Insertar nueva ciudad")
            with st.form("form_add_ciudad", clear_on_submit=True):
                nom = st.text_input("Nombre de la ciudad", max_chars=60)
                submitted = st.form_submit_button("Guardar")
            if submitted:
                if nom.strip():
                    try:
                        new_id = insert_ciudad(nom.strip())
                        st.success(f"Ciudad '{nom.strip()}' creada con Id: {new_id}")
                        st.session_state.show_ciudad_insert = False
                    except Exception as e:
                        st.error(f"Error al insertar la ciudad: {e}")
                else:
                    st.warning("El nombre no puede estar vacío.")

        # Modificar Ciudad
        elif st.session_state.show_ciudad_update:
            st.markdown("### Modificar ciudad existente")
            df_city = list_ciudades()
            if df_city.empty:
                st.warning("No hay ciudades registradas.")
            else:
                opts = df_city.apply(lambda r: f"{r.IdCiudad} - {r.NomCiudad}", axis=1).tolist()
                sel = st.selectbox("Selecciona la ciudad", opts)
                id_sel = sel.split(" - ")[0]
                current = df_city.loc[df_city.IdCiudad == id_sel, "NomCiudad"].values[0]
                new_name = st.text_input("Nuevo nombre", value=current, max_chars=60, key="city_new")
                if st.button("Actualizar", key="btn_update_city"):
                    if new_name.strip():
                        try:
                            update_ciudad(id_sel, new_name.strip())
                            st.success(f"Ciudad {id_sel} actualizada a '{new_name.strip()}'")
                            st.session_state.show_ciudad_update = False
                        except Exception as e:
                            st.error(f"Error al actualizar la ciudad: {e}")
                    else:
                        st.warning("El nombre no puede estar vacío.")

        # Eliminar Ciudad
        elif st.session_state.show_ciudad_delete:
            st.markdown("### Eliminar ciudad")
            df_city = list_ciudades()
            if df_city.empty:
                st.warning("No hay ciudades registradas.")
            else:
                opts = df_city.apply(lambda r: f"{r.IdCiudad} - {r.NomCiudad}", axis=1).tolist()
                sel = st.selectbox("Selecciona la ciudad", opts)
                id_sel = sel.split(" - ")[0]
                if st.button("Eliminar", key="btn_delete_city"):
                    try:
                        delete_ciudad(id_sel)
                        st.success(f"Ciudad {id_sel} eliminada correctamente.")
                        st.session_state.show_ciudad_delete = False
                    except Exception as e:
                        st.error(f"Error al eliminar la ciudad: {e}")

        # Lista de ciudades siempre visible
        st.markdown("### Lista de ciudades")
        st.dataframe(list_ciudades(), use_container_width=True)

    # ======================== ESTADÍSTICA =========================
    elif choice == "📊 CRUD Estadística":
        st.subheader("CRUD Estadística")

        # Inicializar estados
        for key in ("show_est_insert", "show_est_update", "show_est_delete"):
            st.session_state.setdefault(key, False)

        # Botones de acción
        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("➕ Insertar Estadística"):
                st.session_state.show_est_insert ^= True
                st.session_state.show_est_update = False
                st.session_state.show_est_delete = False
        with c2:
            if st.button("✏️ Modificar Estadística"):
                st.session_state.show_est_update ^= True
                st.session_state.show_est_insert = False
                st.session_state.show_est_delete = False
        with c3:
            if st.button("🗑️ Eliminar Estadística"):
                st.session_state.show_est_delete ^= True
                st.session_state.show_est_insert = False
                st.session_state.show_est_update = False

        # Insertar Estadística
        if st.session_state.show_est_insert:
            st.markdown("### Insertar nueva estadística")
            with st.form("form_add_est", clear_on_submit=True):
                desc = st.text_input("Descripción de la estadística", max_chars=60)
                val = st.number_input("Valor", min_value=0, step=1)
                submitted = st.form_submit_button("Guardar")
            if submitted:
                if desc.strip():
                    try:
                        new_id = insert_estadistica(desc.strip(), int(val))
                        st.success(f"Estadística '{desc.strip()}' creada con Id: {new_id}")
                        st.session_state.show_est_insert = False
                    except Exception as Error:
                        st.error(f"Error al insertar la estadística: {Error}")
                else:
                    st.warning("La descripción no puede estar vacía.")

        # Modificar Estadística
        elif st.session_state.show_est_update:
            st.markdown("### Modificar estadística existente")
            df_est = list_estadisticas()
            if df_est.empty:
                st.warning("No hay estadísticas registradas.")
            else:
                opts = df_est.apply(
                    lambda r: f"{r.IdEstadistica} - {r.DescripcionEstadistica} ({r.Valor})", axis=1
                ).tolist()
                sel = st.selectbox("Selecciona la estadística", opts)
                id_sel = sel.split(" - ")[0]
                curr_desc = df_est.loc[df_est.IdEstadistica == id_sel, "DescripcionEstadistica"].values[0]
                curr_val = int(df_est.loc[df_est.IdEstadistica == id_sel, "Valor"].values[0])
                new_desc = st.text_input("Nueva descripción", value=curr_desc, max_chars=60, key="est_new_desc")
                new_val = st.number_input("Nuevo valor", min_value=0, step=1, value=curr_val, key="est_new_val")
                if st.button("Actualizar", key="btn_update_est"):
                    if new_desc.strip():
                        try:
                            update_estadistica(id_sel, new_desc.strip(), int(new_val))
                            st.success(f"Estadística {id_sel} actualizada correctamente.")
                            st.session_state.show_est_update = False
                        except Exception as Error:
                            st.error(f"Error al actualizar la estadística: {Error}")
                    else:
                        st.warning("La descripción no puede estar vacía.")

        # Eliminar Estadística
        elif st.session_state.show_est_delete:
            st.markdown("### Eliminar estadística")
            df_est = list_estadisticas()
            if df_est.empty:
                st.warning("No hay estadísticas registradas.")
            else:
                opts = df_est.apply(
                    lambda r: f"{r.IdEstadistica} - {r.DescripcionEstadistica} ({r.Valor})", axis=1
                ).tolist()
                sel = st.selectbox("Selecciona la estadística a eliminar", opts)
                id_sel = sel.split(" - ")[0]
                if st.button("Eliminar", key="btn_delete_est"):
                    try:
                        delete_estadistica(id_sel)
                        st.success(f"Estadística {id_sel} eliminada correctamente.")
                        st.session_state.show_est_delete = False
                    except Exception as Error:
                        st.error(f"Error al eliminar la estadística: {Error}")

        # Lista de estadísticas siempre visible
        st.markdown("### Lista de estadísticas")
        st.dataframe(list_estadisticas(), use_container_width=True)


    # ======================== EQUIPO =========================
    elif choice == "⚽ CRUD Equipo":
        st.subheader("CRUD Equipo")
        # Inicializar estados
        for key in ("show_eq_insert", "show_eq_update", "show_eq_delete"):
            st.session_state.setdefault(key, False)

        # Botones de acción
        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("➕ Insertar Equipo"):
                st.session_state.show_eq_insert ^= True
                st.session_state.show_eq_update = False
                st.session_state.show_eq_delete = False
        with c2:
            if st.button("✏️ Modificar Equipo"):
                st.session_state.show_eq_update ^= True
                st.session_state.show_eq_insert = False
                st.session_state.show_eq_delete = False
        with c3:
            if st.button("🗑️ Eliminar Equipo"):
                st.session_state.show_eq_delete ^= True
                st.session_state.show_eq_insert = False
                st.session_state.show_eq_update = False

        # Insertar Equipo
        if st.session_state.show_eq_insert:
            st.markdown("### Insertar nuevo equipo")
            with st.form("form_add_eq", clear_on_submit=True):
                nom = st.text_input("Nombre del equipo", max_chars=60)
                df_ci = list_ciudades()
                opciones_ci = df_ci.apply(lambda r: f"{r.IdCiudad} - {r.NomCiudad}", axis=1).tolist()
                sel_ci = st.selectbox("Ciudad", opciones_ci)
                submitted = st.form_submit_button("Guardar")
            if submitted:
                if nom.strip():
                    id_ci = sel_ci.split(" - ")[0]
                    try:
                        new_id = insert_equipo(nom.strip(), id_ci)
                        st.success(f"Equipo '{nom.strip()}' creado con Id: {new_id}")
                        st.session_state.show_eq_insert = False
                    except Exception as e:
                        st.error(f"Error al insertar equipo: {e}")
                else:
                    st.warning("El nombre del equipo no puede estar vacío.")

        # Modificar Equipo
        elif st.session_state.show_eq_update:
            st.markdown("### Modificar equipo existente")
            df_eq = list_equipos()
            if df_eq.empty:
                st.warning("No hay equipos registrados.")
            else:
                opciones_eq = df_eq.apply(lambda r: f"{r.IdEquipo} - {r.NomEquipo} ({r.Ciudad})", axis=1).tolist()
                sel_eq = st.selectbox("Selecciona el equipo", opciones_eq)
                id_sel = sel_eq.split(" - ")[0]
                current_name = df_eq.loc[df_eq.IdEquipo == id_sel, "NomEquipo"].values[0]
                current_city = df_eq.loc[df_eq.IdEquipo == id_sel, "Ciudad"].values[0]
                # Inputs para editar
                new_name = st.text_input("Nuevo nombre", value=current_name, max_chars=60, key="eq_new_name")
                df_ci = list_ciudades()
                opciones_ci = df_ci.apply(lambda r: f"{r.IdCiudad} - {r.NomCiudad}", axis=1).tolist()
                sel_new_ci = st.selectbox("Nueva ciudad", opciones_ci, index=[i for i,o in enumerate(opciones_ci) if o.startswith(df_ci.loc[df_ci.NomCiudad==current_city, 'IdCiudad'].values[0])][0], key="eq_new_ci")
                if st.button("Actualizar", key="btn_update_eq"):
                    if new_name.strip():
                        id_ci_new = sel_new_ci.split(" - ")[0]
                        try:
                            update_equipo(id_sel, new_name.strip(), id_ci_new)
                            st.success(f"Equipo {id_sel} actualizado correctamente.")
                            st.session_state.show_eq_update = False
                        except Exception as e:
                            st.error(f"Error al actualizar equipo: {e}")
                    else:
                        st.warning("El nombre del equipo no puede estar vacío.")

        # Eliminar Equipo (placeholder)
        elif st.session_state.show_eq_delete:
            st.markdown("### Eliminar equipo")
            df_eq = list_equipos()
            if df_eq.empty:
                st.warning("No hay equipos registrados.")
            else:
                opciones_eq = df_eq.apply(lambda r: f"{r.IdEquipo} - {r.NomEquipo} ({r.Ciudad})", axis=1).tolist()
                sel_eq = st.selectbox("Selecciona el equipo a eliminar", opciones_eq)
                id_sel = sel_eq.split(" - ")[0]
                if st.button("Eliminar", key="btn_delete_eq"):
                    try:
                        delete_equipo(id_sel)
                        st.success(f"Equipo {id_sel} eliminado correctamente.")
                        st.session_state.show_eq_delete = False
                    except Exception as e:
                        st.error(f"Error al eliminar equipo: {e}")

        # Lista de equipos siempre visible
        st.markdown("### Lista de equipos")
        st.dataframe(list_equipos(), use_container_width=True)
    
    # ======================== JUGADOR =========================
    elif choice == "🎮 CRUD Jugador":
        st.subheader("CRUD Jugador")

        # Inicializar estados
        for key in ("show_jg_insert", "show_jg_update", "show_jg_delete"):
            st.session_state.setdefault(key, False)

        # Botones de acción
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("➕ Insertar Jugador"):
                st.session_state.show_jg_insert = True
                st.session_state.show_jg_update = False
                st.session_state.show_jg_delete = False
        with col2:
            if st.button("✏️ Modificar Jugador"):
                st.session_state.show_jg_update = True
                st.session_state.show_jg_insert = False
                st.session_state.show_jg_delete = False
        with col3:
            if st.button("🗑️ Eliminar Jugador"):
                st.session_state.show_jg_delete = True
                st.session_state.show_jg_insert = False
                st.session_state.show_jg_update = False

        # Insertar Jugador
        if st.session_state.show_jg_insert:
            st.markdown("### Insertar nuevo jugador")
            with st.form("form_add_jg", clear_on_submit=True):
                nom = st.text_input("Nombre del jugador", max_chars=60)
                df_ci = list_ciudades()
                ci_opts = [f"{r.IdCiudad} - {r.NomCiudad}" for _, r in df_ci.iterrows()]
                sel_ci = st.selectbox("Ciudad", ci_opts)
                fecha = st.date_input("Fecha de nacimiento", min_value=date(1900,1,1), max_value=date.today())
                num = st.number_input("Número de jugador", min_value=0, step=1)
                df_eq = list_equipos()
                eq_opts = [f"{r.IdEquipo} - {r.NomEquipo}" for _, r in df_eq.iterrows()]
                sel_eq = st.selectbox("Equipo", eq_opts)
                submitted = st.form_submit_button("Guardar")
            if submitted and nom.strip():
                id_ci = sel_ci.split(" - ")[0]
                id_eq = sel_eq.split(" - ")[0]
                try:
                    new_id = insert_jugador(nom.strip(), id_ci, fecha, int(num), id_eq)
                    st.success(f"Jugador '{nom.strip()}' creado con Id: {new_id}")
                    st.session_state.show_jg_insert = False
                except Exception as e:
                    st.error(f"Error al insertar jugador: {e}")

        # Modificar Jugador
        if st.session_state.show_jg_update:
            st.markdown("### Modificar jugador existente")
            df_jg = list_jugadores()
            if df_jg.empty:
                st.warning("No hay jugadores registrados.")
            else:
                opts = [f"{r.IdJugador} - {r.NomJugador} ({r.Equipo})" for _, r in df_jg.iterrows()]
                sel = st.selectbox("Selecciona el jugador", opts)
                id_sel = sel.split(" - ")[0]
                curr = df_jg[df_jg['IdJugador'] == id_sel].iloc[0]

                new_nom = st.text_input("Nuevo nombre", value=curr['NomJugador'], max_chars=60)

                df_ci = list_ciudades()
                ci_opts = [f"{r.IdCiudad} - {r.NomCiudad}" for _, r in df_ci.iterrows()]
                ci_index = next(i for i,opt in enumerate(ci_opts) if opt.startswith(curr['IdCiudad']))
                new_ci = st.selectbox("Nueva ciudad", ci_opts, index=ci_index)

                new_fecha = st.date_input(
                    "Nueva fecha de nacimiento",
                    min_value=date(1900,1,1),
                    max_value=date.today(),
                    value=curr['FechaNacimiento']
                )

                new_num = st.number_input(
                    "Nuevo número de jugador",
                    min_value=0,
                    step=1,
                    value=int(curr['NumJugador'])
                )

                df_eq = list_equipos()
                eq_opts = [f"{r.IdEquipo} - {r.NomEquipo}" for _, r in df_eq.iterrows()]
                eq_index = next(i for i,opt in enumerate(eq_opts) if opt.startswith(curr['IdEquipo']))
                new_eq = st.selectbox("Nuevo equipo", eq_opts, index=eq_index)

                if st.button("Actualizar Jugador"):
                    if new_nom.strip():
                        id_ci_new = new_ci.split(" - ")[0]
                        id_eq_new = new_eq.split(" - ")[0]
                        try:
                            update_jugador(id_sel, new_nom.strip(), id_ci_new, new_fecha, int(new_num), id_eq_new)
                            st.success(f"Jugador {id_sel} actualizado correctamente.")
                            st.session_state.show_jg_update = False
                        except Exception as e:
                            st.error(f"Error al actualizar jugador: {e}")
                    else:
                        st.warning("El nombre del jugador no puede estar vacío.")

        # Eliminar Jugador
        if st.session_state.show_jg_delete:
            st.markdown("### Eliminar jugador")
            df_jg = list_jugadores()
            if df_jg.empty:
                st.warning("No hay jugadores registrados.")
            else:
                opts = [f"{r.IdJugador} - {r.NomJugador} ({r.Equipo})" for _, r in df_jg.iterrows()]
                sel = st.selectbox("Selecciona el jugador a eliminar", opts)
                id_sel = sel.split(" - ")[0]
                if st.button("Eliminar Jugador"):
                    try:
                        delete_jugador(id_sel)
                        st.success(f"Jugador {id_sel} eliminado correctamente.")
                        st.session_state.show_jg_delete = False
                    except Exception as e:
                        st.error(f"Error al eliminar jugador: {e}")

        # Lista de jugadores siempre visible
        st.markdown("### Lista de jugadores")
        st.dataframe(list_jugadores(), use_container_width=True)

    # ======================== JUEGO =========================
    elif choice == "🎲 CRUD Juego":
        st.subheader("CRUD Juego")

        # Inicializar estados
        for key in ("show_juego_insert", "show_juego_update", "show_juego_delete"):
            st.session_state.setdefault(key, False)

        # Botones de acción
        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("➕ Insertar Juego"):
                st.session_state.show_juego_insert ^= True
                st.session_state.show_juego_update = False
                st.session_state.show_juego_delete = False
        with c2:
            if st.button("✏️ Modificar Juego"):
                st.session_state.show_juego_update ^= True
                st.session_state.show_juego_insert = False
                st.session_state.show_juego_delete = False
        with c3:
            if st.button("🗑️ Eliminar Juego"):
                st.session_state.show_juego_delete ^= True
                st.session_state.show_juego_insert = False
                st.session_state.show_juego_update = False

        # Insertar Juego
        if st.session_state.show_juego_insert:
            st.markdown("### Insertar nuevo juego")
            with st.form("form_add_juego", clear_on_submit=True):
                # Dropdown de Equipos (muestra nombre, guarda Id)
                df_eq = list_equipos()
                opts = df_eq.apply(lambda r: f"{r.IdEquipo} - {r.NomEquipo}", axis=1).tolist()
                sel_a = st.selectbox("Equipo A", opts)
                sel_b = st.selectbox("Equipo B", opts)
                # Fecha y hora
                fecha = st.date_input("Fecha del juego", min_value=date(1900,1,1), max_value=date.today())
                hora   = st.time_input("Hora del juego")
                submitted = st.form_submit_button("Guardar")
            if submitted:
                id_a = sel_a.split(" - ")[0]
                id_b = sel_b.split(" - ")[0]
                from datetime import datetime
                fecha_hora = datetime.combine(fecha, hora)
                try:
                    new_id = insert_juego(id_a, id_b, fecha_hora)
                    st.success(f"Juego creado con Id: {new_id}")
                    st.session_state.show_juego_insert = False
                except Exception as e:
                    st.error(f"Error al insertar juego: {e}")

                    # Modificar Juego
        elif st.session_state.show_juego_update:
            st.markdown("### Modificar juego existente")
            df_jg = list_juegos()
            if df_jg.empty:
                st.warning("No hay juegos registrados.")
            else:
                # 1) Selección del juego
                opts = df_jg.apply(
                    lambda r: f"{r.IdJuego} - {r.DescripcionJuego} ({r.FechaYHoraJuego})",
                    axis=1
                ).tolist()
                sel = st.selectbox("Selecciona el juego", opts)
                id_sel = sel.split(" - ")[0]
                curr = df_jg[df_jg.IdJuego == id_sel].iloc[0]

                # 2) Dropdown de Equipos
                df_eq = list_equipos()
                eq_opts = [f"{r.IdEquipo} - {r.NomEquipo}" for _, r in df_eq.iterrows()]
                idx_a = next(i for i,o in enumerate(eq_opts) if o.startswith(curr.IdEquipoA))
                idx_b = next(i for i,o in enumerate(eq_opts) if o.startswith(curr.IdEquipoB))
                new_a = st.selectbox("Nuevo Equipo A", eq_opts, index=idx_a)
                new_b = st.selectbox("Nuevo Equipo B", eq_opts, index=idx_b)

                # 3) Fecha y hora
                new_fecha = st.date_input(
                    "Nueva fecha del juego",
                    value=curr.FechaYHoraJuego.date()
                )
                new_hora = st.time_input(
                    "Nueva hora del juego",
                    value=curr.FechaYHoraJuego.time()
                )

                # 4) Botón de actualizar
                if st.button("Actualizar Juego"):
                    id_a = new_a.split(" - ")[0]
                    id_b = new_b.split(" - ")[0]
                    from datetime import datetime
                    nueva_fecha_hora = datetime.combine(new_fecha, new_hora)
                    try:
                        update_juego(id_sel, id_a, id_b, nueva_fecha_hora)
                        st.success(f"Juego {id_sel} actualizado correctamente.")
                        st.session_state.show_juego_update = False
                    except Exception as e:
                        st.error(f"Error al actualizar juego: {e}")

                # Eliminar Juego
        elif st.session_state.show_juego_delete:
            st.markdown("### Eliminar juego")
            df_jg = list_juegos()
            if df_jg.empty:
                st.warning("No hay juegos registrados.")
            else:
                opts = df_jg.apply(
                    lambda r: f"{r.IdJuego} - {r.DescripcionJuego} ({r.FechaYHoraJuego})",
                    axis=1
                ).tolist()
                sel = st.selectbox("Selecciona el juego a eliminar", opts)
                id_sel = sel.split(" - ")[0]
                if st.button("Eliminar Juego", key="btn_delete_juego"):
                    try:
                        delete_juego(id_sel)
                        st.success(f"Juego {id_sel} eliminado correctamente.")
                        st.session_state.show_juego_delete = False
                    except Exception as e:
                        st.error(f"Error al eliminar juego: {e}")


        # Lista de juegos siempre visible
        st.markdown("### Lista de juegos")
        st.dataframe(list_juegos(), use_container_width=True)


            # ==================== ESTADÍSTICAS DEL JUEGO ====================
    elif choice == "📈 Estadísticas Juego":
        st.subheader("📊 Estadísticas del Juego")

        # 1) Selección de partido
        df_jg = list_juegos()
        if df_jg.empty:
            st.warning("No hay juegos registrados.")
        else:
            opts = df_jg.apply(
                lambda r: f"{r.IdJuego} – {r.DescripcionJuego} ({r.FechaYHoraJuego})",
                axis=1
            ).tolist()
            sel = st.selectbox("Selecciona el juego", opts)
            id_sel = sel.split(" – ")[0]

            # 2) Ejecutar SP y obtener DataFrames
            try:
                df_local, df_visit = get_estadisticas_juego(id_sel)

                # 3) Encabezados manuales (ya que los PRINT no llegan como tablas)
                curr = df_jg[df_jg.IdJuego == id_sel].iloc[0]
                st.markdown(f"**Juego:** {id_sel}  **Fecha:** {curr.FechaYHoraJuego}")
                # Nombre de equipos
                df_eq = list_equipos()
                nom_local = df_eq.loc[df_eq.IdEquipo == curr.IdEquipoA, "NomEquipo"].iloc[0]
                nom_visit = df_eq.loc[df_eq.IdEquipo == curr.IdEquipoB, "NomEquipo"].iloc[0]

                # 4) Mostrar tablas
                st.markdown(f"#### Equipo Local: {nom_local}")
                st.dataframe(df_local, use_container_width=True)

                st.markdown(f"#### Equipo Visitante: {nom_visit}")
                st.dataframe(df_visit, use_container_width=True)

                # 5) Marcador final
                pts_local = int(df_local.loc[df_local["Jugador"] == "Total", "Puntos"])
                pts_visit = int(df_visit.loc[df_visit["Jugador"] == "Total", "Puntos"])
                ganador = (
                    nom_local if pts_local > pts_visit
                    else nom_visit if pts_visit > pts_local
                    else "Empate"
                )
                st.markdown(
                    f"**Marcador final:** {nom_local} {pts_local} – {pts_visit} {nom_visit}  \n"
                    f"**Ganador:** {ganador}"
                )

            except Exception as e:
                st.error(f"Error al obtener estadísticas: {e}")


            # ================ AGREGAR ESTADÍSTICA AL JUEGO ================
    elif choice == "➕ Agregar Estadística Juego":
        st.subheader("➕ Agregar Estadística a un Juego")

        # 1) Selección de juego
        df_jg = list_juegos()
        if df_jg.empty:
            st.warning("No hay juegos registrados.")
        else:
            opts_jg = df_jg.apply(
                lambda r: f"{r.IdJuego} - {r.DescripcionJuego} ({r.FechaYHoraJuego})",
                axis=1
            ).tolist()
            sel_juego = st.selectbox("Selecciona el juego", opts_jg)
            id_juego = sel_juego.split(" - ")[0]

            # 2) Selección de equipo (A o B)
            curr = df_jg[df_jg.IdJuego == id_juego].iloc[0]
            df_eq = list_equipos()
            # extrae nombres para los dos equipos del juego
            equipos = []
            for col in ("IdEquipoA", "IdEquipoB"):
                eq_id = curr[col]
                nom = df_eq.loc[df_eq.IdEquipo == eq_id, "NomEquipo"].iloc[0]
                equipos.append(f"{eq_id} - {nom}")
            sel_eq = st.selectbox("Selecciona el equipo", equipos)
            id_equipo = sel_eq.split(" - ")[0]

            # 3) Selección de jugador del equipo
            df_jug = list_jugadores()
            df_jug_eq = df_jug[df_jug.IdEquipo == id_equipo]
            if df_jug_eq.empty:
                st.warning("No hay jugadores en este equipo.")
            else:
                opts_jug = df_jug_eq.apply(
                    lambda r: f"{r.IdJugador} - {r.NomJugador}", axis=1
                ).tolist()
                sel_jug = st.selectbox("Selecciona el jugador", opts_jug)
                id_jugador = sel_jug.split(" - ")[0]

                # 4) Selección de tipo de estadística
                df_est = list_estadisticas()
                opts_est = df_est.apply(
                    lambda r: f"{r.IdEstadistica} - {r.DescripcionEstadistica}", axis=1
                ).tolist()
                sel_est = st.selectbox("Selecciona la estadística", opts_est)
                id_est = sel_est.split(" - ")[0]

                # 5) Cantidad a registrar
                cantidad = st.number_input("Cantidad registrada", min_value=0, step=1)

                # Botón de inserción
                if st.button("Agregar estadística"):
                    try:
                        insert_estadistica_juego(id_juego, id_est, id_jugador, int(cantidad))
                        st.success(
                            f"Estadística {id_est} ({df_est.loc[df_est.IdEstadistica==id_est,'DescripcionEstadistica'].iloc[0]}) "
                            f"para jugador {id_jugador} en juego {id_juego} registrada."
                        )
                    except Exception as e:
                        st.error(f"Error al agregar estadística: {e}")



    



if __name__ == "__main__":
    main()
