from os.path import join

json_ids = os.listdir("/data/honesty/corpora/Twitter/US_politician_twitter_conversations")
json_ids = set([i.split(".")[0] for i in json_ids])

csv_ids = os.listdir("/data/honesty/corpora/Twitter/US_politician_twitter_conversations_csv")
csv_ids = set([i.split(".")[0] for i in csv_ids])
print(f"{len(json_ids)} json conversations, {len(csv_ids)} csv conversations")

diff = json_ids.difference(csv_ids)
dst = "/home/jlasser/Honesty-project/code/corpus_twitter"
print(f"{len(diff)} conversations to convert")
np.savetxt(join(dst, "conversations_to_convert.txt"), np.asarray(list(diff)), fmt='%s')