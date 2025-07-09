#!/usr/bin/env python3
"""
jed2eq.py

Reads a .jed via JedFile, then converts it into
Boolean equations (sum-of-products) for outputs Y1–Y8,
printing each product term on its own line.
"""

import re
import sys
import argparse

class JedFile:
    _RE_ST = re.compile(r"^ST(.+?)(?:\*|$)")
    _RE_QF = re.compile(r"^QF(\d+)")
    _RE_C  = re.compile(r"^C([0-9A-Fa-f]+)")
    _RE_L  = re.compile(r"^L(\d+)\*")

    def __init__(self):
        self.part_number      = None
        self.fuse_count       = 0
        self.default_fuse     = 0
        self.fuses            = []
        self.checksum_section = None
        self.checksum_file    = None

    def parse(self, text):
        current_index = 0
        for raw in text.splitlines():
            line = raw.strip()
            if not line:
                continue

            c0 = line[0]
            if c0 == "S":  # ST...*
                m = self._RE_ST.match(line)
                if m:
                    self.part_number = m.group(1).strip()

            elif c0 == "Q":  # QFnnn*
                m = self._RE_QF.match(line)
                if m:
                    self.fuse_count = int(m.group(1))
                    self.fuses = [self.default_fuse] * self.fuse_count

            elif line.startswith("F0"):
                self.default_fuse = 0
                if self.fuses:
                    self.fuses[:] = [0]*self.fuse_count
            elif line.startswith("F1"):
                self.default_fuse = 1
                if self.fuses:
                    self.fuses[:] = [1]*self.fuse_count

            elif c0 == "C":  # C...*
                nums = re.findall(r"[0-9A-Fa-f]+", line)
                if nums:
                    sec = nums[0]
                    base = 16 if any(ch.isalpha() for ch in sec) else 10
                    self.checksum_section = int(sec, base)
                    if len(nums) > 1:
                        fl = nums[1]
                        base2 = 16 if any(ch.isalpha() for ch in fl) else 10
                        self.checksum_file = int(fl, base2)

            elif c0 == "L":  # Lxxxx*
                m = self._RE_L.match(line)
                if m:
                    current_index = int(m.group(1))

            elif c0 in "01":  # fuse bits
                for ch in line:
                    if ch in "01" and 0 <= current_index < self.fuse_count:
                        self.fuses[current_index] = int(ch)
                        current_index += 1

    def __repr__(self):
        return (f"<JedFile part={self.part_number!r} fuses={self.fuse_count} "
                f"sect_ck={self.checksum_section} file_ck={self.checksum_file}>")

def parse_product(bits40):
    """
    bits40: list of 40 ints (0 or 1).
    returns list of literals (A1–A16), skipping invalid pairs.
    """
    lits = []
    for i in range(16):
        a, na = bits40[2*i], bits40[2*i+1]
        if   (a, na) == (0,1):
            lits.append(f"A{i+1}")
        elif (a, na) == (1,0):
            lits.append(f"!A{i+1}")
        else:
            # skip this literal pair
            continue
    return lits

def main():
    p = argparse.ArgumentParser(
        description="Convert a .jed to Boolean equations Y1–Y8"
    )
    p.add_argument('jed_file', help="path to the .jed file")
    args = p.parse_args()

    try:
        text = open(args.jed_file, "r", encoding="utf-8", errors="ignore").read()
        jed = JedFile()
        jed.parse(text)
    except Exception as e:
        print(f"Error reading/parsing JED: {e}", file=sys.stderr)
        sys.exit(1)

    total = jed.fuse_count
    bits = jed.fuses

    # Expect (40 * n) + 8 = total
    if (total - 8) % 40 != 0:
        print(f"Unexpected fuse count: {total}. Should be 40*n + 8.", file=sys.stderr)
        sys.exit(1)

    rows = (total - 8) // 40
    prod_rows = [ bits[i*40:(i+1)*40] for i in range(rows) ]
    inv_mask  = bits[rows*40 : rows*40 + 8]

    # Build sum-of-products map for Y1–Y8
    eq_map = { f"Y{i+1}": [] for i in range(8) }
    for row in prod_rows:
        lits = parse_product(row)
        if not lits:
            continue
        term = " & ".join(lits)
        for i in range(8):
            if row[32 + i] == 0:   # include in Y{i+1} when bit is 0
                eq_map[f"Y{i+1}"].append(f"({term})")

    # Print each Y1–Y8, listing each product term on its own line
    for i in range(8):
        y = f"Y{i+1}"
        terms = eq_map[y]
        inverted = bool(inv_mask[i])

        if not terms:
            const = "0"
            if inverted:
                print(f"{y} = !({const})")
            else:
                print(f"{y} = {const}")
            continue

        if inverted:
            # inverted: open with '!( ' ... then close with ');' on its own line
            print(f"{y} = !(")
            for idx, term in enumerate(terms):
                prefix = "  + " if idx > 0 else "  "
                print(f"{prefix}{term}")
            print(");")
        else:
            # non-inverted: open, then list terms, appending ';' to the last term
            print(f"{y} =")
            for idx, term in enumerate(terms):
                prefix = "  + " if idx > 0 else "  "
                if idx == len(terms) - 1:
                    # last term: put semicolon here
                    print(f"{prefix}{term};")
                else:
                    print(f"{prefix}{term}")

if __name__ == "__main__":
    main()
