import re

def extract_clauses_from_text(text: str):
    lines = text.splitlines()                                                   
    clauses, current = [], ""                                                   

    # Match clauses like (1). Clause text...
    pattern = re.compile(r'^\(\d+\)\.\s+.*')                                    

    for line in lines:
        line = line.strip()
        if not line:
            continue

        if pattern.match(line):
            if current:
                clauses.append(current.strip())
            current = line
        else:
            current += " " + line
    if current:
        clauses.append(current.strip())

    return clauses


def alpha_end_all_lines(text):
    lines = text.splitlines()
    lines_with_alpha = [line + 'α' for line in lines]
    return '\n'.join(lines_with_alpha)