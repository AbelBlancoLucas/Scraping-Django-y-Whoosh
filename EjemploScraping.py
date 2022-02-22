#encoding:utf-8
from tkinter import *
from tkinter import messagebox
import os
from whoosh.index import create_in,open_dir
from whoosh.fields import Schema, TEXT, KEYWORD, DATETIME, ID,IDLIST
from whoosh.qparser import QueryParser
import sqlite3
from bs4 import BeautifulSoup
import urllib.request
from django.utils.functional import empty
from datetime import datetime
import time



def cargar():
    datos=extraerDatosURL()
    #nuevo=datos[1]
    #nuevo=nuevo[0]
    #nuevo=nuevo[2]
   
   

    if not os.path.exists("Temas"):
        os.mkdir("Temas")
    if not os.path.exists("Respuestas"):
        os.mkdir("Respuestas")

    ix = create_in("Temas", get_schema())
    ix1 = create_in("Respuestas",get_schema1())
    
    writer = ix.writer()
    writer1 =ix1.writer()
    i=0
    j=0
    numero= add_doc(writer,datos[0],i)
    numero1=add_doc1(writer1,datos[1],j)
    messagebox.showinfo("Indexación", "Se han indexado "  + str(numero) + " TEMAS")
    messagebox.showinfo("Indexación", "Se han indexado "  + str(numero1) + " RESPUESTAS")
    writer.commit()
    writer1.commit()

def get_schema(): 
    return Schema(titulo=TEXT(stored=True), enlace=ID(stored=True), autor=KEYWORD(stored=True), fecha=DATETIME(stored=True), respuestas=TEXT(stored=True), visitas=TEXT(stored=True))

def get_schema1(): 
    return Schema(titulo=TEXT(stored=True), enlace=ID(stored=True), texto=TEXT(stored=True), fechas=DATETIME(stored=True), autores=TEXT(stored=True))         
         
def add_doc(writer, datos,i): 
    
    for dato in datos:
        tit=dato[0]
        enl=dato[1]
        aut=dato[2]
        fec=dato[3]
        res=dato[4]
        vis=dato[5]   
    
        writer.add_document(titulo=tit, enlace=enl, autor=aut, fecha=fec, respuestas=res,visitas=vis) 
        
        i=i+1
    return i

def add_doc1(writer, datos,j): 
    
    for dato in datos:
        tit=dato[0]
        enl=dato[1]
        tex=dato[2]
        fec=dato[3]
        aut=dato[4]   
    
        writer.add_document(titulo=tit, enlace=enl, texto=tex, fechas=fec, autores=aut) 
        
        j=j+1
    return j

def extraerDatosURL():
    pagina = urllib.request.urlopen("https://foros.derecho.com/foro/34-Derecho-Inmobiliario").read()
    soup = BeautifulSoup(pagina, 'lxml')
    
    foro = soup.find_all('div', class_ = ["threadlist"])
    
    temas=[]
    respuestas=[]
    
    for div in foro:
        tabla=div.find('ol')
        foros=tabla.find_all('li', class_ = ["threadbit"])
        
        for entrada in foros:
            
            ##################### TEMAS #################################
            
            titulo=entrada.find('div', class_= ["threadinfo"])
            titulo=titulo.find('div', class_= ["inner"])
            titulo=titulo.find('a', class_= ["title"])
            titulo=titulo['title']
            
            
            enlace=entrada.find('div', class_= ["threadinfo"])
            enlace=enlace.find('div', class_= ["inner"])
            enlace=enlace.find('a', class_= ["title"])
            enlace=enlace['href']
            
            
            autor=entrada.find('div', class_= ["popupmenu memberaction"])
            autor=autor.find('a')
            autor=autor.get_text()
          
    
            fecha=entrada.find('dl', class_=["threadlastpost td"])
            fecha=fecha.find_all('dd')
            fecha=fecha[1]
            fecha=fecha.get_text().split()[0]
            fecha=fecha[0:-1]
            fecha=datetime.strptime(fecha,"%d/%m/%Y")
            
            respuesta=entrada.find("ul", class_= ["threadstats td alt"])
            respuesta=respuesta.find('li')
            respuesta=respuesta.get_text()
            
            visitas=entrada.find("ul", class_= ["threadstats td alt"])
            visitas=visitas.find_all('li')
            visitas=visitas[1].get_text()
            
            ################## RESPUESTAS ##########################################
            
            inEnlace="https://foros.derecho.com/"+enlace
            
            expresion = re.compile( "tema\/[\d]{1,}")
            prueba =expresion.search(inEnlace)
            inEnlace="https://foros.derecho.com/"+prueba.group(0)
           
            inPagina = urllib.request.urlopen(inEnlace).read()
            inSoup = BeautifulSoup(inPagina, 'lxml')
            
            inForo =  inSoup.find('div',class_=["postlist restrain"])
            inForo= inForo.find('ol',class_=["posts"])
            inForo=inForo.find_all('li', class_=["postbitlegacy postbitim postcontainer old"])
     
            fechas=[]
            autores=[]
            
            for div in inForo:
                texto=div.find('div',class_=["postdetails"])
                texto=texto.find('blockquote')
        
                texto=texto.get_text().strip()
                
                fechasRe=div.find('span',class_=["date"]).get_text().split()[0]
                fechasRe=fechasRe[0:-1]
                fechasRe=datetime.strptime(fechasRe,"%d/%m/%Y")
                fechas.append(fechasRe)
                
                
                autoresRe=div.find('div',class_=["username_container"])
                autoresRe=autoresRe.find('a')
                if autoresRe !=None:
                    autoresRe=autoresRe.get_text()
                    autores.append(autoresRe)
                
                tuplaRespuesta=(titulo,enlace,texto,fechas,autores)
                respuestas.append(tuplaRespuesta)

            tuplaTema=(titulo,enlace,autor,fecha,respuesta,visitas)
            temas.append(tuplaTema)
            
            
            
    
         
    print(respuestas)  
    return temas, respuestas
    
    
     
    

def titulo():
    def mostrar_titulo(event):
        lb.delete(0,END)
        ix=open_dir("Temas")
        with ix.searcher() as searcher:
            query = QueryParser("titulo", ix.schema).parse(str(en.get())) 
            results = searcher.search(query)
            
            for r in results:
                lb.insert(END,r['titulo'])
                lb.insert(END,r['autor'])
                lb.insert(END,r['fecha'])
                lb.insert(END,'')
                   
    v = Toplevel()
    v.title("Busqueda por TITULO")
    f =Frame(v)
    f.pack(side=TOP)
    l = Label(f, text="Introduzca el titulo:")
    l.pack(side=LEFT)
    en = Entry(f)
    en.bind("<Return>", mostrar_titulo)
    en.pack(side=LEFT)
    sc = Scrollbar(v)
    sc.pack(side=RIGHT, fill=Y)
    lb = Listbox(v, yscrollcommand=sc.set)
    lb.pack(side=BOTTOM, fill = BOTH)
    sc.config(command = lb.yview)   
            
        
    

def autor():
    def mostrar_autor(event):
        lb.delete(0,END)
        ix=open_dir("Temas")
        with ix.searcher() as searcher:
            query = QueryParser("autor", ix.schema).parse(str(en.get())) 
            results = searcher.search(query)
            
            for r in results:
                lb.insert(END,r['titulo'])
                lb.insert(END,r['autor'])
                lb.insert(END,r['fecha'])
                lb.insert(END,'')
                   
    v = Toplevel()
    v.title("Busqueda por AUTOR")
    f =Frame(v)
    f.pack(side=TOP)
    l = Label(f, text="Introduzca el autor:")
    l.pack(side=LEFT)
    en = Entry(f)
    en.bind("<Return>", mostrar_autor)
    en.pack(side=LEFT)
    sc = Scrollbar(v)
    sc.pack(side=RIGHT, fill=Y)
    lb = Listbox(v, yscrollcommand=sc.set)
    lb.pack(side=BOTTOM, fill = BOTH)
    sc.config(command = lb.yview)  

def texto():
    def mostrar_texto(event):
        lb.delete(0,END)
        ix=open_dir("Respuestas")
        with ix.searcher() as searcher:
            query = QueryParser("texto", ix.schema).parse(str(en.get())) 
            results = searcher.search(query)
           
            
            for r in results:
                lb.insert(END,r['texto'])
                lb.insert(END,r['autores'])
                lb.insert(END,r['fechas'])
                lb.insert(END,'')
                   
    v = Toplevel()
    v.title("Busqueda por TEXTO")
    f =Frame(v)
    f.pack(side=TOP)
    l = Label(f, text="Introduzca el texto:")
    l.pack(side=LEFT)
    en = Entry(f)
    en.bind("<Return>", mostrar_texto)
    en.pack(side=LEFT)
    sc = Scrollbar(v)
    sc.pack(side=RIGHT, fill=Y)
    lb = Listbox(v, yscrollcommand=sc.set)
    lb.pack(side=BOTTOM, fill = BOTH)
    sc.config(command = lb.yview)  

################################################## TKINTER ####################################################
    
def ventana_principal():
    
    root=Tk()
    menubar = Menu(root)
    root.config(menu=menubar)
    
    filemenu = Menu(menubar, tearoff=0)
    editmenu = Menu(menubar, tearoff=0)
    updatemenu1 = Menu(menubar,tearoff=0)
    updatemenu2 = Menu(menubar,tearoff=0)
           
    menubar.add_cascade(label="Inicio", menu=filemenu)
    menubar.add_cascade(label="Buscar", menu=editmenu)
    
    filemenu.add_command(label="Indexar", command=cargar)
    filemenu.add_separator()
    filemenu.add_command(label="Salir", command=root.quit)
    
    editmenu.add_cascade(label="Temas", menu=updatemenu1)
    editmenu.add_cascade(label="Respuestas",menu=updatemenu2)
   
    updatemenu1.add_command(label="Titulo",command=titulo)
    updatemenu1.add_command(label="Autor",command=autor)
    updatemenu2.add_command(label="Texto",command=texto)
    
    root.mainloop()
                           
if __name__ == '__main__':
    ventana_principal()