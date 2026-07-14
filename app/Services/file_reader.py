
from pathlib import Path

SUPPORTED_EXTENSIONS = {
    ".py", ".js", ".ts", ".tsx", ".jsx", ".go", ".java", 
    ".cpp", ".c", ".cs", ".php", ".rb", ".rs", ".swift", ".kt"
}

IGNORED_DIRS = {
    ".git", "node_modules", "venv", ".venv", "dist", 
    "build", "__pycache__", ".idea", ".vscode"}

MAX_FILES = 30
MAX_CHARS_PER_FILE = 3000

def read_repo(repo_path: str)->str:
    root_path = Path(repo_path)
    output_segments = []
    file_count = 0

    for file_path in root_path.rglob("*"):
        if file_count >= MAX_FILES:
            break

        if not file_path.is_file():
            continue
        if any(part in IGNORED_DIRS for part in file_path.parts):
            continue 
        if file_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue
        try:
            
            content = file_path.read_text(encoding="utf-8", errors="ignore")
            
            
            truncated_content = content[:MAX_CHARS_PER_FILE]
            if len(content) > MAX_CHARS_PER_FILE:
                truncated_content += "\n[... Content truncated due to length limits ...]"

            
            relative_display_name = file_path.relative_to(root_path)

            
            file_block = (
                f"===== {relative_display_name} =====\n"
                f"{truncated_content}\n"
                f"====================\n\n"
            )
            
            output_segments.append(file_block)
            file_count += 1

        except Exception:
           
            continue

   
    return "".join(output_segments).strip()

