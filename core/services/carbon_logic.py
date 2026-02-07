def calculate_metrics(user_entries):
    total = sum(entry.co2_total for entry in user_entries)
    # 21kg is the avg CO2 absorbed by one tree per year
    trees_equivalent = round(total / 21, 2) 
    return {
        'total': total,
        'trees': trees_equivalent,
        'status': 'Green' if total < 500 else 'High Alert'
    }