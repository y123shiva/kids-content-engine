import os
import webbrowser
import pandas as pd
import matplotlib.pyplot as plt
from tqdm import tqdm
from app.eval.rag_eval_set import RAG_EVAL_SET
from app.eval.recall import recall_at_k, precision_at_k, context_overlap
from app.services.rag_adapter import retrieve_context
from app.core.models import RAGQuery
from app.api.routes_rag_media import rag_manager

# Directories
METRICS_DIR = "eval_metrics"
os.makedirs(METRICS_DIR, exist_ok=True)

# ANSI colors
GREEN = "\033[92m"
RED = "\033[91m"
RESET = "\033[0m"

def normalize_results(results):
    """Ensure every result is a string for metric calculations."""
    normalized = []
    for r in results:
        if isinstance(r, dict):
            text = str(r.get("text", "")).replace("nan", "")
        else:
            try:
                text = str(r)
            except:
                text = ""
        normalized.append(text)
    return normalized

def evaluate(mode="faiss", k=3):
    all_metrics = []
    print(f"\n🔎 Evaluating mode: {mode.upper()}, k={k}\n")
    print(f"{'Query':<50} | {'Top-k Results':<80} | {'Relevant':<20} | {'Hit'}")
    print("-"*180)

    for item in tqdm(RAG_EVAL_SET, desc=f"Evaluating {mode} k={k}"):
        req = RAGQuery(query=item["query"], k=k)

        results = retrieve_context(
            req=req,
            df=rag_manager.df,
            model=rag_manager.model,
            index=rag_manager.index,
            mode=mode
        )

        if not results:
            results = []

        # Normalize results to strings
        normalized_results = normalize_results(results)

        # Top-k texts for printing
        topk_texts = normalized_results[:k]

        # Metrics
        hit = recall_at_k(normalized_results, item["relevant"])
        precision = precision_at_k(normalized_results, item["relevant"])
        overlap = context_overlap(normalized_results, item["relevant"])

        all_metrics.append({
            "query": item["query"],
            "mode": mode,
            "k": k,
            "topk_results": " | ".join(topk_texts),
            "relevant": ", ".join(item["relevant"]),
            "hit": hit,
            "precision": precision,
            "context_overlap": overlap
        })

        hit_display = f"{GREEN}✔{RESET}" if hit else f"{RED}✖{RESET}"
        print(f"{req.query[:50]:<50} | {', '.join(topk_texts)[:80]:<80} | {', '.join(item['relevant']):<20} | {hit_display}")

    # Save metrics CSV
    df_metrics = pd.DataFrame(all_metrics)
    csv_file = os.path.join(METRICS_DIR, f"rag_eval_metrics_{mode}_k{k}.csv")
    df_metrics.to_csv(csv_file, index=False)
    print(f"\n💾 Metrics saved to {csv_file}")

    return df_metrics

def plot_metrics(df_all):
    plt.figure(figsize=(8,6))
    for metric in ["hit", "precision", "context_overlap"]:
        for mode in ["faiss", "keyword"]:
            subset = df_all[df_all["mode"] == mode].groupby("k")[metric].mean()
            plt.plot(subset.index, subset.values, marker="o", label=f"{mode}-{metric}")
    plt.title("RAG Evaluation Metrics")
    plt.xlabel("k")
    plt.ylabel("Score")
    plt.ylim(0,1.05)
    plt.legend()
    plot_file = os.path.join(METRICS_DIR, "metrics_plot.png")
    plt.savefig(plot_file)
    plt.close()
    return plot_file

def generate_html_report(df_all, plot_file):
    html_file = os.path.join(METRICS_DIR, "rag_eval_report.html")
    with open(html_file, "w", encoding="utf-8") as f:
        f.write("<html><head><title>RAG Evaluation Report</title></head><body>")
        f.write("<h1>RAG Evaluation Metrics</h1>")
        f.write("<img src='{}' style='max-width:600px;'><br><br>".format(os.path.basename(plot_file)))
        f.write(df_all.to_html(index=False))
        f.write("</body></html>")
    print(f"🌐 HTML report generated at {html_file}")
    webbrowser.open(f"file://{os.path.abspath(html_file)}")

def main():
    # Build FAISS index if needed
    if not rag_manager.is_ready():
        print("🔧 Building FAISS index...")
        rag_manager.build_index()

    df_all = pd.DataFrame()
    for mode in ["faiss", "keyword"]:
        for k in [3,5]:
            df_metrics = evaluate(mode=mode, k=k)
            df_all = pd.concat([df_all, df_metrics], ignore_index=True)

    # Plot metrics
    plot_file = plot_metrics(df_all)

    # Generate HTML
    generate_html_report(df_all, plot_file)

if __name__ == "__main__":
    main()
