import attr
import numpy as np
import soundfile as sf

from i2i.py2store.py2store import KeyValPersister
from i2i.py2store.py2local.py2local import LocalFileDeletionMixin, IterableDirMixin


# Audio Persistence
@attr.s
class WfsrLocalPersister(LocalFileDeletionMixin, IterableDirMixin, KeyValPersister):
    # """ Waveform persister """
    subtype = attr.ib(default='PCM_16')
    dtype = attr.ib(default='int16')

    def dump(self, wfsr, path):
        return sf.write(path, data=wfsr[0], samplerate=wfsr[1], subtype=self.subtype)

    def load(self, path):
        return sf.read(path, dtype=self.dtype)


########################################################################################################################
# chunker

def simple_fixed_step_chunker(seq, chk_size, chk_step=None):
    """
      a function to get (an iterator of) segments [bt, tt) of chunks from an seqquence seq
      of size chk_size, with a step of chk_step

      :param seq: sequence of elements
      :param chk_size: length of the chunks
      :param chk_step: step between chunks
      :return: an iterator of the chunks
    >>> seq = list(range(19))
    >>> seq
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18]
    >>> print(list(simple_fixed_step_chunker(seq, 5)))
    [[0, 1, 2, 3, 4], [5, 6, 7, 8, 9], [10, 11, 12, 13, 14]]
    >>> print(list(simple_fixed_step_chunker(seq, 5, 3)))
    [[0, 1, 2, 3, 4], [3, 4, 5, 6, 7], [6, 7, 8, 9, 10], [9, 10, 11, 12, 13], [12, 13, 14, 15, 16]]
    """

    chk_step = chk_step or chk_size
    seq_minus_chk_length = len(seq) - chk_size
    for bt in range(0, seq_minus_chk_length, chk_step):
        yield seq[bt:(bt + chk_size)]


########################################################################################################################
# featurizers


def mean_intensity(chk) -> float:
    """
    Mean intensity (mean of abs values)
    :param chk: a waveform (list of numbers)
    :return: the mean intensity
    >>> wf = [1, 2, 3, 4]
    >>> mean_intensity(wf)
    2.5
    >>> wf = [10, -10, 10, -10, 10, -10]
    >>> mean_intensity(wf)
    10.0
    >>> wf = [5, 10, 20, -10, -20, 9, -10]
    >>> mean_intensity(wf)
    12.0
    """
    return float(np.mean(np.abs(chk)))


def mean_zero_crossing(chk) -> float:
    """
    Mean zero crossing
    :param chk: a waveform (list of numbers)
    :return: mean zero crossing
    >>> wf = [1, 2, 3, 4]
    >>> mean_zero_crossing(wf)  # if all numbers are positive (or negative), the mean zero crossing is zero
    0.0
    >>> wf = [10, -10, 10, -10, 10, -10]  # if changing signs at every new element, the mean crossing is 1
    >>> mean_zero_crossing(wf)
    1.0
    >>> wf = [5, 10, 20, -10, -20, 9, -10]  # example where the sign changes half of the time
    >>> mean_zero_crossing(wf)
    0.5
    """
    return float(np.mean(np.diff(np.array(chk) > 0)))

# seq = list(range(19))
# print(list(simple_fixed_step_chunker(seq, 5)))
# print(list(simple_fixed_step_chunker(seq, 5, 3)))
