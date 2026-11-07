\# BharatVoice Bench



\*\*An evaluation framework for testing multilingual speech recognition under controlled background noise.\*\*



BharatVoice Bench evaluates how reliably \*\*Gnani Prisma v2.5\*\* transcribes English, Hindi, and Hinglish speech across different speakers and background noise conditions.



This project was developed as part of the \*\*Great Indian AI Internship Challenge\*\*.



\## Research Question



How reliably does Gnani Prisma v2.5 preserve spoken content across English, Hindi, and Hinglish when exposed to different speakers and controlled background noise?



\## Key Features



\- Multilingual speech recognition evaluation.

\- English, Hindi, and Hinglish test recordings.

\- Evaluation across three speakers.

\- Controlled background noise: crowd, fan, and traffic.

\- Three signal-to-noise ratio (SNR) conditions: 0 dB, 10 dB, and 20 dB.

\- Word Error Rate (WER) calculation.

\- Strict and normalized transcription error analysis.

\- Interactive Flask dashboard with charts, filters, and recording-level metrics.



\## Experiment Overview



| Parameter | Details |

|---|---|

| Speech recognition model | Gnani Prisma v2.5 |

| Languages | English, Hindi, Hinglish |

| Speakers | 3 |

| Clean recordings | 9 |

| Generated noisy recordings | 81 |

| Successful noisy transcriptions | 78 |

| Noise conditions | Crowd, fan, traffic |

| SNR conditions | 0, 10, 20 dB |



Three noisy transcription requests did not return usable results because of HTTP 403 responses. These were excluded from WER calculations and are not treated as ASR errors.



\## Evaluation Method



The primary evaluation metric is Word Error Rate (WER).



\\\[

WER = \\frac{S+D+I}{N}\\times100

\\]



Where:



\- \*\*S\*\* = Substitutions

\- \*\*D\*\* = Deletions

\- \*\*I\*\* = Insertions

\- \*\*N\*\* = Number of words in the reference transcript



Both strict and normalized evaluation approaches were explored. Normalization helps account for selected formatting and number-expression variations. Original transcription outputs are retained in the private research data.



\## Dashboard



The Flask dashboard provides:



\- Overall evaluation metrics.

\- WER comparisons by language.

\- WER comparisons by noise type.

\- WER comparisons by SNR.

\- WER comparisons by speaker.

\- Searchable and filterable recording-level results.

\- Interactive charts.



The public repository uses an anonymized evaluation dataset. Original recordings, reference sentences, and raw transcripts are not included.



\## Project Structure



```text

BharatVoice-Bench/

│

├── app.py

├── main.py

├── normalization.py

├── score.py

├── score\_noise.py

├── error\_analysis.py

├── inspect\_errors.py

├── make\_graphs.py

├── mix\_audio.py

├── prepare\_noise.py

├── check\_failed.py

├── export\_public\_data.py

│

├── public\_data/

│   └── noisy\_wer\_summary.csv

│

├── static/

│   ├── css/

│   ├── js/

│   └── graphs/

│

├── templates/

│

├── references/          # Excluded from public repository

├── data/                # Excluded from public repository

├── results/             # Excluded from public repository

│

├── .gitignore

├── PROJECT\_STATUS.md

└── README.md

```



\## Run the Dashboard Locally



\### 1. Clone the repository



```bash

git clone https://github.com/YOUR\_USERNAME/BharatVoice-Bench.git

cd BharatVoice-Bench

```



\### 2. Create a virtual environment



```bash

python -m venv venv

```



Activate it on Windows:



```bash

venv\\Scripts\\activate

```



\### 3. Install dependencies



```bash

pip install -r requirements.txt

```



\### 4. Start the application



```bash

python app.py

```



Open:



`http://127.0.0.1:5000`



\## Privacy and Reproducibility



The public repository contains anonymized evaluation metrics for demonstration and inspection.



The following are intentionally excluded:



\- Original audio recordings.

\- Personal reference transcripts.

\- Raw ASR transcription outputs.

\- Private intermediate CSV files.

\- API credentials and environment files.



The public dataset preserves the numerical evaluation fields needed by the dashboard.



\## Limitations



\- The experiment uses a small pilot dataset of three speakers.

\- Accent and speaker diversity are limited.

\- Three requests did not produce usable transcriptions because of HTTP 403 responses.

\- WER measures transcription accuracy, not semantic understanding.

\- Results should not be interpreted as a comprehensive benchmark of all Indian languages or speakers.



\## Technology Stack



\- \*\*Speech recognition:\*\* Gnani Prisma v2.5

\- \*\*Backend:\*\* Python, Flask

\- \*\*Frontend:\*\* HTML, CSS, JavaScript

\- \*\*Charts:\*\* Plotly

\- \*\*Evaluation:\*\* Word Error Rate (WER)

\- \*\*Audio processing:\*\* FFmpeg and Python audio-processing tools



\## Project Context



Built independently as a solo project for the Great Indian AI Internship Challenge.



\*\*BharatVoice Bench is an evaluation framework, not a newly trained speech recognition model.\*\*
