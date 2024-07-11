"""
C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" --profile-directory="Profile 2"  --remote-debugging-port=3556 --force-renderer-accessibility
如上，浏览器要添加--remote-debugging-port=3556
指定端口，这样才能用代码联接
"""

import pychrome
from bs4 import BeautifulSoup
import time
import os



class BrowserAutomation:
    def __init__(self, browser_url):
        """
        初始化BrowserAutomation类，连接到指定的Chrome浏览器实例
        参数:
        browser_url (str): Chrome远程调试URL
        例："http://127.0.0.1:3556"
        """
        self.browser = pychrome.Browser(url=browser_url)
        self.tab = None
        print('浏览器初使化完成')

    def switch_to_tab_with_keyword(self, keyword):
        """
        根据关键字或URL(包含http)切换到包含该关键字的标签页
        参数:
        keyword (str): 标签页标题中的关键字
        返回:
        bool: 如果找到并切换到标签页则返回True，否则返回False
        """
        tabs = self.browser.list_tab()
        find_key = False
        for tab in tabs:
            try:
                tab.start()
                tab.Page.enable()

                # 获取当前标签页的URL或标题
                if 'http' in keyword:
                    result = tab.Runtime.evaluate(expression="window.location.href")
                    # print(result)
                    current_value = result.get('result', {}).get('value', '')
                else:
                    result = tab.Runtime.evaluate(expression="document.title")
                    # print(result)
                    current_value = result.get('result', {}).get('value', '')

                if keyword in current_value:
                    self.tab = tab
                    tab.Page.bringToFront()
                    find_key = True
                    return True

            except Exception as e:
                print(f"Error while processing tab ID {tab.id}: {e}")
                return False
        if not find_key and 'http' in keyword:
            self.new_tab_with_url(keyword)
            return self.switch_to_tab_with_keyword(keyword)
        return False

    # 刷新页面
    def refresh_tab(self):
        """
       刷新页面
        """
        if self.tab:
            self.tab.Page.reload(ignoreCache=True)

    # 激活标签
    def activate_tab(self):
        """
        激活标签
        """
        if self.tab:
            self.tab.Page.bringToFront()

    def click_element(self, element_selector):
        """
        点击指定的元素
        参数:
        element_selector (str): 要点击的元素的CSS选择器
        F12中复制的JS路径
        """
        if not self.tab:
            print("没有网页标签，退出！")
            return None
            # 等待元素加载并可见
        click_script = f"""
            function waitForElement(selector, callback) {{
                var element = document.querySelector(selector);
                if(element) {{
                    callback(element);
                }} else {{
                    setTimeout(function() {{
                        waitForElement(selector, callback);
                    }}, 100);
                }}
            }}
            waitForElement('{element_selector}', function(element) {{
                element.scrollIntoView();
                element.click();
            }});
        """

        # click_script = f"document.querySelector('{element_selector}').click();"
        self.tab.Runtime.evaluate(expression=click_script)

    def get_dingdan(self):
        """
        获取定单信息
        """

        url = "https://qsm.qoo10.jp/GMKT.INC.Gsm.Web/Delivery/DeliveryManagement.aspx"
        # 要点击的元素选择器
        element_selector = "#tab_main_request > a"
        yibanpeisong_BT = "#txt_shipping_type_registered"
        print('开始获取定单信息')
        # 切换到包含关键词的标签页
        url_pd = self.switch_to_tab_with_keyword(url)
        # print(url_pd)
        if url_pd == False:
            self.new_tab_with_url(url)
            return self.get_dingdan()

        time.sleep(1)

        self.click_element(element_selector)
        time.sleep(2)
        self.click_element(yibanpeisong_BT)
        time.sleep(2)
        # 定单表格
        tab_str = '#__grid_goods_grid > div:nth-child(2) > div.objbox > table'
        tab_html = self.get_table_html(tab_str)
        dingdian_data = self.get_tr(tab_html)

        time.sleep(2)
        rujinmaqi_str = '#txt_cnt_awaiting_orders1'
        self.click_element(rujinmaqi_str)
        time.sleep(2)
        # 定单表格
        tab_str = '#__grid_goods_grid > div:nth-child(2) > div.objbox > table'
        tab_html = self.get_table_html(tab_str)
        rujinmaqi_data = self.get_tr(tab_html)
        # print(rujinmaqi_data)
        if rujinmaqi_data:
            for index, item in enumerate(rujinmaqi_data[1::]):
                dingdian_data.append(item)
        # print(dingdian_data)

        # 获取标题行
        tab_str = '#__grid_goods_grid > div:nth-child(2) > div.xhdr > table'
        tab_html = self.get_table_html(tab_str)
        title_data = self.get_tr(tab_html)
        # print(title_data, len(title_data), len(title_data[1]))

        dingdian_data[0] = title_data[1]
        # 根据入金日升序排序
        re_data = self.sort_table_by_date(dingdian_data)
        return re_data

    def down_Qoo10data(self):
        """
        下载Qoo10data
        """
        url = 'https://qsm.qoo10.jp/GMKT.INC.Gsm.Web/Product/ProductListSummary.aspx'
        self.switch_to_tab_with_keyword(url)
        time.sleep(1)
        pd_url = self.open_tab_with_url(url)
        if pd_url == False:
            self.new_tab_with_url(url)
            return self.down_Qoo10data()
        tab_data = []
        for i in range(4):
            tab_str = '#__grid_DataDwonload_Grid > div.objbox > table'
            tab_html = self.get_table_html(tab_str)

            tab_data = self.get_tr(tab_html)
            print(tab_data)
            if tab_data:
                break
        if tab_data:
            filename = tab_data[1][3]
            if filename == "":
                print("Qoo10data数据没有准备好")
                return None

            # 判断文件是否以下载
            path = "D:\\Users\\Downloads\\"
            if os.path.isfile(path + filename):
                print('文件以下载，不在重复下载！')
                return filename

            time.sleep(1)
            # 下载第一行
            bt_rom1 = '#__grid_DataDwonload_Grid > div.xhdr'
            self.scroll_to_element(bt_rom1)
            time.sleep(2)
            bt_str = '#__grid_DataDwonload_Grid > div.objbox > table > tbody > tr:nth-child(2) > td:nth-child(4) > a'

            self.click_element(bt_str)
            return filename
        else:
            print('Qoo10data下载失败')
            return None

    def get_quxiaodingdan(self):
        """
        获取キャンセル的定单
        """
        url = 'https://qsm.qoo10.jp/GMKT.INC.Gsm.Web/Claim/ClaimManagement.aspx'
        self.switch_to_tab_with_keyword(url)
        bt_str = '#ctl00_ctl00_MainMaster_MainHolder_cancel_end'
        self.click_element(bt_str)
        time.sleep(3)

        tab_str = '#__grid_ClaimGrid > div.objbox'
        tab_html = self.get_table_html(tab_str)
        data = self.get_tr(tab_html)
        # print(data)
        data_list = []
        if data:
            for item in data:
                if item and '販売者の責任' in item[3]:
                    data_list.append(item)

        if data_list:
            title_str = '#__grid_ClaimGrid > div.xhdr'
            title_html = self.get_table_html(title_str)
            title_data = self.get_tr(title_html)
            # print(title_data)
            data_list.insert(0, title_data[1])
        # print(data_list)
        return data_list

    def get_element_text(self, element_selector):
        """
        获取指定元素的文本内容
        参数:
        element_selector (str): 要获取文本内容的元素的CSS选择器
        返回:
        str: 元素的文本内容
        """
        get_text_script = f"""
        (function() {{
            var element = document.querySelector('{element_selector}');
            if (element) {{
                return element.textContent;
            }} else {{
                return "Element not found";
            }}
        }})();
        """
        result = self.tab.Runtime.evaluate(expression=get_text_script)
        if 'result' in result and 'value' in result['result']:
            return result['result']['value']
        else:
            return "Error: Unable to retrieve element text content."
    def sort_table_by_date(self, data):
        """
         根据指定列标题排序表格数据
         参数:
         data (list): 包含表格数据的二维数组
         column_title (str): 要排序的列标题
         返回:
         list: 按指定列标题排序后的表格数据
         """
        # 找到指定列标题在标题行的索引
        title_row = data[0]
        column_title = '入金日'
        column_index = title_row.index(column_title)

        # 跳过标题行，对数据行按指定列进行排序
        sorted_data = sorted(data[1:], key=lambda row: row[column_index])

        # 将标题行添加回排序后的数据
        return [title_row] + sorted_data

    def get_table_html(self, selector):
        """
        获取指定元素的HTML内容
        参数:
        selector (str): 要获取HTML内容的元素的CSS选择器
        返回:
        str: 元素的HTML内容
        """
        get_table_script = f"""
        (function() {{
            var table = document.querySelector('{selector}'); // 替换成你需要获取的表格的选择器
            if (table) {{
                return table.outerHTML;
            }} else {{
                return "Table not found";
            }}
        }})();
        """
        result = self.tab.Runtime.evaluate(expression=get_table_script)
        # print(result)
        if 'result' in result and 'value' in result['result']:
            return result['result']['value']
        else:
            return "Error: Unable to retrieve table HTML content."

    def get_table_select(self, tab_html):
        """
        解析HTML表格，获取img标签的src属性中的文件名和表格数据
        参数:
        tab_html (str): 包含HTML表格的字符串
        返回:
        list: 包含表格数据的列表，每行数据是一个子列表，第一个元素是img标签的src文件名
        """
        soup = BeautifulSoup(tab_html, 'html.parser')
        data = []
        for tr in soup.find_all('tr'):
            row = []
            for index, td in enumerate(tr.find_all('td')):
                if index == 0:
                    # 找到 img 标签
                    img_tag = td.find('img')
                    if img_tag:
                        # 获取 img 标签的 src 属性值
                        title_value = img_tag.get('src', '')  # 获取 img 标签的 src 属性值
                        # print(title_value)
                        if 'item_chk1.gif' in title_value:
                            row.append('OK')
                        else:
                            row.append('')
                else:
                    row.append(td.text.strip())
            data.append(row)
        return data

    def get_page_html(self):
        """
        获取当前标签页的HTML内容
        返回:
        str: 当前标签页的HTML内容
        """
        get_page_script = "document.documentElement.outerHTML"
        result = self.tab.Runtime.evaluate(expression=get_page_script)
        if 'result' in result and 'value' in result['result']:
            return result['result']['value']
        else:
            return "Error: Unable to retrieve page HTML content."

    def get_tr(self, htmlcode):
        """
        解析HTML，获取表格中的所有tr和td元素，生成二维数组
        参数:
        htmlcode (str): 包含HTML表格的字符串
        返回:
        list: 包含表格数据的二维数组
        """
        soup = BeautifulSoup(htmlcode, 'html.parser')
        data = []
        for tr in soup.find_all('tr'):
            row = []
            for td in tr.find_all('td'):
                row.append(td.text.strip())
            data.append(row)
        return data

    def new_tab_with_url(self, url):
        """
        新建标签页并打开指定的URL
        参数:
        url (str): 要打开的URL
        """
        self.tab = self.browser.new_tab()
        self.tab.start()
        self.tab.Page.enable()

        # 用于事件触发结果的标志
        self.page_loaded = False

        # 注册页面加载完成事件回调
        def on_load_event_fired(**kwargs):
            print("Page load event fired.")
            self.page_loaded = True
            # self.tab.stop()  # 停止事件监听
            return True

        self.tab.Page.loadEventFired = on_load_event_fired

        # 导航到指定URL
        self.tab.Page.navigate(url=url)

        # 等待事件触发
        try:
            self.tab.wait(5)  # 最多等待10秒
        except pychrome.TimeoutException:
            print("Page load timed out.")
            return False

        return self.page_loaded

    def open_tab_with_url(self, url):
        """
        在当前标签页加载指定的URL，并监视页面加载完成
        参数:
        url (str): 要加载的URL
        返回:
        bool: 页面是否成功加载完成
        """
        if not self.tab:
            print("No tab available.")
            return False

        # 重置页面加载完成的标志
        self.page_loaded = False

        # 注册页面加载完成事件回调
        def on_load_event_fired(**kwargs):
            print("Page load event fired.")
            self.page_loaded = True
            # self.tab.stop()  # 停止事件监听
            return True

        self.tab.Page.loadEventFired = on_load_event_fired

        # 导航到指定URL
        self.tab.Page.navigate(url=url)

        # 等待事件触发
        try:
            self.tab.wait(5)  # 最多等待10秒
        except pychrome.TimeoutException:
            print("Page load timed out.")
            return False

        return self.page_loaded

    def get_element_coordinates(self, element_selector):
        """
        获取元素的坐标
        """
        get_coordinates_script = f"""
                (function() {{
                    var element = document.querySelector('{element_selector}');
                    if (element) {{
                        var rect = element.getBoundingClientRect();
                        return {{
                            x: rect.left + (rect.width / 2),
                            y: rect.top + (rect.height / 2)
                        }};
                    }}
                    return null;
                }})();
                """
        result = self.tab.Runtime.evaluate(expression=get_coordinates_script)
        print(result)
        if 'result' in result and 'objectId' in result['result']:
            object_id = result['result']['objectId']
            properties = self.tab.Runtime.getProperties(objectId=object_id)
            coordinates = {}
            for prop in properties['result']:
                if prop['name'] == 'x' or prop['name'] == 'y':
                    coordinates[prop['name']] = prop['value']['value']
            print(f'得到坐标返回值 ：{coordinates}')
            return coordinates
        return None

    def click_element_by_coordinates(self, x, y):
        """
        在指定的坐标 (x, y) 处点击元素
        """
        self.tab.Input.dispatchMouseEvent(type='mouseMoved', x=x, y=y)
        self.tab.Input.dispatchMouseEvent(type='mousePressed', x=x, y=y, button='left', clickCount=1)
        self.tab.Input.dispatchMouseEvent(type='mouseReleased', x=x, y=y, button='left', clickCount=1)

    def close_tab_with_keyword(self, keyword):
        """
        根据关键字关闭包含该关键字的标签页
        参数:
        keyword (str): 标签页标题中的关键字
        返回:
        bool: 如果找到并关闭标签页则返回True，否则返回None
        """
        tabs = self.browser.list_tab()
        tab_PD = False
        print(f'开始查找标签页:{keyword},{tabs}')
        for tab in tabs:
            tab.start()
            tab.Page.enable()
            result = tab.Runtime.evaluate(expression="document.title")
            title = result['result']['value']
            print(title)
            if keyword in title:
                self.browser.close_tab(tab.id)
                tab_PD = True
                return True
        if not tab_PD:
            print('没有找到标签页')
            return None

    def scroll_to_element(self, css_selector):
        """
        滚动页面到指定元素可见
        """
        js_script = f"""
        var element = document.querySelector('{css_selector}');
        if (element) {{
            element.scrollIntoView({{
                behavior: 'smooth',
                block: 'center',
                inline: 'center'
            }});
        }}
        """
        self.execute_js_in_tab(js_script)

    def execute_js_in_tab(self, js_script):
        """
        在当前标签页中执行指定的JavaScript代码
        参数:
        js_script (str): 要执行的JavaScript代码
        """
        if self.tab:
            data = self.tab.Runtime.evaluate(expression=js_script)
            return data

    def close_tab(self):
        """
        关闭标签
        """
        if self.tab:
            self.browser.close_tab(self.tab.id)
            self.set_current_tab()

    def set_current_tab(self):
        """
        获取当前激活的标签页，并更新self.tab
        """
        tabs = self.browser.list_tab()
        if tabs:
            self.tab = tabs[0]
            self.tab.start()
            self.tab.Page.enable()
            result = self.tab.Runtime.evaluate(expression="document.title")
            title = result['result']['value']
            print(f"Current Tab ID: {self.tab.id}, Title: {title}")
            return self.tab
        else:
            print("No active tabs found.")
            return None

    def stop_browser(self):
        """
        关闭浏览器
        """
        self.browser.close()

# 示例用法
# if __name__ == "__main__":
#     chrom = BrowserAutomation("http://127.0.0.1:3556")
#     data = chrom.down_Qoo10data()
#     print(data)
#     print('运行完成')
