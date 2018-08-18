import asyncio
import tempfile
import websockets
import time
import os
import ujson as json
import hashlib
import aiy.audio  # noqa # pylint: disable=import-error
import aiy.voicehat  # noqa # pylint: disable=import-error
from gtts import gTTS
from ._player import simple_player
from ._recorder import simple_recorder
from .logger import logger
from .exceptions import WebSocketAuthenticationError
import glob

DEMO = True
DEMO_CNT = 0
#DEMO = False

PJ = os.path.join
this_dir = os.path.dirname(os.path.abspath(__file__))

ws_endpoint = os.environ.get('WS_ENDPOINT')
ws_token = os.environ.get('WS_TOKEN')

led = aiy.voicehat.get_led()

if ws_endpoint is None or ws_token is None :
    raise ValueError('Must provide websocket')

def update_data():
    '''
    query sql
    '''
    a = 1


def load_data():
    with open('./data/data.json', 'r') as f:
        d = json.load(f)
    return d

def response(sentence):
    led.set_state(led.ON)
    audio_dir = 'audio/'

    if '本周' in sentence and '熱門' in sentence:
        with open(PJ(this_dir, 'audio/week.mp3'), 'rb') as fd:
            simple_player.play_bytes(fd)
        audio_dir += 'hot_week/*'
        path = PJ(this_dir,audio_dir)
        filelist = glob.glob(path)
        for f in sorted(filelist):
            print(f)

    elif '網友' in sentence and '推薦' in sentence:
        with open(PJ(this_dir, 'audio/web.mp3'), 'rb') as fd:
            simple_player.play_bytes(fd)
        audio_dir += 'hot_web/*'
        path = PJ(this_dir,audio_dir)
        filelist = glob.glob(path)
        for f in sorted(filelist):
            print(f)

    elif '更新' in sentence and '資料' in sentence:
        update_data()
        with open(PJ(this_dir, 'audio/update_finish.mp3'), 'rb') as fd:
            simple_player.play_bytes(fd)

    led.set_state(led.BLINK)
async def record_to_buffer(ws_queue):
    led.set_state(led.PULSE_QUICK)
    logger.info('Recording from microphone.')
    retcode = await simple_recorder.record_wav(ws_queue)
    logger.info('Recording is finished.')
    logger.info('Calling ASR service')
    return retcode

async def handle_websocket(ws_queue):
    logger.info('Opening websocket to WS_HOST')
    async with websockets.connect(ws_endpoint) as ws:
        logger.info('Checking authentication')
        await ws.send(json.dumps(dict(action='open_session', pipeline='ime')))
        recv = await ws.recv()
        auth = ws_token + ' ' + json.loads(recv).get('auth_challenge')  # XXX
        hash_auth = hashlib.sha1(auth.encode('utf-8'))

        payload = dict(authorization=hash_auth.hexdigest())
        await ws.send(json.dumps(payload))

        recv = await ws.recv()
        logger.info('Finishing websocket setup: %s' % recv)
        if json.loads(recv).get('status') != 'ok':
            raise WebSocketAuthenticationError('The websocket api token may not be available.')
        logger.info('Ready to send PCM bytes to WS_HOST.')

        async def wait_for_queue():
            while True:
                data = await ws_queue.get()
                await ws.send(data)
                if len(data) == 0:
                    break

        async def wait_for_ws():
            sentences = []
            while True:
                msg = await ws.recv()
                body = json.loads(msg)
                # logger.info(msg)
                if 'asr_sentence' in body['pipe']:
                    sentences.append(body['pipe'].get('asr_sentence'))
                    continue
                if body['pipe'].get('asr_eof', False):
                    break
            return sentences[-1] if len(sentences) > 0 else '蛤'

        asyncio.ensure_future(wait_for_queue())
        out = await asyncio.ensure_future(wait_for_ws())
        with open(PJ(this_dir, 'res/response.mp3'), 'rb') as fd:
            simple_player.play_bytes(fd)
        logger.info('STT result: %s' % out) 
        led.set_state(led.BLINK_3)
        
        if DEMO:
            if DEMO_CNT == 1:
                out = '本周熱門'
            elif DEMO_CNT == 2:
                out = '網友推薦'
            elif DEMO_CNT == 0:
                out = '更新資料'
        response(out) 
        
def main():
    if DEMO:
        global DEMO_CNT
        DEMO_CNT += 1 
        DEMO_CNT %= 3

    led.set_state(led.ON)
    with open(PJ(this_dir,'audio/welcome.mp3'), 'rb') as fd:
        simple_player.play_bytes(fd)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    ws_queue = asyncio.Queue()
    speaker_queue = asyncio.Queue()

    try:
        loop.run_until_complete(
            asyncio.gather(record_to_buffer(ws_queue),
                           handle_websocket(ws_queue))
        )
        with open(PJ(this_dir, 'res/deactivate.mp3'), 'rb') as fd:
            simple_player.play_bytes(fd)

    except Exception as err:
        logger.error(err)
        loop.stop()
        loop.run_forever()

    finally:
        loop.close()
        led.set_state(led.BLINK)
    logger.info('Done')


if __name__ == '__main__':
    with open(PJ(this_dir, 'res/init.mp3'), 'rb') as fd:
        simple_player.play_bytes(fd)
    led.set_state(led.BLINK)

    button = aiy.voicehat.get_button()
    button.on_press(main)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass

    finally:
        led.set_state(led.OFF)
        led.stop()
