import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
import numpy as np

# Carregar os dados
data = pd.read_csv("train.csv")

# Selecionar as features relevantes para a tarefa:
# 'GrLivArea' = square footage da área habitável
# 'BedroomAbvGr' = número de quartos acima do solo
# 'FullBath' = número de banheiros completos
# Target: 'SalePrice' = preco da casa

# Verifique se as colunas existem
features = ['GrLivArea', 'BedroomAbvGr', 'FullBath']
target = 'SalePrice'

# Tratar valores ausentes: para simplicidade, removemos linhas com dados faltantes nessas colunas
data = data.dropna(subset=features + [target])

X = data[features]
y = data[target]

# Dividir os dados em treino e teste (80% treino, 20% teste)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Criar o modelo de regressão linear
model = LinearRegression()

# Treinar o modelo
model.fit(X_train, y_train)

# Fazer previsões no conjunto de teste
y_pred = model.predict(X_test)

# Avaliar o modelo
mse = mean_squared_error(y_test, y_pred)
rmse = np.sqrt(mse)
r2 = r2_score(y_test, y_pred)

print(f"Root Mean Squared Error (RMSE): {rmse:.2f}")
print(f"R^2 Score: {r2:.2f}")

# Exemplos de previsão
print("\nExemplo de previsões:")
for i in range(5):
    print(f"Casa com área {X_test.iloc[i]['GrLivArea']} sqft, {X_test.iloc[i]['BedroomAbvGr']} quartos, {X_test.iloc[i]['FullBath']} banheiros.")
    print(f"Preço real: ${y_test.iloc[i]:,.2f}")
    print(f"Preço previsto: ${y_pred[i]:,.2f}\n")
