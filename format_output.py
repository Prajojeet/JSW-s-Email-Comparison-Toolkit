def format_clause_html(html_text):

    # 2. Handle α → single line break
    html_text = html_text.replace('α', '<br>')

    return html_text

def display_comparison_results(comparison_results):
    full_html = "<html><body style='font-family:Courier; font-size:15px; white-space:pre-wrap;'>"
    full_html += "".join(format_clause_html(clause_html) for clause_html in comparison_results)
    full_html += "</body></html>"

    return full_html