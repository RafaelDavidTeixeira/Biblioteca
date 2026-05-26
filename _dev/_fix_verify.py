import os

files = ['app/templates/app.html', 'app/static/js/app.js']
corrupted_patterns = ['\u00e3', '\u00e7', '\u00e9', '\u00e1', '\u00f3', '\u00fa', '\u00f5', '\u00ea', '\u00e2', '\u00f4', '\u00ed', '\u00ba', '\u00aa']
# These are the CORRECT accented chars - we want to verify they appear (not corrupted versions)

# Now check for mojibake patterns (UTF-8 bytes viewed as Latin-1)
mojibake = ['\u00c3', '\u00c7', '\u00c9', '\u00c1', '\u00d3', '\u00da', '\u00d5', '\u00ca', '\u00c2', '\u00d4', '\u00cd', '\u00b0']

for path in files:
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    found_moji = []
    for pat in mojibake:
        if pat in content:
            found_moji.append(repr(pat))
    if found_moji:
        print(f"{os.path.basename(path)}: AINDA TEM MOJIBAKE: {', '.join(found_moji)}")
    else:
        print(f"{os.path.basename(path)}: OK - sem mojibake")

    # Verify correct chars exist
    for correct, moji in [('Licen\u00e7a', 'Licen\u00c3\u00a7a'), ('Empr\u00e9stimos', None)]:
        if correct in content:
            pass
