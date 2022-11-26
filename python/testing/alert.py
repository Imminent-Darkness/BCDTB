# -*- coding: utf-8 -*-
"""
Created on Fri Oct 14 16:01:43 2022

@author: Dell
"""

# Import smtplib for the actual sending function
import smtplib
# Import the email modules we'll need
from email.message import EmailMessage
# Import the email modules we'll need
from email.parser import BytesParser, Parser
from email.policy import default

class alert:

    def __init__(self, textfile, symbol):

        #  Or for parsing headers in a string (this is an uncommon operation), use:
        headers = Parser(policy=default).parsestr(
                'From: Foo Bar <user@example.com>\n'
                'To: <someone_else@example.com>\n'
                'Subject: Test message\n'
                '\n'
                'Body would go here\n')
    
    # me == the sender's email address
    # you == the recipient's email address
    msg['Subject'] = 'The contents of %s' % textfile
    msg['From'] = me
    msg['To'] = you
    
    # Send the message via our own SMTP server, but don't include the
    # envelope header.
    s = smtplib.SMTP('localhost')
    s.sendmail(me, [you], msg.as_string())
    s.quit()