import time
import random
from speech import Speech

if __name__ == "__main__":
    # sp1 = Speech("./wav/", tts_mode=True)
    sp2 = Speech("./wav/", tts_mode=False)
    count = 1
    while (True):
        count += 1
        # sp1.talk(1, "いちばん", 0.7, 12, 5.0)
        # sp1.talk(2, "にばん", 0.7, 12, 5.0)
        # sp1.talk(3, "さんばん", 0.7, 12, 5.0)

        target_index = random.randint(1, 3)
        sp2.talk(index=target_index, limit_sec=5.0)
        print(f"index={target_index}")
        if count == 3:
            count = 1
        time.sleep(1.0)
