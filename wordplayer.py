import requests
import time
import random
import re
import hashlib
import os
import sys
import json
import webbrowser
from tkinter import *
from tkinter import messagebox
from tkinter import filedialog
from tkinter import font


class WordPlayerUI:
    def __init__(self):
        self.user = "Anonymous"
        self.root = Tk()
        self.root.minsize(820, 500)
        self.root.title('WordPlayer')
        self.ft = lambda x=15: font.Font(font=('Microsoft YaHei', x, 'normal'))
        # 以下菜单部分分为  出题词库、题目形式、附加功能、其他信息
        m = Menu(self.root)
        self.root.config(menu=m)
        m1 = Menu(m)  # 菜单一
        m.add_cascade(label="词库", menu=m1)
        m1.add_radiobutton(label="四级", command=lambda: self.GetFiles("CET4.txt"))
        m1.add_radiobutton(label="六级", command=lambda: self.GetFiles("CET6.txt"))
        m1.add_radiobutton(label="其它", command=lambda: self.GetFiles())
        m2 = Menu(m)  # 菜单二
        m.add_cascade(label="形式", menu=m2)
        m2.add_radiobutton(label="填空题", command=self.TianKongTi)
        m21 = Menu(m2)
        m2.add_cascade(label='选择题', menu=m21)
        m21.add_radiobutton(label='英-->汉', command=lambda: self.XuanZeTi(1))
        m21.add_radiobutton(label='汉-->英', command=lambda: self.XuanZeTi(0))
        m3 = Menu(m)  # 菜单三
        m.add_cascade(label='功能', menu=m3)
        m3.add_command(label='增词', command=self.AddWord)
        m3.add_command(label='查词', command=self.SearchWord)
        m3.add_command(label='批量查单词', command=self.ProcessWord)
        m31 = Menu(m3)
        m3.add_cascade(label='分析', menu=m31)
        m31.add_command(label='四级词汇', command=lambda: self.AnalyseArticle("CET4.txt"))
        m31.add_command(label='六级词汇', command=lambda: self.AnalyseArticle("CET6.txt"))
        m4 = Menu(m)  # 菜单四
        m.add_cascade(label="帮助", menu=m4)
        m4.add_command(label='关于', command=self.About)
        m41 = Menu(m4)
        m4.add_cascade(label="用户", menu=m41)
        m41.add_command(label="当前用户", command=self.UserInfo)
        m41.add_command(label="登录", command=self.LoginOrRegister)
        m41.add_command(label="注册", command=self.LoginOrRegister)
        m4.add_command(label='退出', command=self.QuitMe)
        # 下面的frame用来输出用户答题的判断结果
        Frame(self.root, height=125, width=600, bd=4, bg='DarkGray').place(x=0, y=380)
        # 下面的构件主要是 错词展示栏(mis_words)和当前时间栏(timebar)
        self.mis_count = 0  # 错题数量
        self.ques_count = 0  # 总题目数
        self.mis_bar = Frame(self.root, height=500, width=200, bd=4, bg='DimGray')
        self.mis_bar.place(x=600, y=0)
        Label(self.mis_bar, text='   <错词展示栏>   0|0', font=self.ft(13), fg='yellow', bg='DimGray').place(x=0, y=0)
        self.mis_words = Listbox(self.mis_bar, height=480, width=300, fg='red', bg='SkyBlue')
        for i in range(700):
            self.mis_words.insert(1, ' ')
        self.sl = Scrollbar(self.root)
        self.sl.pack(side=RIGHT, fill=Y)
        self.mis_words['yscrollcommand'] = self.sl.set
        self.sl['command'] = self.mis_words.yview
        self.mis_words.place(x=0, y=30)
        # 时间栏
        self.timebar = Label(self.mis_bar, text="", height=2, width=28, bg='#383838', fg='white')
        self.timebar.place(x=0, y=460)
        # 本地词典
        self.local_dict = self.LoadLocalDict()
        self.UpdateClock()
        self.root.mainloop()
    
    def LoadLocalDict(self):
        """加载本地词典"""
        with open(os.path.join(lexicon_path, 'LocalDict.json'), encoding="utf-8") as f:
            local_dict = json.load(f)
        return local_dict
    
    def UpdateClock(self):
        """更新时间栏"""
        now = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        self.timebar.configure(text=now)
        self.root.after(1000, self.UpdateClock)
    
    def GetFiles(self, fname=None):
        """打开词库文件，读取所有行(每行只有一个单词及其翻译)"""
        if fname:
            fname = os.path.join(lexicon_path, fname)
        else:
            fname = filedialog.askopenfilename(filetypes=[("all files", "*")], initialdir='./Lexicons')
            # 未选择文件
            if not fname:
                messagebox.showwarning('Warning', "未选择文件!")
                return
        
        try:
            with open(fname, encoding='utf-8') as f:
                self.lines = f.readlines()
        except:
            messagebox.showerror('Error', f'打开文件失败\n{sys.exc_info()[1]}')
            return
    
    def GetWords(self):
        """从之前的列表中选单词作为出题单词"""
        self.aLine = self.word = self.expre = self.word1 = self.word2 = self.word3 = self.expre1 = self.expre2 = self.expre3 = ""
        while '' in [self.aLine, self.word, self.expre, self.word1, self.word2,
                     self.word3, self.expre1, self.expre2, self.expre3]:  # 防止词库文件有有空行
            try:
                self.aLine = self.lines[random.randint(1, len(self.lines))]
                self.word = self.aLine.split()[0].strip()
                self.expre = self.aLine.split()[1].strip()
                self.word1 = self.lines[random.randint(1, len(self.lines))].split()[0].strip()
                self.word2 = self.lines[random.randint(1, len(self.lines))].split()[0].strip()
                self.word3 = self.lines[random.randint(1, len(self.lines))].split()[0].strip()
                self.expre1 = self.lines[random.randint(1, len(self.lines))].split()[1].strip()
                self.expre2 = self.lines[random.randint(1, len(self.lines))].split()[1].strip()
                self.expre3 = self.lines[random.randint(1, len(self.lines))].split()[1].strip()
            except:
                return None  # 可表明用户没有选词库
        return True
    
    def TianKongTi(self):
        if not self.GetWords():  # 防止用户未选词库就点击题型
            messagebox.showerror(message='请先选择词库！')
            return
        
        # 出题
        def ques():
            global v
            self.GetWords()
            f1 = Frame(frame, bd=4, relief="groove", height=100, width=100)
            f1.place(x=150, y=100)
            Label(f1, text=self.expre, height=3, width=25, font=self.ft()).grid()
            v = StringVar()
            e = Entry(f1, width=25, bd=2, textvariable=v)
            e.bind('<Return>', lambda x: judge())
            e.grid()
            e.focus_set()
            Label(f1, text=' ').grid()
        
        # 判断
        def judge():
            f1 = Frame(self.root, height=125, width=600, bd=4, bg='DarkGray')
            f1.place(x=0, y=380)
            
            f2 = Frame(f1, relief="groove", height=100, width=100)
            f2.place(x=180, y=0)
            if v.get() == '' or v.get().strip().lower() != self.word:  # 答错则保存到错词本
                with open(os.path.join(users_data_path, self.user, f'{self.user}_mis_words.txt'), 'a+',
                          encoding='utf-8') as f:
                    item = f'{self.word}    {self.expre}\n'
                    f.write(item)
                wrong_ans = Label(f2, text=f'回答错误!\n正确答案是 {self.word}\n已为您添加至错词本！', width=25, font=self.ft())
                wrong_ans.grid()
                self.mis_words.insert(0, item)  # 答错的词显示在"错词展示栏"界面
                self.mis_count += 1
            else:
                Label(f2, text='回答正确！', width=25, font=1).grid()
            self.ques_count += 1
            ques()
            Label(self.mis_bar, text=f'   <错词展示栏>   {self.mis_count}|{self.ques_count}', font=self.ft(13),
                  fg='yellow', bg='DimGray').place(x=0, y=0)
        
        frame = Frame(self.root, height=380, width=600, bd=4, bg='PaleGreen')
        frame.place(x=0, y=0)
        ques()
        Button(frame, text='确认', bd=2, width=8, command=judge).place(x=265, y=250)
    
    def XuanZeTi(self, mode):
        if self.GetWords() is None:  # 防止用户未选词库就点击题型
            messagebox.showerror(message='请先选择词库！')
            return
        messagebox.showwarning(title='Tips', message='对着选项双击左键即可判断并切换')
        
        # 出题
        def ques(mode):
            global v, center, right_item, right_ans
            self.GetWords()
            if mode == 1:  # 英--->汉
                center, right_ans, ops2, ops3, ops4 = self.word, self.expre, self.expre1, self.expre2, self.expre3
            else:  # 汉--->英
                center, right_ans, ops2, ops3, ops4 = self.expre, self.word, self.word1, self.word2, self.word3
            v = IntVar()
            ops = [right_ans, ops2, ops3, ops4]
            random.shuffle(ops)  # 打乱顺序
            A, B, C, D = ops
            right_item = ops.index(right_ans)
            
            f3 = Frame(frame, bd=4, relief="groove", height=100, width=100)
            f3.place(x=180, y=80)
            Label(f3, text=center, width=20, font=self.ft(), bd=2).grid()
            rb1 = Radiobutton(f3, text=A, variable=v, value=0, height=1, font=self.ft())
            rb2 = Radiobutton(f3, text=B, variable=v, value=1, height=1, font=self.ft())
            rb3 = Radiobutton(f3, text=C, variable=v, value=2, height=1, font=self.ft())
            rb4 = Radiobutton(f3, text=D, variable=v, value=3, height=1, font=self.ft())
            rb1.bind('<Double-Button-1>', lambda x: judge())
            rb2.bind('<Double-Button-1>', lambda x: judge())
            rb3.bind('<Double-Button-1>', lambda x: judge())
            rb4.bind('<Double-Button-1>', lambda x: judge())
            rb1.grid(stick=W)
            rb2.grid(stick=W)
            rb3.grid(stick=W)
            rb4.grid(stick=W)
        
        # 判断
        def judge():
            f = Frame(self.root, height=125, width=600, bd=4, bg='DarkGray')
            f.place(x=0, y=380)
            f4 = Frame(f, relief="groove", height=100, width=100)
            f4.place(x=180, y=0)
            if v.get() == right_item:
                Label(f4, text='回答正确！', width=25, font=self.ft()).grid()
            else:  # 答错则保存到错词本 "
                with open(os.path.join(users_data_path, self.user, f'{self.user}_mis_words.txt'), 'a+',
                          encoding='utf-8') as f:
                    if mode == 1:
                        item = f'{center}    {right_ans}\n'
                    else:
                        item = f'{right_ans}    {center}\n'
                    f.write(item)
                wrong_ans = Label(f4, text=f'回答错误!\n正确答案 {right_ans}\n已添加至错词本！', width=30, font=self.ft())
                wrong_ans.grid()
                self.mis_words.insert(0, item)
                self.mis_count += 1
            ques(mode)
            self.ques_count += 1
            # 更新 "错词展示栏"
            Label(self.mis_bar, text=f'   <错词展示栏>   {self.mis_count}|{self.ques_count}', font=self.ft(13), fg='yellow',
                  bg='DimGray').place(x=0, y=0)
        
        frame = Frame(self.root, height=380, width=600, bd=4, bg='PaleGreen')
        frame.place(x=0, y=0)
        ques(mode)
        Button(frame, text='确认', bd=2, width=8, command=judge).place(x=265, y=300)
    
    def LookupWord(self, word):
        """本地查词"""
        
        def haici(word):
            """用 海词 查单词"""
            headers = {
                'Connection': 'keep-alive',
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) Gecko/20100101 Firefox/51.0'
            }
            s = requests.session()
            s.headers.update(headers)
            url = 'http://dict.cn/' + word
            
            p1 = re.compile('<ul class="dict-basic-ul">([\s\S]*?)</ul>')
            p2 = re.compile('<span>(.*)</span>')
            p3 = re.compile('<strong>(.*)</strong>')
            data = s.get(url).text
            trans_content = re.findall(p1, data)
            trans1 = re.findall(p2, trans_content[0])
            trans2 = re.findall(p3, trans_content[0])
            trans = ''
            for i in range(min(len(trans1), len(trans2))):
                trans += trans1[i] + trans2[i] + '\n'
            if trans_content:
                return trans
            else:
                return
        
        return self.local_dict.get(word) or haici(word)
    
    def AddWord(self):
        def addit():
            word = v.get().lower()
            if not word:
                return
            trans = self.LookupWord(word)
            with open(os.path.join(users_data_path, self.user, f'{self.user}_add_words.txt'), 'a+',
                      encoding='utf-8') as f:
                if trans != None:
                    item = f'{word}      {trans}\n'
                    f.write(item)  # 论编码的重要性，，，
                    Label(top, text='成功加入！').grid(row=2)
                else:
                    Label(top, text='查无此词！').grid(row=2)
            v.set('')
            e.focus_set()
        
        top = Toplevel()
        top.wm_attributes('-topmost', 1)  # 使查词的子窗口始终置于最前面
        v = StringVar()
        Label(top, text="请输入所增单词").grid()
        e = Entry(top, textvariable=v, bd=2)
        e.bind('<Return>', lambda x: addit())
        e.grid(padx=4, pady=4)
        e.focus_set()
        btn = Button(top, text='确认', command=addit)
        btn.grid()
        Label(top, text='').grid(row=2)
    
    def SearchWord(self):
        def searchit():
            word = v.get().lower()
            if not word:
                return
            trans = self.LookupWord(word)
            if trans:
                messagebox.showinfo(title='查询结果', message=trans)
            else:
                messagebox.showinfo(title='查询结果', message='未查到该单词释义！')
            v.set('')
            e.focus_set()
        
        top = Toplevel()
        top.wm_attributes('-topmost', 1)  # 子窗口置于最前面
        v = StringVar()
        Label(top, text="请输入所查单词").grid()
        e = Entry(top, textvariable=v, bd=2)
        e.bind('<Return>', lambda x: searchit())
        e.grid(padx=4, pady=4)
        e.focus_set()
        btn = Button(top, text='确认', command=searchit)
        btn.grid()
    
    def ProcessWord(self):
        """批量查单词，待查单词应该是每行一个单词的文本文件"""
        fname = filedialog.askopenfilename(filetypes=[("all files", "*")], initialdir='./RawWords/')
        if not fname:
            messagebox.showwarning('Warning', "未选择文件!")
            return
        
        try:
            with open(fname, encoding='utf-8') as f:
                word_list = sorted(list(set(f.readlines())))
            messagebox.showinfo('Info', '请按确认开始并等待')
        except:
            messagebox.showerror('Error', f'无法打开文件\n{sys.exc_info()}')
            return
        
        count_of_words = len(word_list)
        fname = os.path.basename(fname)
        
        start = time.time()
        failed_words = []
        with open(os.path.join(lexicon_path, fname), 'w', encoding='utf-8') as f:
            for word in word_list:
                word = word.strip()
                trans = self.LookupWord(word)
                if trans:
                    f.write(f'{word}     {trans}\n')
                else:
                    failed_words.append(word)
        
        with open(os.path.join(lexicon_path, (f'failed_words-{fname}')), 'w', encoding='utf-8') as f:
            for word in failed_words:
                f.write(word + '\n')
        time_cost = time.time() - start
        
        messagebox.showinfo(message=f'用时{time_cost:.2f}秒\n处理单词共{count_of_words}条\n请在 Lexicons 文件夹中查看')
    
    def AnalyseArticle(self, reference):
        """从英文文章中分析出四六级单词"""
        """
        :param reference: 参考词库
        """
        fname = filedialog.askopenfilename(filetypes=[("all files", "*")], initialdir='./Articles')
        if not fname:
            messagebox.showwarning('Warning', "未选择文件!")
            return
        
        try:
            with open(fname, encoding="utf-8") as f:
                data = f.read().lower()
            for ch in ",.;~!@#$%^&*()_+=-:":
                data = data.replace(ch, ' ')
            data = data.split()
            messagebox.showinfo('Info', '分析中，请按确认开始并等待。')
        except:
            messagebox.showerror('Error', f'无法打开文件\n{sys.exc_info()[1]}')
            return
        
        count_of_words = 0
        start = time.time()
        with open(os.path.join('Articles', os.path.basename(fname)), 'a+', encoding='utf-8') as f:  # 用来存放分析出的单词
            for line in open(os.path.join(lexicon_path, reference), encoding="utf-8"):
                word = line.strip().split()[0]
                trans = line.strip().split()[1]
                if word in data:
                    item = f'{word}    {trans}\n'
                    f.write(item)
                    count_of_words += 1
            time_cost = time.time() - start
        messagebox.showinfo(message=f'用时{time_cost:.2f}秒\n析出单词共{count_of_words}条\n请在 Articles 文件夹中查看')
    
    def About(self):
        """软件信息"""
        
        def openlink(event):
            webbrowser.open_new("https://voldikss/github.io")
        
        top = Toplevel()
        top.focus_set()
        top.bind('<Return>', lambda x: top.destroy())
        Label(top, text="Developer").grid()
        lbox = Listbox(top, fg='blue', bg='white', height=5, width=35)
        lbox.bind("<Double-Button-1>", openlink)
        lbox.insert(1, '@Author: VOLDIKSS')
        lbox.insert(2, '@Date: 2017/6/1')
        lbox.insert(3, '@Last update time: 2017/6/1')
        lbox.insert(4, '@Contact: dyzplus@gmail.com')
        lbox.insert(5, '@Website: voldikss.github.io(双击打开)')
        lbox.grid(padx=3, pady=4)
        top.mainloop()
    
    def UserInfo(self):
        """用户信息"""
        top = Toplevel()
        top.focus_set()
        top.bind('<Return>', lambda x: top.destroy())
        Label(top, text="Current user:").grid()
        lbox = Listbox(top, fg='blue', bg='white', height=2, width=20)
        lbox.insert(1, self.user)
        lbox.grid(padx=3, pady=4)
        top.mainloop()
    
    def LoginOrRegister(self):
        def action():
            get_name = name.get().strip()
            get_pswd = pswd.get().strip()
            if not (get_name and get_pswd):  # 如果用户未输入信息就提示并重新输入
                messagebox.showwarning(message='请输入账号或密码！')
                re_enter()
                return
            elif not re.match('[a-zA-Z0-9]', get_pswd):  # 判断密码格式，不符合标准则提示
                messagebox.showwarning(message='密码必须是字母和数字的组合！')
                re_enter()
                return
            else:
                with open(os.path.join(users_data_path, "users.json"), encoding="utf-8") as f:
                    accounts = json.load(f)
                # 用户选择注册，加密保存用户信息
                if v.get() == 0:
                    if get_name in accounts:
                        messagebox.showerror(message='用户名已存在!')
                        re_enter()
                        return
                    else:
                        messagebox.showinfo(message=' 成功注册！')
                        self.user = get_name
                        accounts[get_name] = encrypt(get_pswd)
                        with open(os.path.join(users_data_path, "users.json"), 'w', encoding="utf-8") as f:
                            json.dump(accounts, f)
                        # 创建个人文件夹
                        os.mkdir(os.path.join(users_data_path, self.user))
                
                # 用户选择登录，验证用户信息
                elif v.get() == 1:
                    if get_name in accounts:
                        if accounts[get_name] == encrypt(get_pswd):
                            messagebox.showinfo(message='成功登录！')
                            self.user = get_name
                        else:
                            messagebox.showerror(message='密码错误！')
                            re_enter()
                            return
                    else:
                        messagebox.showerror(message='用户名不存在！')
                        re_enter()
                        return
            # 成功登录后注销窗口
            top.destroy()
        
        def encrypt(str):
            """采用 md5 加密"""
            md5 = hashlib.md5()
            md5.update(str.encode('utf-8'))
            return md5.hexdigest()
        
        def re_enter():
            """清空原先输入内容"""
            name.set('')
            pswd.set('')
            e1.focus_set()
        
        top = Toplevel()
        top.wm_attributes('-topmost', 1)
        top.geometry('300x125')
        name = StringVar()
        pswd = StringVar()
        Label(top, text='账号').grid(row=3, column=1)
        Label(top, text='密码').grid(row=4, column=1)
        e1 = Entry(top, textvariable=name)
        e1.bind('<Return>', lambda x: action())
        e1.grid(row=3, column=2)
        e1.focus_set()
        e2 = Entry(top, textvariable=pswd, show='*')
        e2.bind('<Return>', lambda x: action())
        e2.grid(row=4, column=2)
        v = IntVar()
        v.set(1)
        Radiobutton(top, text='登录', variable=v, value=1).grid(row=1, column=1, padx=30)
        Radiobutton(top, text='注册', variable=v, value=0).grid(row=1, column=2, sticky=E)
        Button(top, text='确认', command=action).grid(row=5, column=1)
        Button(top, text='重输', command=re_enter).grid(row=5, column=2, sticky=E)
        top.mainloop()
    
    def QuitMe(self):
        self.root.destroy()


if __name__ == '__main__':
    dir_path = os.path.dirname(os.path.abspath(__file__))
    lexicon_path = os.path.join(dir_path, "Lexicons")
    users_data_path = os.path.join(dir_path, "UsersData")
    
    wp = WordPlayerUI()
