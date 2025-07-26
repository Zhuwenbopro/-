import os
import re
import sys

# --- 配置 ---

# 1. 源文件夹名称
SOURCE_DIRECTORY = "output_stage3_final"

# 2. 最终合并后的文件名
MERGED_FILENAME = "容器资源管理-最终合并稿.md"

# 3. [关键] 定义一级章节的结构。
#    这是脚本用来生成一级标题的依据。
#    请确保这里的编号和标题与您的项目规划一致。
CHAPTER_MAP = {
    "1.1": "虚拟化与容器",
    "1.2": "容器镜像管理",
    "1.3": "容器存储管理",
    "1.4": "容器网络管理",
    "1.5": "容器安全管理",
    "1.6": "容器运行时生态",
    "1.7": "容器化思维",
    # 如果有更多章节，请继续在这里添加
}


def intelligent_merge():
    """
    智能地合并 Markdown 文件，自动根据文件名生成
    正确的一级和二级标题层级。
    """
    print("--- 启动智能标书章节合并程序 ---")

    # 步骤 1: 检查源目录
    if not os.path.isdir(SOURCE_DIRECTORY):
        print(f"❌ 错误：源目录 '{SOURCE_DIRECTORY}' 未找到。")
        sys.exit(1)

    # 步骤 2: 获取并排序 .md 文件
    try:
        files_to_merge = sorted([f for f in os.listdir(SOURCE_DIRECTORY) if f.endswith('.md')])
    except OSError as e:
        print(f"❌ 错误：无法读取目录 '{SOURCE_DIRECTORY}'。详情: {e}")
        sys.exit(1)

    if not files_to_merge:
        print(f"⚠️ 警告：在目录 '{SOURCE_DIRECTORY}' 中没有找到任何 .md 文件。")
        return

    print(f"✅ 成功找到 {len(files_to_merge)} 个章节文件，将进行智能合并。")

    # 步骤 3: 开始合并流程
    try:
        with open(MERGED_FILENAME, 'w', encoding='utf-8') as outfile:
            current_main_chapter_id = None  # 用于追踪当前的一级标题编号

            for filename in files_to_merge:
                # 从文件名中解析出章节号和标题文本
                # 例如从 "1.1.1 虚拟化技术的定义.md" 解析
                match = re.match(r'(\d+\.\d+)\.(\d+)\s(.*)\.md', filename)
                if not match:
                    print(f"  - 警告：跳过格式不匹配的文件: {filename}")
                    continue

                main_id, sub_id, sub_title_text = match.groups()
                full_subsection_title = f"{main_id}.{sub_id} {sub_title_text}"

                # 步骤 3a: 检查是否需要插入新的一级标题
                if main_id != current_main_chapter_id:
                    # 检查映射表中是否存在该标题
                    if main_id in CHAPTER_MAP:
                        # 插入新的一级标题
                        main_title_text = CHAPTER_MAP[main_id]
                        # 对于第一个标题之外的标题，在前面加一些换行以增加间距
                        if current_main_chapter_id is not None:
                            outfile.write("\n\n---\n\n")
                        outfile.write(f"## {main_id} {main_title_text}\n\n")
                        print(f"\n插入新的一级标题: ## {main_id} {main_title_text}")
                        current_main_chapter_id = main_id
                    else:
                        print(f"  - 警告：在CHAPTER_MAP中找不到 {main_id} 的标题，将不插入一级标题。")

                # 步骤 3b: 插入二级标题
                # outfile.write(f"## {full_subsection_title}\n\n")
                # print(f"  -> 合并中: ## {full_subsection_title}")

                # 步骤 3c: 插入子文件的正文内容
                filepath = os.path.join(SOURCE_DIRECTORY, filename)
                with open(filepath, 'r', encoding='utf-8') as infile:
                    content = infile.read()
                    outfile.write(content)
                    # 在每个子章节后添加两个换行符
                    outfile.write("\n\n")

    except IOError as e:
        print(f"❌ 错误：写入文件 '{MERGED_FILENAME}' 时发生I/O错误。详情: {e}")
        sys.exit(1)

    final_path = os.path.abspath(MERGED_FILENAME)
    print(f"\n🎉 恭喜！所有章节已按层级结构成功合并。")
    print(f"最终的完整文稿已保存至: {final_path}")


if __name__ == "__main__":
    intelligent_merge()
