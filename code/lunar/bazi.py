from lunar_python import Solar, Lunar

def calculate_bazi(year, month, day, hour, minute, gender):
    """
    八字排盘核心函数
    :param year: 年 (阳历)
    :param month: 月
    :param day: 日
    :param hour: 时
    :param minute: 分
    :param gender: 性别 (1男, 0女) - 影响大运顺逆
    :return: 包含排盘信息的字典
    """
    
    # 1. 初始化阳历对象
    solar = Solar.fromYmdHms(year, month, day, hour, minute, 0)
    
    # 2. 转为农历对象
    lunar = solar.getLunar()
    
    # 3. 获取八字对象 (核心)
    bazi = lunar.getEightChar()
    
    # --- A. 基础四柱 (干支) ---
    # 这里的 getYear() 返回的是干支字符串，如 "甲子"
    pillars = {
        "年柱": bazi.getYear(), 
        "月柱": bazi.getMonth(),
        "日柱": bazi.getDay(),
        "时柱": bazi.getTime()
    }
    
    # --- B. 五行分析 (金木水火土) ---
    # 获取每柱的五行（天干地支分开）
    wuxing_detail = {
        "年柱五行": bazi.getYearWuXing(),
        "月柱五行": bazi.getMonthWuXing(),
        "日柱五行": bazi.getDayWuXing(),
        "时柱五行": bazi.getTimeWuXing()
    }

    # 组合成列表形式
    wuxing_list = [
        bazi.getYearWuXing(),
        bazi.getMonthWuXing(),
        bazi.getDayWuXing(),
        bazi.getTimeWuXing()
    ]

    # 统计五行个数 (看缺什么)
    wuxing_count = {"金": 0, "木": 0, "水": 0, "火": 0, "土": 0}
    all_wuxing_str = "".join(wuxing_list)
    for w in wuxing_count:
        wuxing_count[w] = all_wuxing_str.count(w)

    # --- C. 十神 (用于分析性格/事业) ---
    # 十神是相对于日干(日主)来说的
    ten_gods = {
        "年干十神": bazi.getYearShiShenGan(),  # 祖业
        "月干十神": bazi.getMonthShiShenGan(),  # 父辈/兄弟
        "日干十神": bazi.getDayShiShenGan(),    # 自己（通常是空或日主）
        "时干十神": bazi.getTimeShiShenGan(),   # 子女/晚年
        "年支十神": bazi.getYearShiShenZhi(),   # 年支藏干十神（列表）
        "月支十神": bazi.getMonthShiShenZhi(),  # 月支藏干十神（列表）
        "日支十神": bazi.getDayShiShenZhi(),    # 配偶宫（列表）
        "时支十神": bazi.getTimeShiShenZhi()    # 时支藏干十神（列表）
    }

    # --- D. 纳音 (如：海中金) ---
    nayin = {
        "年柱纳音": bazi.getYearNaYin(),
        "月柱纳音": bazi.getMonthNaYin(),
        "日柱纳音": bazi.getDayNaYin(),
        "时柱纳音": bazi.getTimeNaYin()
    }
    
    # --- E. 大运 (未来运势) ---
    # getYun(gender) 1为男，0为女，决定大运顺排还是逆排
    yun = bazi.getYun(gender)

    # 起运信息（出生后多久起运）
    qiyun_info = {
        "起运年数": yun.getStartYear(),
        "起运月数": yun.getStartMonth(),
        "起运天数": yun.getStartDay(),
        "起运描述": f"出生{yun.getStartYear()}年{yun.getStartMonth()}个月{yun.getStartDay()}天后起运"
    }

    # 获取大运列表（通常取前 8 步大运）
    dayun_list = yun.getDaYun()
    dayun_data = []
    for i, dy in enumerate(dayun_list[:8]):  # 取前8步大运
        try:
            gan_zhi = dy.getGanZhi()
        except:
            gan_zhi = "起运前"  # 第0步大运可能没有干支信息

        dayun_data.append({
            "序号": i,
            "大运干支": gan_zhi,
            "起运年份": dy.getStartYear(),
            "起运年龄": dy.getStartAge(),
            "结束年龄": dy.getEndAge()
            # "十神": dy.getShiShen()  # DaYun 对象没有 getShiShen() 方法
        })

    # --- F. 流年 (某一步大运的流年) ---
    # 示例：获取第1步大运的流年（可根据需要调整）
    liunian_data = []
    if len(dayun_list) > 1:
        liunian_list = dayun_list[1].getLiuNian()  # 第1步大运的流年
        for i, ln in enumerate(liunian_list):
            liunian_data.append({
                "序号": i,
                "年份": ln.getYear(),
                "年龄": ln.getAge(),
                "干支": ln.getGanZhi()
                # "十神": ln.getShiShen()  # LiuNian 对象没有 getShiShen() 方法
            })

    # --- 组装返回数据 ---
    result = {
        "user_info": {
            "阳历": f"{year}-{month}-{day} {hour}:{minute}",
            "农历": f"{lunar.getYearInChinese()}年 {lunar.getMonthInChinese()}月 {lunar.getDayInChinese()}",
            "生肖": lunar.getYearShengXiao(),
            "性别": "男" if gender == 1 else "女"
        },
        "bazi": pillars,  # 四柱干支
        "day_master": bazi.getDayGan(),  # 日主 (你是谁，例如：甲木人)
        "wuxing": {
            "detail": wuxing_detail,  # 每柱的五行详情
            "list": wuxing_list,  # 八字五行列表
            "counts": wuxing_count  # 五行统计
        },
        "nayin": nayin,  # 纳音
        "shi_shen": ten_gods,  # 十神详情
        "qi_yun": qiyun_info,  # 起运信息
        "da_yun": dayun_data,  # 大运
        "liu_nian": liunian_data  # 流年（第1步大运的流年）
    }

    return result

# --- 格式化输出函数 ---
def print_bazi_result(data):
    """格式化打印八字排盘结果"""
    print("\n" + "="*60)
    print("八字排盘结果".center(56))
    print("="*60)

    # 用户信息
    print("\n【基本信息】")
    for key, value in data["user_info"].items():
        print(f"  {key}: {value}")

    # 四柱八字
    print("\n【四柱八字】")
    print(f"  日主: {data['day_master']}")
    for key, value in data["bazi"].items():
        print(f"  {key}: {value}")

    # 五行
    print("\n【五行分析】")
    for key, value in data["wuxing"]["detail"].items():
        print(f"  {key}: {value}")
    print(f"  五行统计: {data['wuxing']['counts']}")

    # 纳音
    print("\n【纳音】")
    for key, value in data["nayin"].items():
        print(f"  {key}: {value}")

    # 十神
    print("\n【十神】")
    for key, value in data["shi_shen"].items():
        if isinstance(value, list):
            print(f"  {key}: {' '.join(value)}")
        else:
            print(f"  {key}: {value}")

    # 起运
    print("\n【起运】")
    print(f"  {data['qi_yun']['起运描述']}")

    # 大运
    print("\n【大运】")
    for dy in data["da_yun"]:
        print(f"  第{dy['序号']}步: {dy['大运干支']} | {dy['起运年龄']}-{dy['结束年龄']}岁 | {dy['起运年份']}年")

    # 流年
    if data["liu_nian"]:
        print("\n【流年】(第1步大运)")
        for ln in data["liu_nian"][:10]:  # 只显示前10个流年
            print(f"  {ln['年份']}年 | {ln['年龄']}岁 | {ln['干支']}")
        if len(data["liu_nian"]) > 10:
            print(f"  ... 共{len(data['liu_nian'])}个流年")

    print("\n" + "="*60 + "\n")


# --- 测试运行 ---
if __name__ == "__main__":
    # 假设：男，1995年10月5日 14点30分
    data = calculate_bazi(1987, 3, 28, 11, 00, 1)

    # 格式化输出
    print_bazi_result(data)

    # 如果需要 JSON 格式，取消下面的注释
    # import json
    # print(json.dumps(data, indent=2, ensure_ascii=False))