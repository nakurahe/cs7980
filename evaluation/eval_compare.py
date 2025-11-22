# eval_compare.py
# Generic evaluator for any course folder (e.g., data_course1, data_course2)
# Usage:
#   python3 eval_compare.py --course data_course1
#   python3 eval_compare.py --course data_course2

import argparse
import json
from pathlib import Path
import statistics

from bert_score import score as bert_score
from rouge_score import rouge_scorer
import sacrebleu


# -------------------------
# Load JSON or JSONL helpers
# -------------------------
def load_json_files(folder: Path, prefix: str):
    files = sorted(folder.glob(f"{prefix}*.json"))
    if not files:
        raise FileNotFoundError(f"No files found in {folder} matching {prefix}*.json")

    data_list = []
    for f in files:
        with open(f, "r") as fh:
            data = json.load(fh)
            data_list.append((f, data))
    return data_list


def extract_questions(data_list):
    texts = []
    for _, data in data_list:
        questions = data.get("questions", [])
        for q in questions:
            texts.append(q.get("question_text", "").strip())
    return texts


def load_references_jsonl(path: Path):
    refs = []
    with open(path, "r") as f:
        for line in f:
            if line.strip():
                obj = json.loads(line)
                refs.append(obj["text"].strip())
    if not refs:
        raise ValueError(f"No reference questions loaded from {path}")
    return refs


# -------------------------
# Compute metrics
# -------------------------
def compute_metrics(hypos, refs):
    assert len(hypos) == len(refs), "Hypotheses and references count mismatch."

    # BERTScore
    _, _, F1 = bert_score(hypos, refs, lang="en", verbose=True)
    bert_f1_mean = float(F1.mean())

    # ROUGE
    scorer = rouge_scorer.RougeScorer(["rouge1", "rougeL"], use_stemmer=True)
    rouge1, rougel = [], []

    for h, r in zip(hypos, refs):
        s = scorer.score(r, h)
        rouge1.append(s["rouge1"].fmeasure)
        rougel.append(s["rougeL"].fmeasure)

    # BLEU
    bleu = sacrebleu.corpus_bleu(hypos, [refs])

    return {
        "bert_f1_mean": bert_f1_mean,
        "rouge1_mean": statistics.mean(rouge1),
        "rougel_mean": statistics.mean(rougel),
        "bleu": bleu.score,
    }


# -------------------------
# Main
# -------------------------
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--course", type=str, required=True,
                        help="Folder name: e.g. data_course1 or data_course2")
    args = parser.parse_args()

    COURSE_DIR = Path(args.course)
    QUIZ_DIR = COURSE_DIR / "quiz"
    BASELINE_DIR = COURSE_DIR / "baseline"

    # Pick correct reference file
    if args.course == "data_course1":
        REF_PATH = COURSE_DIR / "references.jsonl"
    else:
        REF_PATH = COURSE_DIR / "references_cs5130.jsonl"

    print(f"\n=== Running evaluation for {args.course} ===")

    # Load data
    quiz_data = load_json_files(QUIZ_DIR, prefix="quiz")
    base_data = load_json_files(BASELINE_DIR, prefix="baseline")

    quiz_texts = extract_questions(quiz_data)
    base_texts = extract_questions(base_data)
    ref_texts = load_references_jsonl(REF_PATH)

    if len(quiz_texts) != len(base_texts):
        raise ValueError(f"Mismatch: quiz={len(quiz_texts)} baseline={len(base_texts)}")

    if len(ref_texts) != len(quiz_texts):
        raise ValueError(f"Mismatch: reference={len(ref_texts)} != quiz={len(quiz_texts)}")

    print(f"Loaded {len(quiz_texts)} questions.\n")

    # Multimodal
    print("=== Multimodal vs Reference ===")
    multi = compute_metrics(quiz_texts, ref_texts)
    print(multi)

    # Baseline
    print("\n=== Baseline vs Reference ===")
    base = compute_metrics(base_texts, ref_texts)
    print(base)

    # Deltas
    print("\n=== Improvements (Multimodal - Baseline) ===")
    print({
        "Δ_BERTScore": multi["bert_f1_mean"] - base["bert_f1_mean"],
        "Δ_ROUGE1": multi["rouge1_mean"] - base["rouge1_mean"],
        "Δ_ROUGEL": multi["rougel_mean"] - base["rougel_mean"],
        "Δ_BLEU": multi["bleu"] - base["bleu"],
    })

    print("\nEvaluation complete.\n")


if __name__ == "__main__":
    main()
