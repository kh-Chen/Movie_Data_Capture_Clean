import os
import re
import sys
import typing

import logger

G_SPAT = re.compile(
    "^\w+\.(cc|com|net|me|club|jp|tv|xyz|biz|wiki|info|tw|us|de)@|^22-sht\.me|"
    "^(fhd|hd|sd|1080p|720p|4K)(-|_)|"
    "(-|_)(fhd|hd|sd|1080p|720p|4K|x264|x265|uncensored|hack|leak)",
    re.IGNORECASE)

# 按javdb数据源的命名规范提取number
G_TAKE_NUM_RULES = {
    'tokyo.*hot': lambda x: str(re.search(r'(cz|gedo|k|n|red-|se)\d{2,4}', x, re.I).group()),
    'carib': lambda x: str(re.search(r'\d{6}(-|_)\d{3}', x, re.I).group()).replace('_', '-'),
    '1pon|mura|paco': lambda x: str(re.search(r'\d{6}(-|_)\d{3}', x, re.I).group()).replace('-', '_'),
    '10mu': lambda x: str(re.search(r'\d{6}(-|_)\d{2}', x, re.I).group()).replace('-', '_'),
    'x-art': lambda x: str(re.search(r'x-art\.\d{2}\.\d{2}\.\d{2}', x, re.I).group()),
    'xxx-av': lambda x: ''.join(['xxx-av-', re.findall(r'xxx-av[^\d]*(\d{3,5})[^\d]*', x, re.I)[0]]),
    'heydouga': lambda x: 'heydouga-' + '-'.join(re.findall(r'(\d{4})[\-_](\d{3,4})[^\d]*', x, re.I)[0]),
    'heyzo': lambda x: 'HEYZO-' + re.findall(r'heyzo[^\d]*(\d{4})', x, re.I)[0],
    'caribpr': lambda x: str(re.search(r'\d{6}(-|_)\d{3}', x, re.I).group()).replace('_', '-'),
    'fc2': lambda x: "FC2-" + str(re.search(r'(fc2)(-|_){0,1}(ppv){0,1}(-|_){0,1}(\d{7})(?=\D)', x, re.I).group(5)),
}

def get_number(file_path: str) -> str:
    """
    从文件路径中提取番号
    """
    filename = os.path.basename(file_path)
    filename = G_SPAT.sub("", filename)
    try:
        for k, v in G_TAKE_NUM_RULES.items():
            try:
                if re.search(k, filename, re.I):
                    return v(filename)
            except Exception as e:
                logger.error(f"get_number with G_TAKE_NUM_RULES[{k}] from [{filename}] error. [{e}]")
                # print(f"get_number with G_TAKE_NUM_RULES[{k}] from [{filename}] error. [{e}]")
        

        result = re.search(r'([a-zA-Z]{2,6})(-|_{1,})(\d{2,5})',filename)
        if result is None:
            result = re.search(r'([a-zA-Z]{2,6})(-|_{0,1})(\d{2,5})',filename)
        if result is None:
            return None

        return "-".join(result.group(1,3))
    except Exception as e:
        logger.error(f'Number Parser exception: {e} [{file_path}]')
        # print(f'Number Parser exception: {e} [{file_path}]')
        return None


# class Cache_uncensored_conf:
#     prefix = None

#     def is_empty(self):
#         return bool(self.prefix is None)

#     def set(self, v: list):
#         if not v or not len(v) or not len(v[0]):
#             raise ValueError('input prefix list empty or None')
#         s = v[0]
#         if len(v) > 1:
#             for i in v[1:]:
#                 s += f"|{i}.+"
#         self.prefix = re.compile(s, re.I)

#     def check(self, number):
#         if self.prefix is None:
#             raise ValueError('No init re compile')
#         return self.prefix.match(number)


# G_cache_uncensored_conf = Cache_uncensored_conf()


# # ========================================================================是否为无码
# def is_uncensored(number) -> bool:
#     if re.match(
#             r'[\d-]{4,}|\d{6}_\d{2,3}|(cz|gedo|k|n|red-|se)\d{2,4}|heyzo.+|xxx-av-.+|heydouga-.+|x-art\.\d{2}\.\d{2}\.\d{2}',
#             number,
#             re.I
#     ):
#         return True
#     if G_cache_uncensored_conf.is_empty():
#         uncensored_prefix = "PT-,S2M,BT,LAF,SMD,SMBD,SM3D2DBD,SKY-,SKYHD,CWP,CWDV,CWBD,CW3D2DBD,MKD,MKBD,MXBD,MK3D2DBD,MCB3DBD,MCBD,RHJ,MMDV"
#         G_cache_uncensored_conf.set(uncensored_prefix.split(','))
#     return bool(G_cache_uncensored_conf.check(number))


def test():
    #     import doctest
    #     doctest.testmod(raise_on_error=True)
    test_use_cases = (
        "MEYD-594-C.mp4",
        "SSIS-001_C.mp4",
        "SSIS100-C.mp4",
        "SSIS101_C.mp4",
        "ssni984.mp4",
        "ssni666.mp4",
        "SDDE-625_uncensored_C.mp4",
        "SDDE-625_uncensored_leak_C.mp4",
        "SDDE-625_uncensored_leak_C_cd1.mp4",
        "Tokyo Hot n9001 FHD.mp4",  # 无-号，以前无法正确提取
        "TokyoHot-n1287-HD SP2006 .mp4",
        "caribean-020317_001.nfo",  # -号误命名为_号的
        "257138_3xplanet_1Pondo_080521_001.mp4",
        "ADV-R0624-CD3.wmv",  # 多碟影片
        "XXX-AV   22061-CD5.iso",  # 支持片商格式 xxx-av-22061 命名规则来自javdb数据源
        "xxx-av 20589.mp4",
        "Muramura-102114_145-HD.wmv",  # 支持片商格式 102114_145  命名规则来自javdb数据源
        "heydouga-4102-023-CD2.iso",  # 支持片商格式 heydouga-4102-023 命名规则来自javdb数据源
        "HeyDOuGa4236-1048 Ai Qiu - .mp4",  # heydouga-4236-1048 命名规则来自javdb数据源
        "pacopacomama-093021_539-FHD.mkv",  # 支持片商格式 093021_539 命名规则来自javdb数据源
        "sbw99.cc@heyzo_hd_2636_full.mp4",
        "hhd800.com@STARS-566-HD.mp4",
        "jav20s8.com@GIGL-677_4K.mp4",
        "sbw99.cc@iesp-653-4K.mp4",
        "4K-ABP-358_C.mkv",
        "n1012-CD1.wmv",
        "[]n1012-CD2.wmv",
        "rctd-460ch.mp4",  # 除支持-C硬字幕外，新支持ch硬字幕
        "rctd-461CH-CD2.mp4",  # ch后可加CDn
        "rctd-461-Cd3-C.mp4",  # CDn后可加-C
        "rctd-461-C-cD4.mp4",  # cD1 Cd1 cd1 CD1 最终生成.nfo时统一为大写CD1
        "MD-123.ts",
        "MDSR-0001-ep2.ts",
        "MKY-NS-001.mp4",
        "FC2-PPV-1234567.mp4",
        "FC2PPV-1234567.mp4",
        "FC2-1234567.mp4",
        "FC21234567.mp4",
        "FC2-PPV-1234567-1.mp4",
        "FC2-1234567啊啊啊啊.mp4",
    )


    for t in test_use_cases:
        print(t, get_number(t))


