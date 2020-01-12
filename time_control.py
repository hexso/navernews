from datetime import datetime,timedelta


#특정 날짜(년,월,일)로부터 지금까지의 날짜를 리스트로 반환해준다.
#이 때 20190101형식으로 반환한다.
def GetTimeList(year, month, day):
    from_time = datetime(year,month,day)
    now_time = datetime.now()

    time_list = list()

    while from_time.date() != now_time.date() :
        time_list.append(from_time.strftime("%Y%m%d"))
        from_time = from_time + timedelta(days=1)
    print(time_list)
    return time_list

def GetNowTime():
    now_time = datetime.now()
    return now_time.strftime("%Y%m%d")