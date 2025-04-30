# simulacao de filas

Organização do código:
main.py = código principal da simulação
evento.py, fila.py, escalonador.py = classes

Como rodar:
1. Instalar dependências
```
pip install -r requirements.txt
```

2. Gerar model.yml:
Para o exemplo do T1, o model.yml já está gerado, mas caso deseja-se utilizar outros valores, precisa alterar o documento.

3. Rodar:
```
python main.py --config model.yml
```
