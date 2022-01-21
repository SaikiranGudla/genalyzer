import sys
import os

loc = os.path.join(*['C:', os.sep, 'genalyzer', 'genalyzer','bindings', 'python', 'deps'])
files = os.listdir(loc)

os.environ["PATH"]+=";"+loc
import genalyzer
import glob
import pytest
import os

test_dir = os.path.join(*['..', '..', '..', 'tests', 'test_vectors'])
loc = os.path.dirname(__file__)
test_gen_tone_files = [
    f for f in glob.glob(os.path.join(loc, test_dir, "test_gen_tone_*.txt"))
]
test_quantize_files = [
    f for f in glob.glob(os.path.join(loc, test_dir, "test_quantize_*.txt"))
]
test_gen_ramp_files = [
    f
    for f in glob.glob(
        os.path.join(loc, test_dir, "test_gen_ramp_[^and_quantize_]*.txt")
    )
]
test_gen_ramp_and_quantize_files = [
    f
    for f in glob.glob(os.path.join(loc, test_dir, "test_gen_ramp_and_quantize_*.txt"))
]
test_rfft_input_files = [
    f for f in glob.glob(os.path.join(loc, test_dir, "test_rfft_input_*.txt"))
]
test_fft_input_files = [
    f for f in glob.glob(os.path.join(loc, test_dir, "test_fft_input_*.txt"))
]


def get_test_config(f):
    inputs = dict()
    for line in f:
        if "----------" in line:
            break
        else:
            (key, val) = line.split("=")
            (val, new_line) = val.split("\n")
            if key in ["domain_wf", "type_wf", "nfft", "navg", "num_tones", "res", "npts"]:
                inputs[key] = int(val)
            else:
                inputs[key] = float(val)
    
    inputs["freq"] = []
    inputs["phase"] = []
    inputs["scale"] = []
    if "num_tones" in inputs:
        for n in range(inputs["num_tones"]):
            fvar_name = "freq%d"%(n)
            inputs["freq"].append(inputs[fvar_name])
            del(inputs[fvar_name])
            pvar_name = "phase%d"%(n)
            inputs["phase"].append(inputs[pvar_name])
            del(inputs[pvar_name])
            svar_name = "scale%d"%(n)
            inputs["scale"].append(inputs[svar_name])
            del(inputs[svar_name])

    config_obj = genalyzer.gn_params(**inputs)
    return config_obj


@pytest.mark.parametrize("filename", test_gen_tone_files)
def test_gen_tone(filename):
    with open(filename, "r") as f:
        config_obj = get_test_config(f)
        c = genalyzer.config_tone_meas(config_obj)
        awf = genalyzer.gen_tone(c)
        assert len(awf) != 0, "the list is non empty"


@pytest.mark.parametrize("filename", test_quantize_files)
def test_quantize(filename):
    with open(filename, "r") as f:
        config_obj = get_test_config(f)
        c = genalyzer.config_tone_meas(config_obj)
        awf = genalyzer.gen_tone(c)
        qwf = genalyzer.quantize(c, awf)
        assert len(qwf) != 0, "the list is non empty"


@pytest.mark.parametrize("filename", test_gen_ramp_files)
def test_gen_ramp(filename):
    with open(filename, "r") as f:
        config_obj = get_test_config(f)
        c = genalyzer.config_ramp_nl_meas(config_obj)
        awf = genalyzer.gen_ramp(c)
        assert len(awf) != 0, "the list is non empty"


@pytest.mark.parametrize("filename", test_rfft_input_files)
def test_rfft(filename):
    with open(filename, "r") as f:
        config_obj = get_test_config(f)
        c = genalyzer.config_tone_meas(config_obj)
        awf = genalyzer.gen_tone(c)
        qwf = genalyzer.quantize(c, awf)
        out_i, out_q = genalyzer.rfft(c, qwf)
        assert len(out_i) != 0, "the list is non empty"
        assert len(out_q) != 0, "the list is non empty"


@pytest.mark.parametrize("filename", test_fft_input_files)
def test_fft(filename):
    with open(filename, "r") as f:
        config_obj = get_test_config(f)
        c = genalyzer.config_tone_meas(config_obj)
        awf = genalyzer.gen_tone(c)
        qwf = genalyzer.quantize(c, awf)
        qwf_i = [qwf[i] for i in range(len(qwf)) if i % 2 == 0]
        qwf_q = [qwf[i] for i in range(len(qwf)) if i % 2 != 0]
        out_i, out_q = genalyzer.fft(c, qwf_i, qwf_q)
        assert len(out_i) != 0, "the list is non empty"
        assert len(out_q) != 0, "the list is non empty"


@pytest.mark.parametrize("filename", test_quantize_files)
def test_metric_t(filename):
    with open(filename, "r") as f:
        config_obj = get_test_config(f)
        c = genalyzer.config_tone_meas(config_obj)
        awf = genalyzer.gen_tone(c)
        qwf = genalyzer.quantize(c, awf)
        result, fft_i, fft_q, err_code = genalyzer.metric_t(c, qwf, "SFDR")
        assert err_code != 22, "invalid argument"


@pytest.mark.parametrize("filename", test_fft_input_files)
def test_fft_metric_f(filename):
    with open(filename, "r") as f:
        config_obj = get_test_config(f)
        c = genalyzer.config_tone_meas(config_obj)
        awf = genalyzer.gen_tone(c)
        qwf = genalyzer.quantize(c, awf)
        qwf_i = [qwf[i] for i in range(len(qwf)) if i % 2 == 0]
        qwf_q = [qwf[i] for i in range(len(qwf)) if i % 2 != 0]
        fft_i, fft_q = genalyzer.fft(c, qwf_i, qwf_q)
        fft_data = [val for pair in zip(fft_i, fft_q) for val in pair]
        result, err_code = genalyzer.metric_f(c, fft_data, "SFDR")
        assert err_code != 22, "invalid argument"


@pytest.mark.parametrize("filename", test_rfft_input_files)
def test_rfft_metric_f(filename):
    with open(filename, "r") as f:
        config_obj = get_test_config(f)
        c = genalyzer.config_tone_meas(config_obj)
        awf = genalyzer.gen_tone(c)
        qwf = genalyzer.quantize(c, awf)
        rfft_i, rfft_q = genalyzer.rfft(c, qwf)
        rfft_data = [val for pair in zip(rfft_i, rfft_q) for val in pair]
        result, err_code = genalyzer.metric_f(c, rfft_data, "SFDR")
        assert err_code != 22, "invalid argument"