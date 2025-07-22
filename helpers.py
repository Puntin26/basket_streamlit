import os
import pyodbc
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

#  Configuracion base de datos 
load_dotenv()
CONN_STR = os.getenv("DB_CONN")

@st.cache_resource  # mantiene una sola conexion por sesion
def get_conn():
    return pyodbc.connect(CONN_STR, autocommit=True)

# Helpers genericos 

def fetch_df(sql: str, params=()):
    """Ejecuta un SELECT y devuelve un DataFrame."""
    return pd.read_sql(sql, get_conn(), params=params)

def exec_sql(sql: str, params=()):
    """Ejecuta una instrucción DML sin retorno de filas."""
    with get_conn().cursor() as cur:
        cur.execute(sql, params)

# Helper - CIUDAD

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

# Helper - ESTADISTICA

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

# Helper - EQUIPO
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

# Helper - JUGADOR

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

# Helper – JUEGO

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

# Helper - JUEGO (SP Estadisticas)

def get_estadisticas_juego(id_juego: str):
    """
    Ejecuta el sp_EstadisticasDelJuego y devuelve dos DataFrames:
     - df_local: detalle (jugadores + total) del equipo local
     - df_visit: detalle (jugadores + total) del equipo visitante
    """
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("EXEC dbo.sp_EstadisticasDelJuego ?", id_juego)

    # Primer resultset -> stats del equipo local
    cols = [col[0] for col in cur.description]
    rows = cur.fetchall()
    df_local = pd.DataFrame.from_records(rows, columns=cols)

    # Segundo resultset -> stats del equipo visitante
    if cur.nextset():
        cols = [col[0] for col in cur.description]
        rows = cur.fetchall()
        df_visit = pd.DataFrame.from_records(rows, columns=cols)
    else:
        df_visit = pd.DataFrame(columns=cols)

    return df_local, df_visit

# Helper - ESTADISTICA_JUEGO (INSERT)
def insert_estadistica_juego(id_juego: str, id_estadistica: str, id_jugador: str, cantidad: int):
    exec_sql(
        """
        INSERT INTO dbo.EstadisticaJuego
            (IdJuego, IdEstadistica, IdJugador, CantEstadisticaRegistrada)
        VALUES (?, ?, ?, ?)
        """,
        (id_juego, id_estadistica, id_jugador, cantidad),
    )
