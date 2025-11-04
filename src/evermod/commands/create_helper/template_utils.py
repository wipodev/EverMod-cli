from jinja2 import Template
from pathlib import Path

def render_template(template_path: Path, context: dict, output_path: Path):
    """Render a Jinja2 template and write to destination."""
    with open(template_path, encoding="utf-8") as f:
        template = Template(f.read())
    result = template.render(context)
    output_path.write_text(result, encoding="utf-8")
