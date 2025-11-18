import random
import requests
from DrissionPage import Chromium, ChromiumOptions, SessionPage, SessionOptions
import threading
import os


class Downloader:
    def __init__(self, browser, stop_flag=None, on_complete_callback=None, work_dir="./"):
        self.browser = browser
        self.tab = browser.latest_tab  
        self.chapters = {}
        self.waitScope = (1, 2)
        self.scrollScope = (100, 800)
        self.randomScope = (1, 2)
        self.stop_flag = stop_flag
        self.on_complete_callback = on_complete_callback
        self.manga_name = None
        # 使用绝对路径
        self.work_dir = os.path.abspath(work_dir)
        
        # 确保工作目录存在
        os.makedirs(self.work_dir, exist_ok=True)
        print(f"工作目录设置为: {self.work_dir}")
        

    def check_stop(self):
        """检查是否需要停止"""
        if self.stop_flag and self.stop_flag.is_set():
            print("检测到停止信号，正在停止下载...")
            try:
                self.browser.quit()
            except:
                pass
            raise InterruptedError("下载已被用户停止")

    def randomMove(self):
        for i in range(random.randint(*self.randomScope)):
            self.check_stop()
            self.browser.wait(*self.waitScope)
            self.tab.actions.scroll(delta_y=random.randint(*self.scrollScope))
    
    def download_manga(self, url, element_selector='#chapter-list-0', index=0):
        self.check_stop()
        
        self.tab.get(url, retry=1, timeout=10)
        
        adultBtn = self.tab.ele("#checkAdult")
        if adultBtn:
            adultBtn.click()
        
        self.randomMove()
        
        self.check_stop()
        
        # 等待加载
        self.tab.wait.ele_displayed(element_selector)
        chapterList = self.tab.eles(element_selector)[index].eles('tag:a')
        
        # 获取书名
        bookTitle = self.tab.ele('.book-title').ele('tag:h1').text
        self.manga_name = bookTitle
        print(f"漫画名称: {self.manga_name}")

        # 遍历章节
        for chapter in chapterList:
            self.check_stop()
            
            # 获取章节名 - 只保留章节标题，不重复漫画名
            chapterTitle = chapter.attr('title')
            chapterLink = chapter.attr('href')
            self.chapters[chapterTitle] = chapterLink
            
        print(f"总共找到 {len(self.chapters)} 个章节")
            
        # 遍历章节
        for chapterTitle, chapterLink in self.chapters.items():
            self.check_stop()
            
            # 完整章节名用于显示
            fullChapterName = f"{bookTitle} - {chapterTitle}"
            print("开始下载:" + fullChapterName)
            self.download_manga_per_chapter(chapterLink, chapterTitle)
            print("下载完毕:" + fullChapterName)
        
        # 下载完成，调用回调函数
        if self.on_complete_callback and self.manga_name:
            print(f"下载完成，调用回调函数，漫画名: {self.manga_name}")
            self.on_complete_callback(self.manga_name)
        
        
    def download_manga_per_chapter(self, url, chapterTitle):
        self.check_stop()
        
        self.tab.get(url)
        self.tab.wait.ele_displayed('#mangaFile')
        pageSelect = self.tab.ele('#pageSelect')

        totalPages = pageSelect.child_count
        
        # 创建文件夹结构: work_dir/漫画名/漫画名 - 章节名
        fullChapterName = f"{self.manga_name} - {chapterTitle}"
        saved_folder = os.path.join(self.work_dir, self.manga_name, fullChapterName)
        os.makedirs(saved_folder, exist_ok=True)
        
        print(f"保存路径: {saved_folder}")
        print(f"总页数: {totalPages}")

        for i in range(1, totalPages+1):
            self.check_stop()
            
            self.randomMove()
            self.tab.wait.ele_displayed('#mangaFile')
            mangaFile = self.tab.ele('#mangaFile')
            
            img_url = mangaFile.attr('src')
            print(f"第 {i}/{totalPages} 页 - 下载: {img_url}")
            
            try:
                # 使用 DrissionPage 的 download 方法
                self.tab.download(img_url, saved_folder)
            except Exception as e:
                print(f"下载失败: {str(e)}")
            
            self.check_stop()
            
            nextBtn = self.tab.ele('#next')
            if nextBtn:
                nextBtn.click()


def start(url, headLess=False, proxy=None, element_selector='#chapter-list-0', 
          index=0, stop_flag=None, on_complete_callback=None, work_dir="./"):
    """
    启动下载
    
    Args:
        url: 漫画URL
        headLess: 是否使用无头模式
        proxy: 代理地址
        element_selector: 章节列表选择器
        index: 章节列表索引
        stop_flag: threading.Event 对象，用于停止下载
        on_complete_callback: 下载完成后的回调函数，参数为漫画名称
        work_dir: 工作目录，下载文件保存位置
    """
    browser = None
    work_dir_abs = os.path.abspath(work_dir)
    
    try:
        if(headLess):
            co = ChromiumOptions().headless()
        else:
            co = ChromiumOptions()
        
        co.incognito(True)
        
        # Docker 环境必需的参数
        co.set_argument('--no-sandbox')
        co.set_argument('--disable-dev-shm-usage')
        co.set_argument('--disable-gpu')
        co.set_argument('--headless=new')  # Docker 中必须使用无头模式
        
        # 设置下载路径
        print(f"设置浏览器下载路径: {work_dir_abs}")
        co.set_download_path(work_dir_abs)
        
        co.set_user_agent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36')
        if(proxy!=None):
            co.set_proxy("http://{}".format(proxy))
            

        browser = Chromium(co)
        
        downloader = Downloader(browser, stop_flag=stop_flag, 
                               on_complete_callback=on_complete_callback,
                               work_dir=work_dir_abs)
        downloader.download_manga(url, element_selector=element_selector, index=index)
        
    except InterruptedError as e:
        print(f"下载被中断: {e}")
        raise
    except Exception as e:
        print(f"下载出错: {e}")
        raise
    finally:
        # 确保浏览器被关闭
        if browser:
            try:
                browser.quit()
            except:
                pass


def get_proxy():
    return requests.get("http://127.0.0.1:5010/get/").json()

def delete_proxy(proxy):
    requests.get("http://127.0.0.1:5010/delete/?proxy={}".format(proxy))

def main(url, element_selector='#chapter-list-0', index=0, work_dir="./"):
    start(url, headLess=False, proxy=None, element_selector=element_selector, 
          index=index, work_dir=work_dir)

if __name__ == "__main__":
    url = "https://www.manhuagui.com/comic/49301/"
    work_dir = "./downloads"
    main(url, element_selector='#chapter-list-0', index=0, work_dir=work_dir)