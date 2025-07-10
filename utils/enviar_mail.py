import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def enviar_alerta(destinatario, asunto, cuerpo):
    # Configurar cuenta
    remitente = "federi.al2001@gmail.com"
    contraseña = "iukn jaja eybj wuzx" 
    #OJO ES RE INSEGURO DEJAR ESTO ACA, peligroso, no subir 

    # Crear mensaje
    mensaje = MIMEMultipart()
    mensaje['From'] = remitente
    mensaje['To'] = destinatario
    mensaje['Subject'] = asunto

    mensaje.attach(MIMEText(cuerpo, 'plain'))

    try:
        servidor = smtplib.SMTP('smtp.gmail.com', 587)
        servidor.starttls()
        servidor.login(remitente, contraseña)
        servidor.sendmail(remitente, destinatario, mensaje.as_string())
        servidor.quit()
        print("Correo enviado al administrador.")
    except Exception as e:
        print(f"Error al enviar correo: {e}")

