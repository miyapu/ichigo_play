import time
import random
from speech import Speech

if __name__ == "__main__":
    # sp = Speech("./wav/", tts_mode=True)
    sp = Speech("./wav/", tts_mode=False)
    count = 1
    while (True):
        count += 1
        # sp.talk(1, "いちばん", 0.7, 12, 5.0)
        # sp.talk(2, "にばん", 0.7, 12, 5.0)
        # sp.talk(3, "さんばん", 0.7, 12, 5.0)

        target_index = random.randint(1, 3)
        sp.talk(index=target_index, limit_sec=3.0)
        print(f"index={target_index}")

        if count == 3:
            count = 1
        time.sleep(1.0)
