from user_data import obter_dados_viga
from internal_forces import calculate_reactions, calculate_moments
from otimization_AI import otimizar_posicionamento

# Obter dados do usuário
viga = obter_dados_viga()

# Calcular as reações e momentos
reactions = calculate_reactions(viga)
moments = calculate_moments(viga)

# Otimizar (se implementado)
otimizar_posicionamento(viga)

# Mostrar resultados
print(reactions, moments)
