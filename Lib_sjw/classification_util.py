from sklearn.preprocessing import label_binarize
from sklearn.metrics import precision_recall_curve ,auc , roc_auc_score
import numpy as np

# metric function 을 여기에 정의한다. 
def aucpr(class_values = None , y = None, pred =None):
    y_onehot = y.copy()
    pred_onehot = pred.copy()
    if class_values != None: # 가끔식 클래스4개인데, 실제 샘플은 클래스 3 종류로만 이루어 졌을 경우가 있다. 
        y_onehot = label_binarize(y, class_values)
        pred_onehot = label_binarize(pred , class_values )
    elif len(y.shape) == 1:
        y_onehot = label_binarize(y, np.unique(y))
        pred_onehot = label_binarize(pred , np.unique(y) )
    
    precision, recall, _ = precision_recall_curve(y_onehot.ravel(),pred_onehot.ravel()) # 평균까지 같이 내준다. 
    score_aucpr = auc(recall , precision) # recall is x axis , precision is y axis
    return score_aucpr
'''
def aucpr_multi(class_values = None , y = None, pred =None):
    y_onehot = y.copy()
    pred_onehot = pred.copy()
    if class_values != None:
        y_onehot = label_binarize(y, class_values)
        pred_onehot = label_binarize(pred , class_values )
    elif len(y.shape) == 1:
        y_onehot = label_binarize(y, np.unique(y))
        pred_onehot = label_binarize(pred , np.unique(y) )
    
    precision, recall, _ = precision_recall_curve(y_onehot.ravel(),pred_onehot.ravel()) # 평균까지 같이 내준다. 
    score_aucpr = auc(recall , precision) # recall is x axis , precision is y axis
    return score_aucpr
'''
def auc_multi(class_values = None , y = None, pred =None):
    y_onehot = y.copy()
    pred_onehot = pred.copy()
 
    if class_values != None:
        y_onehot = label_binarize(y, class_values)
        
     
    elif len(y.shape) == 1:
        y_onehot = label_binarize(y, np.unique(y))
        

 
    auc = roc_auc_score(y_onehot.ravel(),pred.ravel()) # 평균까지 같이 내준다. 
    return auc




import pandas as pd
import numpy as np
from scipy import interp

from  sklearn.metrics import precision_recall_fscore_support
from sklearn.metrics import roc_curve, auc
from sklearn.preprocessing import LabelBinarizer

def class_report(y_true, y_pred, y_score=None, average='micro'):
    if y_true.shape != y_pred.shape:
        print("Error! y_true %s is not the same shape as y_pred %s" % (
              y_true.shape,
              y_pred.shape)
        )
        return

    lb = LabelBinarizer()

    if len(y_true.shape) == 1:
        lb.fit(y_true)

    #Value counts of predictions
    labels, cnt = np.unique(
        y_pred,
        return_counts=True)
    n_classes = len(labels)
    pred_cnt = pd.Series(cnt, index=labels)

    metrics_summary = precision_recall_fscore_support(
            y_true=y_true,
            y_pred=y_pred,
            labels=labels)

    avg = list(precision_recall_fscore_support(
            y_true=y_true, 
            y_pred=y_pred,
            average='weighted'))

    metrics_sum_index = ['precision', 'recall', 'f1-score', 'support']
    class_report_df = pd.DataFrame(
        list(metrics_summary),
        index=metrics_sum_index,
        columns=labels)

    support = class_report_df.loc['support']
    total = support.sum() 
    class_report_df['avg / total'] = avg[:-1] + [total]

    class_report_df = class_report_df.T
    class_report_df['pred'] = pred_cnt
    class_report_df['pred'].iloc[-1] = total

    if not (y_score is None):
        fpr = dict()
        tpr = dict()
        roc_auc = dict()
        for label_it, label in enumerate(labels):
            fpr[label], tpr[label], _ = roc_curve(
                (y_true == label).astype(int), 
                y_score[:, label_it])

            roc_auc[label] = auc(fpr[label], tpr[label])

        if average == 'micro':
            if n_classes <= 2:
                fpr["avg / total"], tpr["avg / total"], _ = roc_curve(
                    lb.transform(y_true).ravel(), 
                    y_score[:, 1].ravel())
            else:
                fpr["avg / total"], tpr["avg / total"], _ = roc_curve(
                        lb.transform(y_true).ravel(), 
                        y_score.ravel())

            roc_auc["avg / total"] = auc(
                fpr["avg / total"], 
                tpr["avg / total"])

        elif average == 'macro':
            # First aggregate all false positive rates
            all_fpr = np.unique(np.concatenate([
                fpr[i] for i in labels]
            ))

            # Then interpolate all ROC curves at this points
            mean_tpr = np.zeros_like(all_fpr)
            for i in labels:
                mean_tpr += interp(all_fpr, fpr[i], tpr[i])

            # Finally average it and compute AUC
            mean_tpr /= n_classes

            fpr["macro"] = all_fpr
            tpr["macro"] = mean_tpr

            roc_auc["avg / total"] = auc(fpr["macro"], tpr["macro"])

        class_report_df['AUC'] = pd.Series(roc_auc)

    return class_report_df