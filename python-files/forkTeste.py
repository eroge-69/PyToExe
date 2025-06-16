from multiprocessing import Process, Semaphore
import time
import os

NUM_PROCESSOS = 5

# Função representa um processo que usa a impressora.

def imprimir(semaforo):
    pid = os.getpid()
    print(f"Processo {pid} esperando uma impressora...")
    semaforo.acquire()
    print(f"Processo {pid} está imprimindo...")
    time.sleep(2)
    print(f"Processo {pid} terminou de imprimir.")
    semaforo.release()

if __name__ == "__main__":

    # Cria um semáforo com valor inicial pra duas impressoras.

    impressoras = Semaphore(2)
    processos = []

    for _ in range(NUM_PROCESSOS):
        p = Process(target=imprimir, args=(impressoras,))
        p.start()
        processos.append(p)

    for p in processos:
        p.join()

    print("Todos os processos terminaram.")
