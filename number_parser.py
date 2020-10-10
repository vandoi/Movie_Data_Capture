import os
import re
from core import *

# regex
censor_re = re.compile("([a-zA-Z]{2,5})-?([0-9]{3,5})((-|_)[a-zA-Z0-9])?") # group1: publisher, group2: number, group3: section
heyzo_re = re.compile("([a-zA-Z]{5})(-|_)([0-9]{4})") # special regex for heyzo, only grab video number
uncensor_re = re.compile("([0-9]{6}(-|_)[0-9]{3})") # only grab the number
fc2_re = re.compile("(-|_)([0-9]{7})") # special regex for fc2, only grab the number
# use to identify uncensored video
unsensor_publisher = {
    'carib': 'Caribbean',
    'caribbean': 'Caribbean',
    '1pon': '1Pondo',
    '1pondo': '1Pondo',
    'heyzo': 'HEYZO',
    'tokyo-hot': 'Tokyo-Hot',
    'pacopa': 'Pacopacomama',
    'Pacopacomama': 'Pacopacomama'
}

# movie name filter
# filter_name_path = "./filter_name.txt"
# filter_name = []
# with open(filter_name_path, 'r') as filter_d:
#     for line in filter_d:
#         filter_name.append(line.rstrip('\n'))

def get_number(debug, filepath: str, conf: config.Config) -> str:
    filename = os.path.basename(filepath)

    try:
        if '-' in filename or '_' in filename:  # 普通提取番号 主要处理包含减号-和_的番号
            # strip unwanted text in movie name
            filter_names = conf.filter_names()
            # print("filter_names: {}".format(filter_names))
            for unwanted in conf.filter_names():
                filename = filename.replace(unwanted, '')
            # 去除文件名中时间
            filename = str(re.sub("\[\d{4}-\d{1,2}-\d{1,2}\] - ", "", filename))
            # convert filename to lower case
            filename = filename.lower()

            # extract unique identifier according to movie type
            publisher = ""
            identifier = ""
            if 'heyzo' in filename or 'HEYZO' in filename: # heyzo movies, it uses 4 digits numbers
                print("[!]Detected a Heyzo movie")
                publisher = unsensor_publisher['heyzo']
                results = heyzo_re.findall(filename)
                if len(results) == 0:
                    raise ValueError('Unable to capture identifier')
                else:
                    results = results[0]
                number = results[2] # the third capture group is number
                identifier =  publisher + '-' + number
            elif any(pub in filename for pub in unsensor_publisher.keys()): # unsensored movies
                print("[!]Detected an uncensored movie")
                publisher = list(filter(lambda x: (x in filename), unsensor_publisher.keys()))[0]
                results = uncensor_re.findall(filename)
                if len(results) == 0:
                    raise ValueError('Unable to capture identifier')
                else:
                    results = results[0]
                number = results[0] # the first capture group is number
                print("number: {}, results: {}".format(number, results))
                identifier = number
            elif 'FC2' in filename or 'fc2' in filename: # FC2 movies
                print("[!]Detected a FC2 movie")
                # filename = filename \
                #             .replace('PPV', '').replace('ppv', '') \
                #             .replace('FC2', '').replace('fc2', '') \
                #             .replace('--', '-').replace('_', '-')
                results = fc2_re.findall(filename)
                # print("filename: {}, results: {}".format(filename, results))
                if len(results) == 0:
                    raise ValueError('Unable to capture identifier')
                else:
                    results = results[0]
                number = results[1] # the second capture group is number
                identifier = 'FC2-' + number
            else: # generic for censored movies
                print("[!]Detected a censored movie")
                results = censor_re.findall(filename)
                if len(results) == 0:
                    raise ValueError('Unable to capture identifier')
                else:
                    results = results[0]
                publisher = results[0].upper() # the first caputre group is publisher
                number = results[1] # the second capture group is number
                identifier = publisher + '-' + number

            if identifier == "":
                identifier = filename
                
            return identifier
        else:  # 提取不含减号-的番号，FANZA CID
            try:
                return str(
                    re.findall(r'(.+?)\.',
                                str(re.search('([^<>/\\\\|:""\\*\\?]+)\\.\\w+$', filename).group()))).strip(
                    "['']").replace('_', '-')
            except:
                return re.search(r'(.+?)\.', filename)[0]
    except Exception as e:
        print('[-]' + str(e))
        return
    except ValueError as e:
        return filename

def get_number_bak(debug,filename: str) -> str:
    # """
    # >>> from number_parser import get_number
    # >>> get_number("/Users/Guest/AV_Data_Capture/snis-829.mp4")
    # 'snis-829'
    # >>> get_number("/Users/Guest/AV_Data_Capture/snis-829-C.mp4")
    # 'snis-829'
    # >>> get_number("C:¥Users¥Guest¥snis-829.mp4")
    # 'snis-829'
    # >>> get_number("C:¥Users¥Guest¥snis-829-C.mp4")
    # 'snis-829'
    # >>> get_number("./snis-829.mp4")
    # 'snis-829'
    # >>> get_number("./snis-829-C.mp4")
    # 'snis-829'
    # >>> get_number(".¥snis-829.mp4")
    # 'snis-829'
    # >>> get_number(".¥snis-829-C.mp4")
    # 'snis-829'
    # >>> get_number("snis-829.mp4")
    # 'snis-829'
    # >>> get_number("snis-829-C.mp4")
    # 'snis-829'
    # """
    filename = os.path.basename(filename)

    if debug == False:
        try:
            if '-' in filename or '_' in filename:  # 普通提取番号 主要处理包含减号-和_的番号
                filename = filename.replace("_", "-")
                filename.strip('22-sht.me').strip('-HD').strip('-hd')
                filename = str(re.sub("\[\d{4}-\d{1,2}-\d{1,2}\] - ", "", filename))  # 去除文件名中时间
                if 'FC2' or 'fc2' in filename:
                    filename = filename.replace('PPV', '').replace('ppv', '').replace('--', '-').replace('_', '-')
                file_number = re.search(r'\w+-\w+', filename, re.A).group()
                return file_number
            else:  # 提取不含减号-的番号，FANZA CID
                try:
                    return str(
                        re.findall(r'(.+?)\.',
                                   str(re.search('([^<>/\\\\|:""\\*\\?]+)\\.\\w+$', filename).group()))).strip(
                        "['']").replace('_', '-')
                except:
                    return re.search(r'(.+?)\.', filename)[0]
        except Exception as e:
            print('[-]' + str(e))
            return
    elif debug == True:
        if '-' in filename or '_' in filename:  # 普通提取番号 主要处理包含减号-和_的番号
            filename = filename.replace("_", "-")
            filename.strip('22-sht.me').strip('-HD').strip('-hd')
            filename = str(re.sub("\[\d{4}-\d{1,2}-\d{1,2}\] - ", "", filename))  # 去除文件名中时间
            if 'FC2' or 'fc2' in filename:
                filename = filename.replace('PPV', '').replace('ppv', '').replace('--', '-').replace('_', '-')
            file_number = re.search(r'\w+-\w+', filename, re.A).group()
            return file_number
        else:  # 提取不含减号-的番号，FANZA CID
            try:
                return str(
                    re.findall(r'(.+?)\.',
                               str(re.search('([^<>/\\\\|:""\\*\\?]+)\\.\\w+$', filename).group()))).strip(
                    "['']").replace('_', '-')
            except:
                return re.search(r'(.+?)\.', filename)[0]


# if __name__ == "__main__":
#     import doctest
#     doctest.testmod(raise_on_error=True)