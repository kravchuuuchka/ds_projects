import sys
from analytics import Research
from config import num_of_steps, report_filename, report_extension, report_template


def make_report(path: str, has_header: bool = True) -> None:
    research = Research(path)
    data = research.file_reader(has_header=has_header)
    analytics = Research.Analytics(data)

    heads, tails = analytics.counts()
    head_pct, tail_pct = analytics.percentages(heads, tails)
    predictions = analytics.predict_random(num_of_steps)
    pred_heads = sum(row[0] for row in predictions)
    pred_tails = sum(row[1] for row in predictions)
    total = heads + tails

    report = report_template.format(
        total=total,
        heads=heads,
        tails=tails,
        head_frac=head_pct,
        tail_frac=tail_pct,
        num_of_steps=num_of_steps,
        pred_heads=pred_heads,
        pred_tails=pred_tails,
    )

    analytics.save_file(report, report_filename, report_extension)


if __name__ == '__main__':
    try:
        if len(sys.argv) not in (2, 3):
            raise ValueError("Usage: python3 make_report.py <path_to_csv> [true|false]")
        if len(sys.argv) == 3:
            if sys.argv[2].lower() not in ("true", "false"):
                raise ValueError("Second argument must be 'true' or 'false'")
            make_report(sys.argv[1], has_header=sys.argv[2].lower() == "true")
        else:
            make_report(sys.argv[1])
    except Exception as e:
        print(e)