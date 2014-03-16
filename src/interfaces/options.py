from optparse import OptionParser


def _get_options():
    parser = OptionParser()
    parser.add_option('-c', "--chunk", dest="chunk",
                      help="chunk number", default=1)
    parser.add_option("-l", "--logfile", dest="logfile",
                      help="file name for logging")
    parser.add_option('-p', "--port", dest="port",
                      help="listener port", default=None)
    parser.add_option('-f', "--policy-port", dest="policy_port",
                      help="policy listener port", default=None)

    return parser.parse_args()


def validate_options():
    return _get_options()[0]

OPTIONS = validate_options()
