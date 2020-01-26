import pandas as pd
import re
import os
from konlpy.tag import Komoran
import glob
#엑셀의 경로, 해당 열을 받아서 리스트를 반환해준다.
def ReadExcel(file_path, col = 4) :
    csv = pd.read_csv(file_path, encoding='euc-kr', header=None)
    content = csv.iloc[:,col:col+1]
    content = content.values.tolist()
    real_content = list()
    for i in content :
        real_content.append(i[0])
    return real_content



#excel 파일로 저장
#dict 형식으로 받아서 처리한다.
#category 폴더의 날짜 이름으로 저장한다.
def WriteInfoToCsv(news_class, classCategory) :

    folder_name = news_class['category']
    #폴더 있는지 체크
    if not os.path.isdir(folder_name) :
        os.makedirs(os.path.join(folder_name))

    # 뉴스 날짜를 20200110 형식으로 만든다.
    dateformat = news_class['date'].replace('.', '')[:8]

    #원소를 list 형식으로 바꾼다.
    #DataFrame 때문
    for index, (key, elem) in enumerate(news_class.items()) :
        tmp_list = list()
        tmp_list.append(elem)
        news_class[key] = tmp_list
    print(news_class)
    dataframe = pd.DataFrame(news_class)
    
    dataframe.to_csv(folder_name+'/' + dateformat + '.csv', header=False, index=False, mode='a',encoding='euc-kr')

#해당 csv파일을 불필요한 문자들을 제거하고 txt파일로 만든다.
def CsvToTxtWithEdit(files = glob.glob("*/*.csv", recursive=True), overwrite=False):

    file_list = list()
    for file in files :
        if overwrite == False and os.path.isfile(file[:-4]+'.txt') :
            continue
        content_list = ReadExcel(file,4)
        clear_sentence_list = list()

        #기사내용중 불필요한 단어들 제거
        for content in content_list :
            clear_sentence_list.append(RemoveWord(content))

        #기사내용을 txt파일로 쓴다.
        f = open(file[:-4] + '.txt', 'w')
        for each_line in clear_sentence_list :
            f.write(each_line + '\n')
        f.close()
        file_list.append(file[:-4] + '.txt')
    return file_list


#불필요한 단어들 제거하기
#특수문자 같은 불필요한것들 모두 지우기
def RemoveWord(sentence):
    REMOVE_DICTIONARY = [
        "flash 오류를 우회하기 위한 함수 추가",
        "function _flash_removeCallback() {}",
        "무단전재", "무단 배포 금지", "재배포 금지", "배포 금지", "배포금지", 
        "기자",
        "머니투데이", "서울경제""데일리안"
    ]
    for i in REMOVE_DICTIONARY :
        sentence = sentence.replace(i, "")
    edit_sentence = re.sub('[^a-zA-Z0-9 ㄱ-ㅣ 가-힣]', '', sentence)
    return edit_sentence



#코모란을 이용하여 파일을 읽어서 ,으로 나누어서 다시 txt파일로 저장한다
#이때 라인단위로 분류하여 읽고 쓴다.
def FixWithKomoran(files = glob.glob("*/????????.txt", recursive=True), overwrite=False):
    USERDIRECTORY = "./user_dictionary"
    ko = Komoran(userdic=USERDIRECTORY)
    for file in files :
        if overwrite == False and os.path.isfile(file[:-4]+'_komoran.txt') :
            continue
        target = open(file, 'r')
        to_save = open(file[:-4] + '_komoran.txt', 'w')
        target_list = target.readlines()
        print(file)
        try:
            for sentence in target_list :
                edit_sentence = ko.nouns(sentence)
                for  i in edit_sentence :
                    if len(i) == 1:
                        edit_sentence.remove(i)
                to_save.write(','.join(edit_sentence) + '\n')
        except Exception as e:
            print(sentence)
        target.close()
        to_save.close()
    return file[:-4] + '_komoran.txt'






