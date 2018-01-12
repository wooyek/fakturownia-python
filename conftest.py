# coding=utf-8
import doctest
import logging

log = logging.getLogger(__name__)


class ExtendedOutputChecker(doctest.OutputChecker):
    """Will match '...' as a whole line

    https://stackoverflow.com/a/5820975/260480
    """

    def check_output(self, want, got, optionflags):
        if optionflags & doctest.ELLIPSIS:
            want = want.replace("'...'", "...")
        return super(doctest.OutputChecker, self).check_output(want, got, optionflags)


doctest.OutputChecker = ExtendedOutputChecker
