from flask import Flask, request, jsonify, render_template
import threading
from downloader import start
from converter import convertor
import os

app = Flask(__name__)

# 存储下载任务
download_tasks = {}
# 存储线程对象和停止标志
task_threads = {}
task_stop_flags = {}

# 工作目录
WORK_DIR = "./downloads"
os.makedirs(WORK_DIR, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    data = request.get_json()
    url = data.get('url')
    element_selector = data.get('element_selector', '#chapter-list-0')
    index = data.get('index', 0)
    headless = data.get('headless', False)
    proxy = data.get('proxy', None)
    auto_convert = data.get('auto_convert', True)
    
    if not url:
        return jsonify({'success': False, 'message': 'URL is required'}), 400
    
    task_id = str(len(download_tasks) + 1)
    
    # 创建停止标志
    stop_flag = threading.Event()
    task_stop_flags[task_id] = stop_flag
    
    def download_task():
        manga_name = None
        try:
            download_tasks[task_id] = {
                'status': 'running', 
                'message': '下载中...',
                'url': url,
                'element_selector': element_selector,
                'index': index,
                'auto_convert': auto_convert
            }
            
            # 下载完成后的回调函数
            def on_download_complete(name):
                nonlocal manga_name
                manga_name = name
                if auto_convert:
                    download_tasks[task_id]['message'] = f'下载完成，开始转换PDF...'
            
            # 传递停止标志、回调函数和工作目录给下载函数
            start(url, headLess=headless, proxy=proxy, 
                  element_selector=element_selector, index=index, 
                  stop_flag=stop_flag,
                  on_complete_callback=on_download_complete,
                  work_dir=WORK_DIR)
            
            # 检查是否被停止
            if stop_flag.is_set():
                download_tasks[task_id].update({
                    'status': 'stopped', 
                    'message': '已停止下载'
                })
            else:
                # 如果需要自动转换
                if auto_convert and manga_name:
                    try:
                        download_tasks[task_id]['message'] = f'正在转换 "{manga_name}" 为PDF...'
                        convertor(manga_name, work_dir=WORK_DIR)
                        download_tasks[task_id].update({
                            'status': 'completed', 
                            'message': f'下载并转换完成！PDF已保存到 {WORK_DIR}/{manga_name} 文件夹'
                        })
                    except Exception as e:
                        download_tasks[task_id].update({
                            'status': 'completed_with_warning', 
                            'message': f'下载完成，但转换PDF时出错: {str(e)}'
                        })
                else:
                    download_tasks[task_id].update({
                        'status': 'completed', 
                        'message': f'下载完成！文件已保存到 {WORK_DIR}'
                    })
                
        except InterruptedError:
            download_tasks[task_id].update({
                'status': 'stopped', 
                'message': '已停止下载'
            })
        except Exception as e:
            if stop_flag.is_set():
                download_tasks[task_id].update({
                    'status': 'stopped', 
                    'message': '已停止下载'
                })
            else:
                download_tasks[task_id].update({
                    'status': 'failed', 
                    'message': str(e)
                })
        finally:
            # 清理线程引用
            if task_id in task_threads:
                del task_threads[task_id]
            if task_id in task_stop_flags:
                del task_stop_flags[task_id]
    
    thread = threading.Thread(target=download_task)
    thread.daemon = True
    task_threads[task_id] = thread
    thread.start()
    
    return jsonify({'success': True, 'task_id': task_id, 'message': '下载任务已启动'})

@app.route('/convert', methods=['POST'])
def manual_convert():
    """手动触发转换"""
    data = request.get_json()
    manga_name = data.get('manga_name')
    
    if not manga_name:
        return jsonify({'success': False, 'message': '漫画名称不能为空'}), 400
    
    try:
        convertor(manga_name, work_dir=WORK_DIR)
        return jsonify({'success': True, 'message': f'转换完成！PDF已保存到 {WORK_DIR}/{manga_name} 文件夹'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'转换失败: {str(e)}'}), 500

@app.route('/stop/<task_id>', methods=['POST'])
def stop_download(task_id):
    """停止下载任务"""
    if task_id not in download_tasks:
        return jsonify({'success': False, 'message': '任务不存在'}), 404
    
    current_status = download_tasks[task_id]['status']
    if current_status not in ['running']:
        return jsonify({
            'success': False, 
            'message': f"任务状态为 {current_status}，无法停止"
        }), 400
    
    if task_id in task_stop_flags:
        task_stop_flags[task_id].set()
        download_tasks[task_id]['status'] = 'stopping'
        download_tasks[task_id]['message'] = '正在停止...'
        return jsonify({'success': True, 'message': '停止信号已发送，浏览器即将关闭'})
    
    return jsonify({'success': False, 'message': '无法停止任务'}), 400

@app.route('/status/<task_id>', methods=['GET'])
def get_status(task_id):
    if task_id not in download_tasks:
        return jsonify({'success': False, 'message': '任务不存在'}), 404
    
    return jsonify({
        'success': True,
        'task_id': task_id,
        'status': download_tasks[task_id]['status'],
        'message': download_tasks[task_id]['message'],
        'url': download_tasks[task_id].get('url', ''),
        'element_selector': download_tasks[task_id].get('element_selector', ''),
        'index': download_tasks[task_id].get('index', 0),
        'auto_convert': download_tasks[task_id].get('auto_convert', True)
    })

@app.route('/tasks', methods=['GET'])
def get_all_tasks():
    """获取所有任务列表"""
    return jsonify({
        'success': True,
        'tasks': download_tasks
    })

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)