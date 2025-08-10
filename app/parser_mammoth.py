import re
import mammoth

# Mapeia estilos PT/EN de Word para headings reais
DEFAULT_STYLE_MAP = """
p[style-name='Title'] => h1:fresh
p[style-name='Título 1'] => h1:fresh
p[style-name='Heading 1'] => h1:fresh
p[style-name='Título 2'] => h2:fresh
p[style-name='Heading 2'] => h2:fresh
p[style-name='Título 3'] => h3:fresh
p[style-name='Heading 3'] => h3:fresh
"""

def to_markdown(path: str, style_map: str = DEFAULT_STYLE_MAP):
    with open(path, "rb") as f:
        result = mammoth.convert_to_markdown(f, style_map=style_map)
    return {
        "markdown": result.value.strip(),
        "warnings": [m.message for m in result.messages],
    }

def to_html(path: str, style_map: str = DEFAULT_STYLE_MAP):
    with open(path, "rb") as f:
        result = mammoth.convert_to_html(f, style_map=style_map)
    return {
        "html": result.value,
        "warnings": [m.message for m in result.messages],
    }

def md_to_text(md: str) -> str:
    # TXT simples para prompt (remove marcações básicas)
    md = re.sub(r"```.*?```", "", md, flags=re.S)                # code blocks
    md = re.sub(r"`[^`]+`", "", md)                              # inline code
    md = re.sub(r"!\[.*?\]\(.*?\)", "", md)                      # imagens
    md = re.sub(r"\[([^\]]+)\]\(.*?\)", r"\1", md)               # links
    md = re.sub(r"^[#>\-\*\+]+\s*", "", md, flags=re.M)          # prefixos
    md = md.replace("|", "\t")                                    # tabelas -> tabs
    md = re.sub(r"\n{3,}", "\n\n", md)
    return md.strip()
