import pandas as pd
import os

#경로, 해당 열 받아서 리스트를 반환해준다.
#이때 리스트안의 데이터 타입은 리스트다.
def ReadExcel(file_path, col = 4):
    csv = pd.read_csv("C:\\Users\\jun\\Desktop\\navernews\\20200117.csv", encoding='euc-kr')
    content = csv.iloc[:,col:col+1]
    return content.values.tolist()



#excel 파일로 저장
#dict 형식으로 받아서 처리한다.
#category 폴더의 날짜 이름으로 저장한다.
def WriteInfoToCsv(news_class, classCategory):

    folder_name = news_class['category']
    #폴더 있는지 체크
    if not os.path.isdir(folder_name) :
        os.makedirs(os.path.join(folder_name))

    # 뉴스 날짜를 20200110 형식으로 만든다.
    dateformat = news_class['date'].replace('.', '')[:8]

    #원소를 list 형식으로 바꾼다.
    #DataFrame 때문
    for index, (key, elem) in enumerate(news_class.items()):
        tmp_list = list()
        tmp_list.append(elem)
        news_class[key] = tmp_list
    print(news_class)
    dataframe = pd.DataFrame(news_class)
    
    dataframe.to_csv(folder_name+'/'+ classCategory +'_' + dateformat + '.csv', header=False, index=False, mode='a',encoding='euc-kr')