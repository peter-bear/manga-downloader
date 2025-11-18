import os
import re
from PIL import Image
import glob
import concurrent.futures
import gc

def extract_page_number(filename):
    """从文件名中提取页码数字"""
    # 从类似 'seemh-001-f1b6.png.webp' 的文件名中提取数字
    match = re.findall(r'\d+', filename)
    if match:
        return int(match[0])
    return 0

def convert_webp_to_jpg(folder_path):
    """将WebP图片转换为PIL Image对象列表"""
    images = []
    # 获取所有webp文件
    folder_path = os.path.join(folder_path, '')
    webp_files = glob.glob(folder_path + "*.webp")
    
    webp_files.sort(key=lambda x: extract_page_number(os.path.basename(x)))
    
    # 转换文件
    for index, webp_file in enumerate(webp_files, start=1):
        try:
            # 打开WebP图片
            with Image.open(webp_file) as img:
                # 如果是RGBA模式，转换为RGB
                if img.mode == 'RGBA':
                    img = img.convert('RGB')
                else:
                    img = img.convert('RGB')
                
                # 复制图像以避免文件关闭后无法访问
                images.append(img.copy())
                
        except Exception as e:
            print(f"转换文件 {webp_file} 时出错: {str(e)}")

    return images


def save_images_as_pdf(images, output_path):
    """将图片列表保存为PDF"""
    if images:
        images[0].save(output_path, save_all=True, append_images=images[1:])


def process_folder(folder, work_dir="./", manga_name=""):
    """处理单个文件夹"""
    if folder.startswith(manga_name) and folder != manga_name:
        
        print(f"正在处理文件夹: {folder}")
        
        path = os.path.join(work_dir, manga_name ,folder)
        
        jpg_images = convert_webp_to_jpg(path)
        
        if jpg_images:
            output_path = os.path.join(work_dir, manga_name, str(folder) + ".pdf")
            print(f"保存PDF到: {output_path}")
            save_images_as_pdf(jpg_images, output_path)
            
            # # move the processed folder to manga_name directory
            # new_folder_path = os.path.join(current_dir, manga_name, folder)
            # try:
            #     os.rename(folder_path, new_folder_path)
            #     print(f"已移动文件夹到: {new_folder_path}")
            # except Exception as e:
            #     print(f"移动文件夹失败: {str(e)}")
            
            # delete the original folder after processing
            try:
                for file in os.listdir(path):
                    file_path = os.path.join(path, file)
                    os.remove(file_path)
                os.rmdir(path)
                print(f"已删除原始文件夹: {path}")
            except Exception as e:
                print(f"删除文件夹失败: {str(e)}")
            
            # 显式释放内存
            del jpg_images
            gc.collect()
        else:
            print(f"文件夹 {folder} 中没有找到WebP图片")


def convertor(manga_name, work_dir="./", max_workers=4):
    """
    转换漫画文件夹为PDF
    
    Args:
        manga_name: 漫画名称
        work_dir: 工作目录，默认为当前目录
        max_workers: 最大并发数，默认为4
    """
    manga_dir = os.path.join(work_dir, manga_name)
    
    # 获取所有文件夹
    manga_folders = [entry.name for entry in os.scandir(manga_dir) if entry.is_dir()]
    
    # 过滤需要处理的文件夹
    folders_to_process = [f for f in manga_folders if f.startswith(manga_name) and f != manga_name]
    
    if not folders_to_process:
        print(f"没有找到以 '{manga_name}' 开头的文件夹")
        return
    
    print(f"找到 {len(folders_to_process)} 个文件夹待处理")
    
    # 使用线程池并发处理
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(process_folder, folder, work_dir=work_dir, manga_name=manga_name) 
                   for folder in folders_to_process]
        
        # 等待所有任务完成
        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(f"处理文件夹时出错: {str(e)}")
    
    print(f"转换完成！PDF文件已保存到 {manga_dir} 文件夹中")


if __name__ == "__main__":
    manga_name = "槐与优"
    convertor(manga_name, work_dir="./downloads", max_workers=4)