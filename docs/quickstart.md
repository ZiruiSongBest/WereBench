---
layout: default
title: Quick Start
nav_order: 2
---

# Quick Start

1.  **Clone the repository**
    ```bash
    git clone GITHUB_REPO
    cd WereBench
    ```

2.  **Create and activate a Conda environment**
    ```bash
    conda create -n werebench python=3.9
    conda activate werebench
    ```

3.  **Install dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Download the Dataset**

    Preferred source is Hugging Face 🤗:
    ```bash
    hf download LINK_TO_HF
    ```

5. **Minimal evaluation**
    
    Make sure you modify the script's call and model to suit your needs before running it
    ```bash
    # for Decision Evaluation
    python eval/Decision_Evaluation/inference.py

    # for Role Performance
    python eval/Role_Performance/inference.py
    ```