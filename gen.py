import argparse
import io
import os
import sys
import time
from collections import OrderedDict
from os.path import basename, exists, join, splitext

import IPython
import numpy as np
import torch
from localimport import localimport
from matplotlib import pylab as plt
import textract

from TTS.utils.audio import AudioProcessor
from TTS.utils.generic_utils import setup_model
from TTS.utils.io import load_config
from TTS.utils.synthesis import synthesis
from TTS.utils.text.symbols import phonemes, symbols
from TTS.vocoder.utils.generic_utils import setup_generator

sys.path.append('TTS')
sys.path.append('WaveRNN')





# wavernn_pretrained_model = 'wavernn_models/checkpoint_433000.pth.tar'
# wavernn_pretrained_model_config = 'wavernn_models/config.json'
# tts_pretrained_model = 'tts_models/checkpoint_261000.pth.tar'
# tts_pretrained_model_config = 'tts_models/config.json'

# model paths
TTS_MODEL = "tts_model.pth.tar"
TTS_CONFIG = "config.json"
VOCODER_MODEL = "vocoder_model.pth.tar"
VOCODER_CONFIG = "config_vocoder.json"

# load configs
TTS_CONFIG = load_config(TTS_CONFIG)
VOCODER_CONFIG = load_config(VOCODER_CONFIG)

use_cuda = False
batched_wavernn = True
OUT_FOLDER = "output"

# load the audio processor
ap = AudioProcessor(**TTS_CONFIG.audio)
print(ap)

# LOAD TTS MODEL
# multi speaker
speaker_id = None
speakers = []

# load the model
num_chars = len(phonemes) if TTS_CONFIG.use_phonemes else len(symbols)
model = setup_model(num_chars, len(speakers), TTS_CONFIG)

# load model state
cp =  torch.load(TTS_MODEL, map_location=torch.device('cpu'))

# load the model
model.load_state_dict(cp['model'])
if use_cuda:
    model.cuda()
model.eval()

# set model stepsize
if 'r' in cp:
    model.decoder.set_r(cp['r'])



# LOAD VOCODER MODEL
vocoder_model = setup_generator(VOCODER_CONFIG)
vocoder_model.load_state_dict(torch.load(VOCODER_MODEL, map_location="cpu")["model"])
vocoder_model.remove_weight_norm()
vocoder_model.inference_padding = 0

ap_vocoder = AudioProcessor(**VOCODER_CONFIG['audio'])
if use_cuda:
    vocoder_model.cuda()
vocoder_model.eval()


def tts(model, text, CONFIG, use_cuda, ap, use_gl, figures=True, filename="test"):
    t_1 = time.time()
    waveform, alignment, mel_spec, mel_postnet_spec, stop_tokens, inputs = synthesis(model, text, CONFIG, use_cuda, ap, speaker_id, style_wav=None,
                                                                             truncated=False, enable_eos_bos_chars=CONFIG.enable_eos_bos_chars)
    # mel_postnet_spec = ap._denormalize(mel_postnet_spec.T)
    if not use_gl:
        waveform = vocoder_model.inference(torch.FloatTensor(mel_postnet_spec.T).unsqueeze(0))
        waveform = waveform.flatten()
    if use_cuda:
        waveform = waveform.cpu()
    waveform = waveform.numpy()
    rtf = (time.time() - t_1) / (len(waveform) / ap.sample_rate)
    tps = (time.time() - t_1) / len(waveform)
    print(waveform.shape)
    print(" > Run-time: {}".format(time.time() - t_1))
    print(" > Real-time factor: {}".format(rtf))
    print(" > Time per step: {}".format(tps))
    # IPython.display.display(IPython.display.Audio(waveform, rate=CONFIG.audio['sample_rate']))
    # os.makedirs(OUT_FOLDER, exist_ok=True)
    # file_name = filename + ".wav"
    # out_path = os.path.join(OUT_FOLDER, file_name)
    # ap.save_wav(waveform, out_path)
    return alignment, mel_postnet_spec, stop_tokens, waveform




def split_text_to_len(text, length):
    text_split = text.split()
    splits = {0:""}
    idx = 0
    for word in text_split:
        if (len(splits[idx]) < 1000):
            if len(splits[idx]) > 800 and '.' in word:
                splits[idx] = " ".join([splits[idx], word])
                idx += 1
                splits[idx] = ""
            else:
                splits[idx] = " ".join([splits[idx], word])
        else:
            idx += 1
            splits[idx] = word

    if splits[idx] == '':
        del splits[idx]
    return splits
import numpy as np

def tts_splits(splits):
    complete = []
    for k,v in splits.items():
        print(k,v)
        print("Procerss Batch: ", k)
        align, spec, stop_tokens, wav = tts(model, v, TTS_CONFIG, use_cuda, ap, use_gl=False, figures=True, filename=str(k))
        print(wav.shape)
        ap.save_wav(wav, "output/tmp_{:03d}.wav".format(k))

# sentence =  "Bill got in the habit of asking himself “Is that thought true?” and if he wasn’t absolutely certain it was, he just let it go."
# align, spec, stop_tokens, wav = tts(model, text, TTS_CONFIG, use_cuda, ap, use_gl=False, figures=True, filename="abstr")

def gen_file_names(splits):
    names = []
    for k in splits.keys():
        names.append(os.path.join(OUT_FOLDER, "tmp_{:03d}.wav".format(k)))
    return names


def post_wav_merge(files):
    import wave
    outfile = "sounds_complete.wav"

    data = []
    for infile in files:
        w = wave.open(infile, 'rb')
        data.append( [w.getparams(), w.readframes(w.getnframes())] )
        w.close()
    output = wave.open(outfile, 'wb')
    output.setparams(data[0][0])
    for i in range(len(data)):
        output.writeframes(data[i][1])
    output.close()


def parser():
    parser = argparse.ArgumentParser(description='Process Text in PDF files and convert them to .wav audio.')
    parser.add_argument('path', type=str,
                    help='Path to PDF')
    return parser.parse_args()

def main():
    parser()


    text = textract.process("/home/schorschi/Desktop/acp.pdf", method="pdfminer").decode("utf-8")

    splits = split_text_to_len(text, 1000)
    print(splits)
    tts_splits(splits)
    file_names = gen_file_names(splits)
    file_names.sort(key=lambda f: int(f.split('_')[1].split('.')[0]))
    print(file_names)
    print("Merge generated audio!")
    post_wav_merge(file_names)


if __name__ == "__main__":
    main()
