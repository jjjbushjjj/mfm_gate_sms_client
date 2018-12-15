import sys
import argparse
import logging
import logging.handlers
from uuid import uuid4

LOG_FILENAME = '/tmp/sms.log'

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
# 100M per logfile rotate every 2
handler_logfile = logging.handlers.RotatingFileHandler(
              LOG_FILENAME, maxBytes=104857600, backupCount=2)
handler_logfile.setFormatter(formatter)
handler_logfile.setLevel(logging.INFO)

logger.addHandler(handler_logfile)

def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    logger.critical("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))

sys.excepthook = handle_exception


# subcommand functions

# Send message
def send(args):
    logger.debug("Connecting with those params: Wsdl url: %s, "
                  "Sender name: %s, Sender type: %s, User: %s, "
                  "Pass %s, Sending message to: %s With content: %s",
    args.wsdl, args.sender, args.type, args.user, args.password, args.phone, args.message)

    # Write messageid to logfile allways level info
    messageId = uuid4()
    logger.info("Sending message with ID: %s To: %s", messageId, args.phone)

    # Sender implementation here

# Get message status
def get_status(args):
    logger.debug("Trying to get status for message: %s", args.messageId)

    # Getter implementation here


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
            help="Sms gate wsdl url",
            action="store_true", default='http://sms-gate/sendmessage.wsdl')
    
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
            help="Sender name. Displayed in sms header. Must be set according provider rules. Default: Sovcombank",
                        action="store", default='Sovcombank')
    send_parser.add_argument("-t", "--type",
            help="Sender type. Sender type needed for sms gate",
                        action="store", default='some type')
    send_parser.set_defaults(func=send)


    args = parser.parse_args()

    if args.verbose:
        # Add another logging handler to get output to console
        handler_stream = logging.StreamHandler(sys.stdout)
        handler_stream.setFormatter(formatter)
        handler_stream.setLevel(logging.DEBUG)
        logger.addHandler(handler_stream)
        logger.setLevel(logging.DEBUG)
    else:
        # Just logs this level of messages
        logger.setLevel(logging.INFO)

    args.func(args)
    
    
if __name__ == '__main__':
    main()

