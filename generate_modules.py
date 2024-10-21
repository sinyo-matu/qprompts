import os
import re
from jinja2 import Template, TemplateSyntaxError, Environment, meta
from frontmatter import Frontmatter
import inspect


def to_pascal_case(name):
    # アンダースコアとハイフンを空白に置換し、各単語の先頭を大文字にする
    words = re.split(r"[_-]", name)
    return "".join(word.capitalize() for word in words)


def get_module_path(file_path, source_dir, target_dir):
    relative_path = os.path.relpath(file_path, source_dir)
    module_path = os.path.join(
        "prompt_class", os.path.splitext(relative_path)[0] + ".py"
    )
    return os.path.join(target_dir, module_path)


def get_template_parameters(template_dict):
    params = set()
    env = Environment()
    for template_str in template_dict.values():
        if not template_str:
            continue
        try:
            ast = env.parse(template_str)
            params.update(meta.find_undeclared_variables(ast))
        except TemplateSyntaxError:
            print(f"Warning: Invalid template syntax in: {template_str[:50]}...")
    return list(params)


def process_prompty_file(file_path, source_dir, target_dir):
    module_path = get_module_path(file_path, source_dir, target_dir)

    prompty_content = Frontmatter.read_file(file_path)
    attributes = prompty_content["attributes"]
    body = prompty_content["body"]

    # ファイル名をPascalCaseに変換してインスタンス名として使用
    file_name = os.path.splitext(os.path.basename(file_path))[0]
    class_name = to_pascal_case(file_name)

    sample_params = get_template_parameters(
        attributes.get("sample", {}).get("chat_history", {})
    )
    body_params = get_template_parameters(body)

    # Pythonファイルとして保存
    os.makedirs(os.path.dirname(module_path), exist_ok=True)
    with open(module_path, "w") as f:
        f.write(
            "from prompt_structure import PromptStructure, Model, ModelConfiguration, ModelParameters, ChatMessage, ChatRole\n"
        )
        f.write("from typing import list\n\n")
        f.write(f"class {class_name}(PromptStructure):\n")
        f.write("    def __init__(self):\n")
        f.write("        super().__init__(\n")
        f.write(f"            name={repr(attributes.get('name', ''))},\n")
        f.write(f"            description={repr(attributes.get('description'))},\n")
        f.write(f"            authors={repr(attributes.get('authors', []))},\n")

        # モデル情報の構造化
        model_data = attributes.get("model", {})
        f.write("            model=Model(\n")
        f.write(f"                api={repr(model_data.get('api'))},\n")
        f.write("                configuration=ModelConfiguration(\n")
        f.write(
            f"                    type={repr(model_data.get('configuration', {}).get('type'))},\n"
        )
        f.write(
            f"                    name={repr(model_data.get('configuration', {}).get('name'))}\n"
        )
        f.write("                ),\n")
        f.write("                parameters=ModelParameters(\n")
        for param, value in model_data.get("parameters", {}).items():
            f.write(f"                    {param}={repr(value)},\n")
        f.write("                )\n")
        f.write("            ),\n")
        f.write(f"            sample={repr(attributes.get('sample', {}))},\n")
        f.write(f"            body={repr(body)},\n")
        f.write("        )\n\n")

        # Add render methods
        if sample_params:
            f.write(
                f"    def render_sample(self, {', '.join(f'{param}: str' for param in sample_params)}) -> list[ChatMessage]:\n"
            )
            f.write(
                f"        return super().render_sample({', '.join(f'{param}={param}' for param in sample_params)})\n\n"
            )

        if body_params:
            f.write(
                f"    def render_body(self, {', '.join(f'{param}: str' for param in body_params)}) -> list[ChatMessage]:\n"
            )
            f.write(
                f"        return super().render_body({', '.join(f'{param}={param}' for param in body_params)})\n"
            )

    print(f"Created Python file: {module_path}")


def create_module(source_dir, target_dir):
    for root, dirs, files in os.walk(source_dir):
        for file in files:
            if file.endswith(".prompty"):
                file_path = os.path.join(root, file)
                process_prompty_file(file_path, source_dir, target_dir)

        for dir in dirs:
            init_path = os.path.join(
                target_dir,
                "prompt_class",
                os.path.relpath(os.path.join(root, dir), source_dir),
                "__init__.py",
            )
            os.makedirs(os.path.dirname(init_path), exist_ok=True)
            open(init_path, "a").close()
            print(f"Created __init__.py: {init_path}")

    root_init_path = os.path.join(target_dir, "prompt_class", "__init__.py")
    open(root_init_path, "a").close()
    print(f"Created root __init__.py: {root_init_path}")


if __name__ == "__main__":
    source_dir = os.path.join(os.getcwd(), "prompts")
    target_dir = os.getcwd()
    if os.path.exists(source_dir):
        create_module(source_dir, target_dir)
    else:
        print("prompts directory not found in the current working directory.")
