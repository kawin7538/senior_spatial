import warnings
warnings.filterwarnings("ignore")

from testcase_modules.test_playcase import TestPlayCase

if __name__ == '__main__':

    TestPlayCase(full_precision=False)