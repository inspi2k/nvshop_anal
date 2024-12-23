# 240801 nv shopping rank tracking
# inspi@hanmail.net

# 1) 각 키워드별 순위를 추적 - API만
#    - JSON은 속도가 느리고, header-sbth 잡아야 해서 추후 업데이트할 것
# 2) google sheet 읽고, 기록
# 3) 체크 되어 있는 키워드만 검색하도록
# 4) api limit 체크해서 업데이트 할 것 
#    (# API Call Limit - 1유저 당 60초간 60회)

from datetime import datetime
import math
import sys
import pandas as pd
import gspread
import warnings
# import callNvJson as nvjson
import callNVAPI as nvapi
import callNVAd as nvad
import callGetKey as getkey
import time

# from tabulate import tabulate
# tabulate.WIDE_CHARS_MODE = False

print(datetime.now().strftime(" %y-%m-%d_%H:%M:%S"))

# secret info
GS_JSON = getkey.get_apikey('GS_JSON', 'gsheet_info.json')
GS_URL = getkey.get_apikey('GS_URL', 'gsheet_info.json')
GSHEET_KEYWORDS = getkey.get_apikey('GSHEET_KEYWORDS', 'gsheet_info.json')
GSHEET_RANK_PRE = getkey.get_apikey('GSHEET_RANK_PRE', 'gsheet_info.json')

# gspread 로 keyword list 가져오기
gc = gspread.service_account(filename=f'./{GS_JSON}')
doc = gc.open_by_url(GS_URL)
ws_keywords = doc.worksheet(GSHEET_KEYWORDS)

df = pd.DataFrame(ws_keywords.get_all_records(), columns=['MID', 'KEYWORD', 'TRACKING', 'STORE', 'ITEM'])
# header 삭제
# df.drop(df.index[0], axis='index', inplace=True)
# MID 섞여있을지 모르니 정렬
try:
    df.sort_values('MID', ascending=True)
# MID 비어있으면 예외처리
except:
    print('MID - Blank Check')

# 중복 제거 후 인덱스 재설정 - https://mizykk.tistory.com/93
# mids = df.drop_duplicates(subset=['MID'], ignore_index=True)
# mid_list = mids['MID']

now = datetime.now()
now_date = f'{now.strftime("%y. %m. %d")}'
now_time = f'{now.strftime("%H:%M:%S")}'

# rank dataframe 생성
df_rank = df[df['TRACKING'] == 1].copy()

# rank dataframe - column 추가/정리
df_rank.drop(['TRACKING'], axis='columns', inplace=True)
df_rank.insert(0, 'TIME', [now_time for i in range(len(df_rank))])
df_rank.insert(0, 'DATE', [now_date for i in range(len(df_rank))])
df_rank['RANK'] = ''
df_rank['CHANNEL'] = 'nsAPI'
df_rank['NAME_PRD'] = ''
df_rank['AMT_SEARCH'] = ''
df_rank['AMT_PRDS'] = ''

count = 0

# 키워드별로 키워드 정보 및 상품 랭킹 구하기
# for keyword in keyword_list:
for idx, row in df_rank.iterrows():

    if(row['MID'] == ''): 
        print('\nMID is null - ', row['KEYWORD'], end='', flush=True)
        continue

    keyword = row['KEYWORD'].strip()

    # 키워드 정보 출력
    # print('검색어: {:<8}'.format(keyword), end='\t', flush=True)
    amount_search = nvad.getTotalQcCnt(keyword) # 월간 총 검색수 구하기
    # print('총 검색수: {:<8}'.format(format(int(amount_search), ',')), end='\t', flush=True)
    df_rank.loc[idx, 'AMT_SEARCH'] = int(amount_search)

    # 상품량 구하기
    [amount_total, cat6, cat20, cat40, cate_name, cate_count]  = nvapi.getNVTotal(keyword)
    # print('\n  상품량: {:<15}'.format(format(int(amount_total), ',')), end='\t', flush=True)
    # print('카탈로그(6/20/40)[1p]: {}/{}/{}'.format(cat6, cat20, cat40), flush=True)
    df_rank.loc[idx, 'AMT_PRDS'] = amount_total

    # 랭킹 구하기
    print(' ', end='',flush=True)
    count += 1
    print(count, end='', flush=True)        #print('', flush=True)

    # 1초에 10회 호출 제한 https://developers.naver.com/notice/article/7692
    if count % 50 == 0:  # 50의 배수일 때 대기
        for i in range(10):  # 1초 동안 대기
            print('+' if i % 2 == 0 else '*', end='', flush=True)  # +와 * 반복
            time.sleep(0.1)  # 0.1초 대기

    # rank_api = nvapi.getNVRank(str(row['MID']), keyword)
    [rank_api, title_api] = nvapi.getNVRankInfo(str(row['MID']), keyword)
    # print(':', end='', flush=True)
    if rank_api == False:
        print(f'{row["MID"]} / {keyword} - Error in API call')
    elif rank_api == -1:
        print(f'{row["MID"]} / {keyword} - No Result in API call')
    elif rank_api == 0:
        print(f'{row["MID"]} / {keyword} - No Data in API Result')
    elif rank_api == 9999999:
        # df_rank.loc[idx, 'RANK'] = 1201
        df_rank.drop(idx, axis=0, inplace=True) # 행삭제
        print(',', end='', flush=True)
    #     rank_keyword = nvjson.getNVRank(row['MID'], keyword, 29)
    #     if (rank_keyword == -1): print('[JSON] Not within top 100p')
    #     else: print('[JSON] 랭킹: {0} ({1}p {2})'.format(format(rank_keyword,','), format(math.ceil(rank_keyword/40)), format(rank_keyword%40)))
    elif rank_api > 0:
        # print('[API] 랭킹: {0} ({1}p {2})'.format(format(rank_api,','), format(math.ceil(rank_api/40)), format((rank_api-1)%40+1)))
        # df_rank.loc[idx, 'RANK'] = format(int(rank_api), ',')
        df_rank.loc[idx, 'RANK'] = int(rank_api)
        df_rank.loc[idx, 'NAME_PRD'] = title_api
    else:
        # print(f'{row["MID"]} / {keyword} - System Check')
        print(f'{row["MID"]} / {keyword} - System Check')
        
    # print()
        
    # print(datetime.now())

# df_rank를 MID별로 그룹화하여 각각 다른 시트에 기록
for mid in df_rank['MID'].unique():
    # 해당 MID의 데이터만 필터링
    df_mid = df_rank[df_rank['MID'] == mid]
    
    # 시트 이름을 MID로 설정
    sheet_name = f'{mid}'
    
    try:
        # 해당 이름의 시트가 있는지 확인
        ws_rank = doc.worksheet(sheet_name)
    except gspread.exceptions.WorksheetNotFound:
        # 없으면 새로 생성
        ws_rank = doc.add_worksheet(sheet_name, 1000, 11)  # 1000행, 11열로 생성
        headers = ['DATE', 'TIME', 'MID', 'KEYWORD', 'STORE', 'ITEM', 'RANK', 'CHANNEL', 'NAME_PRD', 'AMT_SEARCH', 'AMT_PRDS']
        # 새로운 update 메서드 사용법
        ws_rank.update(values=[headers], range_name='A1:K1')

    row_last = len(ws_rank.col_values(1))
    
    # 데이터 업데이트도 새로운 방식으로 변경
    ws_rank.update(values=df_mid.values.tolist(), range_name=f'A{row_last + 1}:K{row_last + len(df_mid)}')

print()
print(datetime.now().strftime(" %y-%m-%d_%H:%M:%S"))

# gspread의 deprecation 경고 무시
warnings.filterwarnings('ignore', category=DeprecationWarning)
warnings.filterwarnings('ignore', message='legacy_spreadsheet')