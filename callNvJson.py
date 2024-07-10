# 231206 네이버 쇼핑 JSON 불러오기
# nv shopping SEO
# inspi@hanmail.net

# 모듈 독립화

import requests
import urllib.request
import json
import random
import callGetKey as getkey

list_sbth = getkey.get_apikey('list_sbth', 'nvshop_headers.json')
list_agent = getkey.get_apikey('list_agent', 'nvshop_headers.json')

# browser 정보 바꾸기
def get_header_browser(keyword, pageIndex, pageSize, mode='', npay=''):

    # random.seed()
    ranNum = random.randrange(0, len(list_sbth)) # 0~4 임의의 정수 생성

    encText = urllib.parse.quote(keyword)
    # print(query, encText)

    mode_productSet_value = 'total'
    query_npay = ''
    if npay == 'on':
        mode_productSet_value = 'checkout'
        query_npay += '&npayType='


    cookies = { # macOS Safari 기준
        'NNB': 'SKQRMHARKCWWI',
        'ASID': '735ba6a50000018a1851dac40000005e',
        '_fwb': '5ftAOid4Vp25ZbAcCZmxC.1704037548301',
        '_ga': 'GA1.2.44251984.1680889918',
        'SHP_BUCKET_ID': '4',
    }

    header = {
        'accept': 'application/json, text/plain, */*', #(0)
        'accept-language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7', #(0)
        # 'cookie': 'NNB=2GICURDNCHCWG; autocomplete=use; NV_WETR_LOCATION_RGN_M="MDkxNDA1OTA="; NV_WETR_LAST_ACCESS_RGN_M="MDkxNDA1OTA="; ASID=735ba6a500000187bd60309700000052; _fwb=222Wp30HWLzitInHaTEpuzY.1703512850576; _ga_451MFZ9CFM=GS1.1.1703717211.3.1.1703718531.0.0.0; _ga=GA1.2.807677109.1703555362; SHP_BUCKET_ID=9; page_uid=imacOsqVOswssR8T48Nssssstho-415276; spage_uid=imacOsqVOswssR8T48Nssssstho-415276; nid_inf=675561392; NID_JKL=rdGXFBtvCk45eJWYq3C7Rg2zxTORkMarIfuHicOkZ7I=; ncpa=5684525|lut6f5ls|d1977b1f63a1e976156509bbc969fe3d0b223d6b|s_1c210c0912715|d5e18bbce024e2cdca105879799f16c65ce4bb14:1178739|lut6fy5k|fed46dda18b208d028e347f7ed2408438a60ea60|s_2fdd995bfb415|58722196bb76b9e8038b41bd7b618945af2d9c1b; CBI_SES=TZ45qPzTZtcvV1F64P6jgYF54D8Jt8Qec0GqP21TwJA/u8liqf76gw+VMeMrxYWSBFPci4zPOt0HXbvPzy0HyMS7E67zSfc+DxOutQ7EixG1kx8SnPqehfaB4Lptj0fSe2KefIRpm5EXSMuA4WA0KXxJIWNI3jpEuy421GstHRBsrfW1uZ4XUKuQIqQZVSwqOflpOPEYICZtCG4OLk0xcZaZjtE++tyIpuRdrYL/Mw4zDdbNjh3oV2VNbNS38J1OaJ0rKpmOkwUiAj9fkwH6cknh3/DKLSYCafrAE6zrd4g1YIdUymMllaRphbgo2wUiEP8otPwTXScXK5YcbgB4xFQabyKgpag7tAy7p+Fp4IVhKUBnsLARjE4htIrAf5kItojswU1iofzsj8KogrJwIZzdVlZkg3PE5kqaHTGzYQTrLLNt4mFET/RfEum56cUJ; CBI_CHK="r5V0mf9uRUZHZ/vmLGy3ez7f4/k4aqWXL5o03eN68frNwJJm/nj4kJc1H9YfdZbLnG6Xa479/k/iJI7dAxrbtujKaPEnZmCbkWUnH1nraUjB+A/gkz1FwCNNF6BgujsbhYReq2FGDDorwt7fRndICx+fg8bfVsi0b5su9TvBP+g="',
        'logic': 'PART', #(0)
        # 'referer': 'https://search.shopping.naver.com/search/all?adQuery=xxx&fo=true&origQuery=...'
        'referer': 'https://search.shopping.naver.com/search/all?' #(0)
        + 'adQuery=' + encText
        + query_npay
        + '&origQuery=' + encText
        + '&pagingIndex=' + ('1' if npay=='on' else str(pageIndex))
        + '&pagingSize=' + str(pageSize)
        + '&productSet=' + mode_productSet_value
        + '&query=' + encText
        + '&sort=rel&timestamp=&viewType=list',
        'sbth': list_sbth[ranNum], #(0)
        # 'sec-ch-ua': '"Google Chrome";v="123", "Not:A-Brand";v="8", "Chromium";v="123"', #(0)
        'sec-fetch-dest': 'empty', #(0)
        'sec-fetch-mode': 'cors', #(0)
        'sec-fetch-site': 'same-origin', #(0)
        'user-agent': list_agent[ranNum], #(0)#####
    }

    params = {
        'adQuery': keyword,
        'eq': '',
        # 'fo': 'true',
        'iq': '',
        # 'npayType': '2',
        'origQuery': keyword,
        'pagingIndex': str(pageIndex),
        'pagingSize': str(pageSize),
        'productSet': mode_productSet_value,
        'query': keyword,
        'sort': 'rel',
        'viewType': 'list',
        'window': '',
        'xq': '',
    }
    if mode == 'only':
        params['fo'] = 'true'

    if npay == 'on':
        params['npayType'] = '2'

    return [header, params, cookies]

# 네이버 쇼핑 JSON 함수
def callNvJson(keyword, pageIndex=1, pageSize=40, mode='', npay=''):

    [headers, params, cookies] = get_header_browser(keyword, pageIndex, pageSize, mode, npay)

    try:
        response = requests.get(
            'https://search.shopping.naver.com/api/search/all',
            params=params,
            headers=headers,
            cookies=cookies
        )
    except Exception as e:
        print('Request Error', e)
        return

    try:
        items = json.loads(response.text)
    except Exception as e:
        # print(keyword)
        print('Json Load Error', e)
        with open(f'./error.txt', 'w', encoding='utf-8', errors='ignore') as f:
            # f.write(str(headers))
            # f.write(str(params))
            f.write(response.text)
        return

    # print('headers', headers)
    # print('params', params)
    # print()
    # print(items)

    if len(items) < 1:
        print('No Result')
        return False

    if items['shoppingResult']['total'] < 1:
        print('\nCan not Product Searching\nPlease Retry - {}'.format(keyword))
        return 0

    return items

# 최대로 순위 검색할 페이지 limit_page = 100p
def getNVRank(mid, keyword, pageIndex=1, pageSize=40, limit_page=100):
    while pageIndex <= limit_page:
        
        items = callNvJson(keyword, pageIndex, pageSize)

        # print('{}_'.format(pageIndex),end='',flush=True)
        if (pageIndex % 5) == 0:
            print(',', end='', flush=True)
            # time.sleep(0.1)

        if items == False: return False
        elif items == 0: return 0
        else:
            for item in items['shoppingResult']['products']:
                if mid == item['id']: 
                    return int(item['rank'])

        pageIndex += 1

    return -1

def getVisit(channelUid, channelUrl):
    headers = {
        'accept': 'application/json, text/plain, */*',
        'sec-ch-ua': '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
    }

    response = requests.get(
        'https://smartstore.naver.com/i/v2/channels/' + channelUid + '/visit',
        headers=headers,
    )

    res = json.loads(response.text)

    if len(res) < 1:
        print('No Result')
        return False

    return res
