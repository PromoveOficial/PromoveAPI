DATA_TRAINING = [
    ("Eu quero uma TV Samsung 4k de 55 polegadas.", {"entities": [(12, 39, "PRODUTO"), (15, 22, "MARCA")]}),
    ("Você tem o iPhone 15 Pro Max de 256gb azul?", {"entities": [(11, 30, "PRODUTO"), (34, 39, "CAPACIDADE"), (40, 44, "COR")]}),
    ("Preciso de um fone de ouvido da Sony.", {"entities": [(15, 32, "PRODUTO"), (29, 33, "MARCA")]}),
    ("Estou procurando um notebook Dell com 16gb de RAM.", {"entities": [(20, 34, "PRODUTO"), (29, 33, "MARCA")]}),
    ("O Galaxy S24 Ultra é o melhor da Samsung.", {"entities": [(2, 20, "PRODUTO"), (34, 41, "MARCA")]}),
    ("Quanto custa um Playstation 5?", {"entities": [(18, 32, "PRODUTO")]}),
    ("Tem o livro O Hobbit?", {"entities": [(12, 21, "PRODUTO")]}),
    # Exemplo negativo (sem entidades de produto) para ajudar o modelo a não generalizar demais
    ("Qual o endereço da loja?", {"entities": []}),
    ("Obrigado pela ajuda.", {"entities": []}),
]