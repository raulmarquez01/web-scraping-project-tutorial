"""
Web Scraping Project: Population by Country (Worldometer)

Descarga la tabla de poblacion por pais desde Worldometer, la limpia
y la guarda en una base de datos SQLite, y genera visualizaciones
exploratorias.
"""
import sqlite3
from io import StringIO

import matplotlib.pyplot as plt
import pandas as pd
import requests

URL = "https://www.worldometers.info/world-population/population-by-country/"
HEADERS = {"User-Agent": "Mozilla/5.0"}


def limpiar_numero(valor):
    if isinstance(valor, str):
        valor = valor.replace('%', '').replace(',', '').replace('−', '-').strip()
    return pd.to_numeric(valor, errors='coerce')


def obtener_datos():
    response = requests.get(URL, headers=HEADERS)
    response.encoding = 'utf-8'
    tables = pd.read_html(StringIO(response.text))
    df = tables[0]
    return df


def limpiar_datos(df):
    columnas_a_limpiar = ['Yearly Change', 'Net Change', 'Migrants (net)', 'Urban Pop %', 'World Share']
    for col in columnas_a_limpiar:
        df[col] = df[col].apply(limpiar_numero)
    df = df.dropna(how='all')
    return df


def guardar_en_sqlite(df, db_name='population.db'):
    conn = sqlite3.connect(db_name)
    df.to_sql('population_by_country', conn, if_exists='replace', index=False)
    conn.commit()
    return conn


def graficar(df):
    top10 = df.nlargest(10, 'Population 2026')
    plt.figure(figsize=(10, 6))
    plt.barh(top10['Country (or dependency)'], top10['Population 2026'])
    plt.xlabel('Population 2026')
    plt.title('Top 10 Most Populous Countries')
    plt.gca().invert_yaxis()
    plt.tight_layout()
    plt.show()

    plt.figure(figsize=(10, 6))
    plt.scatter(df['Land Area (Km²)'], df['Density (P/Km²)'], alpha=0.6)
    plt.xlabel('Land Area (Km²)')
    plt.ylabel('Density (P/Km²)')
    plt.title('Population Density vs. Land Area')
    plt.tight_layout()
    plt.show()

    plt.figure(figsize=(10, 6))
    plt.hist(df['Fert. Rate'].dropna(), bins=20, edgecolor='black')
    plt.xlabel('Fertility Rate')
    plt.ylabel('Number of Countries')
    plt.title('Distribution of Fertility Rate by Country')
    plt.tight_layout()
    plt.show()


if __name__ == '__main__':
    df = obtener_datos()
    df = limpiar_datos(df)
    conn = guardar_en_sqlite(df)

    verificacion = pd.read_sql('SELECT * FROM population_by_country LIMIT 5', conn)
    print(verificacion)

    graficar(df)
