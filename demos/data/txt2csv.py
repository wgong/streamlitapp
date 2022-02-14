import pandas as pd
filename = "wl_futures_etf"
txt = open(f"{filename}.txt").read()
etf_dict = {}
for i in txt.replace(",", "").split("\n"):
    i = i.strip()
    if not i: continue
    d = i.split(";")
    sector = d[-1]
    d2 = d[0].split()
    etf = d2[0]
    name = " ".join(d2[1:])
    etf_dict[etf] = [name.strip(), sector.strip()]
# print(etf_dict)
columns = ["symbol", "name", "sector", "rank", "notes"]

data = []
for s in etf_dict.keys():
    data.append([s, etf_dict[s][0], etf_dict[s][1], 0, ""])

df = pd.DataFrame(data=data, columns = columns)
df.to_csv(f"{filename}.csv", index=False)
