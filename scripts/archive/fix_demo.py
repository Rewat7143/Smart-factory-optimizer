with open('backend/api/demo.py', 'r') as f:
    lines = f.readlines()

out = []
in_try = False
for line in lines:
    if line.strip() == "try:":
        out.append(line)
        in_try = True
    elif line.strip() == "except Exception as e:":
        in_try = False
        out.append(line)
    elif in_try:
        if line.strip() == "":
            out.append("\n")
        else:
            out.append("    " + line)
    else:
        out.append(line)

with open('backend/api/demo.py', 'w') as f:
    f.writelines(out)
