import os

report_filename = "report"
report_extension = "txt"

num_of_steps = 3

report_template = (
    "We made {total} observations by tossing a coin: {tails} were tails and {heads} were heads. "
    "The probabilities are {tail_frac}% and {head_frac}%, respectively. "
    "Our forecast is that the next {num_of_steps} observations will be: {pred_tails} tail and {pred_heads} heads."
)

tg_token = os.environ.get("TG_TOKEN")
tg_channel = os.environ.get("TG_CHANNEL")
tg_url = f"https://api.telegram.org/bot{tg_token}/sendMessage"

log_file = "analytics.log"