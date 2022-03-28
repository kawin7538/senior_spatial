from sklearn.metrics import confusion_matrix


class CustomConfusionMatrix:
    def __init__(self, y_true, y_pred, labels) -> None:
        tn, fp, fn, tp = confusion_matrix(y_true,y_pred,labels=labels).ravel()
        self.tn=tn
        self.fp=fp
        self.fn=fn
        self.tp=tp
        self.population=tn+fp+fn+tp
        self.accuracy=((tp+tn)/self.population) if self.population else 0
        self.prevalence=((tp+fp)/self.population) if self.population else 0
        self.precision=tp/(tp+fp) if tp+fp else 0
        self.npv=tn/(tn+fn) if tn+fn else 0
        self.recall=tp/(tp+fn) if tp+fn else 0
        self.specificity=tn/(tn+fp) if tn+fp else 0
        self.f1=2*(self.precision*self.recall)/(self.precision+self.recall) if self.precision+self.recall else 0

    @staticmethod
    def get_column_names():
        return ['tn','fp','fn','tp','population','accuracy','prevalence','precision','npv','recall','specificity','f1']

    def get_values(self):
        return [self.tn,self.fp,self.fn,self.tp,self.population,self.accuracy,self.prevalence,self.precision,self.npv,self.recall,self.specificity,self.f1]
