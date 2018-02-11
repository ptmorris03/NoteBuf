import random
import numpy as np

from notebuf.oscillator import OscSine, OscSquare, OscSawtooth, OscTriangle
from notebuf.envelope import EnvExponential
from notebuf.synth import SynHarmonic
from notebuf.mixer import MonoMixer, StereoMixer
from notebuf.player import Player
from notebuf.filter import LowPass, HighPass, BandPass, BandStop
from notebuf.param import ParamGroup

def test_synth_sub():
    params = ParamGroup({
        "duration": .08,
        "sample_rate": 44100 })
    
    player = Player(params)

    env_params = params.copy_with({
        "amplitude": 0.7,
        "attack": 0.02,
        "decay": 0.01,
        "sustain": 0.6,
        "release": 0.03 })

    filt_params = params.copy_with({
        "lowcut": 1000,
        "highcut": 2000 })

    filt_params2 = params.copy_with({
        "highcut": 3000 })

    mix_params = ParamGroup({"amplitude": 1})

    def apply(buff):
        BandStop(filt_params).apply(buff)
        LowPass(filt_params2).apply(buff)
        EnvExponential(env_params).apply(buff)
        return buff

    buffs1, buffs2 = [], []
    for i in range(32):
        i_params = params.copy_with({
            "start": 0.02 + i * 0.10,
            "amplitude": 1 - (i / 64),
            "frequency": 860 - (i * 2),
            "pan": 0.2 })

        buffs1.append(apply(OscSawtooth(i_params).buff))

    for i in range(32):
        i_params = params.copy_with({
            "start": i * 0.10,
            "amplitude": 1 - (i / 64),
            "frequency": 220 + (i * i * 2),
            "pan": 0.8 })

        buffs2.append(apply(OscSawtooth(i_params).buff))

    sm = StereoMixer(mix_params)

    lbuff, rbuff = sm.mix(*buffs1, *buffs2)

    player.write(lbuff, rbuff)
    player.wait()

    player.write(rbuff, lbuff)
    player.wait()
