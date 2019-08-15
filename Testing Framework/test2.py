import smtplib
import email.utils
from email.mime.text import MIMEText

# Create the message
msg = MIMEText('This is the body of the message.')
msg['To'] = email.utils.formataddr(('Recipient', 'neilbalch@gmail.com'))
msg['From'] = email.utils.formataddr(('Author', 'author@example.com'))
msg['Subject'] = 'Simple test message'

server = smtplib.SMTP('localhost', 1024)
server.set_debuglevel(True) # show communication with the server
try:
    server.connect()
    server.sendmail('example@example.com', ['neilbalch@gmail.com'], msg.as_string())
finally:
    server.quit()
