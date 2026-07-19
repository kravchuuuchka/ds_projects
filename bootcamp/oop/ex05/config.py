num_of_steps = 10

report_filename = "report1"
report_extension = "txt"

report_template = (
    "We made {total} observations by tossing a coin: {tails} were tails and {heads} were heads. "
    "The probabilities are {tail_frac}% and {head_frac}%, respectively. "
    "Our forecast is that the next {num_of_steps} observations will be: {pred_tails} tail and {pred_heads} heads."
)