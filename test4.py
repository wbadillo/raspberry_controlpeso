from pymodbus.server import StartSerialServer
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext, ModbusSequentialDataBlock
from pymodbus.transaction import ModbusRtuFramer
from pymodbus.device import ModbusDeviceIdentification
from threading import Thread
import logging
import time
import RPi.GPIO as GPIO
import serial

identity = ModbusDeviceIdentification()
identity.VendorName = 'Pymodbus'
identity.ProductCode = 'PM'
identity.VendorUrl = 'http://github.com/riptideio/pymodbus/'
identity.ProductName = 'Pymodbus Server'
identity.ModelName = 'Pymodbus Server'
identity.MajorMinorRevision = '1.0'


GPIO.setmode(GPIO.BCM)
GPIO.setup(17,GPIO.OUT) # P0 Compuerta
GPIO.setup(27,GPIO.OUT) # P2 Alarma

GPIO.output(17,True)
GPIO.output(27,True)
time.sleep(2)
GPIO.output(17,False)
GPIO.output(27,False)
            
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

serial_port2 = '/dev/ttySC1'
baudrate = 9600

# Funcion para enviar datos por el puerto serial
def send_data_serial(data):
    try:
        with serial.Serial(serial_port2, baudrate, timeout=1) as ser:
            ser.write(f"{data}\n".encode())
        print(f"Datos enviados por el puerto serial: {data}")
    except serial.SerialException as e:
        print(f"Error al enviar datos por el puerto serial: {e}")

# Actualizar estado de salidas digitales 
def update_gpio_status(data):
    if data == 1:
        GPIO.output(17, True)
        GPIO.output(27, False)
    if data == 2:
        GPIO.output(17, False)
        GPIO.output(27, True)
    if data == 3:
        GPIO.output(17, True)
        GPIO.output(27, True)
    if data == 0:
        GPIO.output(17, False)
        GPIO.output(27, False)
    
    compuerta = GPIO.input(17)
    alarma = GPIO.input(27)  
    
    print(f"Compuerta: {compuerta}")
    print(f"Alarma: {alarma}")

# Funcion para mostrar datos recibidos
def display_received_data():
    old_data = [0] * 5  # Almacena los datos anteriores para detectar cambios
    while True:
        time.sleep(1)  # Esperar un segundo antes de la siguiente verificacion
        
        # Leer los registros actuales del esclavo con ID 3 contex[3] 
        current_data = context[3].getValues(3, 0, count=5)
        #current_data = context[0].getValues(3, 0, count=100)
        
        if current_data != old_data:
            print(f"Datos actualizados recibidos: {current_data}")
            
            old_data = current_data  # Actualizar los datos anteriores    

            save = current_data[1]
            peso = current_data[2]
            lote = current_data[3]
            salidas = current_data[0]
            
            if save == 1:
                 send_data_serial(f"{peso}, {lote}!")
                 
            update_gpio_status(salidas)
            
            print(f"Flag Envio: {current_data[1]}")
            print(f"Peso: {current_data[2]}")
            print(f"Lote: {current_data[3]}")
            
# Definicion del servidor esclavo Modbus RTU
def run_server():
    StartSerialServer(
        context=context,
        framer=ModbusRtuFramer,
        port='/dev/ttySC0',  # puerto serail 1
        baudrate=9600,
        stopbits=1,
        bytesize=8,
        parity='N',
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
        
        print("Started..")
        
        display_received_data()
        update_gpio_status()
        
    except KeyboardInterrupt:  
        # here you put any code you want to run before the program   
        # exits when you press CTRL+C  
        print ("Bye: programa interrumpido... [CTRL+C]\n")
        
    except:  
        # this catches ALL other exceptions including errors.  
        # You won't get any error messages for debugging  
        # so only use it once your code is working  
        print ("Other error or exception occurred!")
      
    finally:  
        GPIO.cleanup() # this ensures a clean exit  
