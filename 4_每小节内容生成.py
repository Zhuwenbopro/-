import re
import os
import time
from openai import OpenAI

# --- 1. API 客户端初始化 ---
API_KEY = "eaxxxxxxxxxxxxxxxxxxx15"  # 在此替换为您的 API Key（如果未使用环境变量）
if API_KEY == "eaxxxxxxxxxxxxxxxx15":
    print("⚠️ 警告：正在使用占位符 API Key。请设置 ARK_API_KEY 环境变量或直接在脚本中修改 API_KEY。")

try:
    client = OpenAI(
        base_url="https://ark.cn-beijing.volces.com/api/v3",
        api_key=API_KEY,
    )
    print("✅ API 客户端初始化成功。")
except Exception as e:
    print(f"❌ API 客户端初始化失败: {e}")
    exit()


def parse_input_file_enhanced(file_path: str) -> list[dict]:
    """
    [修改点 1: 函数增强]
    解析输入文件，额外捕获每个小节的父标题和背景导入。
    """
    print(f"📄 正在读取和解析输入文件: {file_path}")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"❌ 错误：输入文件未找到 -> {file_path}")
        return []

    # 按一级标题（# ...）分割文档，得到每个大章节的内容块
    chapters = re.split(r'\n(?=# )', content)
    parsed_sections = []

    for chapter_content in chapters:
        if not chapter_content.strip():
            continue

        # 提取父标题
        parent_title_match = re.search(r'# (.*?)\n', chapter_content)
        parent_title = parent_title_match.group(1).strip() if parent_title_match else "未知章节"

        # 在当前章节内，按二级标题（## ...）分割出各个小节
        sections_raw = re.split(r'\n(?=## )', chapter_content)

        for raw_section in sections_raw:
            if not raw_section.strip().startswith("##"):
                continue

            # 提取小节标题
            title_match = re.search(r"## (.*?)\n", raw_section)
            if not title_match: continue
            title = title_match.group(1).strip()

            # 提取背景导入
            background_match = re.search(r"### 背景导入\s*\n(.*?)(?=\n###)", raw_section, re.DOTALL)
            background = background_match.group(1).strip() if background_match else ""

            # 提取核心要点
            points_block_match = re.search(r"### (?:核心要点|核心特性)\s*\n([\s\S]*)", raw_section)
            if not points_block_match: continue
            points_block = points_block_match.group(1)
            points = [p.strip() for p in re.findall(r"-\s(.*?)(?:\n|$)", points_block)]

            if title and points:
                parsed_sections.append({
                    "parent_title": parent_title,
                    "section_title": title,
                    "background": background,
                    "points": points
                })
                print(f"  - ✅ 已成功解析: [{parent_title}] -> [{title}]")

    return parsed_sections


def generate_prompt_for_section_enhanced(section: dict) -> str:
    """
    [修改点 2: Prompt 模板升级]
    根据增强后的小节数据，生成上下文更丰富的 Prompt。
    """
    parent_title = section["parent_title"]
    section_title = section["section_title"]
    background = section["background"]
    points = section["points"]

    points_str = "\n".join([f"    {i + 1}. {point}" for i, point in enumerate(points)])

    # 全新设计的、上下文更丰富的 Prompt 模板
    prompt_template = f"""
你是世界级的技术战略顾问和标书撰写专家，正在为一份关于“容器资源管理”的20万字标书撰写关键章节。你的文字风格沉稳、专业、具有高度的逻辑性和说服力，能够将复杂的技术概念转化为流畅、连贯的商业和技术论述。

**写作任务上下文：**

- **所属大章节**：`{parent_title}`
- **当前小节标题**：`{section_title}`
- **本小节的背景介绍（这是你论述的起点和情景）**：
  {background}
- **核心思想与关键概念（请将以下所有概念自然地、无缝地融入到一个连贯的段落式叙述中，而不是分点罗列）**：
  `{points_str}`

**输出要求：**

1.  **【首要】写作形式**：请以**流畅的、连续的段落**形式撰写全文。**避免使用任何分点、列表（如 -、*）或数字层级标题（如 1.1, 1.2）**。将所有概念有机地组织和串联起来，形成一篇完整的、一体化的论述。
2.  **【核心】内容融合**：确保上文提供的“核心思想与关键概念”都已在文中得到充分且深入的探讨，让它们之间的逻辑关系自然呈现。
3.  **总字数**：请将内容扩展至 5000–8000 字。
4.  **写作风格**：保持严谨、专业的商业技术白皮书风格，行文流畅，逻辑严密。
5.  **内容禁忌**：绝对不能包含任何命令行、代码片段、配置文件或具体的实战操作示例。
"""
    return prompt_template.strip()


def call_llm_api(prompt: str) -> str:
    """
    调用火山方舟 LLM API 生成详细内容。
    (此函数无需修改)
    """
    print("    - ⚙️  正在调用火山方舟 LLM API...")
    try:
        response = client.chat.completions.create(
            model="doubao-seed-1-6-flash-250715",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )
        print("    - ✅ API 调用成功，内容已生成。")
        return response.choices[0].message.content
    except Exception as e:
        print(f"    - ❌ API 调用失败: {e}")
        return f"API 调用时发生错误: {e}"


def main():
    """
    主执行函数，串联整个工作流。
    """
    input_file = "cleaned_output.md"
    output_dir = "output_stage3_final"  # 使用新目录

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"📁 已创建输出目录: {output_dir}")

    # 使用增强版的解析函数
    sections = parse_input_file_enhanced(input_file)
    if not sections:
        print("❌ 未能从输入文件中解析出任何有效小节，程序退出。")
        return

    print(f"\n🚀 开始通过【增强版 Prompt】处理 {len(sections)} 个小节...\n")

    total_start_time = time.time()
    for i, section in enumerate(sections):
        section_start_time = time.time()
        print(f"--- 处理第 {i + 1}/{len(sections)} 节: {section['section_title']} ---")

        # 使用增强版的 Prompt 生成函数
        prompt = generate_prompt_for_section_enhanced(section)

        # 为了调试，可以选择性地打印生成的Prompt
        # print("    - 📝 生成的 Prompt 如下:\n", prompt, "\n")
        print("    - 📝 已生成上下文增强的 Prompt。")

        detailed_content = call_llm_api(prompt)

        safe_filename = re.sub(r'[\\/*?:"<>|]', "", section["section_title"])
        output_path = os.path.join(output_dir, f"{safe_filename}.md")

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(detailed_content)

        section_end_time = time.time()
        print(f"    - 💾 已将详细内容保存至: {output_path}")
        print(f"    - ⏱️  本节耗时: {section_end_time - section_start_time:.2f} 秒。\n")


    total_end_time = time.time()
    print("🎉 全部处理完成！")
    print(f"所有小节的详细内容已通过 API 生成并保存在 '{output_dir}' 文件夹中。")
    print(f"⏱️  总计耗时: {total_end_time - total_start_time:.2f} 秒。")


if __name__ == "__main__":
    main()
