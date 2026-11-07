# \# BharatVoice Bench — Development Logbook

#

# \*\*Project:\*\* BharatVoice Bench

# \*\*Purpose:\*\* Evaluating multilingual speech recognition under controlled background noise

# \*\*ASR System:\*\* Gnani Prisma v2.5

# \*\*Developer:\*\* Nini

# \*\*Project Period:\*\* October–November 2026

# \*\*Status:\*\* Development completed; preparing final submission

#

# \---

#

# \## Project Overview

#

# BharatVoice Bench is an experimental evaluation framework designed to study how reliably Gnani Prisma v2.5 recognizes English, Hindi, and Hinglish speech under different speaker conditions and controlled background noise.

#

# The project focuses on measuring transcription accuracy using Word Error Rate (WER), analyzing recognition errors, and presenting the results through an interactive web dashboard.

#

# \## Development Timeline

#

# \### 29 October 2026 — Project Setup and API Integration

#

# \- Created the initial Python project structure.

# \- Set up the Python virtual environment.

# \- Configured environment variables for secure API access.

# \- Began integrating the Gnani Vachana speech-to-text API.

# \- Established the initial transcription workflow.

#

# \### 30 October – 3 November 2026 — Dataset Preparation

#

# \- Planned a multilingual speech dataset covering English, Hindi, and Hinglish.

# \- Recorded speech samples from three speakers.

# \- Prepared reference transcripts for evaluating recognition accuracy.

# \- Organized audio files and supporting reference data.

# \- Explored background audio sources for controlled noise experiments.

#

# \### 4 November 2026 — Noise Generation and Experiment Expansion

#

# \- Generated noisy speech samples using crowd, fan, and traffic background sounds.

# \- Created three signal-to-noise ratio conditions: 0 dB, 10 dB, and 20 dB.

# \- Expanded the experiment to include 81 noisy audio samples.

# \- Organized the processing and transcription scripts.

#

# \### 5 November 2026 — Speech Recognition Experiments

#

# \- Completed the initial clean-audio transcription experiments.

# \- Tested noisy recordings using Gnani Prisma v2.5.

# \- Obtained 78 successful noisy-audio transcriptions.

# \- Identified three unsuccessful requests involving Ram's Hindi crowd-noise recordings.

# \- Investigated the HTTP 403 Cloudflare access restriction.

# \- Started clean and noisy WER calculations.

#

# \### 6 November 2026 — Evaluation and Error Analysis

#

# \- Refined the WER calculation pipeline.

# \- Worked on strict and normalized transcript comparisons.

# \- Developed scripts for inspecting substitutions, deletions, and insertions.

# \- Generated aggregate evaluation graphs.

# \- Analyzed performance across languages, speakers, noise types, and SNR levels.

# \- Developed the Flask-based web dashboard.

# \- Integrated interactive charts and project methodology pages.

#

# \### 7 November 2026 — Dashboard and Final Validation

#

# \- Refined the dashboard and its data presentation.

# \- Reviewed the evaluation results and visualizations.

# \- Organized the project documentation and supporting scripts.

# \- Prepared for final API validation.

# \- Documented the unresolved Cloudflare access restriction.

#

# \### 8 November 2026 — Final API Check and Repository Preparation

#

# \- Performed one controlled final API request using a previously unsuccessful recording.

# \- Received HTTP 403 with a Cloudflare security response.

# \- Classified the event as an API access failure rather than an ASR transcription error.

# \- Confirmed that the existing 81-record result collection was preserved.

# \- Began preparing the project for public GitHub publication.

# \- Reviewed `.gitignore` to exclude credentials, private audio, reference data, and raw transcription results.

# \- Initialized the local Git repository and staged the project source code and dashboard assets.

#

# \---

#

# \## Current Experimental Dataset

#

# | Parameter | Description |

# |---|---|

# | Speakers | 3 |

# | Languages | English, Hindi, Hinglish |

# | Clean recordings | 9 |

# | Generated noisy samples | 81 |

# | Successful noisy transcriptions | 78 |

# | Noise categories | Crowd, fan, traffic |

# | SNR conditions | 0 dB, 10 dB, 20 dB |

# | Evaluation metric | Word Error Rate (WER) |

#

# \## Known Limitations

#

# \- The experiment uses only three speakers and does not represent the full diversity of Indian accents.

# \- Three noisy Hindi requests were unsuccessful because of Cloudflare HTTP 403 access restrictions.

# \- These access failures are not counted as ASR transcription errors.

# \- The dataset contains controlled experiments and should be interpreted as a pilot evaluation rather than a comprehensive benchmark.

# \- Transcript normalization can affect WER, so normalized and strict results must be clearly distinguished.

#

# \## Final Project Components

#

# \- Gnani Prisma v2.5 speech-to-text integration.

# \- Audio preparation and noise-mixing scripts.

# \- Clean and noisy transcription evaluation.

# \- WER calculation and error-analysis pipeline.

# \- Graphs comparing recognition performance.

# \- Flask-based interactive dashboard.

# \- Project methodology and documentation.

#

# \## Remaining Submission Tasks

#

# \- \[ ] Complete README documentation.

# \- \[ ] Review GitHub repository contents and privacy exclusions.

# \- \[ ] Create the public GitHub repository and push the project.

# \- \[ ] Record the 2–3 minute demonstration video.

# \- \[ ] Publish the LinkedIn/X project announcement.

# \- \[ ] Complete the Great Indian AI Internship Challenge submission.

#

# \---

#

# \*This logbook records the major development milestones and experimental decisions made during the project. It is not intended to represent a minute-by-minute activity record.\*
