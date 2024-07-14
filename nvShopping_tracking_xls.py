# 240630 nv shopping SEO
# inspi@hanmail.net

# 1) 각 키워드별 순위를 추적 - API만
#    - JSON은 속도가 느리고, header-sbth 잡아야 해서 추후 업데이트할 것
# 2) 엑셀 읽어서 누적할 수 있도록
# 3) 체크 되어 있는 키워드만 검색하도록

from datetime import datetime
import math
import sys
import pandas as pd
# from tabulate import tabulate
# import callNvJson as nvjson
import callNVAPI as nvapi
import callNVAd as nvad
import callGetKey as getkey

# tabulate.WIDE_CHARS_MODE = False

mid_list = getkey.get_apikey('mid_list', 'mid_list.json')

# 상품 정보 구하기
for i in range(len(mid_list)):
    filename = f'rank_tracking_{mid_list[i]}.xlsx'
    df = pd.read_excel(filename, index_col=None)
    # print(df)

    # Unnamed: 0 컬럼 제거
    df.drop(['Unnamed: 0'], axis=1, inplace=True)

    col_now = f'{datetime.now().strftime("%y%m%d_%H%M%S")}'
    print(f'mid={mid_list[i]}', end='\t', flush=True)
    print(f'datetime={col_now}', end=' ', flush=True)

    # 키워드별로 키워드 정보 및 상품 랭킹 구하기
    # for keyword in keyword_list:
    for idx, row in df.iterrows():

        if row['tracking'] == 1:

            keyword = row['keyword'].strip()

            # 키워드 정보 출력
            # print('검색어: {:<8}'.format(keyword), end='\t', flush=True)
            amount_search = nvad.getTotalQcCnt(keyword) # 월간 총 검색수 구하기
            # print('총 검색수: {:<8}'.format(format(int(amount_search), ',')), end='\t', flush=True)

            # 상품량 구하기
            [amount_total, cat6, cat20, cat40, cate_name, cate_count]  = nvapi.getNVTotal(keyword)
            # print('\n  상품량: {:<15}'.format(format(int(amount_total), ',')), end='\t', flush=True)
            # print('카탈로그(6/20/40)[1p]: {}/{}/{}'.format(cat6, cat20, cat40), flush=True)

            # 랭킹 구하기
            rank_api = nvapi.getNVRank(mid_list[i], keyword)
            print('.', end='', flush=True)
            if rank_api == False:
                print(f'{mid_list[i]} / {keyword} - Error in API call')
            elif rank_api == -1:
                print(f'{mid_list[i]} / {keyword} - No Result in API call')
            elif rank_api == 0:
                print(f'{mid_list[i]} / {keyword} - No Data in API Result')
            elif rank_api == '.':
                print(',', end='', flush=True)
            #     rank_keyword = nvjson.getNVRank(mid_list[i], keyword, 18)
            #     if (rank_keyword == -1): print('[JSON] Not within top 100p')
            #     else: print('[JSON] 랭킹: {0} ({1}p {2})'.format(format(rank_keyword,','), format(math.ceil(rank_keyword/40)), format(rank_keyword%40)))
            elif rank_api > 0:
                # print('[API] 랭킹: {0} ({1}p {2})'.format(format(rank_api,','), format(math.ceil(rank_api/40)), format((rank_api-1)%40+1)))
                df.loc[idx, col_now] = format(int(rank_api), ',')
            else:
                print(f'{mid_list[i]} / {keyword} - System Check')
                
            # print()
                
            # print(datetime.now())

    with pd.ExcelWriter(filename) as w:
        df.to_excel(w, index=True, index_label=None, sheet_name=col_now)
        # print(filename)
        print()

# print('----------'*10)
