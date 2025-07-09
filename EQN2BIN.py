#!/usr/bin/env python3
import re
import sys

# Parses an ABEL expression, remapping inputs via address_map dict
def parse_abel_expression(expr: str, num_inputs, address_map):
    expr = expr.replace("!", "not ")
    expr = expr.replace("&", "and")
    expr = expr.replace("|", "or")
    expr = expr.replace("+", "or")

    # build mapping A1..A{NUM_INPUTS} → physical bit
    bit_index = {f"A{i}": address_map.get(i-1, i-1) for i in range(1, num_inputs+1)}
    for name, bit in bit_index.items():
        expr = re.sub(rf"\b{name}\b", f"((addr >> {bit}) & 1)", expr)

    return eval(f"lambda addr: int({expr.strip()})")

# Load ABEL equations from file and produce {name: func}
def load_equations(eqn_file, num_inputs,address_map):
    outputs = {}
    with open(eqn_file) as f:
        buf = ""
        for line in f:
            s = line.strip()
            if not s or s.startswith("#"): continue
            buf += " " + s
            if ";" in s:
                full = buf.strip(); buf = ""
                if "=" in full:
                    name, expr = full.split("=",1)
                    outputs[name.strip()] = parse_abel_expression(expr.rstrip("; "), num_inputs, address_map)
    return outputs

# Generate truth table list of (addr, value)
def generate_truth_table(outputs, num_inputs, data_map):
    funcs = list(outputs.values())
    table = []
    for addr in range(1 << num_inputs):
        val = 0
        for i, fn in enumerate(funcs):
            bit = fn(addr) & 1
            phys = data_map.get(i, i)
            val |= bit << phys
        table.append((addr, val))
    return table

# Write binary firmware
def save_to_bin(table, bits, fname):
    with open(fname, "wb") as f:
        bw = (bits + 7)//8
        for _, v in table:
            f.write(v.to_bytes(bw, 'little'))
    print(f"✔ {fname} written")

# Main: takes ABEL file and a maps file defining num_inputs, address_map & data_map
def main():
    if len(sys.argv) < 3:
        print("Usage: python EQN2BIN.py <ABEL_EQN.txt> <maps.py> [out.bin]")
        sys.exit(1)

    eqn_file = sys.argv[1]
    maps_file = sys.argv[2]

    try:
        text = open(maps_file).read()
        maps = eval(text, {})

        # extract parameters
        num_inputs = maps['num_inputs']
        address_map = maps['address_map']
        data_map = maps['data_map']
    except Exception as e:
        print(f"Error loading maps: {e}")
        sys.exit(1)

    out_bin = sys.argv[4] if len(sys.argv)>4 else "firmware.bin"

    outputs = load_equations(eqn_file, num_inputs, address_map)
    tbl = generate_truth_table(outputs, num_inputs, data_map)
    names = list(outputs.keys())
    bits = len(names)

    save_to_bin(tbl, bits, out_bin)

if __name__ == "__main__":
    main()
