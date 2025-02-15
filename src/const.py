#中国省级行政区：23个省（包括台湾省）、5个自治区、4个直辖市、2个特别行政区（香港，澳门），合计34个省级行政区。
list_provincial_level=['Inner Mongolia',
 'Heilongjiang',
 'Jilin',
 'Liaoning',
 'Gansu',
 'Ningxia',
 'Qinghai',
 'Shaanxi',
 'Xinjiang',
 'Beijing',
 'Hebei',
 'Shandong',
 'Shanxi',
 'Tianjin',
 'Chongqing',
 'Guizhou',
 'Sichuan',
 'Tibet',
 'Guangdong',
 'Guangxi',
 'Hainan',
 'Yunnan',
 'Henan',
 'Hubei',
 'Hunan',
 'Jiangxi',
 'Anhui',
 'Fujian',
 'Jiangsu',
 'Shanghai',
 'Zhejiang',
 'Taiwan',
 'Hong Kong',
 'Macao']
province_dict={'北京': 'Beijing',
 '天津': 'Tianjin',
 '河北': 'Hebei',
 '山西': 'Shanxi',
 '内蒙古': 'Inner Mongolia',
 '辽宁': 'Liaoning',
 '吉林': 'Jilin',
 '黑龙江': 'Heilongjiang',
 '上海': 'Shanghai',
 '江苏': 'Jiangsu',
 '浙江': 'Zhejiang',
 '安徽': 'Anhui',
 '福建': 'Fujian',
 '江西': 'Jiangxi',
 '山东': 'Shandong',
 '河南': 'Henan',
 '湖北': 'Hubei',
 '湖南': 'Hunan',
 '广东': 'Guangdong',
 '广西': 'Guangxi',
 '海南': 'Hainan',
 '重庆': 'Chongqing',
 '四川': 'Sichuan',
 '贵州': 'Guizhou',
 '云南': 'Yunnan',
 '西藏': 'Tibet',
 '陕西': 'Shaanxi',
 '甘肃': 'Gansu',
 '青海': 'Qinghai',
 '宁夏': 'Ningxia',
 '新疆': 'Xinjiang',
 '台湾': 'Taiwan',
 '香港': 'Hong Kong',
 '澳门': 'Macao'}

region_dict={'NC': ['Beijing','Tianjin','Hebei','Shanxi','Inner Mongolia'],'NEC': ['Liaoning','Jilin','Heilongjiang'], 'CC':['Henan','Hunan','Hubei'],'EC': ['Shanghai','Jiangsu','Zhejiang','Anhui','Fujian','Jiangxi','Shandong','Taiwan'],'SC': ['Guangdong','Guangxi','Hainan','Hong Kong','Macao'],'NW': ['Shaanxi','Gansu','Qinghai','Ningxia','Xinjiang'],'SWC': ['Chongqing','Sichuan','Guizhou','Yunnan','Tibet']}

alpha=5.0 #制氢效率
PHpipe_transcost = 1.4*1e-3  #单位：亿/万吨/km 纯氢管道输氢成本为百公里1.3元/公斤-1.5元/公斤， 来源：https://h2.in-en.com/html/h2-2426505.shtml；欧洲氢能骨干报告：1.18 
PHpipe_capacity_Inner_Beijing=50  # 单位：万吨 https://www.gov.cn/yaowen/2023-04/10/content_5750685.htm
PHpipe_buildcost_Inner_Beijing=600*480*1e-4
 #单位：亿，500-600万元/km,https://h2.in-en.com/html/h2-2426505.shtml  内蒙古到北京480km, 600万/km,管道总价为600*480万元，别的成本因子是相对于这个的

NGpipe_seperate_cost=     0.3826*1e-1/0.43     #单位：亿元/万吨   0.3826元/m3（0.55Mpa,300K时氢气密度0.43kg/m3）
NGpipe_convcost_20=   40*1e-4        #单位：亿元/km  200的1/5
NGpipe_convcost_100=    200*1e-4      #单位：亿元/km   0.5*(3/11+4/15)=0.27  0.5*（0.27+0.4）=0.33 0.33*600=198  https://www.thepaper.cn/newsDetail_forward_13640924，改造现有油气管道为氢气管道带来的成本降幅占比达到 60% 左右。《长距离氢气管道运输的技术经济分析》