#encoding: utf-8

import os
from tkinter import *
from tkinter import messagebox
from whoosh.index import create_in,open_dir
from whoosh.fields import Schema, TEXT, KEYWORD
from whoosh.qparser import QueryParser


class Ventana(object):
    def __init__(self):
        directorioDocumentos = 'Correos'
        directorioDestino = 'Index'
        top = Tk()
        indexar = Button(top, text = 'Indexar', command = lambda: self.indexar(directorioDocumentos, directorioDestino))
        indexar.pack(side = LEFT)
        buscar = Button(top, text = 'Buscar remitente', command = lambda: self.buscarRemitente(directorioDestino))
        buscar.pack(side = LEFT)
        top.mainloop()
        
    def schema(self):
        schema = Schema(remitente=TEXT(stored=True),
                      destinatarios=KEYWORD(stored=True),
                      asunto=TEXT(stored=True),
                      contenido=TEXT(stored=True))
        return schema
    
    def añadirDocumentos(self, writer, ruta, nombreDocumento):
        fichero = open(ruta + '\\' + nombreDocumento, "r")
        remitenteDato = fichero.readline().strip()
        destinatariosDato = fichero.readline().strip()
        asuntoDato = fichero.readline().strip()
        contenidoDato = fichero.read()
        fichero.close()           
        writer.add_document(remitente=remitenteDato, destinatarios=destinatariosDato, asunto=asuntoDato, contenido=contenidoDato)
        
    def indexar(self, directorioDocumentos, directorioDestino):
        if not os.path.exists(directorioDocumentos):
            print ('Error: no existe el directorio de documentos ' + directorioDocumentos)
        else:
            if not os.path.exists(directorioDestino):
                os.mkdir(directorioDestino)
        ix = create_in(directorioDestino, schema = self.schema())
        writer = ix.writer()
        i = 0
        for nombreDocumento in os.listdir(directorioDocumentos):
            if not os.path.isdir(directorioDocumentos + nombreDocumento):
                self.añadirDocumentos(writer, directorioDocumentos, nombreDocumento)
                i = i + 1
        messagebox.showinfo('Fin de indexado', 'Se han indexado ' + str(i) + ' correos')
        writer.commit()
        
    def buscarRemitente(self, directorioDestino):
        def listarBusqueda(event):
            lb.delete(0, END)
            ix = open_dir(directorioDestino)      
            with ix.searcher() as searcher:
                query = QueryParser('remitente', ix.schema).parse(str(en.get()))
                results = searcher.search(query)
                for row in results:
                    lb.insert(END, 'Destinatarios: ' + row['destinatarios'])
                    lb.insert(END, 'Asunto: ' + row['asunto'])
                    lb.insert(END, '')
        v = Toplevel()
        v.title('Búsqueda por remitentes')
        f = Frame(v)
        f.pack(side = TOP)
        lb = Label(f, text = 'Introduzca el correo del remitente:')
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