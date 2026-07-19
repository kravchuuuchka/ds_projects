def data_types():
    int_var = 28
    str_var = "school 21"
    float_var = 3.14
    bool_var = True
    list_var = [3, 6.66, "cat"]
    dict_var = {"i'm": 100, "school": 21, "penalty": False}
    tuple_var = (1984, "rayan gosling", 1.234)
    set_var = {1, 2, 3, 4, 4}
    types = [type(x) for x in [int_var, str_var, float_var, bool_var, list_var, dict_var, tuple_var, set_var,]]
    print("[" + ", ".join(t.__name__ for t in types) + "]")


if __name__ == "__main__":
    data_types()