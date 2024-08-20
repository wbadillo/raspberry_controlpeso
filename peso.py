#!/usr/bin/env python

## 2024-08-20 

from pymodbus.server import StartSerialServer
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext, ModbusSequentialDataBlock
from pymodbus.transaction import ModbusRtuFramer
from pymodbus.device import ModbusDeviceIdentification
from threading import Thread
import logging
import time
import RPi.GPIO as GPIO
import serial
import os
import sys
import csv
from datetime import datetime

import traceback

#getcontext().prec = 1

os.system("sudo fuser -k /dev/ttySC0")
timer = time.time()

identity = ModbusDeviceIdentification()
identity.VendorName = 'Pymodbus'
identity.ProductCode = 'PM'
identity.VendorUrl = 'http://github.com/riptideio/pymodbus/'
identity.ProductName = 'Pymodbus Server'
identity.ModelName = 'Pymodbus Server'
identity.MajorMinorRevision = '1.0'

led_start = 5
p_compuerta = 17
p_alarma = 27

serial_port_1 = '/dev/ttySC0'
serial_port_2 = '/dev/ttySC1'
baudrate = 9600
peso_f = 0

fecha_hora = datetime.now().strftime('%Y%m%d_%H%M%S')

# Ruta de memoria USB para guardar copia de datos
ruta_usb = f'/media/esisco/USB/{fecha_hora}_datos_pesaje.csv'

datos = []

# Configuracion de GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(p_compuerta,GPIO.OUT) # P0 Compuerta
GPIO.setup(p_alarma,GPIO.OUT) # P2 Alarma
GPIO.setup(led_start,GPIO.OUT)  # P21 Led start

# Indicador de Inicio
GPIO.output(led_start,True)
time.sleep(1)
GPIO.output(led_start,False)

# Configurar el logging para ver los detalles de la comunicacion
logging.basicConfig()
log = logging.getLogger()
#log.setLevel(logging.DEBUG)

# Configuracion del contexto de los datos del esclavo
store = ModbusSlaveContext(
    hr=ModbusSequentialDataBlock(0, [0]*10),  # Holding Registers (HR)
)
#context = ModbusServerContext(slaves=store, single=True)
context = ModbusServerContext(slaves={3: store}, single=False)

# Iniciar archivo CSV oara guarda datos 
def start_data_usb():
    try:
        datos.append(['FECHA', 'HORA','PESADA' ,'LOTE', 'PESO'])
        with open(ruta_usb, mode='w', newline='') as file_csv:
            escritor_csv = csv.writer(file_csv)
            escritor_csv.writerows(datos)
    except Exception as e:
        print(f"Error: {str(e)}", flush=True)
        traceback.print_exc()

# Funcion para enviar datos por el puerto serial
def send_data_serial(data):
    try:
        with serial.Serial(serial_port_2, baudrate, timeout=1) as ser:
            ser.write(f"{data}\n".encode())
        print(f"Datos enviados: {data}", flush=True)
    except serial.SerialException as e:
        print(f"Error al enviar datos por el puerto serial: {e}", flush=True)

# Funcion para guardar datos en memoria USB
def save_data_usb(lote, peso, conteo):
    peso_f = peso/10;
    try:
        fecha = datetime.now().strftime('%Y-%m-%d')
        hora = datetime.now().strftime('%H:%M:%S')
        datos.append([fecha, hora, conteo, lote, peso_f])
        with open(ruta_usb, mode='w', newline='') as file_csv:
            escritor_csv = csv.writer(file_csv)
            escritor_csv.writerows(datos)
    except Exception as e:
        print(f"Error: {str(e)}", flush=True)
        traceback.print_exc()
        
# Actualizar estado de salidas digitales
def update_gpio_status(data):
    compuerta = GPIO.input(p_compuerta)
    alarma = GPIO.input(p_alarma)

    GPIO.output(p_compuerta, data in [1, 3])
    GPIO.output(p_alarma, data in [2, 3])
    
    # Imprime el estado actual de los pines
    print(f"Compuerta: {GPIO.input(p_compuerta)} -- Alarma: {GPIO.input(p_alarma)} ", flush=True)
   
# Funcion para mostrar datos recibidos
def display_received_data():
    old_data = [0] * 4  # Almacena los datos anteriores para detectar cambios
    while True:
        time.sleep(0.3)  # Esperar un x segs antes de la siguiente verificacion
        
        # Leer los registros actuales del esclavo con ID 3 contex[3] 
        current_data = context[3].getValues(3, 0, count=5)
        
        if len(current_data) < 5:
            print("Advertencia: Numero insuficiente de datos recibidos.", flush=True)
            continue  # Saltar a la siguiente iteracion del bucle
        
        if current_data != old_data:
           
            print("---------------------------------------------", flush=True)
            #print("Datos actualizados recibidos:", flush=True)
            print(f"{current_data}", flush=True)
            old_data = current_data  # Actualizar los datos anteriores    

            save = current_data[1]
            peso = current_data[2]
            lote = current_data[3]
            conteo = current_data[4]
            salidas = current_data[0]
            
            if save == 1: 
                #if time.time() > timer:
                send_data_serial(f"{peso}, {lote}!")
                save_data_usb(lote, peso, conteo)
                #timer = time.time() + 5
                 
            update_gpio_status(salidas)
            
            print(f"Peso: {current_data[2]} -- Lote: {current_data[3]} -- Envio:{current_data[1]}", flush=True)
            print("---------------------------------------------\n", flush=True)
            
# Definicion del servidor esclavo Modbus RTU
def run_server():
    # Conectar al puerto serial antes de iniciar el servidor para limpiar el buffer
    with serial.Serial(port=serial_port_1, baudrate=baudrate, timeout=1) as ser:
        ser.read_all()  # Leer y descartar todos los datos en el buffer 
    
    StartSerialServer(
        context=context,
        framer=ModbusRtuFramer,
        port=serial_port_1,  
        baudrate=baudrate,
        stopbits=1,
        bytesize=8,
        parity='N',
        timeout=1
    )

    GPIO.output(0,True) 
    time.sleep(1)        
    GPIO.output(0,False)  
    

if __name__ == "__main__":
    # Ejecutar el servidor en un hilo separado
    try:
        server_thread = Thread(target=run_server)
        server_thread.daemon = True
        server_thread.start()

        print("Started..\n", flush=True)
        start_data_usb()

        display_received_data()

    except KeyboardInterrupt:
        # exits when you press CTRL+C  
        print ("Bye: programa interrumpido... [CTRL+C]\n")
    except Exception as e:
        print(f"Error: {str(e)}", flush=True)
        traceback.print_exc()  
      
    finally:  
        GPIO.cleanup() # this ensures a clean exit  
