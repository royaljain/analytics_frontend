import sendgrid
import os
from sendgrid.helpers.mail import *


SENDGRID_API_KEY='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'
#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'

sg = sendgrid.SendGridAPIClient(apikey=SENDGRID_API_KEY)
from_email = Email("royal@astuteinnovations.com")
to_email = Email("royaljain0203@gmail.com")
subject = "Useful tips for you"
content = Content("text/plain", "Hi, This is a lot of text. All is well in this email and it is veyr good. You can think about it further and let me know what is the status of the email and of your health. All is Great. \n Love, \n Royal ")
mail = Mail(from_email, subject, to_email, content)
response = sg.client.mail.send.post(request_body=mail.get())


print(response.status_code)
print(response.body)
print(response.headers)


