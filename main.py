import argparse
import requests
import email, smtplib, ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# PARAMETERS
parser = argparse.ArgumentParser()
parser.add_argument('-l',  '--link',     required=True)
parser.add_argument('-t',  '--title',    required=True)
parser.add_argument('-g',  '--gmail',    required=True)
parser.add_argument('-p',  '--password', required=True)
parser.add_argument('-k',  '--kindle',   required=True)
parser.add_argument('-c',  '--convert',  action='store_true')
args = parser.parse_args()

# PARAMETER SETTERS
subject = "convert" if args.convert else "null"
body = "convert"
sender_email = args.gmail
receiver_email = args.kindle

# Create a multipart message and set headers
message = MIMEMultipart()
message["From"] = sender_email
message["To"] = receiver_email
message["Subject"] = subject
message["Bcc"] = receiver_email  # Recommended for mass emails

# Add body to email
message.attach(MIMEText(body, "plain"))

# DOWNLOAD PDF
pdf_filename = f'{args.title}.pdf'
CHUNK_SIZE = 2000
r = requests.get(args.link, stream=True)
with open(pdf_filename, 'wb') as f:
    for chunk in r.iter_content(CHUNK_SIZE):
        f.write(chunk)

# Open PDF file in binary mode
with open(pdf_filename, "rb") as attachment:
    # Add file as application/octet-stream
    # Email client can usually download this automatically as attachment
    part = MIMEBase("application", "octet-stream")
    part.set_payload(attachment.read())

# Encode file in ASCII characters to send by email    
encoders.encode_base64(part)

# Add header as key/value pair to attachment part
part.add_header(
    "Content-Disposition",
    f"attachment; filename= {pdf_filename}",
)

# Add attachment to message and convert message to string
message.attach(part)
text = message.as_string()

# Log in to server using secure context and send email
context = ssl.create_default_context()
with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
    server.login(sender_email, args.password)
    server.sendmail(sender_email, receiver_email, text)