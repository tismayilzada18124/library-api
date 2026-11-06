
FINE_PER_DAY = 0.50


def calculate_fine(days_overdue):
    if days_overdue <= 0:
        return 0.0

    return round(days_overdue * FINE_PER_DAY, 2)
