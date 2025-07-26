import os
from openai import OpenAI

def generate_secondary_outline():
    # 填写 API Key
    api_key = "eaxxxxxxxxxxxxxxxxxxxxxxx15"
    if not api_key:
        raise ValueError("请先在环境变量中设置 ARK_API_KEY")

    # 初始化 Ark 客户端
    client = OpenAI(
        base_url="https://ark.cn-beijing.volces.com/api/v3",
        api_key=api_key
    )

    # 一级目录列表
    primary_sections = [
        "1.1 虚拟化与容器",
        "1.2 容器镜像管理",
        "1.3 容器存储管理",
        "1.4 容器网络管理",
        "1.5 容器安全管理",
        "1.6 容器运行时生态",
        "1.7 容器化思维"
    ]

    # 构造 Prompt
    prompt = (
        "你是一个技术文档专家，擅长对“容器资源管理”进行概念性、原理性框架设计。"
        "本次任务：\n"
        "- 输入：我提供了一级章节列表，需你根据每节主题，扩展为3–6个二级小节。\n"
        "- 输出：符合技术书写习惯的 Markdown 目录，二级节点有清晰层次和简短标题。\n"
        "- 风格：只写概念、设计、原理等，不包含任何命令行、配置或实战案例细节。\n\n"
        "一级目录：\n"
        + "\n".join(primary_sections)
    )

    # 发起对话补全请求
    response = client.chat.completions.create(
        model="doubao-seed-1-6-flash-250715",
        messages=[{"role": "user", "content": prompt}],
    )

    outline_md = response.choices[0].message.content
    return outline_md

if __name__ == "__main__":
    try:
        markdown = generate_secondary_outline()
        # 输出结果到标准输出
        print(markdown)
        # 同时保存到文件
        with open("secondary_outline.md", "w", encoding="utf-8") as f:
            f.write(markdown)
        print("\\n已生成并保存：secondary_outline.md")
    except Exception as e:
        print(f"错误：{e}")
