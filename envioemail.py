from email.message import EmailMessage
import smtplib


def enviar_email(email_destino, codigo):
    remitente = "chaverras@uninorte.edu.co"
    destinatario = email_destino
    mensaje = "Correo de activación"

    email = EmailMessage()
    email['From'] = remitente
    email['To'] = destinatario
    email['Subject'] = 'Confirmación de Correo'
    email.set_content("Bienvenido, Para Confirmar su cuenta Ingrese el Siguiente Codigo. \n codigo de verificación: " +
                      codigo+" \n Recuerde ingresar este codigo para poder validar su cuenta")
    # email.set_content(mensaje)
    smtp = smtplib.SMTP("smtp-mail.outlook.com", port=587)
    smtp.starttls()
    smtp.login(remitente, "jus3buch4")
    smtp.sendmail(remitente, destinatario, email.as_string())
    smtp.quit()


def recuperar_email(email_destino):
    remitente = "chaverras@uninorte.edu.co"
    destinatario = email_destino
    mensaje="<hr>"
    mensaje = "<h2>Recuperación de Cuenta</h2>"
    mensaje = mensaje + "<a href='http://localhost:5000/restablecer/" + email_destino + \
        "'>Ingrese Aquí para restablecer su Contraseña</a>"
    mensaje=mensaje+ "<hr>"
    email = EmailMessage()
    email['From'] = remitente
    email['To'] = destinatario
    email['Subject'] = 'recuperar Contraseña'
    email.set_content(mensaje, subtype="html")
    smtp = smtplib.SMTP("smtp-mail.outlook.com", port=587)
    smtp.starttls()
    smtp.login(remitente, "jus3buch4")
    smtp.sendmail(remitente, destinatario, email.as_string())
    smtp.quit()
