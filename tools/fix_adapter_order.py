"""Reorder mini_gemini_adapter.py: docker subclass must follow the base class."""
from pathlib import Path

p = Path("sentinelbench/adapters/mini_gemini_adapter.py")
text = p.read_text(encoding="utf-8")
start = text.index("class DockerMiniGeminiAdapter")
end = text.index("class MiniGeminiAdapter:")
docker_cls = text[start:end]
rest = text[:start] + text[end:]
p.write_text(rest.rstrip() + "\n\n\n" + docker_cls.rstrip() + "\n",
             encoding="utf-8", newline="\n")
print("reordered ok")
