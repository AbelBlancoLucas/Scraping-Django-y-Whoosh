#encoding:utf-8

import re
from bs4 import BeautifulSoup
import urllib.request
from tkinter import *
from tkinter import messagebox
import sqlite3

TEMPORADA="2017_2018"

def extraer_jornadas():
    url="http://resultados.as.com/resultados/futbol/primera/"+TEMPORADA+"/calendario/"
    f = urllib.request.urlopen(url)
    s = BeautifulSoup(f,"lxml")
    
    l = s.find_all("div", class_= ["cont-modulo","resultados"])
    print(l)
    return l


def imprimir_lista(cursor):
    v = Toplevel()
    v.title("TEMPORADA "+TEMPORADA)
    sc = Scrollbar(v)
    sc.pack(side=RIGHT, fill=Y)
    lb = Listbox(v, width = 150, yscrollcommand=sc.set)
    jornada=0
    for row in cursor:
        if row[0] != jornada:
            jornada=row[0]
            lb.insert(END,"\n")
            s = 'JORNADA '+ str(jornada)
            lb.insert(END,s)
            lb.insert(END,"-----------------------------------------------------")
        s = "     " + row[1] +' '+ str(row[3]) +'-'+ str(row[4]) +' '+  row[2]
        lb.insert(END,s)
    lb.pack(side=LEFT,fill=BOTH)
    sc.config(command = lb.yview)

 
def almacenar_bd():
    conn = sqlite3.connect('as.db')
    conn.text_factory = str  # para evitar problemas con el conjunto de caracteres que maneja la BD
    conn.execute("DROP TABLE IF EXISTS JORNADAS") 
    conn.execute('''CREATE TABLE JORNADAS
       (JORNADA       INTEGER NOT NULL,
       LOCAL          TEXT    NOT NULL,
       VISITANTE      TEXT    NOT NULL,
       GOLES_L        INTEGER    NOT NULL,
       GOLES_V        INTEGER NOT NULL,
       LINK           TEXT);''')
    l = extraer_jornadas()
    for i in l:
        jornada = int(re.compile('\d+').search(i['id']).group(0))
        partidos = i.find_all("tr",id=True)
        for p in partidos:
            equipos= p.find_all("span",class_="nombre-equipo")
            local = equipos[0].string.strip()
            visitante = equipos[1].string.strip()
            resultado_enlace = p.find("a",class_="resultado")
            if resultado_enlace != None:
                goles=re.compile('(\d+).*(\d+)').search(resultado_enlace.string.strip())
                goles_l=goles.group(1)
                goles_v=goles.group(2)
                link = resultado_enlace['href']
                
                conn.execute("""INSERT INTO JORNADAS VALUES (?,?,?,?,?,?)""",(jornada,local,visitante,goles_l,goles_v,link))
    conn.commit()
    cursor = conn.execute("SELECT COUNT(*) FROM JORNADAS")
    messagebox.showinfo( "Base Datos", "Base de datos creada correctamente \nHay " + str(cursor.fetchone()[0]) + " registros")
    conn.close()


def listar_bd():
    conn = sqlite3.connect('as.db')
    conn.text_factory = str  
    cursor = conn.execute("SELECT * FROM JORNADAS ORDER BY JORNADA")
    imprimir_lista(cursor)
    conn.close()
 
def buscar_bd():
    def lista(event):
            conn = sqlite3.connect('as.db')
            conn.text_factory = str
            cursor = conn.execute("SELECT * FROM JORNADAS WHERE JORNADA='" + en.get() +"'")
            conn.close
            imprimir_lista(cursor) 
      
            
    conn = sqlite3.connect('as.db')
    conn.text_factory = str
        
    v = Toplevel()
    lb = Label(v, text="Introduzca la Jornada")
    en = Entry(v)
    en.bind("<Return>", lista)
    lb.pack(side=LEFT)
    en.pack(side=LEFT)
    
    conn.close()
    
def estadistica_bd():  
    def lista(event):
            conn = sqlite3.connect('as.db')
            conn.text_factory = str
            cursor = conn.execute("SELECT * FROM JORNADAS WHERE JORNADA='" + en.get() +"'")
            ventana_estadistica(cursor)
            conn.close
      
            
    conn = sqlite3.connect('as.db')
    conn.text_factory = str
    v = Toplevel()
    lb = Label(v, text="Introduzca la Jornada")
    en = Entry(v)
    en.bind("<Return>", lista)
    lb.pack(side=LEFT)
    en.pack(side=LEFT)
    
    conn.close()
    
def ventana_estadistica(cursor):
    v = Toplevel()
    v.title("Estadísticas")
    victorias_visitantes=0
    victorias_locales=0
    empates=0
    goles=0
    for row in cursor:
        goles = goles + row[3] + row[4]
        if row[3] == row[4]:
            empates=empates + 1
        elif row[3] < row[4]:
            victorias_visitantes=victorias_visitantes+1
        else:
            victorias_locales=victorias_locales+1
    Label(v, text="Total goles jornada:"+str(goles)).pack()
    Label(v, text="-------------------").pack()
    Label(v, text="Empates:"+str(empates)).pack()
    Label(v, text="Victorias Locales:"+str(victorias_locales)).pack()
    Label(v, text="Victorias visitantes:"+str(victorias_visitantes)).pack()

    
  
def ventana_principal():
    top = Tk()
    top.title("TEMPORADA "+ TEMPORADA)
    almacenar = Button(top, text="Almacenar Resultados", command = almacenar_bd)
    almacenar.pack(side = TOP)
    listar = Button(top, text="Listar Jornadas", command = listar_bd)
    listar.pack(side = TOP)
    buscar = Button(top, text="Buscar Jornada", command = buscar_bd)
    buscar.pack(side = TOP)
    estadistica = Button(top, text="Estadísticas Jornada", command = estadistica_bd)
    estadistica.pack(side = TOP)
    top.mainloop()
    

if __name__ == "__main__":
    ventana_principal()


