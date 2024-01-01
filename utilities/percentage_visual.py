def percentage_visual(percentage: int):
    if 0 <= percentage < 10:
        percentage_text = f'□ □ □ □ □ □ □ □ □ □ {percentage}%'
    elif 10 <= percentage < 20:
        percentage_text = f'■ □ □ □ □ □ □ □ □ □ {percentage}%'
    elif 20 <= percentage < 30:
        percentage_text = f'■ ■ □ □ □ □ □ □ □ □ {percentage}%'
    elif 30 <= percentage < 40:
        percentage_text = f'■ ■ ■ □ □ □ □ □ □ □ {percentage}%'
    elif 40 <= percentage < 50:
        percentage_text = f'■ ■ ■ ■ □ □ □ □ □ □ {percentage}%'
    elif 50 <= percentage < 60:
        percentage_text = f'■ ■ ■ ■ ■ □ □ □ □ □ {percentage}%'
    elif 60 <= percentage < 70:
        percentage_text = f'■ ■ ■ ■ ■ ■ □ □ □ □ {percentage}%'
    elif 70 <= percentage < 80:
        percentage_text = f'■ ■ ■ ■ ■ ■ ■ □ □ □ {percentage}%'
    elif 80 <= percentage < 90:
        percentage_text = f'■ ■ ■ ■ ■ ■ ■ ■ □ □ {percentage}%'
    elif 90 <= percentage < 100:
        percentage_text = f'■ ■ ■ ■ ■ ■ ■ ■ ■ □ {percentage}%'
    elif percentage == 100:
        percentage_text = f'■ ■ ■ ■ ■ ■ ■ ■ ■ ■ {percentage}%'
    else:
        percentage_text = f'■ ■ ■ ■ ■ ■ ■ ■ ■ ■ {percentage}%'
    return percentage_text
