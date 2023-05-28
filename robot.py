import werobot
import openai

import time
import threading


print('load robot.py')

robot = werobot.WeRoBot(
    token='test_token',# 对应公众号的token设置
#     encoding_aes_key='xxxxxx',# 明文传输不需要填写
#     app_id='xxxxx'#明文传输不需要填写
)


@robot.subscribe
def subreply(message):
    text = '''
    欢迎来到小俊的秘密基地

    目前正在开发自动回复相关功能

    1，该功能还处于测试阶段，可能会遇到异常情况。

    2，遇到较复杂问题时，因为gpt生成回答速度较慢，可能会出现异常报错；目前只能回答简答问题。
    '''
    return text


@robot.handler
def handel_reply(message):
    return '该功能还在测试阶段...'

@robot.text
def text_reply(message):
    user_id = message.source
    
    return str(werobot.client.get_user_info(user_id))
#     return reply_gpt1(message)

user_question_answer = {}
print('client',robot.client)


class MyThread(threading.Thread):
    def __init__(self, target, args=()):
        """
            因为threading类没有返回值,因此在此处重新定义MyThread类,使线程拥有返回值
        """
        super(MyThread, self).__init__()
        self.func = target
        self.args = args

    def run(self):
        # 接受返回值
        self.result = self.func(*self.args)

    def get_result(self):
        # 线程不结束,返回值为None
        try:
            return self.result
        except Exception:
            return None

def limit_decor(timeout, granularity):
    """
        timeout 最大允许执行时长, 单位:秒
        granularity 轮询间隔，间隔越短结果越精确同时cpu负载越高
        return 未超时返回被装饰函数返回值,超时则返回 None
    """
    def functions(func):
        def run(*args):
            thre_func = MyThread(target=func, args=args)
            thre_func.setDaemon(True)
            thre_func.start()
            sleep_num = int(timeout//granularity)
            for i in range(0, sleep_num):
                infor = thre_func.get_result()
                if infor:
                    return infor
                else:
                    time.sleep(granularity)
            return '获取回复时间可能较长，请稍后重试'
        return run
    return functions



def reply_gpt1(message):
    prompt = message.content
    print(prompt)
    source = message.source
    print(source)

    # check user
    # True will check; False no check
    if False or source!='o6E-96RZgdjeZE3Kybd6ToqpQ8l4':
        return 'no permission: '+ source

    # ask gpt 1
    conversation_list = []
    conversation_list.append({"role":"user","content":prompt})
    return ask_gpt(conversation_list, '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')

@limit_decor(5,0.1)
def ask_gpt(conversation_list, api_keys):
    openai.api_key = api_keys
    try:
        response = openai.ChatCompletion.create(model="gpt-3.5-turbo",messages=conversation_list)
        # response = openai.ChatCompletion.create(model='davinci',messages=conversation_list)
        answer = response.choices[0].message['content']
        conversation_list.append({"role":"assistant","content":answer})
        print(answer)
    except Exception as err:
        answer = str(err) 
        print(err)
    return answer



  
  
  
