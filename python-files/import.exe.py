import os
import shutil
from cryptography.fernet import Fernet
import time

class SafeEducationalSimulator:
    def __init__(self):
        self.test_dir = "TEST_SIMULATION_ENV"
        self.encrypted_ext = '.cryptotest'
        self.key = Fernet.generate_key()
        self.cipher = Fernet(self.key)
        
    def create_safe_test_environment(self):
        """Cria ambiente de teste seguro"""
        print("🛡️  CRIANDO AMBIENTE DE TESTE SEGURO...")
        
        # Remove qualquer teste anterior
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        
        # Cria nova estrutura
        os.makedirs(self.test_dir)
        
        # Cria arquivos de teste
        test_files = {
            'documents/': ['test_doc.txt', 'important.docx'],
            'images/': ['photo.jpg', 'image.png'],
            'data/': ['database.db', 'config.json']
        }
        
        for folder, files in test_files.items():
            folder_path = os.path.join(self.test_dir, folder)
            os.makedirs(folder_path, exist_ok=True)
            
            for file in files:
                file_path = os.path.join(folder_path, file)
                with open(file_path, 'w') as f:
                    f.write(f"⚠️ ARQUIVO DE TESTE - {file}\n")
                    f.write(f"Este é um arquivo simulado para testes educacionais\n")
                    f.write(f"Gerado em: {time.ctime()}\n")
                    f.write("=" * 50 + "\n")
                    f.write("Conteúdo seguro para fins de aprendizado\n" * 10)
        
        print(f"✅ Ambiente criado em: {os.path.abspath(self.test_dir)}")
    
    def simulate_encryption(self):
        """Simula processo de criptografia"""
        print("\n🔒 SIMULANDO CRIPTOGRAFIA...")
        
        encrypted_count = 0
        for root, dirs, files in os.walk(self.test_dir):
            for file in files:
                if not file.endswith(self.encrypted_ext):
                    file_path = os.path.join(root, file)
                    
                    try:
                        # Lê o arquivo
                        with open(file_path, 'rb') as f:
                            original_data = f.read()
                        
                        # Simula criptografia (apenas adiciona extensão)
                        encrypted_path = file_path + self.encrypted_ext
                        with open(encrypted_path, 'wb') as f:
                            f.write(original_data)
                        
                        # Remove o original (apenas no ambiente de teste)
                        os.remove(file_path)
                        
                        encrypted_count += 1
                        print(f"📁 Simulado: {file} → {file}{self.encrypted_ext}")
                        
                    except Exception as e:
                        print(f"❌ Erro em {file}: {e}")
        
        print(f"✅ {encrypted_count} arquivos simulados criptografados")
    
    def create_ransom_note(self):
        """Cria nota de resgate educacional"""
        note_content = f"""
        ⚠️⚠️⚠️ SIMULAÇÃO EDUCACIONAL ⚠️⚠️⚠️

        SEUS ARQUIVOS FORAM SIMULADAMENTE CRIPTOGRAFADOS!

        🔐 Chave de descriptografia: {self.key.decode()}
        
        📍 Esta é uma simulação para fins educacionais
        📍 Nenhum arquivo real foi danificado
        📍 Use a chave acima para recuperação

        COMO SE PROTEGER DE VERDADE:
        1. Mantenha backups regulares
        2. Use antivírus atualizado
        3. Não clique em links suspeitos
        4. Mantenha sistema atualizado

        ⏰ Data da simulação: {time.ctime()}
        """
        
        note_path = os.path.join(self.test_dir, "LEIA_ISSO_IMPORTANTE.txt")
        with open(note_path, 'w', encoding='utf-8') as f:
            f.write(note_content)
        
        print(f"📝 Nota de simulação criada: {note_path}")
    
    def simulate_recovery(self):
        """Simula processo de recuperação"""
        print("\n🔓 SIMULANDO RECUPERAÇÃO...")
        
        recovered_count = 0
        for root, dirs, files in os.walk(self.test_dir):
            for file in files:
                if file.endswith(self.encrypted_ext):
                    encrypted_path = os.path.join(root, file)
                    original_path = encrypted_path.replace(self.encrypted_ext, '')
                    
                    try:
                        # Lê arquivo "criptografado"
                        with open(encrypted_path, 'rb') as f:
                            data = f.read()
                        
                        # Restaura arquivo original
                        with open(original_path, 'wb') as f:
                            f.write(data)
                        
                        # Remove arquivo criptografado
                        os.remove(encrypted_path)
                        
                        recovered_count += 1
                        print(f"✅ Recuperado: {file} → {file.replace(self.encrypted_ext, '')}")
                        
                    except Exception as e:
                        print(f"❌ Erro ao recuperar {file}: {e}")
        
        print(f"🔓 {recovered_count} arquivos recuperados")

def main():
    print("=" * 60)
    print("🛡️  SIMULADOR EDUCACIONAL DE RANSOMWARE")
    print("=" * 60)
    
    simulator = SafeEducationalSimulator()
    
    # Cria ambiente seguro
    simulator.create_safe_test_environment()
    
    # Simula ataque
    simulator.simulate_encryption()
    simulator.create_ransom_note()
    
    print("\n" + "=" * 60)
    input("Pressione Enter para simular a recuperação...")
    
    # Simula recuperação
    simulator.simulate_recovery()
    
    print("\n" + "=" * 60)
    print("🎓 SIMULAÇÃO CONCLUÍDA COM SUCESSO!")
    print("📍 Ambiente de teste: ", os.path.abspath(simulator.test_dir))
    print("📍 Lembre-se: isto é apenas para educação!")
    print("=" * 60)

if __name__ == "__main__":
    # Verifica se está em ambiente seguro
    if os.path.exists("/home") or os.path.exists("C:\\Users"):
        print("❌ PERIGO: Não execute em sistema real!")
        print("❌ Use uma máquina virtual ou container")
        exit(1)
    
    main()