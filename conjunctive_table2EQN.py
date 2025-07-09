import re
import sys

def parse_matrix(lines):
    # split into input and output sections
    in_inputs = True
    input_rows, output_rows = [], []
    for line in lines:
        m_in = re.match(r"\|\s*(A\d+)\s*\|(.+)\|", line)
        m_out = re.match(r"\|\s*(?:\^?Y\d+)\s*\|(.+)\|", line)
        if m_in:
            row = m_in.group(1)
            data = m_in.group(2)
            # remove separators and spaces
            pattern = re.sub(r"[^01\.*]", "", data)
            input_rows.append((row, pattern))
        elif m_out:
            # capture full label
            label = re.match(r"\|\s*(\^?Y\d+)", line).group(1)
            data = m_out.group(1)
            pattern = re.sub(r"[^A-]", "", data)
            output_rows.append((label, pattern))
    return input_rows, output_rows

def build_product_terms(input_rows):
    terms = {}
    n = len(input_rows[0][1])
    for i in range(n):
        lits = []
        for var, pat in input_rows:
            c = pat[i]
            if c == '1':
                lits.append(var)
            elif c == '0':
                lits.append('!' + var)
            # skip '.' and '*'
        if lits:
            terms[i+1] = ' & '.join(lits)
        else:
            terms[i+1] = ''  # skip empty term
            print(f"Warning: term {i+1} is empty (no variables used)")
    return terms

def build_equations(output_rows, terms):
    # eqs = []
    # for label, pat in output_rows:
    #     name = label.lstrip('^')
    #     idxs = [str(i+1) for i, c in enumerate(pat) if c == 'A']
    #     filtered_idxs = [i for i in idxs if terms[int(i)]]
    #     if not filtered_idxs:
    #         rhs = '0'
    #     else:
    #         groups = [f"{terms[int(i)]} +" for i in filtered_idxs]
    #         groups[-1] = groups[-1].rstrip(' +')  # remove trailing plus from the last term
    #         rhs = '\n       '.join(groups)
    #     eqs.append(f"{name} = {rhs};")
    # return eqs
    eqs = []
    for label, pat in output_rows:
        name     = label.lstrip('^')
        inverted = label.startswith('^')

        # collect only those indices that actually have a non-empty term
        idxs = [i+1 for i, c in enumerate(pat) if c == 'A' and terms[i+1]]
        # build each product term as "(…)"
        products = [f"({terms[i]})" for i in idxs]

        # if no terms, treat as constant 0
        if not products:
            body = "0"
            eqs.append(f"{name} = {body}")
            continue

        # indent & prefix
        lines = []
        for k, prod in enumerate(products):
            prefix = '  + ' if k > 0 else '  '
            lines.append(f"{prefix}{prod}")

        # stitch together
        if inverted:
            eq = f"{name} = !(\n" + "\n".join(lines) + "\n)"
        else:
            eq = f"{name} =\n" + "\n".join(lines)

        eqs.append(eq)
    return eqs

def main():
    if len(sys.argv) != 3:
        print("Usage: python parse_to_eqn.py <input.txt> <output.eqn>")
        return
    with open(sys.argv[1], 'r', encoding='utf-8') as f:
        lines = f.readlines()
    inputs, outputs = parse_matrix(lines)
    terms = build_product_terms(inputs)
    eqs = build_equations(outputs, terms)

    with open(sys.argv[2], 'w', encoding='utf-8') as f:
        for eq in eqs:
            f.write(eq + ';\n')
    print(f"Written {len(eqs)} equations to {sys.argv[2]}")

if __name__ == '__main__':
    main()