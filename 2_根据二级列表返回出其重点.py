import os
import re
from openai import OpenAI
from pathlib import Path


import re

def load_sections_with_parent(md_path):
    """
    返回一个列表，每项是 (parent_idx, parent_title, idx, title)
    """
    sections = []
    parent_idx = parent_title = None
    p1 = re.compile(r'^\s*(\d+\.\d+)\s+(.*)')       # 一级或二级
    p2 = re.compile(r'^\s*(\d+\.\d+\.\d+)\s+(.*)')  # 三级小节
    with open(md_path, encoding='utf-8') as f:
        for line in f:
            m1 = p1.match(line)
            if m1 and line.strip().count('.') == 1:
                parent_idx, parent_title = m1.groups()
            m2 = p2.match(line)
            if m2 and parent_idx:
                idx, title = m2.groups()
                sections.append((parent_idx, parent_title, idx, title))
    return sections


def generate_keypoints_for_section(client, parent_idx, parent_title, idx, title):
    prompt = (
        f"你是资深技术文档写作专家。\n"
        f"- 父章节：{parent_idx} {parent_title}\n"
        f"- 子章节：{idx} {title}\n\n"
        "输出格式：\n"
        "1. 一段 200-300 字的背景导入；\n"
        "2. 列表形式呈现 5-8 条核心要点，每条约 50-80 字；\n"
        "禁止出现任何命令、代码或实战案例。\n"
    )

    response = client.chat.completions.create(
        model="doubao-seed-1-6-flash-250715",
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content
    # rest unchanged


def main():
    # 环境变量读取
    api_key = "eaxxxxxxxxxxxxxxxxxxx15"
    if not api_key:
        raise ValueError("请先在环境变量中设置 ARK_API_KEY")

    client = OpenAI(
        base_url="https://ark.cn-beijing.volces.com/api/v3",
        api_key=api_key
    )

    # 读取二级目录
    md_file = Path("secondary_outline.md")
    if not md_file.exists():
        raise FileNotFoundError("请先运行 generate_outline.py 来生成 secondary_outline.md")

    subsections = load_sections_with_parent(md_file)

    # 输出目录
    output_dir = Path("keypoints")
    output_dir.mkdir(exist_ok=True)

    # 假设你已经把 load_subsections() 改为 load_sections_with_parent(),
    # 返回值变成列表 items = [(parent_idx, parent_title, idx, title), …]

    # 合并所有要点概览
    with open(output_dir / "all_keypoints.md", "w", encoding="utf-8") as summary_f:
        for parent_idx, parent_title, idx, title in subsections:
            print(f"正在生成: {idx} {title} （父：{parent_idx} {parent_title}）")
            # 把父章节也带进 Prompt
            content = generate_keypoints_for_section(
                client,
                parent_idx, parent_title,
                idx, title
            )
            # 单独保存
            filename = output_dir / f"{idx}_keypoints.md"
            with open(filename, "w", encoding="utf-8") as f:
                # 先写父-子标题层级
                f.write(f"# {parent_idx} {parent_title}\n")
                f.write(f"## {idx} {title}\n\n")
                f.write(content)
            # 写入汇总
            summary_f.write(f"# {parent_idx} {parent_title}\n")
            summary_f.write(f"## {idx} {title}\n\n")
            summary_f.write(content + "\n\n")
        print("要点概览生成完毕，见 keypoints/ 目录。")


if __name__ == "__main__":
    main()
