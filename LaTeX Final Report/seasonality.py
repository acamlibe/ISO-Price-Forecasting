secs = dates.map(pd.Timestamp.timestamp)

day = 24*60*60
year = (365.2425)*day

day_sin = np.sin(secs * (2 * np.pi / day))
day_cos = np.cos(secs * (2 * np.pi / day))
year_sin = np.sin(secs * (2 * np.pi / year))
year_cos = np.cos(secs * (2 * np.pi / year))