from sklearn.model_selection import train_test_split , KFold , StratifiedKFold
import numpy as np
from time import time
import datetime
from collections import OrderedDict

# 5-fold
def training_regression():
    pass

def training_binary():
    pass
from lightgbm import LGBMClassifier , LGBMRegressor
# todo : save model 기능 추가해야 한다.
def training_fixedTest_noVal( mode, 
                        model_generator, 
                        model_params, 
                        training_params, 
                        metric_func, 
                        X, y, X_test, 
                        nradom= 7 , verbose = False):
    '''
    mode = [ 'regression' , 'binary' , 'classification']
    def metric_func(y , pred_proba) -> obj
    return -> fold_predict , fold_oof , fold_metric
    '''
    starttime = time()
    if verbose:
        print('-'*100)
        print('Training {}  Model : {}'.format( model_generator.__class__.__name__))
  
    model = model_generator.make(model_params)
    model.fit(X,y , training_params)

    # result 
    res_pred = model.predict_proba(X_test)

        
    print('Total Training Time : {}  [h:m:s]'.format(str(datetime.timedelta(seconds=(time() - starttime)))))
    #print('-'*100)
    return res_pred , model

def training_Testfold_noVal( mode, 
                       model_generator, 
                       model_params, 
                       training_params, 
                       metric_func, 
                       X, y,  
                       test_nfold , nradom = 7 , verbose = False) :

    starttime = time()
    print('-'*100)
    print('-'*100)
    print('** Test Fold {} on Model : {} **'.format( test_nfold , model_generator.__class__.__name__))

    test_fold_index = OrderedDict()

    if mode == 'classification':
        oof = np.zeros( ( X.shape[0]  , len(np.unique(y))) , dtype = np.float)
    else:
        oof = np.zeros( (X.shape[0] ) , dtype = np.float)


    
    model_list = OrderedDict()

    kfold = fold_splitter(mode , X , y , test_nfold , nradom)

    for i , (train_index, test_index)  in enumerate(kfold.split(X,y)):
        print()
        print('* Test Fold {} *'.format( i ))        
        xtrain, xtest = X[train_index], X[test_index]
        ytrain, ytest = y[train_index], y[test_index]

        # test_fold 인덱스 저장 
        test_fold_index['fold'+str(i)] = test_index

        # 폴드 실행
        res_pred , fold_model = training_fixedTest_noVal(mode, model_generator, 
                                                                model_params, 
                                                                training_params, 
                                                                metric_func, 
                                                                xtrain, ytrain, xtest , verbose = verbose)
        if mode == 'classification':
            oof[test_index , : ] = np.array(list(res_pred.values()))
        else:
            oof[test_index ] = res_pred
        
        model_list['fold'+str(i)] = fold_model

    return test_fold_index , oof, model_list


def training_fixedTest( mode, 
                        model_generator, 
                        model_params, 
                        training_params, 
                        metric_func, 
                        X, y, X_test, 
                        nfold , nradom= 7 , verbose = False):
    '''
    mode = [ 'regression' , 'binary' , 'classification']
    def metric_func(y , pred_proba) -> obj
    return -> fold_predict , fold_oof , fold_metric
    '''
    starttime = time()
    if verbose:
        print('-'*100)
        print('Training {} Fold on Model : {}'.format( nfold , model_generator.__class__.__name__))

    fold_metric=OrderedDict()
    
    if mode == 'classification':
        fold_oof = np.zeros((y.shape[0] , len(np.unique(y))) , dtype = np.float)
    else:
        fold_oof = np.zeros_like(y , dtype = np.float)


    fold_predict = OrderedDict()
    fold_model = OrderedDict()
   
    kfold = fold_splitter(mode , X , y , nfold , nradom)

    for i , (train_index, val_index)  in enumerate(kfold.split(X,y)):
        xtrain, xval = X[train_index], X[val_index]
        ytrain, yval = y[train_index], y[val_index]

        model = model_generator.make(model_params)
        model.fit(xtrain,ytrain,xval,yval , training_params)

        # result 
        res_oof = model.predict_proba(xval)
        res_pred = model.predict_proba(X_test)

        #save
        if mode == 'classification': # 클래스의 갯수만큼 마지막 차원이 늘어난다. [ 0.9 , 0.01 , 0.99]
            fold_oof[val_index,:] = res_oof
        else:
            fold_oof[val_index] = res_oof

        
        fold_predict['fold'+str(i)] = res_pred
        fold_metric['fold'+str(i)] = metric_func( yval , res_oof)
        fold_model['fold'+str(i)] = model

        if verbose: print('{} Fold score : {:.4f}'.format(i , fold_metric['fold'+str(i)] ))
            
    print('Total Training Time : {}  [h:m:s]'.format(str(datetime.timedelta(seconds=(time() - starttime)))))
    #print('-'*100)
    return fold_predict , fold_oof , fold_metric , fold_model


def training_Testfold( mode, 
                       model_generator, 
                       model_params, 
                       training_params, 
                       metric_func, 
                       X, y,  
                       test_nfold , val_nfold , nradom = 7 , verbose = False) :
    '''
    데이터 X,y를 넣으면 
    # 3폴드 기준
    | 데이터1 | 데이터2 | 데이터3 |

    데이터1을 test 셋 , (데이터2+데이터3)을 다시 3등분 
    | 데이터1 : 테스트 ||d1 : validation | d2 : train       | d3 : train      ||
    | 데이터1 : 테스트 ||d1 : train      | d2 : validation  | d3 : train      ||
    | 데이터1 : 테스트 ||d1 : train      | d2 : train       | d3 : validation ||

    따라서 데이터1을 예측하는 결과는 총 3개가 나온다. 

    데이터2,3도 똑같이 하면 결국 전체 데이터셋에대한 예측값을 얻을 수 있다. 이값으로  스택킹 가능 

    Cv스코어는 3 * 3 개의 모델의 총 성능점수를 평균한 점수가 cv 스코어 이다. 

    3/3폴드 기준으로 
    1. 총 9개의 스코어 점수가 나오고 
    2. 넣어준 X데이터의 샘플수가 n개라고 하면, n x 3개의 예측값 매트릭스가 나오게 된다. ( n을 3등분해서 각 등분에 대한 예측값을 가져오므로 )

    # 필요한 결과값 
    1. 테스트1 ,2,3을 나누는 인덱스 , val/train을 나누는 인덱스 
    2. 전체 샘플에 대한 예측값들 ( 추후 인덱스를 사용해서 각각의 모델이 사용한 데이터를 추려내기)
    3. 모든 모델 저장 ( models['fold1']['3']의 식으로 ) , 같은 fold 명 같은 데이터 사용
    
    # 입력 파라미터 : X , y , 테스트 fold 수 , train/val fold 수 
    '''

    starttime = time()
    print('-'*100)
    print('-'*100)
    print('** Test Fold {} on Model : {} **'.format( test_nfold , model_generator.__class__.__name__))

    test_fold_index = OrderedDict()

    if mode == 'classification':
        oof = np.zeros( (val_nfold , X.shape[0]  , len(np.unique(y))) , dtype = np.float)
    else:
        oof = np.zeros( (X.shape[0] , val_nfold) , dtype = np.float)


    
    model_list = OrderedDict()

    kfold = fold_splitter(mode , X , y , test_nfold , nradom)

    for i , (train_index, test_index)  in enumerate(kfold.split(X,y)):
        print()
        print('* Test Fold {} *'.format( i ))        
        xtrain, xtest = X[train_index], X[test_index]
        ytrain, ytest = y[train_index], y[test_index]

        # test_fold 인덱스 저장 
        test_fold_index['fold'+str(i)] = test_index

        # 폴드 실행
        fold_predict , _ , _  , fold_model = training_fixedTest(mode, model_generator, 
                                                                model_params, 
                                                                training_params, 
                                                                metric_func, 
                                                                xtrain, ytrain, xtest , val_nfold , verbose = verbose)
        if mode == 'classification':
            oof[:,test_index , : ] = np.array(list(fold_predict.values()))
        else:
            oof[test_index , : ] = np.array(list(fold_predict.values())).T
        
        model_list['fold'+str(i)] = fold_model

    return test_fold_index , oof, model_list

def fold_splitter(mode , X,y , nfold , nrandom):
    if mode == 'regression':
        kfold = KFold(n_splits=nfold, random_state=nrandom, shuffle=True)
    elif (mode == 'classification') or (mode == 'binary'):
        kfold = StratifiedKFold(n_splits=nfold, random_state=nrandom, shuffle=False)
    return kfold

def train_model(model_generator , model_params , training_params ):
    pass





# metric binary
'''
result함수를 따로 만들어서 넣어주기! 
아마도 predict 함수는 사용 안할 것 같다 
'''

