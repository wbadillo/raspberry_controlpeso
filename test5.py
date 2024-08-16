
import logging
import time
import RPi.GPIO as GPIO
import serial


GPIO.setmode(GPIO.BCM)
GPIO.setup(17,GPIO.OUT) # P0 Compuerta
GPIO.setup(27,GPIO.OUT) # P2 Alarma

GPIO.output(17,True)
GPIO.output(27,True)
time.sleep(2)
GPIO.output(17,False)
GPIO.output(27,False)
            
peso = 0
lote = 0

# Configurar el logging para ver los detalles de la comunicacion
logging.basicConfig()
log = logging.getLogger()
#log.setLevel(logging.DEBUG)

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


if __name__ == "__main__":
    # Ejecutar el servidor en un hilo separado
    try:
        print("Started..")
        while True:
        
            peso = peso+1
            lote = lote+2
           
            send_data_serial(f"{peso}, {lote}!")
            time.sleep(2)

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

