#encoding: utf-8

import os
from tkinter import *
from tkinter import messagebox
from whoosh.index import create_in,open_dir
from whoosh.fields import Schema, TEXT, KEYWORD, DATETIME, ID
from whoosh.qparser import QueryParser, MultifieldParser
from datetime import datetime
from whoosh import qparser


class Ventana(object):
    def __init__(self):
        directorioCorreos = 'Correos'
        directorioAgenda = 'Agenda'
        directorioDestino = 'Index'
        agenda = self.leerAgenda(directorioAgenda)
        top = Tk()
        indexar = Button(top, text = 'Indexar', command = lambda: self.indexar(directorioCorreos, directorioDestino))
        indexar.pack(side = LEFT)
        buscarPorAsuntoCuerpo = Button(top, text = 'Buscar por asunto o cuerpo', command = lambda: self.buscarPorAsuntoCuerpo(directorioDestino, agenda))
        buscarPorAsuntoCuerpo.pack(side = LEFT)
        buscarPorFechaPosterior = Button(top, text = 'Buscar por fecha posterior a la introducida', command = lambda: self.buscarPosteriorAFecha(directorioDestino))
        buscarPorFechaPosterior.pack(side = LEFT)
        buscarFicheroSpam = Button(top, text = 'Buscar ficheros marcados como spam según lo introducido', command = lambda: self.buscarFicheroSpam(directorioDestino))
        buscarFicheroSpam.pack(side = LEFT)
        top.mainloop()
        
    def schema(self):
        schema = Schema(remitente=TEXT(stored=True),
                      destinatarios=KEYWORD(stored=True),
                      fecha=DATETIME(stored=True),
                      asunto=TEXT(stored=True),
                      contenido=TEXT(stored=True),
                      nombrefichero=ID(stored=True))
        return schema
    
    def añadirDocumentos(self, writer, ruta, nombreDocumento):
        fichero = open(ruta + '\\' + nombreDocumento, 'r')
        remitenteDato = fichero.readline().strip()
        destinatariosDato = fichero.readline().strip()
        fechaDato = fichero.readline().strip()
        fechaDato = datetime.strptime(fechaDato, '%Y%m%d')
        asuntoDato = fichero.readline().strip()
        contenidoDato = fichero.read()
        fichero.close()           
        writer.add_document(remitente=remitenteDato, destinatarios=destinatariosDato, fecha=fechaDato, asunto=asuntoDato, contenido=contenidoDato, nombrefichero=nombreDocumento)
        
    def indexar(self, directorioCorreos, directorioDestino):
        if not os.path.exists(directorioCorreos):
            print ('Error: no existe el directorio de documentos ' + directorioCorreos)
        else:
            if not os.path.exists(directorioDestino):
                os.mkdir(directorioDestino)
        ix = create_in(directorioDestino, schema = self.schema())
        writer = ix.writer()
        i = 0
        for nombreDocumento in os.listdir(directorioCorreos):
            if not os.path.isdir(directorioCorreos + nombreDocumento):
                self.añadirDocumentos(writer, directorioCorreos, nombreDocumento)
                i = i + 1
        messagebox.showinfo('Fin de indexado', 'Se han indexado ' + str(i) + ' correos')
        writer.commit()
        
    def leerAgenda(self, directorioAgenda):
        if not os.path.exists(directorioAgenda):
            print ('Error: no existe el directorio de agenda ' + directorioAgenda)
        else:
            dic = {}
            fichero = open(directorioAgenda + '\\' + 'agenda.txt', 'r')
            email = fichero.readline()
            while email:
                nombre = fichero.readline()
                dic[email.strip()] = nombre.strip()
                email = fichero.readline()
            print ('Agenda cargada')
            return dic
        
    def buscarPorAsuntoCuerpo(self, directorioDestino, agenda):
        def listarBusqueda(event):
            lb.delete(0, END)
            ix = open_dir(directorioDestino)      
            with ix.searcher() as searcher:
                query = MultifieldParser(['asunto','contenido'], ix.schema).parse(str(en.get()))
                results = searcher.search(query)
                for row in results:
                    lb.insert(END, 'Remitente: ' + agenda[row['remitente']])
                    lb.insert(END, 'Asunto: ' + row['asunto'])
                    lb.insert(END, '')
        v = Toplevel()
        v.title('Búsqueda por asunto o contenido')
        f = Frame(v)
        f.pack(side = TOP)
        lb = Label(f, text = 'Introduzca texto para buscar en el asunto o contenido del correo:')
        lb.pack(side = LEFT)
        en = Entry(f)
        en.bind('<Return>', listarBusqueda)
        en.pack(side = LEFT)
        sc = Scrollbar(v)
        sc.pack(side = RIGHT, fill = Y)
        lb = Listbox(v, yscrollcommand = sc.set)
        lb.pack(side = BOTTOM, fill = BOTH)
        sc.config(command = lb.yview)
    
    def buscarPosteriorAFecha(self, directorioDestino):
        def listarBusqueda(event):
            lb.delete(0, END)
            ix = open_dir(directorioDestino) 
            myquery = '{'+ en.get() + 'TO]'     
            with ix.searcher() as searcher:
                query =  QueryParser('fecha', ix.schema).parse(myquery)
                results = searcher.search(query)
                for row in results:
                    lb.insert(END, 'Fecha: ' + row['fecha'].strftime('%d/%m/%Y'))
                    lb.insert(END, 'Remitente: ' + row['remitente'])
                    lb.insert(END, 'Destinatarios: ' + row['destinatarios'])
                    lb.insert(END, 'Asunto: ' + row['asunto'])
                    lb.insert(END, '')
        v = Toplevel()
        v.title('Búsqueda por fecha posterior a la introducida')
        f = Frame(v)
        f.pack(side = TOP)
        lb = Label(f, text = 'Introduzca la fecha (YYYYMMDD):')
        lb.pack(side = LEFT)
        en = Entry(f)
        en.bind('<Return>', listarBusqueda)
        en.pack(side = LEFT)
        sc = Scrollbar(v)
        sc.pack(side = RIGHT, fill = Y)
        lb = Listbox(v, yscrollcommand = sc.set)
        lb.pack(side = BOTTOM, fill = BOTH)
        sc.config(command = lb.yview)
    
    def buscarFicheroSpam(self, directorioDestino):
        def listarBusqueda(event):
            lb.delete(0, END)
            ix = open_dir(directorioDestino)  
            with ix.searcher() as searcher:
                query =  QueryParser('asunto', ix.schema, group = qparser.OrGroup).parse(str(en.get()))
                results = searcher.search(query)
                for row in results:
                    lb.insert(END, 'Fichero: ' + row['nombrefichero'])
        v = Toplevel()
        v.title('Búsqueda de ficheros por asunto')
        f = Frame(v)
        f.pack(side = TOP)
        lb = Label(f, text = 'Introduzca alguna/s palabra/s:')
        lb.pack(side = LEFT)
        en = Entry(f)
        en.bind('<Return>', listarBusqueda)
        en.pack(side = LEFT)
        sc = Scrollbar(v)
        sc.pack(side = RIGHT, fill = Y)
        lb = Listbox(v, yscrollcommand = sc.set)
        lb.pack(side = BOTTOM, fill = BOTH)
        sc.config(command = lb.yview)    
        
if __name__ == '__main__':
    Ventana()