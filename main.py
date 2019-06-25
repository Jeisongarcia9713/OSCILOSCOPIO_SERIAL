
from PyQt5.QtWidgets import*
from PyQt5.uic import loadUi
import time
from matplotlib.backends.backend_qt5agg import (NavigationToolbar2QT as NavigationToolbar)
import threading
from PyQt5 import QtCore, QtWidgets
import numpy as np
import random
from matplotlib.animation import TimedAnimation
import serial
from PyQt5.QtCore import Qt
import pandas as pd 
import csv 

class Serial():

    def __init__(self,Periodo,label):
        self.periodo=Periodo
        self.datosOsc=np.zeros((8,int(5/self.periodo+1)),dtype=float)
        self.ser = serial.Serial()
        self.ser.baudrate = 115200
        self.ser.port = '/dev/ttyACM0'
        self.open=False
        self.hilo= threading.Thread(target=self.update, args=())
        self.cuenta=0
        self.time=np.linspace(0,5,5/self.periodo+1)
        self.stop=True
        self.Identificacion=False
        self.label=label
        self.tiempo=None
        self.entrada=None
        self.datosID=np.zeros((8,1))
        self.cuenta1=0
    def update(self):
        Rdatos=0
        x=0
        while self.open:
            if self.stop==False:#espera a  exista un dato
                try:
                    datos=self.ser.readline()
               
                    #self.ser.reset_input_buffer()
                except:
                    self.label.setText('puerto serial desconectado')
                    self.ser.close()
                    self.open=False
                    self.label.setStyleSheet('color: red')

                
                if (datos.decode('cp1250').replace('\n','')=='ok'):
                    Rdatos=1
                    x=int(0)
                else:
                    if(datos.decode('cp1250').replace('\n','')=='en'):
                        self.ser.flushInput()
                        Rdatos=0 
                        if self.stop==False:
                            self.cuenta=self.cuenta+1;
                            if(self.cuenta==int(5/self.periodo)):
                                self.correrDatos();
                                self.cuenta=self.cuenta-1;
                        if self.Identificacion==True:
                            self.cuenta1=self.cuenta1+1
                            if self.cuenta1== len(self.entrada):
                                self.stop=True
                                self.Guardar_Iden()
                                self.cuenta1=0
                            else:
                                #print(self.entrada[self.cuenta1])
                                self.write(self.entrada[self.cuenta1])

                    else:
                        try:
                            
                            if(Rdatos==1) and self.stop==False:
                                data=int(datos.decode('cp1250'))
                                if x<8:
                                    try:
                                        self.datosOsc[x,self.cuenta]=float(data/100)
                                        self.datosID[x,self.cuenta1]=float(data/100)
                                    except:
                                        self.datosOsc[x,self.cuenta]=self.datosOsc[x,self.cuenta-1]
                                        print(data)
                                        print(x)
                                x=x+1
                        except:
                            print('error')
                            print(datos)


    def correrDatos(self):
        for n in range(0,self.cuenta-1):
            self.datosOsc[:,n]=self.datosOsc[:,n+1]

    def write(self,message):
        #print(str(int(message*100)).encode('cp1250'))
        self.ser.write(str(int(message*100)).encode('cp1250'))
        self.ser.write(('\n').encode('cp1250'))
     

    def Guardar(self):
        Tiempo  = pd.Series(self.time[range(0,self.cuenta)],name='tiempo')
        Entrada  = pd.Series(self.datosOsc[0,range(0,self.cuenta)],name='entrada')
        P_bola = pd.Series(self.datosOsc[1,range(0,self.cuenta)],name='Pbola')
        V_bola = pd.Series(self.datosOsc[2,range(0,self.cuenta)],name='Vbola')
        I_bola = pd.Series(self.datosOsc[3,range(0,self.cuenta)],name='Ibola')
        S_control = pd.Series(self.datosOsc[4,range(0,self.cuenta)],name='Scontrol')
        A_barra = pd.Series(self.datosOsc[5,range(0,self.cuenta)],name='A_barra')
        v_barra = pd.Series(self.datosOsc[6,range(0,self.cuenta)],name='V_barra')
        I_barra = pd.Series(self.datosOsc[7,range(0,self.cuenta)],name='I_barra')
        m =pd.concat([Tiempo,Entrada,P_bola,V_bola,I_bola,S_control,A_barra,v_barra,I_barra],axis=1)
        m.to_csv('datos_salida.txt',header=True,index=False)

    def Guardar_Iden(self):
        Tiempo  = pd.Series(self.time[range(0,self.cuenta1)],name='tiempo')
        Entrada  = pd.Series(self.datosID[0,range(0,self.cuenta1)],name='entrada')
        P_bola = pd.Series(self.datosID[1,range(0,self.cuenta1)],name='Pbola')
        V_bola = pd.Series(self.datosID[2,range(0,self.cuenta1)],name='Vbola')
        I_bola = pd.Series(self.datosID[3,range(0,self.cuenta1)],name='Ibola')
        S_control = pd.Series(self.datosID[4,range(0,self.cuenta1)],name='Scontrol')
        A_barra = pd.Series(self.datosID[5,range(0,self.cuenta1)],name='A_barra')
        v_barra = pd.Series(self.datosID[6,range(0,self.cuenta1)],name='V_barra')
        I_barra = pd.Series(self.datosID[7,range(0,self.cuenta1)],name='I_barra')
        m =pd.concat([Tiempo,Entrada,P_bola,V_bola,I_bola,S_control,A_barra,v_barra,I_barra],axis=1)
        m.to_csv('datos_identificacion.txt',header=True,index=False)

 


     
class MatplotlibWidget(QMainWindow):
    
    def __init__(self):
        
        QMainWindow.__init__(self)
        loadUi("test.ui",self)
        self.Serial=Serial(0.01,self.lbSerial)
        self.setWindowTitle("OSCILOSCOPIO BALL AND BEAM")

        self.btnStart.clicked.connect(self.Start)
        self.btnDetener.clicked.connect(self.Detener)
        self.btnIdentificacion.clicked.connect(self.Identificacion)
        self.btnGuardar.clicked.connect(self.Guardar)
        self.addToolBar(NavigationToolbar(self.MplWidget.canvas, self))
        
        self.CEntrada.stateChanged.connect(self.checkbox)
        self.CPbola.stateChanged.connect(self.checkbox1)
        self.CVbola.stateChanged.connect(self.checkbox2)
        self.CIbola.stateChanged.connect(self.checkbox3)
        self.CScontrol.stateChanged.connect(self.checkbox4)
        self.CAbarra.stateChanged.connect(self.checkbox5)
        self.CVbarra.stateChanged.connect(self.checkbox6)
        self.CIbarra.stateChanged.connect(self.checkbox7)

        self.hilo= threading.Thread(target=self.update_figure, args=())
        self.mostrar=np.zeros((1,8),dtype=bool)
        self.hiloCreado=False

    def Identificacion(self):
        if self.Serial.open==False:
            if self.conectarSerial()==False:
                time.sleep(1)
                self.Serial.ser.flushInput()
                self.Serial.ser.write(('A\n').encode('cp1250'))
                dato=self.Serial.ser.readline()
                print(dato)
                if dato.decode('cp1250').replace('\n','')=='ok':
                    print('funciono')
                    datos=pd.read_csv('entrada.txt',header=0)
                    self.Serial.tiempo=datos['tiempo']
                    self.Serial.entrada=datos['entrada']
                    self.Serial.datosID=np.zeros((8,len(self.Serial.entrada)),dtype=float)
                    self.Serial.write(self.Serial.entrada[0])
                    self.Serial.ser.flushInput()
                    self.Serial.open=True
                    self.Serial.stop=False
                    self.Serial.cuenta=0
                    self.Serial.hilo.start()
            else:
                self.Serial.stop=True
        else:
            pass
       
        
        
       
        if self.hiloCreado ==False:
            self.hilo.start()
            self.hiloCreado= True;
    
    def conectarSerial(self):
        i=0
        cuenta=0
        self.lbSerial.setText('intentando conectar')
        self.lbSerial.setStyleSheet('color: red')
        while i==0 and cuenta<10:
            try:
                self.Serial.ser.open()
                i=1
            except:
                i=0
                cuenta=cuenta+1
            time.sleep(0.05)

        if cuenta<10 :
            self.lbSerial.setStyleSheet('color: green')
            self.lbSerial.setText('conectado')
            time.sleep(2)
            return False
        else:
            self.lbSerial.setText('no se pudo conectar')
            self.lbSerial.setStyleSheet('color: red')
            return True

    def Detener(self):
        self.Serial.stop=True
        self.graficar()
          #self.timer.stop()

    def Start(self):

        if self.Serial.open==False:
            if self.conectarSerial()==False:
                time.sleep(1)
                self.Serial.ser.write(('A\n').encode('cp1250'))
                #self.Serial.ser.flushInput()
                self.Serial.stop=False
                self.Serial.Identificacion=False
                self.Serial.open=True
                self.Serial.cuenta=0
                self.Serial.hilo.start()
                print('entro')
            else:
                self.Serial.stop=True
        else:
            self.Serial.stop=False
            self.Serial.Identificacion=False

        if self.hiloCreado ==False:
            self.hilo.start()
            self.hiloCreado= True;
           
    def graficar(self):

        self.MplWidget.canvas.axes.cla()
        self.MplWidget.canvas.axes1.cla()
        self.MplWidget.canvas.axes.set_xlim(0, 5)
        self.MplWidget.canvas.axes1.set_xlim(0, 5)
        self.MplWidget.canvas.axes.grid(True)
        self.MplWidget.canvas.axes1.grid(True)
        #self.MplWidget.canvas.axes1.set_ylim(-10, 10)
        cuentas=self.Serial.cuenta
        if(self.mostrar[0,0]==1):
            self.MplWidget.canvas.axes.plot(self.Serial.time[range(0,cuentas)],self.Serial.datosOsc[0,range(0,cuentas)],color='blue')
        if(self.mostrar[0,1]==1):
            self.MplWidget.canvas.axes.plot(self.Serial.time[range(0,cuentas)],self.Serial.datosOsc[1,range(0,cuentas)],color='red')
        if(self.mostrar[0,2]==1):
            self.MplWidget.canvas.axes.plot(self.Serial.time[range(0,cuentas)],self.Serial.datosOsc[2,range(0,cuentas)],color='green')
        if(self.mostrar[0,3]==1):
            self.MplWidget.canvas.axes.plot(self.Serial.time[range(0,cuentas)],self.Serial.datosOsc[3,range(0,cuentas)],color='blue')
        if(self.mostrar[0,4]==1):
            self.MplWidget.canvas.axes.plot(self.Serial.time[range(0,cuentas)],self.Serial.datosOsc[4,range(0,cuentas)],color='red')
        if(self.mostrar[0,5]==1):
            self.MplWidget.canvas.axes1.plot(self.Serial.time[range(0,cuentas)],self.Serial.datosOsc[5,range(0,cuentas)],color='green')
        if(self.mostrar[0,6]==1):
            self.MplWidget.canvas.axes1.plot(self.Serial.time[range(0,cuentas)],self.Serial.datosOsc[6,range(0,cuentas)],color='red')
        if(self.mostrar[0,7]==1):
            self.MplWidget.canvas.axes1.plot(self.Serial.time[range(0,cuentas)],self.Serial.datosOsc[7,range(0,cuentas)],color='green')
                
        self.MplWidget.canvas.draw()

    def update_figure(self):
        while 1:
            if self.Serial.stop== False:
                self.graficar()
                time.sleep(0.05)

    def Guardar(self):
        self.Serial.Guardar()

    def checkbox(self,state):
        if state == Qt.Checked:
            self.mostrar[0,0]=1
        else:
            self.mostrar[0,0]=0

    def checkbox1(self,state):
        if state == Qt.Checked:
            self.mostrar[0,1]=1
        else:
            self.mostrar[0,1]=0

    def checkbox2(self,state):
        if state == Qt.Checked:
            self.mostrar[0,2]=1
        else:
            self.mostrar[0,2]=0

    def checkbox3(self,state):
        if state == Qt.Checked:
            self.mostrar[0,3]=1
        else:
            self.mostrar[0,3]=0

    def checkbox4(self,state):
        if state == Qt.Checked:
            self.mostrar[0,4]=1
        else:
            self.mostrar[0,4]=0

    def checkbox5(self,state):
        if state == Qt.Checked:
            self.mostrar[0,5]=1
        else:
            self.mostrar[0,5]=0

    def checkbox6(self,state):
        if state == Qt.Checked:
            self.mostrar[0,6]=1
        else:
            self.mostrar[0,6]=0

    def checkbox7(self,state):
        if state == Qt.Checked:
            self.mostrar[0,7]=1
        else:
            self.mostrar[0,7]=0

if __name__ == '__main__':
    app = QApplication([])
    window = MatplotlibWidget()
    window.show()
    app.exec_()