import os
import traceback
from oto_data_storage_api_client import AudioApi, SessionsApi, FindSessionsRequest
from oto.sound.audio_reader import WfReader  # replace to import from audio_utils

os.environ['EXTERNAL_DATA_STORAGE_API_HOST'] = 'https://api.oto-dev.analoggarage.com/data-storage'

audio_api = AudioApi()
sessions_api = SessionsApi()

example_source_id = 'arbitrary_string'
minimum_allowed_bt = 1262304000000000  # 00:00 January 1, 2010 GMT
example_file_path = '/path/to/audio.wav'

example_jwt = 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3NMZXZlbHMiOlsiYWRtaW4iLCJ1c2VyIl0sImFjY291bnQiOiJhbmFsb2dkZXZpY2VzIiwiZW1haWwiOiJzdGV2ZS5oZXJ6b2dAb3Rvc2Vuc2UuY29tIiwiaWF0IjoxNTcxMzM0ODg1LCJleHAiOjE2MDI4OTI0ODV9.YSv3iX3Uai88knxSgvXlJ7k-BxwoVERsnPqoGGr86YTxnLkrGHHsgALSnX_3VPGKqbRWgSMU8OP5zZERlgm6d5vsxE5A1mQknIi49MKIsy_jXljqaIFiCGPmogcy9n4DgiHnlShLsOGy4Sz5QFQ1NE1LLkrVW-q0YxTduEzqDp9AP-RNAImtF-bGLP536zgEvaae8O7SyFmc0Jz8fJmEURyqaNtsLsOrB-m4-zk2fOvwCqlbadrPdKFHN1dBJypK3hwtZUwgoyUPH3jrV4HF8R3Dn61_Bcoi2PzQ8686fodhpD4Ymu7S6qrDopEZp0DDhNo0j5AtaL0qNK_diDXejg'

authorization = 'Bearer {}'.format(example_jwt)


def upload_file_to_source(source_id, file_path, bt=minimum_allowed_bt, sr=44100, bit_depth=16):
    return audio_api.upload_file(authorization=authorization,
                                 source=source_id,
                                 bt=bt,
                                 sr=sr,
                                 bit_depth=bit_depth,
                                 file=file_path)


def get_sessions_for_sources(sources, bt=minimum_allowed_bt, tt=0):
    request = FindSessionsRequest(sources=sources,
                                  bt=bt,
                                  tt=tt)
    return sessions_api.find_sessions(authorization=authorization, find_sessions_request=request)


def get_session_audio(session_id, bt=minimum_allowed_bt, tt=0):
    response = audio_api.get_audio(authorization=authorization,
                                   session_id=session_id,
                                   bt=bt,
                                   tt=tt,
                                   _preload_content=False)
    binary = response.read()
    try:
        reader = WfReader()
        reader.wf_dtype = 'int16'
        result = reader.read_binary(binary)
        return result
    except Exception:
        traceback.print_exc()
        return []
