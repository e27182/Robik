{
    'num_inputs': 15,  # number of inputs (A1, A2, ..., A15)

    # 0-based → 0-based mapping
    # e.g. A1 should come from the original A10, etc.
    'address_map': { # zero-based index
        # any inputs not listed here will map to themselves
    },

    # 0-based → 0-based mapping for outputs (D-lines)
    # e.g. logical output Y1 goes to physical D0, Y1→D0, etc.
    'data_map': {
        # any outputs not listed will map to themselves
    }
}