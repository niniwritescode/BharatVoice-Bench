
<div align="center">

# 🇮🇳 BharatVoice Bench

### Evaluating Multilingual Speech Recognition in Controlled Background Noise

**A research-driven evaluation framework for Gnani Prisma v2.5 across English, Hindi and Hinglish.**

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)
![ASR](https://img.shields.io/badge/Task-Speech_Recognition-6C5CE7?style=for-the-badge)
![Challenge](https://img.shields.io/badge/Great_Indian_AI_Internship-FF9933?style=for-the-badge)

**[GitHub Repository](https://github.com/niniwritescode/BharatVoice-Bench)**

</div>

---

## 🚀 About the Project

**BharatVoice Bench** is a multilingual Automatic Speech Recognition (ASR) evaluation framework developed to study how reliably **Gnani Prisma v2.5** transcribes speech under different language, speaker and background-noise conditions.

The project evaluates speech recognition across English, Hindi and Hinglish using controlled noise experiments and Word Error Rate (WER) analysis.

It also provides an interactive Flask dashboard to visualize evaluation results and compare model performance.

> **Research Question:** How reliably does Gnani Prisma v2.5 preserve spoken content across English, Hindi and Hinglish when exposed to different speakers and controlled background noise?

## 📊 Experiment Overview

| Parameter | Details |
|---|---|
| ASR Model | Gnani Prisma v2.5 |
| Languages | English, Hindi, Hinglish |
| Speakers | 3 |
| Clean Recordings | 9 |
| Generated Noisy Recordings | 81 |
| Successful Noisy Transcriptions | 78 |
| Noise Conditions | Crowd, Fan, Traffic |
| SNR Levels | 0 dB, 10 dB, 20 dB |
| Evaluation Metric | Word Error Rate (WER) |

## 🔍 Key Results

### Clean Recording Evaluation

| Language | Corpus WER |
|---|---:|
| English | 3.60% |
| Hindi | 6.31% |
| Hinglish | 9.38% |

### Noisy Recording Evaluation

**Overall normalized corpus WER: 5.45%**

| Evaluation Category | Group | WER |
|---|---|---:|
| Language | English | 5.31% |
| Language | Hindi | 2.03% |
| Language | Hinglish | 9.14% |
| Noise | Crowd | 6.64% |
| Noise | Fan | 4.09% |
| Noise | Traffic | 5.77% |
| SNR | 0 dB | 7.74% |
| SNR | 10 dB | 4.91% |
| SNR | 20 dB | 3.71% |
| Speaker | Speaker 1 | 5.45% |
| Speaker | Speaker 2 | 4.74% |
| Speaker | Speaker 3 | 6.08% |

**Important evaluation note:**

- Strict, non-normalized corpus WER: 37.48%.
- Normalized corpus WER: 5.45%.
- Mean per-record WER: 5.63%.

Normalization accounts for selected formatting and number-expression variations. These metrics use different calculation approaches and should not be treated as interchangeable.

Three transcription requests returned HTTP 403 errors and were excluded from WER calculations. These are API request failures, not ASR transcription errors.

The resulting subgroup counts are slightly uneven.

## 📈 Dashboard & Visualizations

The project includes an interactive Flask dashboard for exploring evaluation results.

### WER by Language

![WER by Language](static/graphs/wer_by_language.png)

### WER by Noise Condition

![WER by Noise](static/graphs/wer_by_noise.png)

### WER by Signal-to-Noise Ratio

![WER by SNR](static/graphs/wer_by_snr.png)

### WER by Speaker

![WER by Speaker](static/graphs/wer_by_speaker.png)

### Dashboard Features

- Overall evaluation metrics
- Language-wise performance comparison
- Noise-wise WER analysis
- SNR-based performance analysis
- Speaker-wise evaluation
- Recording-level result exploration
- Interactive charts and visual summaries

## 🧪 Evaluation Methodology

The primary evaluation metric is **Word Error Rate (WER)**.

\[
WER = \frac{S+D+I}{N}\times100
\]

Where:

- S = Substitutions
- D = Deletions
- I = Insertions
- N = Number of words in the reference transcript

### Experiment Workflow

1. Prepare clean speech recordings in English, Hindi and Hinglish.
2. Generate noisy audio samples using crowd, fan and traffic noise.
3. Apply controlled Signal-to-Noise Ratio levels of 0, 10 and 20 dB.
4. Submit audio samples to Gnani Prisma v2.5.
5. Obtain speech-to-text transcription outputs.
6. Compare outputs against reference transcripts.
7. Calculate strict and normalized WER.
8. Analyze errors and generate visualizations.
9. Export anonymized evaluation data for the public dashboard.

## 🛠️ Technology Stack

| Technology | Purpose |
|---|---|
| Python | Core programming |
| Gnani Prisma v2.5 | Speech recognition |
| Flask | Web dashboard backend |
| HTML & CSS | Dashboard interface |
| JavaScript | Frontend interactions |
| Matplotlib | Data visualization |
| JiWER | WER evaluation |
| FFmpeg | Audio processing |
| NumPy | Numerical operations |

## 📁 Project Structure

```text
BharatVoice-Bench/
│
├── app.py
├── main.py
├── normalization.py
├── score.py
├── score_noise.py
├── error_analysis.py
├── inspect_errors.py
├── make_graphs.py
├── mix_audio.py
├── prepare_noise.py
├── check_failed.py
├── export_public_data.py
│
├── public_data/
│   └── noisy_wer_summary.csv
│
├── static/
│   ├── css/
│   ├── js/
│   └── graphs/
│
├── templates/
│
├── requirements.txt
├── PROJECT_STATUS.md
├── .gitignore
└── README.md
```

Private research directories containing original audio, reference transcripts and intermediate results are intentionally excluded from the public repository.

## 💻 Run Locally

### 1. Clone the Repository

```bash
git clone https://github.com/niniwritescode/BharatVoice-Bench.git
```

```bash
cd BharatVoice-Bench
```

### 2. Create a Virtual Environment

**Windows:**

```cmd
python -m venv venv
venv\Scripts\activate
```

**Linux / macOS:**

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the Dashboard

```bash
python app.py
```

Open your browser and visit:

```text
http://127.0.0.1:5000
```

The public dashboard uses the anonymized dataset in `public_data/` and does not require an API key.

## 🔐 Privacy & Data Protection

The public repository contains an anonymized evaluation dataset and the code required to explore the results.

The following materials are intentionally excluded:

- Original audio recordings
- Personal reference sentences
- Raw transcription outputs
- Private intermediate result files
- API credentials and `.env` files

Speaker names and recording identifiers are anonymized in the public dataset.

## ⚠️ Limitations

- The experiment uses only three speakers.
- Accent and speaker diversity are limited.
- Three API requests failed with HTTP 403 errors.
- Some evaluation groups have unequal sample counts.
- WER measures word-level transcription accuracy, not semantic understanding.
- Normalized and strict WER values depend on different text-comparison procedures.

This project is an **ASR evaluation framework**, not a newly trained speech recognition model.

## 👩‍💻 Project & Developer

**Project:** BharatVoice Bench

**Developer:** Nandini

**Project Type:** Independent Research & Development

**Challenge:** Great Indian AI Internship Challenge

**Model Evaluated:** Gnani Prisma v2.5

---

<div align="center">

### 🇮🇳 BharatVoice Bench

*Evaluating multilingual speech recognition, one recording at a time.*

**Built with Python, research and curiosity.**

[View Repository](https://github.com/niniwritescode/BharatVoice-Bench)

</div>
