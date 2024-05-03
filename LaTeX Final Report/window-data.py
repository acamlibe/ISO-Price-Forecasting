def get_window_data(np_arr, n_past, n_future):
    X, y = [], []
    for i in range(n_past, len(np_arr) - n_future + 1):
        X.append(np_arr[i - n_past:i])
        y.append(np_arr[i:i + n_future, 0])

    return np.array(X), np.array(y)