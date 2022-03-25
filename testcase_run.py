from testcase_modules.test_playcase import TestPlayCase
import warnings

from testcase_modules.test_playcase2 import TestPlayCase2
warnings.filterwarnings("ignore")

if __name__ == '__main__':

    # TestPlayCase(full_precision=False,startwith100=True)
    tester=TestPlayCase2(n_sim=100)
    tester.simulate_case()
    tester.action_case()
    tester.evaluate_case()