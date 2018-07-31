import contextlib
import datetime
now = datetime.datetime.now()
count_limit = 500
time_limit = float("inf")
name = f"{now.month}.{now.day} {now.hour}:{now.minute} count {count_limit} time {time_limit} TestLog.txt"
import SemanticExtraction
import CorpusBuilder
sents = CorpusBuilder.get_mixed(count_limit)
if count_limit > len(sents):
    count_limit = len(sents)
import time
start_time = time.time()
count = 0
while time.time()-start_time < time_limit and count < count_limit:
    print("======")
    loop_time = time.time()
    with open(name, 'a') as f:
        with contextlib.redirect_stdout(f):
            print(f"run {count}".center(50, "="))
            # noinspection PyBroadException
            try:
                image = SemanticExtraction.extract(sents[count], True)
                image_ascii = image.draw(None, None, force_ascii=True)
                print(image_ascii)
                print(image.to_networkx().number_of_edges())
                print(image.iterate())
            except Exception as e:
                print(str(e))
            print(f"end {time.time()-loop_time}".center(50, "="))
    count += 1
    print(count)
end_time = time.time()
print(f"average runtime: {(start_time-end_time)/count}")
