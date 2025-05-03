import os

with open("structure.txt", 'w', encoding='utf-8') as f:
    f.write('FTR/\n')
    f.write('    .gitignore\n')
    f.write('    .python-version\n')
    f.write('    LICENSE\n')
    f.write('    README.md\n')
    f.write('    requirements.txt\n')
    
    paths = ["assets", "configs", "projects", "src"]
    for path in paths:    
        if not os.path.exists(path):
            continue
        for root, dirs, files in os.walk(path):
            if "__pycache__" in root:
                continue
            nivel = root.replace(path, '').count(os.sep)
            indentacao = '    ' * (nivel + 1)
            f.write(f'{indentacao}{os.path.basename(root)}/\n')
            for nome in files:
                f.write(f'{indentacao}    {nome}\n')
