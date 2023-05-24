import os
import subprocess
import time
from collections import deque
from threading import Thread


class Speech(object):
    def __init__(self, wavdir, tts_mode=False):
        '''
        コンストラクタ
        '''
        self.tts_mode = tts_mode
        self.wavdir = wavdir
        self.fname_list = []
        self.playdt_dict = {}
        self.playdt = 0
        self.proc_dict = {}
        self.queue = deque()
        self.reset()

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

    def __get_fname(self, index, text, speed_rate, volume_db):
        '''
        音声合成パラメータ等からWAVファイル名称(文字列)を生成する
        '''
        if self.tts_mode:
            return str(index) + "_" + str(int(100 * speed_rate)) + "_" + str(int(100 * volume_db)) + "_" + text
        else:
            return str(index)

    def __get_tts_info(self, fname):
        '''
        WAVファイル文字列から必要な音声合成パラメータを取り出す
        '''
        arr = fname.split('_')
        index = int(arr[0])
        speed_rate = int(arr[1]) / 100.0
        volume_db = int(arr[2]) / 100.0
        text = arr[3]
        return index, speed_rate, volume_db, text

    def __get_tts_command(self, speed_rate, volume_db):
        '''
        音声合成発話コマンド文字列生成
        '''
        open_jtalk = ['open_jtalk']
        mech = ['-x', '/var/lib/mecab/dic/open-jtalk/naist-jdic']
        speed = ['-r', str(speed_rate)]
        volume = ['-g', str(volume_db)]
        samp = ['-s', '48000']
        htsvoice = ['-m', '/usr/share/hts-voice/mei/mei_normal.htsvoice']
        return open_jtalk + mech + htsvoice + speed + volume + samp

    def __generate_wav(self, fname, speed_rate, volume_db, text):
        '''
        対象のWAVファイルが無い場合, 音声合成コマンドを実行し, WAVファイルを生成する
        '''
        wav_fname = '%s%s.wav' % (os.path.expanduser(self.wavdir), fname)
        if os.path.exists(wav_fname) == False:
            # WAVファイルが存在しない場合, WAVファイル生成する
            print("generate wav file : %s" % (wav_fname))
            outwav = ['-ow', wav_fname]
            c = subprocess.Popen(
                self.__get_tts_command(speed_rate, volume_db) + outwav,
                stdin=subprocess.PIPE)
            c.stdin.write(text.encode())
            c.stdin.close()
            c.wait()
            return True
        return False

    def __talk_thread(self):
        while self.thread_active_flg:
            try:
                if 0 < len(self.queue):
                    fname = self.queue.popleft()
                    # self.playdt_dict[fname] = time.perf_counter()
                    self.playdt = time.perf_counter()

                    # 音声合成モードの場合, テキスト情報に基づきWAVを生成する
                    if self.tts_mode:
                        index, speed_rate, volume_db, text = self.__get_tts_info(
                            fname)
                        if self.__generate_wav(
                            fname, speed_rate, volume_db, text):
                            continue
                        print(f"play {text}")
                    else:
                        print(f"play {fname}")

                    # 全てのWAV再生インスタンスをKillする
                    for tmp_fname in self.fname_list:
                        if self.proc_dict[tmp_fname] is not None:
                            self.proc_dict[tmp_fname].kill()

                    # WAV再生実行
                    aplay_cmd = ['aplay', '-q',  '%s%s.wav' %
                                 (os.path.expanduser(self.wavdir), fname)]
                    self.proc_dict[fname] = subprocess.Popen(aplay_cmd,
                                                             shell=False,
                                                             stdout=subprocess.PIPE)
                else:
                    time.sleep(0.1)
            except Exception as e:
                print("exception at speech.talk_thread() : %s" % (e))

    def reset(self):
        self.queue.clear()
        for fname in self.fname_list:
            self.playdt_dict[fname] = 0
            self.playdt = 0
            self.proc_dict[fname] = None

    def talk(self, index=0, text="", speed_rate=1.0, volume_db=12, limit_sec=1.0):
        try:
            if limit_sec <= 0:
                self.queue.clear()

            target_fname = self.__get_fname(index, text, speed_rate, volume_db)

            is_exist = False
            for fname in self.fname_list:
                if fname == target_fname:
                    is_exist = True
                    break

            if is_exist == False:
                # 新規音声出力の場合, リストに追加しておく
                self.fname_list.append(target_fname)
                self.playdt_dict[target_fname] = 0
                self.proc_dict[target_fname] = None
                self.queue.append(target_fname)

            # 指定秒数を超えた場合, 発音許可する
            # elif limit_sec <= 0 or limit_sec <= (time.perf_counter() - self.playdt_dict[target_fname]):
            elif limit_sec <= 0 or (0 < self.playdt and limit_sec <= (time.perf_counter() - self.playdt)):

                # 全ての再生インスタンスをKillする
                for fname in self.fname_list:
                    if self.proc_dict[fname] is not None:
                        try:
                            self.proc_dict[fname].kill()
                        except:
                            pass
                        finally:
                            self.proc_dict[fname] = None

                self.queue.append(target_fname)

        except Exception as e:
            print("exception at talk() : %s" % (e))

