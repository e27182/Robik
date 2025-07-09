{
    'num_inputs': 15,  # number of inputs (A1, A2, ..., A15)

    # 0-based → 0-based mapping
    # e.g. A1 should come from the original A10, etc.
    'address_map': { # zero-based index
        7: 12, # A7 (in RT2) comes from A12 (in 27C512)
        6: 7,
        5: 6,
        4: 5,
        3: 4,
        2: 3,
        1: 2,
        0: 1,
        15: 0,
        14: 10,
        13: 15,
        12: 11,
        11: 9,
        10: 8,
        9: 13,
        8: 14
        # any inputs not listed here will map to themselves
    },

    # 0-based → 0-based mapping for outputs (D-lines)
    # e.g. logical output Y1 goes to physical D0, Y1→D0, etc.
    'data_map': {
        0: 6, # Y0 (in RT2) comes from D6 (in 27C512)
        1: 5,
        2: 4,
        3: 3,
        4: 2,
        5: 1,
        6: 0,
        7: 7
        # any outputs not listed will map to themselves
    }
}