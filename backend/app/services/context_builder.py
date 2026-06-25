def build_context(question, similar_questions, law_chunks):

    similar_text = "\n".join(
        [f"- {q['question']}" for q in similar_questions]
    )

    law_text = "\n".join(
        [f"- {l['content']}" for l in law_chunks]
    )

    return f"""
[문제]
{question}

[유사 문제]
{similar_text}

[관련 법령]
{law_text}

[요청]
이 문제를 왜 틀렸는지 설명하고,
정답 근거를 법령 기반으로 설명해줘.
"""