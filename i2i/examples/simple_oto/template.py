import os

from typing import Tuple, List, Dict, NamedTuple, Any, Callable, Union
from i2i.examples.simple_oto.utils import mean_intensity, mean_zero_crossing, simple_fixed_step_chunker
from i2i.examples.simple_oto.utils import resolve_filepath_of_name

Waveform = List[int]
WfSr = Tuple[Waveform, int]
FeatureVector = List[float]

SourceAnnotation = Tuple[str, Any]
SourceSegmentAnnotation = Tuple[str, Any, int, int]
Annotation = Union[SourceAnnotation, SourceSegmentAnnotation]
Annotations = List[Annotation]

WfSegmentTag = Tuple[str, int, int, str]
DictList = List[dict]

Featurizer = Callable[[Waveform], FeatureVector]
FvModel = Callable[[FeatureVector], Any]
WfModel = Callable[[Waveform], List[Any]]

# defaults

import soundfile as sf
import json

DFLT_CHK_SIZE = 21 * 2048


def dflt_dump_wfsr(wfsr: WfSr, wf_name: str):
    return sf.write(wf_name, data=wfsr[0], samplerate=wfsr[1], subtype='PCM_16')


def dflt_load_wfsr(wfsr: WfSr, wf_name: str):
    return sf.read(wf_name, dtype='int16')


def dflt_featurizer(chk):
    return [mean_intensity(chk), mean_zero_crossing(chk)]


# directory resolution

app_data_root = os.path.expanduser('~/simple_oto')
# app_data_root = None
if app_data_root:
    wav_dir = os.path.join(app_data_root, 'wav_files')
    annots_dir = os.path.join(app_data_root, 'annots')
    models_dir = os.path.join(app_data_root, 'models')

    for dirpath in [app_data_root, wav_dir, annots_dir, models_dir]:
        if not os.path.isdir(dirpath):
            os.mkdir(dirpath)
else:
    wav_dir, annots_dir, models_dir = [None] * 3


# source io
@resolve_filepath_of_name(wav_dir, 'wf_name')
def dump_wfsr(wfsr: WfSr, wf_name: str):
    """Store the wfsr under given name"""
    return dflt_dump_wfsr(wfsr, wf_name)


@resolve_filepath_of_name(wav_dir, 'wf_name')
def load_wfsr(wf_name: str) -> WfSr:
    """Load the wav file, returning the waveform and sample rate"""
    return dflt_load_wfsr(wf_name)


# annotations io
@resolve_filepath_of_name(annots_dir, 'annots_name')
def load_annotations(annots_name: str) -> Annotations:
    return json.load(open(annots_name))


@resolve_filepath_of_name(annots_dir, 'annots_name')
def dump_annotations(annots: Annotations, annots_name: str):
    return json.dump(annots, open(annots_name, 'w'))


def load_featurizer(featurizer_name: str = None) -> Featurizer:
    """Load the featurizer, given a name"""
    if featurizer_name is None:
        featurizer = dflt_featurizer
    else:
        pass
    return featurizer


def _file_tags_gen(file_tags_name: str, tags: List[str]):
    file_tags = load_file_tags(file_tags_name)


#     for

def _chk_tag_gen(tags: List[str], chk_size=DFLT_CHK_SIZE, chk_step=None):
    pass


def fit_model_from_tags(tags: List[str]) -> FvModel:
    pass


def fit_and_save_model(tags: List[str], model_name: str):
    pass


def load_wf(file_name: str) -> Waveform:
    """Load the wav file, returning the waveform only"""
    return load_wf(file_name)[0]


def mk_chunker(chk_size, chk_step=None):
    def chunker(wf):
        return simple_fixed_step_chunker(wf, chk_size, chk_step)

    return chunker


def run_model_on_wf(wf: Waveform, featurizer: Featurizer, fv_model: FvModel, chk_size=DFLT_CHK_SIZE, chk_step=None) -> \
List[Any]:
    """Run the model on """
    model_outputs = list()
    for chk in simple_fixed_step_chunker(wf, chk_size, chk_step):
        fv = featurizer(chk)
        model_outputs.append(fv_model(fv))
    return model_outputs


def run_model_on_file(file_name: str, featurizer: Featurizer, fv_model: FvModel, chk_size=DFLT_CHK_SIZE,
                      chk_step=None) -> List[Any]:
    """Run the model on """
    wf = load_wf(file_name)
    return run_model_on_wf(wf, featurizer, fv_model, chk_size, chk_step)

# alternative using decorator
# run_model_on_file = use_loader(run_model_on_file, load_wf)
