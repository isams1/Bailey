REPORT_FORMAT = [
    ('pdf', 'PDF'),
    ('xls', 'XLS')
]

# styles
_pfc = '26'  # default pattern fore_color
_bc = '22'   # borders color
decimal_format = '#,##0.00'
date_format = 'DD-MM-YYYY'
streamline_xls_styles = {
    'xls_title': 'font: bold true, height 350;',
    'xls_sub_title': 'font: bold true',
    'bold': 'font: bold true;',
    'underline': 'font: underline true;',
    'italic': 'font: italic true;',
    'fill': 'pattern: pattern solid, fore_color %s;' % _pfc,
    'fill_blue': 'pattern: pattern solid, fore_color 27;',
    'fill_grey': 'pattern: pattern solid, fore_color 22;',
    'borders_all':
        'borders: '
        'left thin, right thin, top thin, bottom thin, '
        'left_colour %s, right_colour %s, '
        'top_colour %s, bottom_colour %s;'
        % (_bc, _bc, _bc, _bc),
    'left': 'align: horz left;',
    'center': 'align: horz center;',
    'right': 'align: horz right;',
    'wrap': 'align: wrap true;',
    'top': 'align: vert top;',
    'bottom': 'align: vert bottom;',
}