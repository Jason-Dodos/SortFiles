import os
import shutil
import sys
import argparse
from pathlib import Path
import json

# 定义文件分类规则
FILE_CATEGORIES = {
    '文档资料': {
        'extensions': ['.doc', '.docx', '.pdf', '.txt', '.rtf', '.xls', '.xlsx', '.ppt', '.pptx', '.odt', '.ods', '.odp'],
        'directory': '文档资料'
    },
    '图片素材': {
        'extensions': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.svg', '.webp', '.ico'],
        'directory': '图片素材'
    },
    '视频资料': {
        'extensions': ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.m4v'],
        'directory': '视频资料'
    },
    '音频资料': {
        'extensions': ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma', '.m4a'],
        'directory': '音频资料'
    },
    '压缩文件': {
        'extensions': ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2'],
        'directory': '压缩文件'
    },
    '程序软件': {
        'extensions': ['.exe', '.msi', '.bat', '.cmd', '.sh'],
        'directory': '程序软件'
    },
    '代码文件': {
        'extensions': ['.py', '.java', '.cpp', '.c', '.js', '.html', '.css', '.php', '.sql', '.xml', '.json'],
        'directory': '代码文件'
    },
    '数据文件': {
        'extensions': ['.csv', '.dat', '.db', '.sqlite', '.mdb', '.json', '.xml'],
        'directory': '数据文件'
    }
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
    """根据文件扩展名确定文件分类"""
    for category, info in FILE_CATEGORIES.items():
        if extension.lower() in info['extensions']:
            return category
    return '其他文件'

def get_subcategory_by_extension(category, extension):
    """根据文件扩展名确定子分类"""
    if category in SUBCATEGORIES:
        for subcategory, extensions in SUBCATEGORIES[category].items():
            if extension.lower() in extensions:
                return subcategory
    return None

def create_directory(path):
    """创建目录（如果不存在）"""
    if not os.path.exists(path):
        os.makedirs(path)

def move_file(src_path, dest_dir, filename):
    """移动文件到目标目录，如果文件已存在则重命名"""
    dest_path = os.path.join(dest_dir, filename)
    
    # 如果目标文件已存在，则添加序号
    if os.path.exists(dest_path):
        name, ext = os.path.splitext(filename)
        counter = 1
        while True:
            new_filename = f"{name}_{counter}{ext}"
            new_dest_path = os.path.join(dest_dir, new_filename)
            if not os.path.exists(new_dest_path):
                dest_path = new_dest_path
                break
            counter += 1
    
    shutil.move(src_path, dest_path)
    return dest_path

def load_progress(progress_file):
    """加载处理进度"""
    if os.path.exists(progress_file):
        with open(progress_file, 'r') as f:
            return json.load(f)
    return {'last_processed_dir': None}

def save_progress(progress_file, last_processed_dir):
    """保存处理进度"""
    with open(progress_file, 'w') as f:
        json.dump({'last_processed_dir': last_processed_dir}, f)

def classify_files(source_path, target_path):
    """对指定路径下的文件进行分类"""
    # 创建目标根目录
    create_directory(target_path)
    
    # 创建分类目录
    category_stats = {}
    for category, info in FILE_CATEGORIES.items():
        dir_path = os.path.join(target_path, info['directory'])
        create_directory(dir_path)
        category_stats[category] = 0
    
    # 创建"其他文件"目录
    other_dir = os.path.join(target_path, '其他文件')
    create_directory(other_dir)
    category_stats['其他文件'] = 0
    
    # 检查源路径是否存在
    if not os.path.exists(source_path):
        raise FileNotFoundError(f"源路径不存在: {source_path}")
    
    # 如果源路径是目录，则递归遍历其中的所有文件
    if os.path.isdir(source_path):
        print(f"正在处理目录: {source_path}")
        
        processed_count = 0
        
        # 递归遍历所有文件
        for root, dirs, files in os.walk(source_path):
            for filename in files:
                file_path = os.path.join(root, filename)
                
                # 获取文件扩展名
                _, ext = os.path.splitext(filename)
                
                # 确定文件分类
                category = get_category_by_extension(ext)
                
                # 确定子分类
                subcategory = get_subcategory_by_extension(category, ext)
                
                # 确定目标目录
                if category == '其他文件':
                    target_dir = other_dir
                elif subcategory:
                    # 创建子分类目录
                    target_dir = os.path.join(target_path, FILE_CATEGORIES[category]['directory'], subcategory)
                    create_directory(target_dir)
                else:
                    target_dir = os.path.join(target_path, FILE_CATEGORIES[category]['directory'])
                
                # 移动文件
                try:
                    move_file(file_path, target_dir, filename)
                    category_stats[category] += 1
                    processed_count += 1
                    
                    if processed_count % 100 == 0:
                        print(f"已处理 {processed_count} 个文件")
                        
                except FileNotFoundError:
                    # 文件可能已经被移动或删除，跳过它
                    print(f"文件 {filename} 未找到，可能已被移动或删除")
                    continue
                except Exception as e:
                    print(f"移动文件 {filename} 时出错: {str(e)}")
    
        return category_stats, processed_count
    
    # 如果源路径是文件，则直接处理该文件
    elif os.path.isfile(source_path):
        filename = os.path.basename(source_path)
        _, ext = os.path.splitext(filename)
        
        # 确定文件分类
        category = get_category_by_extension(ext)
        
        # 确定子分类
        subcategory = get_subcategory_by_extension(category, ext)
        
        # 确定目标目录
        if category == '其他文件':
            target_dir = other_dir
        elif subcategory:
            # 创建子分类目录
            target_dir = os.path.join(target_path, FILE_CATEGORIES[category]['directory'], subcategory)
            create_directory(target_dir)
        else:
            target_dir = os.path.join(target_path, FILE_CATEGORIES[category]['directory'])
        
        # 移动文件
        try:
            move_file(source_path, target_dir, filename)
            category_stats[category] = 1
            print(f"已处理文件: {filename}")
            return category_stats, 1
        except Exception as e:
            raise Exception(f"移动文件 {filename} 时出错: {str(e)}")
    
    else:
        raise ValueError("源路径既不是文件也不是目录")

def generate_report(category_stats, processed_count, report_path):
    """生成分类报告"""
    total_files = sum(category_stats.values())
    
    # 修复编码问题
    with open(report_path, 'w', encoding='utf-8-sig') as f:
        f.write('# 文件分类报告\n\n')
        f.write('## 总体统计\n')
        f.write(f'- 已分类文件数: {processed_count}\n')
        f.write(f'- 总文件数: {total_files}\n\n')
        
        f.write('## 各分类详细统计\n\n')
        f.write('| 分类名称 | 文件数量 | 占比 |\n')
        f.write('|---------|---------|------|\n')
        
        for category, count in sorted(category_stats.items()):
            percentage = (count / total_files * 100) if total_files > 0 else 0
            f.write(f'| {category} | {count} | {percentage:.2f}% |\n')
    
    print(f"分类报告已生成: {report_path}")

def main():
    parser = argparse.ArgumentParser(description='文件分类工具')
    parser.add_argument('source', help='待分类的文件或目录路径')
    parser.add_argument('target', help='存放分类后文件的目录路径')
    parser.add_argument('-r', '--report', help='生成分类报告的路径')
    
    # 如果没有参数，则显示帮助信息
    if len(sys.argv) == 1:
        parser.print_help()
        return
    
    args = parser.parse_args()
    
    source_path = args.source
    target_path = args.target
    
    print(f"开始文件分类处理...")
    print(f"源路径: {source_path}")
    print(f"目标路径: {target_path}")
    
    try:
        # 进行文件分类
        category_stats, processed_count = classify_files(source_path, target_path)
        
        # 生成分类报告
        if args.report:
            report_path = args.report
        else:
            report_path = os.path.join(target_path, '分类报告.md')
        
        generate_report(category_stats, processed_count, report_path)
        
        print("文件分类处理完成!")
        print("各类别文件统计:")
        for category, count in sorted(category_stats.items()):
            print(f"  {category}: {count} 个文件")
            
    except Exception as e:
        print(f"错误: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()