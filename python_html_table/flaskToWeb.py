from flask import Flask, render_template, jsonify, request
from datetime import datetime
import pandas as pd

print('初使化中……')
app = Flask(__name__)

# 初始化一个空列表
update_list = []
dongzuo = ''
nowtime = ''
filepath = r"D:\Users\Downloads\Qoo10_ItemInfo_20240429152927_1 (1).xlsx"
Qoo10data = pd.read_excel(filepath)

# 用数据的前4行做为表头
newdata = Qoo10data.head(3)
# print(Qoo10data)

print('初使化完成')


@app.route('/')
def index():
    # 在渲染模板时传递 update_list 数据到模板中
    global dongzuo, nowtime
    # nowtime = datetime.now()
    # nowtime = nowtime.strftime('%Y-%m-%d %H:%M:%S')

    return render_template('index.html', update_list=update_list, nowtime=nowtime, dongzuo=dongzuo)


@app.route('/update_data', methods=['POST'])
def update_data():
    # 在这里通过请求的数据更新 update_list
    # 这里假设请求数据是一个包含字符串的列表
    global update_list, dongzuo, nowtime
    data = request.json
    print(f'接收到的内容={len(data)}，{data}')

    # 将新数据追加到 update_list
    if len(data) <= 1:
        return jsonify({'message': '数据格式不正确'})

    update_list.append(data)
    print(f'上传的数据={update_list}')

    # 对 update_list 按第5列降序排列
    update_list = sorted(update_list, key=lambda x: int(x[5]), reverse=True)
    # 返回更新后的数据，这里使用 jsonify 将列表转换为 JSON 格式
    # return jsonify({'message': '数据已更新', 'data': data})

    nowtime = datetime.now()
    nowtime = nowtime.strftime('%Y-%m-%d %H:%M:%S')
    dongzuo = '添加数据'
    print(f'上传的数据={update_list}，nowtime = {nowtime},dongzuo ={dongzuo}')

    return render_template('index.html', update_list=update_list, nowtime=nowtime, dongzuo=dongzuo)


@app.route('/save_data', methods=['POST'])
def save_data():
    global newdata
    data = request.json
    print('保存数据 ', data)
    # 在这里处理接收到的数据，例如保存到数据库中
    # 假设 data 是一个列表，每个元素为一个列表，包含番号和改后价格

    # 如果 data 是一个空列表，则不执行后续操作
    if not data:
        return jsonify({'message': '没有要保存的数据'})

    for item in data:
        number = item[2]  # 番号
        data_DF = search_banhao(number,item[10])
        newdata = newdata.append(data_DF, ignore_index=True)
        # 保存新表为 new.xlsx，并保留表头，指定编码格式为 ANSI
    newdata.to_excel(r"D:\Users\Downloads\new.xlsx", index=False, header=True, encoding='ANSI')
    return jsonify({'message': '保存成功'})


# 使用 query 方法进行筛选
def search_banhao(banhao,jiage):
    global Qoo10data
    print('开始查打番号',banhao)
    index_to_replace = Qoo10data.query(f"item_number == '{banhao}'").index

    # 如果找到了匹配的行，则替换 'price_yen' 列的值为数据中的改后价格
    if not index_to_replace.empty:
        index = index_to_replace[0]
        Qoo10data.loc[index, 'price_yen'] = jiage  # 使用数据中的改后价格替换 'price_yen' 列的值
        # print(Qoo10data.iloc[index])
        # 返回修改后的行数据
        # newdata = newdata.append(Qoo10data.iloc[index], ignore_index=True)
        return Qoo10data.iloc[index]


@app.route('/clear_list', methods=['POST'])
def clear_list():
    global update_list, dongzuo
    update_list = []  # 清空列表
    print(f'update_list已清空 {update_list}')
    dongzuo = '添加数据'
    return render_template('index.html', update_list=update_list, dongzuo=dongzuo)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
