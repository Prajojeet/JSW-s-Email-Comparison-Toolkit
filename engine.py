import re
import os
import diff_match_patch as dmp_module
from langchain_openai import OpenAIEmbeddings
import numpy as np
from dotenv import load_dotenv


# Load .env into environment
load_dotenv()

EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def normalize_whitespace(text):
    return re.sub(r'\s+', ' ', text).strip()

def convert_diff_to_html(diff):
    html_output = ""
    for op, data in diff:
        if op == dmp_module.diff_match_patch.DIFF_INSERT:
            html_output += f'&nbsp<span style="color:red;text-decoration:line-through;">{data}</span>'
        elif op == dmp_module.diff_match_patch.DIFF_DELETE:
            html_output += f'<span style="color:red;">{data}</span>'
        else:
            html_output += f'<span>{data}</span>'
    return html_output

def _l2norm_rows(a, eps=1e-12):
    """Return row-wise L2-normalized array; guards zero vectors."""
    a = np.asarray(a, dtype=np.float32)
    if a.ndim == 1:
        a = a[None, :]
    norms = np.linalg.norm(a, axis=1, keepdims=True)
    norms = np.maximum(norms, eps)
    return a / norms

def compare_clauses_sequentially(original_clauses, revised_clauses, window, threshold):
    if not original_clauses:
        return []
    if not revised_clauses:
        return [f"<div style='color:red;'>{normalize_whitespace(c)}</div>" for c in original_clauses]

    # Load model
    model = OpenAIEmbeddings(
    model=EMBEDDING_MODEL,
    api_key=OPENAI_API_KEY
    )

    dmp = dmp_module.diff_match_patch()

    # Normalize all clauses once
    original_clauses = [normalize_whitespace(c) for c in original_clauses]
    revised_clauses  = [normalize_whitespace(c) for c in revised_clauses]

    # Precompute all embeddings (batch)
    original_embeddings = model.embed_documents(original_clauses)  # list[list[float]]
    revised_embeddings  = model.embed_documents(revised_clauses)

    # Convert to arrays and L2-normalize once (cosine => dot on normalized vectors)
    original_embeddings = _l2norm_rows(original_embeddings)  # (N, d)
    revised_embeddings  = _l2norm_rows(revised_embeddings)   # (M, d)

    used_revised = set()
    output_html = [""] * max(len(original_clauses), len(revised_clauses))

    for i, orig_emb in enumerate(original_embeddings):
        start = max(0, i - window)
        end   = min(len(revised_embeddings), i + window + 1)

        cand = revised_embeddings[start:end]  # (k, d)
        if cand.size == 0:
            output_html[i] = (
                f"<div style='font-family:Courier; font-size:15px; white-space:pre-wrap; color:red;'>"
                f"{original_clauses[i]}</div>"
            )
            continue

        # cosine similarities == dot products after L2-normalization
        sims = cand @ orig_emb  # (k,)
        # Guard against any numerical oddities
        if np.isnan(sims).any():
            sims = np.nan_to_num(sims, nan=-1.0)

        best_idx = int(np.argmax(sims))
        best_score = float(sims[best_idx])
        actual_rev_idx = start + best_idx

        if best_score > threshold and actual_rev_idx not in used_revised:
            diffs = dmp.diff_main(original_clauses[i], revised_clauses[actual_rev_idx])
            dmp.diff_cleanupSemantic(diffs)
            html_result = convert_diff_to_html(diffs)
            output_html[i] = (
                f"<div style='font-family:Courier; font-size:15px; white-space:pre-wrap;'>{html_result}</div>"
            )
            used_revised.add(actual_rev_idx)
        else:
            output_html[i] = (
                f"<div style='font-family:Courier; font-size:15px; white-space:pre-wrap; color:red;'>"
                f"{original_clauses[i]}</div>"
            )

    # Add unmatched revised clauses
    for idx, clause in enumerate(revised_clauses):
        if idx not in used_revised:
            red_strike = (
                f"<div style='font-family:Courier; font-size:15px; white-space:pre-wrap; "
                f"color:red;text-decoration:line-through;'>{clause}</div>"
            )
            if idx < len(output_html) and output_html[idx] == "":
                output_html[idx] = red_strike
            else:
                output_html.append(red_strike)

    return output_html
