import os
import subprocess
import time
from threading import Thread


class Play(object):
    def __init__(self, wavdir):
        '''
        コンストラクタ
        '''
        self.wavdir = wavdir
        self.fname = None
        self.playdt = 0
        self.proc = None

        self.thread_active_flg = True
        self.thread = Thread(target=self.__talk_thread, args=())
        self.thread.daemon = True
        self.thread.start()

    def __del__(self):
        '''
        デストラクタ
        '''
        print("deleted speech instance!")
        self.thread_active_flg = False
        if self.thread is not None:
            self.thread.join()
            self.thread = None

    def __talk_thread(self):
        while self.thread_active_flg:
            try:
                if self.fname is not None:
                    fname = self.fname
                    self.fname = None
                    self.playdt = time.perf_counter()

                    # # WAV再生インスタンスをKillする
                    if self.proc is not None:
                        self.proc.kill()

                    # WAV再生実行
                    aplay_cmd = ['aplay', '-q',  '%s%s.wav' %
                                 (os.path.expanduser(self.wavdir), fname)]
                    print(f"play {fname}.wav")
                    self.proc = subprocess.Popen(
                        aplay_cmd, shell=False, stdout=subprocess.PIPE)

            except Exception as e:
                print("exception at speech.talk_thread() : %s" % (e))
            finally:
                time.sleep(0.1)

    def talk(self, index=0, limit_sec=1.0):
        try:
            if self.fname is not None:
                return
            # 指定秒数を超えた場合, 発音許可する
            if limit_sec <= 0 or (limit_sec <= (time.perf_counter() - self.playdt)):
                self.fname = index
        except Exception as e:
            print("exception at talk() : %s" % (e))
