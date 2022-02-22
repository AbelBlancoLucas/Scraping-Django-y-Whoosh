#encoding: utf-8

import urllib.request, re
from tkinter import *
from tkinter import messagebox
import sqlite3
from bs4 import BeautifulSoup
import datetime

class VentanaDatos:
    def __init__(self, Ventana):
        menubar = Ventana.menubar
        filemenu = Menu(menubar, tearoff = 0)
        filemenu.add_command(label = 'Cargar', command = self.leerYCargarDatos)
        filemenu.add_command(label = 'Mostrar', command = self.mostrar)
        filemenu.add_separator()
        filemenu.add_command(label = 'Salir', command = lambda: self.salir(Ventana))
        menubar.add_cascade(label = 'Datos', menu = filemenu)

    def leerYCargarDatos(self):
        conexion = sqlite3.connect('ejercicioBeautifulSoup3.db')
        conexion.text_factory = str
        conexion.execute('DROP TABLE IF EXISTS NOTICIAS')
        conexion.execute('''CREATE TABLE NOTICIAS
           (ID INTEGER PRIMARY KEY  AUTOINCREMENT,
           TITULO TEXT NOT NULL,
           ENLACE TEXT NOT NULL,
           AUTOR TEXT NOT NULL,
           FECHA_HORA TEXT NOT NULL,
           CONTENIDO TEXT NOT NULL);''')
        for pagina in range(1, 4):
            url = 'https://www.meneame.net/?page' + str(pagina)
            file = urllib.request.urlopen(url)
            paser = BeautifulSoup(file, 'html.parser')
            items = paser.find_all('div', class_= 'center-content')
            for i in items:
                titulo = i.find('h2').find('a').string
                enlace = i.find('h2').find('a')['href']
                autor = i.find('div', class_= 'news-submitted').find_all('a')[1].string
                try:
                    fecha_hora = i.find('div', class_= 'news-submitted').find_all('span')[1]['data-ts']
                except IndexError:
                    fecha_hora = i.find('div', class_= 'news-submitted').find_all('span')[0]['data-ts']
                fecha_hora = datetime.datetime.fromtimestamp(int(fecha_hora))
                fecha_hora = fecha_hora.strftime('%d/%m/%Y %H:%M')
                contenido = i.find('div', class_= 'news-content').text
                conexion.execute('INSERT INTO NOTICIAS (TITULO, ENLACE, AUTOR, FECHA_HORA, CONTENIDO) VALUES (?, ?, ?, ?, ?)', (titulo, enlace, autor, fecha_hora, contenido)) 
        conexion.commit()
        query = conexion.execute('SELECT COUNT(*) FROM NOTICIAS')  
        messagebox.showinfo('Base Datos', 'Base de datos creada correctamente \nHay ' + str(query.fetchone()[0]) + ' registros')
        conexion.close()
        
    def mostrar(self):
        conn = sqlite3.connect('ejercicioBeautifulSoup3.db')
        conn.text_factory = str
        cursor = conn.execute('SELECT TITULO, AUTOR, FECHA_HORA FROM NOTICIAS')
        v = Toplevel()
        sc = Scrollbar(v)
        sc.pack(side = RIGHT, fill = Y)
        lb = Listbox(v, width = 150, yscrollcommand = sc.set)
        for row in cursor:
            lb.insert(END,'Título: ' + row[0])
            lb.insert(END,'Autor: ' + row[1])
            lb.insert(END,'Fecha y hora de publicación: ' + row[2])
            lb.insert(END,'')
        lb.pack(side = LEFT, fill = BOTH)
        sc.config(command = lb.yview)
        conn.close()
           
    def salir(self,Ventana):
        Ventana.tk.quit()
        
class VentanaBuscar:  
    def __init__(self, Ventana):
        menubar = Ventana.menubar
        filemenu = Menu(menubar, tearoff = 0)
        filemenu.add_command(label='Noticias por autor', command = self.eligeAutor)
        filemenu.add_command(label='Fecha', command = self.buscarPorFecha)
        menubar.add_cascade(label='Buscar', menu = filemenu)
        
    def eligeAutor(self):
        conn = sqlite3.connect('ejercicioBeautifulSoup3.db')
        conn.text_factory = str
        autores = conn.execute('SELECT DISTINCT AUTOR FROM NOTICIAS')
        autores = autores.fetchall()
        aut = []
        for i in autores:
            i = i[0].split(',')
            aut.append(i)
        res = list(map(lambda x:x[0], aut));
        v = Toplevel()
        spinb = Spinbox(v, values = res)
        spinb.pack()
        spinb.grid(row = 0, column = 0)
        B = Button(v, text = 'Seleccionar autor', command = lambda: self.mostrarAutor(spinb.get()))
        B.grid(row = 1, column = 0)
        self.marca = spinb.get()
        
    def mostrarAutor(self, autores):
        conn = sqlite3.connect('ejercicioBeautifulSoup3.db')
        conn.text_factory = str
        s = '%' + autores + '%'
        cursor = conn.execute('SELECT TITULO, AUTOR, FECHA_HORA FROM NOTICIAS WHERE AUTOR LIKE ?', (s,))
        v = Toplevel()
        sc = Scrollbar(v)
        sc.pack(side = RIGHT, fill = Y)
        lb = Listbox(v, width = 150, yscrollcommand = sc.set)
        for row in cursor:
            lb.insert(END, 'Título: ' + row[0])
            lb.insert(END, 'Autor: ' + row[1])
            lb.insert(END, 'Fecha y hora de publicación: ' + row[2])
            lb.insert(END, '')
        lb.pack(side = LEFT, fill = BOTH)
        sc.config(command = lb.yview)
        conn.close()
    
    def buscarPorFecha(self):
        def listarBusqueda(event):
            conn = sqlite3.connect('ejercicioBeautifulSoup3.db')
            conn.text_factory = str
            s = '%' + en.get() + '%' 
            cursor = conn.execute('SELECT TITULO, AUTOR, FECHA_HORA FROM NOTICIAS WHERE FECHA_HORA LIKE ?', (s,))
            v = Toplevel()
            sc = Scrollbar(v)
            sc.pack(side = RIGHT, fill = Y)
            lb = Listbox(v, width = 150, yscrollcommand = sc.set)
            for row in cursor:
                lb.insert(END, 'Título: ' + row[0])
                lb.insert(END, 'Autor: ' + row[1])
                lb.insert(END, 'Fecha y hora de publicación: ' + row[2])
                lb.insert(END, '')
            lb.pack(side = LEFT, fill = BOTH)
            sc.config(command = lb.yview)
            conn.close()
        v = Toplevel()
        lb = Label(v, text='Introduzca la fecha (dd/mm/aaaa): ')
        lb.pack(side = LEFT)
        en = Entry(v)
        en.bind('<Return>', listarBusqueda)
        en.pack(side = LEFT)
        
class Ventana:
    def lanzar(self):
        self.tk.mainloop()
        
    def __init__(self):      
        self.tk = Tk()
        self.menubar = Menu(self.tk)
        VentanaDatos(self)
        VentanaBuscar(self)
        self.tk.config(menu=self.menubar)
        self.lanzar()

if __name__ == '__main__':
    Ventana()
