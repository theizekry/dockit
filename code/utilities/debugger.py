import sys
import pprint

class Debugger:
    @staticmethod
    def dd(*args):
        for arg in args:
            pprint.pprint(arg)
            print()
        sys.exit()

    @staticmethod
    def die(msg=None):
        if msg:
            print(msg)
        sys.exit()

    @staticmethod
    def dump(*args):
        for arg in args:
            pprint.pprint(arg)
            print()