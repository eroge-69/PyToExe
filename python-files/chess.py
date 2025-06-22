import chess
import chess.engine

# Utilise le moteur interne de Stockfish, si tu l'as installé
STOCKFISH_PATH = "stockfish"  # Remplace par le chemin complet si besoin

def jouer_contre_ia():
    board = chess.Board()
    try:
        engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)
    except FileNotFoundError:
        print("Erreur : Stockfish n'est pas installé ou introuvable.")
        return

    print("Bienvenue dans le jeu d'échecs contre une IA ! (vous êtes les Blancs)")
    while not board.is_game_over():
        print(board)
        print("Entrez votre coup (ex: e2e4) :")
        move_input = input("> ")

        try:
            move = chess.Move.from_uci(move_input)
            if move in board.legal_moves:
                board.push(move)
            else:
                print("Coup illégal. Réessayez.")
                continue
        except:
            print("Entrée invalide. Réessayez.")
            continue

        if board.is_game_over():
            break

        # Coup de l'IA
        print("L'IA réfléchit...")
        result = engine.play(board, chess.engine.Limit(time=1.0))
        board.push(result.move)
        print(f"L'IA joue : {result.move}")

    print(board)
    print("Fin de la partie :", board.result())
    engine.quit()

if __name__ == "__main__":
    jouer_contre_ia()
