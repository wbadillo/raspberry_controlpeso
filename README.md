# -*- coding: utf-8 -*-

#---------------------------------------------
####Crear y activar un entorno virtual 
#---------------------------------------------
mkdir -p  ~/Botero
python3 -m venv ~/Botero
source ~/Botero/bin/activate

sudo systemctl daemon-reload
sudo systemctl start test1.service
sudo systemctl enable test1.service
sudo systemctl status test1.service

sudo journalctl -u test1.service -f

#---------------------------------------------
### Instalar las librerias necesarias 
#---------------------------------------------

pip install wheel
pip install pymudbus
pip install pyserial
pip install RPi.GPO


#---------------------------------------------
###Sedactivar y desbloquear el puerto ttySC0 (Serial1) 

sudo fuser -k /dev/ttySC0


##---------------------------------------------
#Listar scripts ejecutandose
ps -ef | grep main

#Parar script 
kill <pid>


##---------------------------------------------
#prgramacion de tareas CRON

Ruta absoluta
Otro error muy extendido al utilizar crons es ignorar la ruta del archivo.
Debe utilizar la ruta completa para que funcione correctamente.

Este cron no funcionarÃ¡, incluso en el crontab raÃ­z :

@reboot service ssh start
Si no se especifica la ruta absoluta, cron no sabrÃ¡ dÃ³nde se encuentra el archivo de servicio.
AsÃ­ que tienes que escribir /usr/sbin/service para que este cron funcione.

Presta tambiÃ©n atenciÃ³n al contenido de sus scripts.
Por ejemplo, si tienes un script PHP que incluye otro archivo (ej: include Â«file.phpÂ»), y aÃ±ades este script al crontab, no funcionarÃ¡.
TendrÃ¡s que aÃ±adir la ruta absoluta en el include de la funciÃ³n o hacer algo como esto:

@reboot cd /var/www/html; /usr/bin/php test.php
De esta forma, la inclusiÃ³n se harÃ¡ en /var/www/html y el script PHP encontrarÃ¡ el archivo Â«file.phpÂ».
 
Syslog :
Syslog es otra valiosa ayuda para comprobar quÃ© ha pasado con tus crons.
Es un archivo de registro ubicado en /var/log/syslog.

Puedes leer los Ãºltimos mensajes sobre crons con este comando :

tail -f /var/log/syslog | grep CRON
Y te mostrarÃ¡ los Ãºltimos errores, con actualizaciÃ³n en tiempo real si se inicia un nuevo cron.



##---------------------------------------------
Opciones de top y htop
Ambas herramientas ofrecen varias opciones y configuraciones que pueden ayudarte a personalizar la vista de los procesos.

top:

Filtrar por usuario: Usa u seguido del nombre del usuario.
Cambiar la columna de orden: Usa o seguido del nombre de la columna.
htop:

Buscar procesos: Presiona F3 y escribe el nombre del proceso.
Matar procesos: Presiona F9 y selecciona el proceso para terminarlo.
Cambiar la visualizaciÃ³n: Usa F2 para acceder a la configuraciÃ³n y personalizar la vista.
