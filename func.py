import matplotlib.pyplot as plt
import numpy as np


def plot_ethusdt_regression(data, regression_coefficient):

    # Выберем только нужные столбцы
    selected_data = data[['timestamp', 'ethusdt', 'btcusdt']]

    # Добавим столбец с разницей цен ethusdt и коэффициент btcusdt
    selected_data['ethusdt_adjusted'] = selected_data['ethusdt'] - (
                selected_data['btcusdt'] * regression_coefficient)

    # Используем numpy для подготовки данных
    X = selected_data['btcusdt'].values.reshape(-1, 1)
    y = selected_data['ethusdt_adjusted'].values

    # Выполним линейную регрессию
    A = np.vstack([X.flatten(), np.ones(len(X))]).T
    m, c = np.linalg.lstsq(A, y, rcond=None)[0]

    # Предсказание значений
    predicted_ethusdt = m * X.flatten() + c

    # Построим график
    plt.figure(figsize=(10, 6))
    plt.scatter(selected_data['btcusdt'], selected_data['ethusdt_adjusted'],
                label='ETHUSDT Adjusted')
    plt.plot(X.flatten(), predicted_ethusdt, color='red', linewidth=2,
             label='Regression Line')
    plt.xlabel('BTCUSDT')
    plt.ylabel('ETHUSDT Adjusted')
    plt.legend()
    plt.title('ETHUSDT Regression Adjusted')
    plt.show()
