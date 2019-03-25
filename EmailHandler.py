
# Email Handler
import os
import atexit
import smtplib
import logging

from email import encoders
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart


class EmailHandler:

    """ SMTP + MIMEMultipart Wrapper for Handling Emails Sending """

    def __init__(self, address='', password='', server='smtp.gmail.com:587', **kwargs):
        """
        :param address:     String  --   Email Address to use as sender (localhost can be used if enabled)
        :param password:    String  --   Email Address Password
        :param server:      String  --   Server Type
        :param kwargs:      Dict    --   Default Options modifiers

        Creates An EmailHandler Instance capable of handling Mail notifications through smtp connection

        options:
            inline:         Boolean     -- Include the attachment inline
            delete:         Boolean     -- Delete the attachment file after including it into the email
            newline:        Boolean     -- Include a Line Break after the attachment
            newlinenumber   Int         -- Number of new line to include after attachment
            textformat:     Str         -- [plain | html]
        """

        self.logger = logging.getLogger(__name__)
        self.default_options = {
            'inline': False,
            'delete': False,
            'newline': True,
            'newlinenumber': 1,
            'textformat': 'plain'
        }

        self.attachments = []
        self.address = address
        self.msg = MIMEMultipart()

        self.default_options.update(kwargs)  # Changing Default Options

        try:
            # Server Connection
            self.server = smtplib.SMTP(server, kwargs.get('timeout', 600))
            atexit.register(lambda: self.server.quit())  # Closing SMTP Connection at script exit

            if self.server != 'localhost':
                self.server.ehlo()  # Start Connection
                self.server.starttls()  # Secure Connection
                self.server.login(address, password)

        except smtplib.SMTPAuthenticationError as e:
            self.logger.critical('Authentication Error: {}'.format(e))
            raise

        except Exception as e:
            self.logger.error('Unknown Error: {}'.format(e))
            raise

    def __call__(self, text, **kwargs):
        """
        :param text:    Str    -- Text to include into the email
        :param kwargs:  Dict   -- Options

        Wrapper of attachMessage Method
        """
        self.attachMessage(text, **kwargs)

    def __add__(self, attachment):
        """
        :param attachment: List or Dict Attachments

        Wrapper of addAttachment Method
        """
        self.addAttachments(attachment)

    def __updateOptions__(self, option_dict):
        """ Factory Method called when Default Options dict needs update """
        out = self.default_options.copy()
        out.update(option_dict)
        return out

    def __newLine__(self, n=2):
        return MIMEText('\n'*n)

    def __prepareText__(self, dict_input):

        text = dict_input.get('input')
        options = dict_input.get('options', {})
        options = self.__updateOptions__(options)

        self.attachments.append(MIMEText(text, options.get('textformat', 'plain')))

        # Options
        if options.get('newline'):
            self.attachments.append(self.__newLine__(options.get('newlinenumber')))

    def __prepareCsv__(self, dict_input):

        path = dict_input.get('input')
        options = dict_input.get('options', {})
        options = self.__updateOptions__(options)

        part = MIMEBase('application', 'octet-stream')

        with open(path, 'rb') as f:
            part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', 'attachment; filename={}'.format(path.split('/')[-1]))
            self.attachments.append(part)

        if options.get('delete'):
            os.remove(path)

        if options.get('newline'):
            self.attachments.append(self.__newLine__(options.get('newlinenumber')))

    def __prepareDataFrame(self, dict_input):

        _df = dict_input.get('input')
        options = dict_input.get('options', {})
        options = self.__updateOptions__(options)

        self.attachments.append(MIMEText(_df.to_html(), 'html'))

        if options.get('newline'):
            self.attachments.append(self.__newLine__(options.get('newlinenumber')))

    def __prepareImage__(self, dict_input):

        path = dict_input.get('input')
        name = path.split('/')[-1][:-4]
        extension = path.split('/')[-1][-3:]
        options = dict_input.get('options', {})
        options = self.__updateOptions__(options)

        # Add HTML Tag for image
        self.attachments.append(MIMEText('<img src="cid:{}">'.format(name), 'html'))

        try:
            with open(path, 'rb') as file:
                file = MIMEImage(file.read(), extension)
                file.add_header('Content-Disposition', 'attachment', filename=name)

        except FileNotFoundError:
            self.logger.error('Image on path {} not found'.format(path))
            return

        # Adding Options
        if options.get('inline'):
            file.add_header('Content-ID', '<{}>'.format(name))

            # Only Apply new Line if attachment is In-Line
            if options.get('newline'):
                self.attachments.append(self.__newLine__(options.get('newlinenumber')))

        if options.get('delete'):
            os.remove(path)

        self.attachments.append(file)

    def attachMessage(self, text, **kwargs):
        """ Wrapper For adding Message"""
        input_dict = {'type': 'text', 'input': text}
        input_dict.update(kwargs)
        self.addAttachments(input_dict)

    def addAttachments(self, attachments):
        """
        :param attachments: Dict() | List(Dict))
            Dict = {
            'type': object_type,
            'input': object_input,
            'options: options_dict
            }

        Available attachments and object type:
            text : String
            csv: path to saved CSV
            dataframe: pandas DataFrame
            image: path to saved png image
        """

        if not isinstance(attachments, list): attachments = [attachments]

        for attachment in attachments:

            success = {
                'csv': self.__prepareCsv__,
                'text': self.__prepareText__,
                'image': self.__prepareImage__,
                'dataframe': self.__prepareDataFrame
            }.get(attachment.get('type'), False)

            if success:
                success(attachment)
                continue

            self.logger.error(
                '{} has not yet been implemented, please ask Owner for help'.format(attachment.get('type')))

    def sendMessage(self, to, subject='', message='', signature=''):
        """
        :param to:          List(String) | String -- Receivers Email addresses
        :param subject:     String                -- Email Subject
        :param message:     String                -- Body Message of email
        :param signature:   String                -- Signature of email

        Send the Email and reinitialize the msg object
        """

        if not isinstance(to, list): to = [to]

        try:

            self.msg['To'] = ', '.join(to)
            self.msg['Subject'] = subject
            self.msg['From'] = self.address
            self.msg.attach(MIMEText(message + '\n', 'plain'))  # Attach Body

            [self.msg.attach(_) for _ in self.attachments]  # Attach Attachments

            self.msg.attach(MIMEText(signature, 'plain'))  # Attach Signature

            try:
                self.server.send_message(self.msg)
                self.logger.info('Message Successfully sent to {}'.format(to))
            except Exception as e:
                self.logger.critical('Sending Message Failed with error: {}'.format(e))

            # Reinitialize
            self.msg = MIMEMultipart()
            self.attachments = []

        except Exception as e:
            self.logger.critical('SendMessage Failed with error message: {}'.format(e))

            
if __name__ == '__main__':
    # Tests
    import argparse
    import pandas as pd
    import matplotlib.pylab as plt

    logging.basicConfig()

    parser = argparse.ArgumentParser()
    parser.add_argument('-e', '--email', required=True)
    parser.add_argument('-p', '--password', required=True)
    args = parser.parse_args()

    df = pd.DataFrame({'A': [1,2,3], 'B': [2,3,4]})
    df = pd.DataFrame({'A': [1,2,3], 'B': [2,3,4]})
    # plt.plot([1,2,3], [3,4,5])
    # plt.savefig('test.png')

    mail = EmailHandler(args.email, args.password)

    mail + {
        'type': 'text',
        'input': 'I like turtles'
    }

    mail + {'type': 'dataframe', 'input': df}

    mail + {
        'type': 'image',
        'input': '/Users/mathieulallier/QuanticMind/data-science/PyLib/QmDB/QmDB/test.png',
        'options': {'inline': True}
    }

    mail.attachMessage('salut comment ca va')

    mail.sendMessage(args.email, 'test2', 'message', 'signature')
