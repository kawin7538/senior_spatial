from data_loading import DataLoading
from data_loading.corr_customize_data_monthly import CorrCustomizeDataMonthly


class CorrCustomizeDataLogMonthly(CorrCustomizeDataMonthly):
    def __init__(self, raw_data: DataLoading, func_keyword='pearsonr'):
        super().__init__(raw_data, func_keyword=func_keyword)
        self._set_output_folder('corr_log_monthly')
        self.keyword='corr_log_monthly'

    def _rescale_data(self,data: DataLoading):
        return data.rescale_log()

if __name__ == '__main__':
    CorrCustomizeDataLogMonthly().raw_data