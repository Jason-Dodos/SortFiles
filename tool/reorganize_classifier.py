import os
import shutil
from pathlib import Path

# 定义分类规则
CATEGORIES = {
    '文档资料': ['.doc', '.docx', '.pdf', '.txt', '.rtf', '.xls', '.xlsx', '.ppt', '.pptx', '.odt', '.ods', '.odp'],
    '图片素材': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.svg', '.webp', '.ico'],
    '视频资料': ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.m4v'],
    '音频资料': ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma', '.m4a'],
    '压缩文件': ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2'],
    '程序软件': ['.exe', '.msi', '.bat', '.cmd', '.sh'],
    '代码文件': ['.py', '.java', '.cpp', '.c', '.js', '.html', '.css', '.php', '.sql', '.xml', '.json'],
    '数据文件': ['.csv', '.dat', '.db', '.sqlite', '.mdb', '.json', '.xml']
}

# 子分类规则
SUBCATEGORIES = {
    '图片素材': {
        'JPEG': ['.jpg', '.jpeg'],
        'PNG': ['.png'],
        'GIF': ['.gif'],
        'BMP': ['.bmp'],
        'TIFF': ['.tiff'],
        'SVG': ['.svg'],
        'WEBP': ['.webp'],
        'ICO': ['.ico']
    },
    '文档资料': {
        'Word文档': ['.doc', '.docx'],
        'PDF文档': ['.pdf'],
        '文本文件': ['.txt', '.rtf'],
        '表格文档': ['.xls', '.xlsx', '.ods'],
        '演示文档': ['.ppt', '.pptx', '.odp']
    },
    '视频资料': {
        'MP4视频': ['.mp4'],
        'AVI视频': ['.avi'],
        'MKV视频': ['.mkv'],
        'MOV视频': ['.mov'],
        '其他视频': ['.wmv', '.flv', '.webm', '.m4v']
    },
    '音频资料': {
        'MP3音频': ['.mp3'],
        'WAV音频': ['.wav'],
        'FLAC音频': ['.flac'],
        'AAC音频': ['.aac'],
        '其他音频': ['.ogg', '.wma', '.m4a']
    },
    '压缩文件': {
        'ZIP压缩': ['.zip'],
        'RAR压缩': ['.rar'],
        '7Z压缩': ['.7z'],
        'TAR压缩': ['.tar'],
        '其他压缩': ['.gz', '.bz2']
    },
    '程序软件': {
        '可执行程序': ['.exe'],
        '安装包': ['.msi'],
        '批处理脚本': ['.bat', '.cmd'],
        'Shell脚本': ['.sh']
    },
    '代码文件': {
        'Python代码': ['.py'],
        'Java代码': ['.java'],
        'C/C++代码': ['.cpp', '.c'],
        '前端代码': ['.js', '.html', '.css'],
        '后端代码': ['.php', '.sql'],
        '配置文件': ['.xml', '.json']
    },
    '数据文件': {
        'CSV数据': ['.csv'],
        '数据库文件': ['.db', '.sqlite', '.mdb'],
        '其他数据': ['.dat', '.json', '.xml']
    }
}

def get_category_by_extension(extension):
    """根据文件扩展名确定分类"""
    for category, extensions in CATEGORIES.items():
        if extension.lower() in extensions:
            return category
    return '其他文件'

def get_subcategory_by_extension(category, extension):
    """根据文件扩展名确定子分类"""
    if category in SUBCATEGORIES:
        for subcategory, extensions in SUBCATEGORIES[category].items():
            if extension.lower() in extensions:
                return subcategory
    return None

def reorganize_files(base_dir):
    """对已分类的文件进行重新组织，添加子分类"""
    # 统计信息
    reorganized_count = 0
    skipped_count = 0
    
    # 遍历基础目录中的所有分类目录
    for category in os.listdir(base_dir):
        category_path = os.path.join(base_dir, category)
        
        # 只处理目录
        if os.path.isdir(category_path) and category != '其他文件':
            print(f"正在处理分类: {category}")
            
            # 遍历分类目录中的所有文件
            for filename in os.listdir(category_path):
                file_path = os.path.join(category_path, filename)
                
                # 只处理文件，跳过目录
                if os.path.isfile(file_path):
                    # 获取文件扩展名
                    _, extension = os.path.splitext(filename)
                    
                    # 确定子分类
                    subcategory = get_subcategory_by_extension(category, extension)
                    
                    # 如果有子分类，则移动到子目录
                    if subcategory:
                        # 确定目标目录
                        target_dir = os.path.join(category_path, subcategory)
                        
                        # 确保目标目录存在
                        os.makedirs(target_dir, exist_ok=True)
                        
                        # 处理同名文件
                        target_file_path = os.path.join(target_dir, filename)
                        counter = 1
                        base_name, ext = os.path.splitext(filename)
                        while os.path.exists(target_file_path):
                            new_filename = f"{base_name}_{counter}{ext}"
                            target_file_path = os.path.join(target_dir, new_filename)
                            counter += 1
                        
                        # 移动文件
                        try:
                            shutil.move(file_path, target_file_path)
                            print(f"已移动: {filename} -> {category}/{subcategory}")
                            reorganized_count += 1
                        except Exception as e:
                            print(f"移动文件 {filename} 失败: {e}")
                            skipped_count += 1
                    else:
                        # 没有子分类的文件保持原位
                        skipped_count += 1
                else:
                    # 跳过目录
                    skipped_count += 1
    
    # 输出统计信息
    print(f"\n重新组织完成!")
    print(f"已重新组织文件数: {reorganized_count}")
    print(f"跳过项目数: {skipped_count}")

if __name__ == "__main__":
    # 定义基础目录
    base_directory = r'E:\recvr\分类'
    
    # 执行重新组织
    reorganize_files(base_directory)