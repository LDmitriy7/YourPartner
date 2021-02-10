_POST_TEMPLATE = """
<b>{status}</b>

#{work_type}
#{subject}

{description}

<b>Сдача:</b> {date}
<b>Цена:</b> {price}
{note}
"""


def form_post_text(status: str, post_data: dict, with_note=False):
    """Requires all fields from project.data"""
    post_data = post_data.copy()

    subject = post_data['subject'].replace(' ', '_')
    work_type = post_data['work_type'].replace(' ', '_')

    price = post_data['price']
    price = f'{price} грн' if price else 'Договорная'

    date = post_data['date'].split('-')
    date = f'{date[2]}.{date[1]}'

    emojis = {'Активен': '🔥', 'Выполняется': '⏳', 'Выполнен': '✅'}
    status = f'{emojis[status]} {status}'

    note = post_data['note']
    note = f'<b>Ваша заметка:</b> {note}' if note and with_note else ''

    post_data.update(
        subject=subject,
        work_type=work_type,
        price=price,
        date=date,
        status=status,
        note=note,
    )
    text = _POST_TEMPLATE.format(**post_data)
    return text
