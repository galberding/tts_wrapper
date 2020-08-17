# tts_wrapper
Text To Speech wrapper to convert PDFs to wav files.

* Based on [Mozilla TTS Notebook](https://colab.research.google.com/github/tugstugi/dl-colab-notebooks/blob/master/notebooks/Mozilla_TTS_WaveRNN.ipynb#scrollTo=klsVLR6w_u4P)
* And [DDC-TTS Notebook](https://colab.research.google.com/drive/1u_16ZzHjKYFn1HNVuA4Qf_i2MMFB9olY?usp=sharing#scrollTo=X2axt5BYq7gv)

## Installation:
* You need to have [miniconda](https://docs.conda.io/en/latest/miniconda.html) installed
```
source setup.sh
```
* This will setup the environment, download and install all dependencies

## Usage
```
python gen.py path/to/pdf.pdf -o out.wav
```
