# seed = 0 # seed
# 0 <= seed < m

# a # multiplicador
# 0 < a < m

# c # incremento
# 0 <= c < m

# m # modulo
# m > 0

# n # quantidade de números a serem gerados

# pseudo = (a * seed + c) % m

import matplotlib.pyplot as plt


def pseudo_random_generator(seed, a, c, m, n=1000):
    pseudos = []
    pseudo = seed
    for i in range(n):
        pseudo = (a * pseudo + c) % m
        pseudos.append(pseudo)
    return pseudos


def generate_dispersion_graph(pseudos, num_segments=10):
    """
    Generate a dispersion graph for pseudo-random numbers.

    Args:
        pseudos: List of pseudo-random numbers
        num_segments: Number of segments to divide the range into

    Returns:
        matplotlib.figure.Figure: The generated figure
    """
    normalized = [p / max(pseudos) for p in pseudos]

    fig, ax = plt.subplots(figsize=(10, 6))

    # Create n pairs of consecutive numbers
    x_values = normalized[:-1]
    y_values = normalized[1:]

    ax.scatter(x_values, y_values, alpha=0.6, s=5)
    # ax.set_xlabel("X[i]")
    # ax.set_ylabel("X[i+1]")
    ax.set_title("Gráfico de dispersão para 1000 números pseudo-aleatórios")
    ax.grid(True, linestyle="--", alpha=0.7)

    # Set both axes to have the same range
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    return fig


def write_txt_pseudo_numbers(pseudos):
    with open("pseudos.txt", "w") as f:
        for pseudo in pseudos:
            f.write(f"{pseudo} - ")
    print("Pseudo-random numbers written to pseudos.txt")


SEED = 987654321
A = 214013
C = 2531011
M = 98765432112
print(M)

pseudos = pseudo_random_generator(SEED, A, C, M)
write_txt_pseudo_numbers(pseudos)
generate_dispersion_graph(pseudos)

plt.savefig("dispersion_graph.png", dpi=300, bbox_inches="tight")

amount = 0
for p in pseudos:

    length = len(str(p))
    if length < 10:
        print(length)
        amount += 1
print(amount)
