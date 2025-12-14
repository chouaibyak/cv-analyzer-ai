from transformers import pipeline

summarizer = pipeline(
    "summarization",
    model="facebook/bart-large-cnn"
)

text = """
Artificial Intelligence is transforming the world by enabling machines
to learn from data and make intelligent decisions.
"""

result = summarizer(text, max_length=130, min_length=30, do_sample=False)

print("Résumé :")
print(result[0]["summary_text"])
#facebook/bart-large-cnn