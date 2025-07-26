import re
import os


def clean_markdown_file(input_path, output_path):
    """
    读取Markdown文件，根据指定规则进行清理和格式化，并写入新文件。

    规则:
    1. 父标题为 #，二级标题为 ##。
    2. 删除二级标题后重复的三级标题。
    3. “背景导入”和“核心要点”统一为三级标题 ###，不带数字。
    4. “核心要点”下的列表项统一使用 '-'。
    5. 自动为缺少“核心要点”标题的列表补充标题。
    """
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"错误：输入文件 '{input_path}' 不存在。")
        # 创建一个示例输入文件
        with open(input_path, 'w', encoding='utf-8') as f:
            f.write(
                "# 1.3 容器存储管理\n## 1.3.3 容器存储驱动的类型与技术原理\n\n### 1. 背景导入\n背景介绍...\n\n### 2. **devicemapper驱动**\n驱动介绍...\n\n### 3. **overlay2驱动**\n驱动介绍...")
        print(f"已为您创建一个示例输入文件 '{input_path}'，请填入您的内容后重新运行。")
        return

    new_lines = []
    last_h2_title_text = ""
    # 标记是否需要为特殊列表（如1.3.3节）注入“核心要点”标题
    inject_core_points_header = False

    for i, line in enumerate(lines):
        stripped_line = line.strip()

        # 保留空行用于格式化
        if not stripped_line:
            new_lines.append('\n')
            continue

        # 规则1 & 2: 处理父标题和二级标题
        if stripped_line.startswith('# '):
            new_lines.append(stripped_line + '\n')
            continue

        if stripped_line.startswith('## '):
            # 确保是 ## 开头
            clean_h2 = '##' + stripped_line.lstrip('#')
            new_lines.append('\n' + clean_h2 + '\n')
            # 提取标题文本用于去重检查
            last_h2_title_text = re.sub(r'^##\s*[\d\.]*\s*', '', clean_h2)
            continue

        # 规则2: 删除重复的三级标题
        if stripped_line.startswith('### '):
            h3_text = re.sub(r'^###\s*[\d\.]*\s*', '', stripped_line)
            if h3_text and h3_text == last_h2_title_text:
                last_h2_title_text = ""  # 清除，防止误删
                continue

        # 规则3 & 4: 统一“背景导入”和“核心要点”，并处理特殊情况
        if '背景导入' in stripped_line:
            new_lines.append('### 背景导入\n')
            # 向后查找以判断是否是缺少“核心要点”标题的特殊情况
            for j in range(i + 1, min(i + 5, len(lines))):  # 向后看几行
                next_line_stripped = lines[j].strip()
                if not next_line_stripped:
                    continue
                # 如果下一个标题是“核心要点”，则不是特殊情况
                if '核心要点' in next_line_stripped:
                    break
                # 如果找到形如 "### 2. **..." 的列表项，说明是特殊情况
                if re.match(r'^###\s*\d+\.\s*\*\*', next_line_stripped):
                    inject_core_points_header = True
                    break
            continue

        if '核心要点' in stripped_line:
            new_lines.append('\n### 核心要点\n')
            continue

        # 检查是否需要注入“核心要点”标题
        if inject_core_points_header and re.match(r'^###\s*\d+\.\s*\*\*', stripped_line):
            new_lines.append('\n### 核心要点\n')
            inject_core_points_header = False  # 只注入一次

        # 规则4: 统一列表格式
        is_numbered_list = re.match(r'^\d+\.\s', stripped_line)
        is_hyphen_list = stripped_line.startswith('-')
        is_special_list = re.match(r'^###\s*\d+\.\s*\*\*', stripped_line)

        if is_numbered_list or is_hyphen_list or is_special_list:
            # 将所有匹配的列表项格式化为 '- ' 开头
            clean_item = re.sub(r'^\d+\.\s*|^\s*-\s*|^###\s*\d+\.\s*', '- ', stripped_line)
            new_lines.append(clean_item + '\n')
            continue

        # 其他所有行（内容行）直接添加
        new_lines.append(line)

    # 合并并清理多余的空行
    final_content = "".join(new_lines)
    final_content = re.sub(r'\n(\s*\n)+', '\n\n', final_content)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(final_content.strip() + '\n')

    print(f"文件处理完成！清理后的内容已保存到 '{output_path}'。")


# --- 使用方法 ---
# 1. 将您需要处理的Markdown内容保存到一个名为 `input.md` 的文件中。
# 2. 将此文件与Python脚本放在同一目录下。
# 3. 运行此脚本。
# 4. 处理后的内容将被保存在一个名为 `output.md` 的新文件中。

# 定义输入和输出文件名
input_filename = "keypoints/all_keypoints.md"
output_filename = "cleaned_keypoints.md"

# 执行清理函数
# 注意：在执行此代码前，请确保您已将源数据保存为 input.md 文件。
if __name__ == "__main__":
    # 检查输入文件是否存在
    if not os.path.exists(input_filename):
        print(f"错误：输入文件 '{input_filename}' 不存在或无法访问。")
        print("请将您的Markdown内容保存为 input.md 文件后重试。")
    else:
        clean_markdown_file(input_filename, output_filename)
