import chart_studio.plotly as py
import plotly.graph_objs as go

import umap
import pandas as pd
import seaborn as sns
import numpy as np
import warnings
from matplotlib import pyplot as plt
import matplotlib as mlt
warnings.filterwarnings("ignore") 

# metric
dist_list = ['euclidean',
             'manhattan',
             #'cityblock',
             'braycurtis',
             'canberra',
             'chebyshev',
             'correlation',
             'cosine',
             'dice',
             'hamming',
             'jaccard',
             'kulsinski',
             'mahalanobis',
             #'matching',
             'minkowski',
             'rogerstanimoto',
             'russellrao',
             'seuclidean',
             'sokalmichener',
             'sokalsneath',
             #'sqeuclidean',
             'yule',
             'wminkowski']
n_neighbor_list = np.arange(4 , 24 , 4)
min_dist_list = np.arange(0.1 , 1.0 , 0.1)


def plot_umap_unsupervised(xs,ys , issupervised ,n_neighbors , min_dist , dist, figsize = (8,6), save_dir = None):
    umap_model = umap.UMAP(n_neighbors=n_neighbors,
                          min_dist=min_dist,
                          n_components = 2,
                          metric=dist )
    if issupervised:
        embedding = umap_model.fit_transform(xs,ys)
    else:
        embedding = umap_model.fit_transform(xs)
    print('-'*100)
    print(dist , n_neighbors , min_dist)

    fig , ax = plt.subplots(1,1,figsize = figsize)

    #sns.scatterplot(embedding[:,0] , embedding[:,1] , hue = ys , ax = ax)
     # color 의 수는 class 수와 같게 맞춘다. 
    color = sns.color_palette("colorblind", 6)
    sns.scatterplot(embedding[:, 0], embedding[:, 1], hue=ys, ax=ax, palette=color)
    if save_dir is not None:
        plt.savefig( save_dir + '/{}_{}_{}.png'.format(dist , str(n_neighbors) ,str(min_dist)))
    plt.show()
    return embedding

   



def umap_combination_unsupervised(xs, ys = None, dist_list=dist_list, n_neighbor_list=n_neighbor_list, min_dist_list=min_dist_list,
                                                                        issupervised = False , figsize = (8,6) , save_dir = None):
    for dist in dist_list:
        for nn in n_neighbor_list:
            for md in min_dist_list:
                try:
                    plot_umap_unsupervised(xs,ys , issupervised ,nn , md , dist , figsize , save_dir)
                except:
                    continue
                

def plotly_plot(xs , ys , n_class , cmap_name = 'viridis' , title = '' , filename = 'temp'):

    # color amp
    viridis_cmap = mlt.cm.get_cmap('viridis') 
    norm = mlt.colors.Normalize(vmin=0, vmax=n_class) # 컬러맵의 구간을 나눔
    viridis_rgb = [ mlt.colors.colorConverter.to_rgb(viridis_cmap(norm(i))) for i in range(0, n_class) ] # 컬러맵을 RGB컬러로 변환
    viridis_rgb_dict = dict( zip( list(range(3)) , viridis_rgb ) )  # 각 컬러를 숫자로 키값 만듬
    label_color =np.vectorize(lambda x : 'rgb' + str(viridis_rgb_dict[x]) )(ys) # rgb(컬러) 와 같이 만듬

    # 각 점의 텍스트 만들기 
    text_list = [ str(x)+'_'+str(ys[x]) for x in list(range(xs.shape[0]))]

    data = [ go.Scatter(
                        x=xs[:,0],
                        y=xs[:,1],
                        mode = 'markers',
                        marker=dict(size=15, color=label_color),
                        text=text_list)]

    layout = go.Layout( title = title , xaxis = {'title' : 'x1'} , yaxis = {'title' : 'x2'})

    fig = go.Figure(data=data)
    return py.iplot(fig, filename=filename)



# 데이터에 대해서 umap을 하고 plot을 한다. 

# plotly로 디스플레이 

# 먼저 임베딩 하는코드 
# 임베딩 결과를 뿌리는 코드
# 메트릭별 설명도 있으면 좋을듯 



## 아래는 training / validation 의 각각의 클래스별 플롯 + 검은색 십자가로 테스트셋 표기되는 코드 + 저장
def plot_umap_unsupervised_seperate(xs,ys,xtrain,ytrain,xval,yval,xtest , issupervised ,n_neighbors , min_dist , dist, figsize = (8,6) , save_path = './'):
    umap_model = umap.UMAP(n_neighbors=n_neighbors,
                          min_dist=min_dist,
                          n_components = 2,
                          metric=dist)
    if issupervised:
        umap_model.fit(xs,ys)
    else:
        umap_model.fit(xs)
    print('-'*100)
    print(dist , n_neighbors , min_dist)

    #get 

    emtr = umap_model.transform(xtrain)
    emvl = umap_model.transform(xval)
    emte = umap_model.transform(xtest)
    

    
    fig , ax = plt.subplots(1,1,figsize = figsize)

    #sns.scatterplot(embedding[:,0] , embedding[:,1] , hue = ys , ax = ax)
     # color 의 수는 class 수와 같게 맞춘다. 

    color1 = sns.color_palette("Set1", 2) 
    color2 = sns.color_palette("Dark2", 2)

    
    sns.scatterplot(emtr[:,0] , emtr[:,1] , hue = ytrain , style = ytrain , ax = ax , palette = color1 )
    sns.scatterplot(emvl[:,0] , emvl[:,1] , hue = yval   , style = yval , ax = ax , palette = color2 )
    sns.scatterplot(emte[:,0] , emte[:,1] , marker = '1', alpha = 0.7, color = 'black'  , ax = ax  )
    #sns.scatterplot(embedding[:,0] , embedding[:,1] , hue = ys  , ax = ax , palette = color )
  

    ## 저장 부분
    plt.savefig( save_path + '{}_{}_{}.png'.format(dist , str(n_neighbors) ,str(min_dist)))
    #plt.show()
    return embedding

def umap_combination_unsupervised_seperate(xs, ys, xtrain, ytrain, xval, yval, xtest,
dist_list = dist_list , n_neighbor_list = n_neighbor_list, min_dist_list = min_dist_list , issupervised = False , figsize = (8,6), save_path = './'):
    for dist in dist_list:
        for nn in n_neighbor_list:
            for md in min_dist_list:
                try:
                    plot_umap_unsupervised_seperate(xs,ys ,xtrain,ytrain,xval,yval,xtest , issupervised ,nn , md , dist , figsize , save_path)
                except:
                    continue