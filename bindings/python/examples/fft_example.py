import sys

sys.path.insert(1, "../")
import genalyzer
import glob
import pytest
import os

examples_dir = "../../../tests/test_vectors/"


def get_config(f):
    config_dict = {}
    for line in f:
        if "----------" in line:
            break
        else:
            (key, val) = line.split("=")
            (val, new_line) = val.split("\n")
            config_dict[key] = float(val)

    return config_dict


loc = os.path.dirname(__file__)
filename = os.path.join(loc, examples_dir, "test_fft_input_1619707831772.txt")
f = open(filename, "r")

# create test configuration object
config_dict = get_config(f)
c = genalyzer.config_tone_gen(config_dict)

# generate tone
awf = genalyzer.gen_tone(c)

# quantize waveform
qwf = genalyzer.quantize(c, awf)

# generate complex FFT of a complex waveform
qwf_i = [qwf[i] for i in range(len(qwf)) if i % 2 == 0]
qwf_q = [qwf[i] for i in range(len(qwf)) if i % 2 != 0]
out_i, out_q = genalyzer.fft(c, qwf_i, qwf_q)
