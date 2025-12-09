---
layout: default
title: Dataset
nav_order: 3
---

# Dataset

WereBench data are JSON-structured by **categories** and **questions**, with standardized fields such as `id`, `role`, `text`, `options[key,text]`, and `answerKey`. This mirrors the structure used in the public JSON behind WereBench. :contentReference[oaicite:0]{index=0}

**Example for WereBench.json**
```json
{
  "categories": [
    {
      "categoryName": "Role Inference",
      "questions": [
        {
          "id": 1,
          "role": "Player-9",
          "text": "Given the speeches, what is the most plausible identity of Player-12?",
          "options": [
            {"key": "A", "text": "Option A ..."},
            {"key": "H", "text": "Option H ..."}
          ],
          "answerKey": "H"
        }
      ]
    }
  ]
}
```

## Tasks & metrics

Our **WereAlign** evaluation framework consists of two core components:

### 1. Speech Evaluation

We construct a series of multiple-choice questions to assess the model's abilities across five critical social and strategic dimensions:

*   **Role Inference (RI)**: The model's ability to uncover the true identities and intentions of other players.
*   **Strategic Judgment (SJ)**: The model's ability to choose the course of action most beneficial to its faction.
*   **Deception Reasoning (DR)**: The model's ability to identify others' lies or effectively perform masquerades.
*   **Persuasive Statements (PS)**: The model's ability to generate persuasive statements appropriate to the context.
*   **Counterfactual Trade-off (CT)**: The model's ability to examine the potential benefits and risks of different actions under the current scenario.

### 2. Decision Evaluation

Decision evaluation complements the speech-level analysis, further testing whether models choose actions that align with a successful human strategy.

*   **Vote Alignment (VA)**: We score alignment by comparing the model's daytime elimination vote with the MVP's actual vote at the same round, capturing whether the model joins the winning coalition at the right time and on the right target.
*   **Opponent-role Inference (OI)**: The model identifies which players most likely belong to the opposing faction. We compare predictions against ground-truth roles to assess the model's ability to detect inconsistencies and deception in adversaries' speeches.

## Access & license

Dataset: 🤗 [Hugging Face](https://huggingface.co/datasets/Yuan4629/WereBench) (see top-right link).