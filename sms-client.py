#!/usr/bin/env python

import sys
import os
import argparse
import logging
import logging.handlers
from uuid import uuid4
from suds.client import Client

reload(sys)
sys.setdefaultencoding("utf-8")


LOG_FILENAME = '/tmp/sms.log'

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')


def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    logger.critical("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))

sys.excepthook = handle_exception


# subcommand functions

def send(client, auth, args):
    """ Try to send message over sms gateway """

    logger.debug("Connecting with those params: Wsdl url: %s, "
                  "Sender name: %s, Sender type: %s, User: %s, "
                  "Pass %s, Sending message to: %s With content: %s",
    args.wsdl, args.sender, args.type, args.user, args.password, args.phone, args.message)

    # Write messageid to logfile allways level info
    messageId = uuid4()
    logger.info("Sending message with ID: %s To: %s", messageId, args.phone)
    logger.debug("Client: %s", client)

    auth = client.factory.create('ns0:Auth')
    auth.login = args.user
    auth.password = args.password


    # Init message fields
    # Gen messageId
    messageId = uuid4()

    OutMessageTemplate = client.factory.create('ns0:OutMessageTemplate')
    OutMessageTemplate.text = args.message 


    # Format New Message
    consumeOutMessageArg = client.factory.create('ns0:ConsumeOutMessageArg')
    consumeOutMessageArg.messageId = messageId
    consumeOutMessageArg.outMessageTypeId = args.type
    consumeOutMessageArg.subject = args.sender
    consumeOutMessageArg.address = args.phone
    consumeOutMessageArg.outMessageTemplate = OutMessageTemplate

    # Send it
    send_status = client.service.consumeOutMessage(auth=auth, consumeOutMessageArg=consumeOutMessageArg)
    logger.debug(send_status)


def get_status(client, auth, args):
    """ Get status of previously sended message """

    logger.debug("Trying to get status for message: %s", args.messageId)
    getOutMessageDlvStatusArg = client.factory.create('ns0:GetOutMessageDlvStatusArg')
    getOutMessageDlvStatusArg.messageId = args.messageId

    message_status = client.service.getOutMessageDlvStatus(auth=auth, getOutMessageDlvStatusArg=getOutMessageDlvStatusArg)
    message_status = dict(message_status)
    logger.info("Delivery responseCode: %s with status: %s", \
                message_status['responseCode'], \
                message_status['getOutMessageDlvStatusResult'][0]['outMessageDlvStatus']['dlvStatus'])



def main():

    parser = argparse.ArgumentParser(
            description='Simple soap client for sending sms over MFM Sms gateway. \
                    Also it cat get status for previously sended sms')
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-v", "--verbose", action="store_true",
            help="Verbose output")
    group.add_argument("-q", "--quiet", action="store_true", default=True,
            help="Suppres output. Default")
    parser.add_argument("-u", "--user", help="Smsgate user login",
            action="store", type=str)
    parser.add_argument("-p", "--password", help="Smsgate user password",
                        action="store", type=str)
    parser.add_argument("-w", "--wsdl",
            help="Sms gate wsdl url or file.",
            action="store", default='http://sms-gate/sendmessage.wsdl')
    
    subparsers = parser.add_subparsers(help='sub-command help')


    get_parser = subparsers.add_parser('get_status', help='Returns delivery status for sms based on messageId')
    get_parser.add_argument("messageId", help="Message ID to look for")
    get_parser.set_defaults(func=get_status)


    send_parser = subparsers.add_parser('send', help='Send message to sms gateway')
    send_parser.add_argument("phone",
            help="Sender phone number", type=str)
    send_parser.add_argument("message",
            help="Message to send", type=str)
    send_parser.add_argument("-s", "--sender",
            help="Sender name. Displayed in sms header. Must be set according provider rules. Default: Sender",
                        action="store", default='Sender')
    send_parser.add_argument("-t", "--type",
            help="Sender type. Sender type needed for sms gate",
                        action="store", default='senderType')
    send_parser.set_defaults(func=send)


    args = parser.parse_args()


    if args.verbose:
        # Logging to console if verbose flag is present
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(formatter)
        logger.setLevel(logging.DEBUG)
    else:
        # Othewise logs to file
        handler = logging.handlers.RotatingFileHandler(
                      LOG_FILENAME, maxBytes=104857600, backupCount=2)
        handler.setFormatter(formatter)
        logger.setLevel(logging.INFO)
    
    logger.addHandler(handler)

    #Constuct wsdl url
    if args.wsdl.split(':')[0] in ['https', 'http']:
        # use as it is
        pass
    else:
        # local file
        args.wsdl = 'file://' + os.path.abspath(args.wsdl)

    # Init new soap client
    client = Client(args.wsdl)

    # Add auth info
    auth = client.factory.create('ns0:Auth')
    auth.login = args.user
    auth.password = args.password

    # run appropriate function
    args.func(client, auth, args)

    
    
if __name__ == '__main__':
    main()

