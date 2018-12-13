import sys
import argparse
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
handler = logging.StreamHandler(stream=sys.stdout)
handler.setFormatter(formatter)
logger.addHandler(handler)

def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    logger.critical("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))

sys.excepthook = handle_exception


def main():

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
            action="store", type=str)
    parser.add_argument("-p", "--password", help="Smsgate user password",
                        action="store", type=str)
    parser.add_argument("-s", "--sender",
            help="Sender name. Displayed in sms header. Must be set according provider rules. Default: Sovcombank",
                        action="store", default='Sovcombank')
    parser.add_argument("-t", "--type",
            help="Sender type. Sender type needed for sms gate",
                        action="store", default='some type')
    parser.add_argument("-w", "--wsdl",
            help="Sms gate wsdl url",
            action="store_true", default='http://sms-gate/sendmessage.wsdl')


    args = parser.parse_args()

    if args.verbose:
        logger.setLevel('DEBUG')
    else:
        logger.setLevel('INFO')

    logger.debug("Connecting with those params: Wsdl url: %s, "
                  "Sender name: %s, Sender type: %s, User: %s, "
                  "Pass %s, Sending message to: %s With content: %s",
    args.wsdl, args.sender, args.type, args.user, args.password, args.phone, args.message)

    
if __name__ == '__main__':
    main()
