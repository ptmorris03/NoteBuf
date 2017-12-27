import numpy as np
import math

from param import _Param


class _Envelope(_Param):
    def __init__(self, params):
        self.param_list.extend(["duration", "amplitude", "sample_rate"])
        self.opt_param_list.extend(["attack", "decay", "sustain", "release"])
        super().__init__(params)
        assert self.attack + self.decay + self.release < self.duration or math.isclose(self.attack + self.decay + self.release, self.duration)
        
        self.env = np.empty(int(self.sample_rate * self.duration)).astype(np.float32)

        self.a = int(self.attack * self.sample_rate)
        self._d = int(self.decay * self.sample_rate)
        self.d = int((self.attack+self.decay) * self.sample_rate)
        self.s = int((self.duration-self.release) * self.sample_rate)
        self.r = int(self.release * self.sample_rate)
    
    def _set_opt_param_vals(self, params):
        super()._set_opt_param_vals(params)
        if not "attack" in params:
            self.attack = 0.1 * params["duration"]
        if not "decay" in params:
            self.decay = 0.1 * params["duration"]
        if not "sustain" in params:
            self.sustain = params["amplitude"]
        if not "release" in params:
            self.release = 0.1 * params["duration"]

    def apply(self, buffer):
        assert buffer.size == self.env.size
        buffer *= self.env


class EnvExponential(_Envelope, _Param):
    def __init__(self, params):
        self.opt_param_list.extend(["exp_factor"])
        super().__init__(params)

        self.env[:self.a] = self._env_exp(np.linspace(0.0, self.attack, self.a), 0.0, self.amplitude, 0.0, self.attack)
        self.env[self.a:self.d] = self._env_exp(np.linspace(self.attack, self.attack + self.decay, self._d), self.amplitude, self.sustain, self.attack, self.attack + self.decay)
        self.env[self.d:self.s] = self.sustain
        self.env[self.s:] = self._env_exp(np.linspace(self.duration - self.release, self.duration, self.r), self.sustain, 0.0, self.duration - self.release, self.duration)

    def _set_opt_param_vals(self, params):
        super()._set_opt_param_vals(params)
        if not "exp_factor" in params:
            self.exp_factor = 0.326

    def _env_exp(self, x, a0, a1, t0, t1):
        assert self.exp_factor > 0 and self.exp_factor <= 1
        assert a0 >= 0 and a0 <= 1
        assert a1 >= 0 and a1 <= 1
        assert t0 >= 0 and t1 > 0

        return (a0 - a1) * np.power(1 - (x - t0) / (t1 - t0), 1 / self.exp_factor) + a1


class EnvLinear(_Envelope):

    def __init__(self, params):
        super().__init__(params)

        self.env[:a] = np.linspace(0.0, self.amplitude, a)
        self.env[a:d] = np.linspace(self.amplitude, self.sustain, _d)
        self.env[d:s] = self.sustain
        self.env[s:] = np.linspace(self.sustain, 0.0, r)
