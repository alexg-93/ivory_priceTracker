import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from bidi.algorithm import get_display

def send_email(product_title,product_price,URL):
    gmailUser = 'gordienko1993@gmail.com'
    gmailPassword = 'tkfxxux1993'
    recipient = 'alexgordienko1993@gmail.com'
    subject = f"Price Alert for {get_display(product_title)} "
    message = f"Hey!\n Product : {get_display(product_title)} is now on SALE!\n Price : ₪{product_price}\nLink : {URL} Hurry up don't miss that!"
    
    msg = MIMEMultipart()
    msg['From'] = f'{gmailUser}'
    msg['To'] = recipient
    msg['Subject'] = subject
    msg.attach(MIMEText(message))

    try:
        mailServer = smtplib.SMTP('smtp.gmail.com', 587)
        mailServer.ehlo()
        mailServer.starttls()
        mailServer.ehlo()
        mailServer.login(gmailUser, gmailPassword)
        mailServer.sendmail(gmailUser, recipient, msg.as_string())
        mailServer.close()
        print ('Email sent!')
    except:
        print ('Something went wrong...')