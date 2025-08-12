import os
import preprocessing
import engine
import format_output


def run_comparison_engine(email_text: str, original_text: str):

    # Treating the original text first
    alpha_added = preprocessing.alpha_end_all_lines(original_text)
    original_clauses = preprocessing.extract_clauses_from_text(alpha_added)

    # Treating the HTML second
    email_clauses = preprocessing.extract_clauses_from_text(email_text)

    # Window Size
    window = int(abs(len(email_clauses)-len(original_clauses))*1.5 + 5) # Threshold set
    sim_threshold = float(os.getenv("SIM_THRESHOLD"))

    #Comparison Results
    comparison_results = engine.compare_clauses_sequentially(original_clauses, email_clauses, window, sim_threshold)
    full_html = format_output.display_comparison_results(comparison_results)

    return full_html


if __name__ == '__main__':
    email_text = input(str)
    original_text = input(str)

    print(run_comparison_engine(email_text, original_text))