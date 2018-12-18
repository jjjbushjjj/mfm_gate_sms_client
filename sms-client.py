#!/usr/bin/python

import sys
import os
import argparse
import logging
import logging.handlers
from suds.client import Client
from uuid import uuid4


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(formatter)
logger.addHandler(handler)


def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    logger.critical("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))

sys.excepthook = handle_exception


def main():

    # Local working WSDL because requested from server has wrong soap address location
    url = 'file:///'+ os.getcwd() + '/OutMessageService.wsdl.prod'
    wsdl_local = url

    parser = argparse.ArgumentParser(description='Simple soap client for sending sms over MFM Sms gateway')
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-v", "--verbose", action="store_true",
            help="Verbose output")
    group.add_argument("-q", "--quiet", action="store_true", default=True,
            help="Suppres output. Default")

    parser.add_argument("phone",
            help="Sender phone number", type=str)
    parser.add_argument("message",
            help="Message to send", type=str)

    parser.add_argument("-u", "--user", help="Smsgate user login",
            action="store", type=str, default='ws')
    parser.add_argument("-p", "--password", help="Smsgate user password",
                        action="store", type=str, default='ws')
    parser.add_argument("-s", "--sender",
            help="Sender name. Displayed in sms header. Must be set according provider rules. Default: Sovcombank",
                        action="store", default='Sovcombank')
    parser.add_argument("-t", "--type",
            help="Sender type outMessageTypeId. Sender type needed for sms gate",
                        action="store", default='sys_monitoring')
    parser.add_argument("-w", "--wsdl",
            help="Sms gate wsdl url",
            action="store_true", default=wsdl_local)


    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.ERROR)

    logger.debug("Connecting with those params: Wsdl url: %s, "
                  "Sender name: %s, Sender type: %s, User: %s, "
                  "Pass %s, Sending message to: %s With content: %s",
    args.wsdl, args.sender, args.type, args.user, args.password, args.phone, args.message)

    # Sms client implemetation
    client = Client(args.wsdl)
    logger.debug(client)

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


    
if __name__ == '__main__':
    main()
