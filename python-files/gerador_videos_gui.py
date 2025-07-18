import subprocess
import sys
import os
import platform
import random
import colorsys
import math
from PIL import Image, ImageDraw, ImageFilter, ImageChops
from PIL.ImageEnhance import Contrast, Color 
import numpy as np

# A importação de VideoClip será feita após a verificação das dependências.
# from moviepy.editor import VideoClip 

# --- Bloco de Verificação e Instalação de Dependências ---
# Este bloco é mais para o script original. Para o EXE, as libs já estarão empacotadas.
# Mas mantemos para o caso de alguém rodar o .py diretamente.
required_packages = {
    "moviepy": None, 
    "numpy": None,
    "Pillow": None
}

def install_package(package_name, version=None):
    """Instala um pacote pip, opcionalmente com uma versão específica."""
    try:
        if version:
            print(f"Tentando instalar {package_name}=={version}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", f"{package_name}=={version}"])
        else:
            print(f"Tentando instalar {package_name}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        print(f"{package_name} instalado com sucesso.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Erro ao instalar {package_name}: {e}")
        return False

def check_and_install_packages(packages):
    """Verifica e instala pacotes se não estiverem presentes."""
    installed_all = True
    for package, version in packages.items():
        try:
            if package == "moviepy":
                from moviepy.editor import VideoClip 
                # print(f"{package} já está instalado (versão compatível).") # Comentado para evitar log repetitivo no EXE
            elif package == "Pillow":
                from PIL import Image
                # print(f"{package} já está instalado.") # Comentado para evitar log repetitivo no EXE
            else:
                __import__(package)
                # print(f"{package} já está instalado.") # Comentado para evitar log repetitivo no EXE
            # Se for um EXE, essas libs já estão. Se for .py, este check garante.
        except ImportError:
            # Este caminho só será executado se o script for rodado como .py e as libs não estiverem instaladas
            print(f"{package} não encontrado. Iniciando instalação...")
            if not install_package(package, version):
                installed_all = False
                break
        except Exception as e:
            print(f"Ocorreu um erro ao verificar {package}: {e}")
            installed_all = False
            break

    if not installed_all:
        print("\nAlguns pacotes essenciais não puderam ser instalados. Por favor, verifique sua conexão com a internet ou as permissões do seu ambiente virtual.")
        sys.exit(1)

# check_and_install_packages(required_packages) # Chamado apenas se o script for rodado como .py
# --- Fim do Bloco de Verificação e Instalação ---

# Agora que as dependências estão garantidas, podemos importar moviepy
from moviepy.editor import VideoClip 

# --- Funções de Ajuda para Cores e Perlin Noise ---
def hsv_to_rgb(h, s, v):
    """Converte valores HSV (0-1) para RGB (0-255)."""
    return tuple(int(i * 255) for i in colorsys.hsv_to_rgb(h, s, v))

def get_unique_palette(seed_val):
    """Gera uma paleta de cores complexa e única baseada em uma semente, com diferentes esquemas."""
    random.seed(seed_val)
    palette = []
    num_colors = random.randint(4, 7)

    scheme = random.choice(['complementary', 'analogous', 'triadic', 'split_complementary', 'monochromatic_analogous', 'random_vibrant'])
    
    base_hue = random.uniform(0, 1)

    if scheme == 'complementary':
        palette.append(hsv_to_rgb(base_hue, random.uniform(0.7, 1.0), random.uniform(0.8, 1.0)))
        palette.append(hsv_to_rgb((base_hue + 0.5) % 1.0, random.uniform(0.7, 1.0), random.uniform(0.8, 1.0)))
    elif scheme == 'analogous':
        for i in range(num_colors):
            hue = (base_hue + (i - num_colors/2) * random.uniform(0.05, 0.15)) % 1.0
            palette.append(hsv_to_rgb(hue, random.uniform(0.6, 1.0), random.uniform(0.7, 1.0)))
    elif scheme == 'triadic':
        palette.append(hsv_to_rgb(base_hue, random.uniform(0.7, 1.0), random.uniform(0.8, 1.0)))
        palette.append(hsv_to_rgb((base_hue + 1/3) % 1.0, random.uniform(0.7, 1.0), random.uniform(0.8, 1.0)))
        palette.append(hsv_to_rgb((base_hue + 2/3) % 1.0, random.uniform(0.7, 1.0), random.uniform(0.8, 1.0)))
    elif scheme == 'split_complementary':
        palette.append(hsv_to_rgb(base_hue, random.uniform(0.7, 1.0), random.uniform(0.8, 1.0)))
        palette.append(hsv_to_rgb((base_hue + 0.5 - random.uniform(0.05, 0.1)) % 1.0, random.uniform(0.7, 1.0), random.uniform(0.8, 1.0)))
        palette.append(hsv_to_rgb((base_hue + 0.5 + random.uniform(0.05, 0.1)) % 1.0, random.uniform(0.7, 1.0), random.uniform(0.8, 1.0)))
    elif scheme == 'monochromatic_analogous': 
        base_saturation = random.uniform(0.7, 1.0)
        base_value = random.uniform(0.6, 1.0)
        for i in range(num_colors):
            hue = (base_hue + (i - num_colors/2) * random.uniform(0.01, 0.05)) % 1.0
            saturation = base_saturation * random.uniform(0.8, 1.0)
            value = base_value * random.uniform(0.7, 1.0)
            palette.append(hsv_to_rgb(hue, saturation, value))
    elif scheme == 'random_vibrant': # Cores vibrantes totalmente aleatórias
        for _ in range(num_colors):
            palette.append(hsv_to_rgb(random.uniform(0,1), random.uniform(0.8, 1.0), random.uniform(0.8, 1.0)))

    palette.append(hsv_to_rgb(base_hue, random.uniform(0.1, 0.3), random.uniform(0.2, 0.4))) 
    palette.append(hsv_to_rgb(base_hue, random.uniform(0.0, 0.1), random.uniform(0.9, 1.0))) 

    random.shuffle(palette)
    return palette

class PerlinNoise:
    def __init__(self, seed=None):
        self.perm = np.arange(256, dtype=int)
        if seed is not None:
            np.random.seed(seed)
        np.random.shuffle(self.perm)
        self.perm = np.stack([self.perm, self.perm]).flatten()

    def _fade(self, t):
        return t * t * t * (t * (t * 6 - 15) + 10)

    def _grad(self, hash, x, y=0, z=0):
        h = hash & 15
        u = x if h < 8 else y
        v = y if h < 4 else (x if h == 12 or h == 14 else z)
        return (u if (h & 1) == 0 else -u) + (v if (h & 2) == 0 else -v)

    def noise(self, x, y=0, z=0):
        X = math.floor(x) & 255
        Y = math.floor(y) & 255
        Z = math.floor(z) & 255

        x -= math.floor(x)
        y -= math.floor(y)
        z -= math.floor(z)

        u = self._fade(x)
        v = self._fade(y)
        w = self._fade(z)

        A = self.perm[X] + Y
        AA = self.perm[A] + Z
        AB = self.perm[A + 1] + Z
        B = self.perm[X + 1] + Y
        BA = self.perm[B] + Z
        BB = self.perm[B + 1] + Z

        return (
            (self._grad(self.perm[AA], x, y, z) * (1 - u) * (1 - v) * (1 - w))
            + (self._grad(self.perm[BA], x - 1, y, z) * u * (1 - v) * (1 - w))
            + (self._grad(self.perm[AB], x, y - 1, z) * (1 - u) * v * (1 - w))
            + (self._grad(self.perm[BB], x - 1, y - 1, z) * u * v * (1 - w))
            + (self._grad(self.perm[AA + 1], x, y, z - 1) * (1 - u) * (1 - v) * w)
            + (self._grad(self.perm[BA + 1], x - 1, y, z - 1) * u * (1 - v) * w)
            + (self._grad(self.perm[AB + 1], x, y - 1, z - 1) * (1 - u) * v * w)
            + (self._grad(self.perm[BB + 1], x - 1, y - 1, z - 1) * u * v * w)
        )

# --- Função Principal para Gerar Cada Frame Orgânico e Distorcido ---
def create_dynamic_frame(width, height, t, video_params):
    """
    Cria um frame de animação com efeitos orgânicos, distorção e alto contraste.
    t: tempo (float) dentro do clipe.
    video_params: Dicionário de parâmetros únicos para este vídeo.
    """
    seed_val = video_params['seed']
    style = video_params['style']
    palette = video_params['palette']
    perlin = video_params['perlin_noise']
    
    random.seed(seed_val * 1000 + int(t * 1000))
    np.random.seed(seed_val * 1000 + int(t * 1000))

    # Inicializa bg_img e bg_draw aqui para que estejam sempre definidos
    bg_img = Image.new('RGB', (width, height), color=(0,0,0))
    bg_draw = ImageDraw.Draw(bg_img) 

    # --- Fundo Dinâmico ---
    if style.get('background_type') == 'perlin_smoke':
        # *** OTIMIZAÇÃO CRÍTICA AQUI: GERAR PERLIN EM BAIXA RES E UPSCALAR ***
        low_res_width = width // 4 
        low_res_height = height // 4 

        # Ajuste a forma como smoke_scale_factor é calculado para garantir que seja sempre positivo.
        # Normaliza o ruído para 0-1, depois o usa para modular a densidade.
        smoke_scale_factor = style.get('bg_smoke_density_base', 0.005) + (perlin.noise(t * style.get('bg_smoke_density_speed', 0.2), 0, 0) + 1) / 2.0 * style.get('bg_smoke_density_amp', 0.002)
        # Garante que smoke_scale_factor seja sempre maior que um valor mínimo para evitar divisão por zero ou escalas muito grandes.
        smoke_scale_factor = max(0.0001, smoke_scale_factor) # Garante um mínimo positivo

        smoke_speed_factor = style.get('bg_smoke_speed_base', 0.1)
        time_offset = t * smoke_speed_factor
        
        low_res_bg_array = np.zeros((low_res_height, low_res_width, 3), dtype=np.uint8)
        for y_lr in range(low_res_height):
            for x_lr in range(low_res_width):
                noise_val = perlin.noise(x_lr * smoke_scale_factor, y_lr * smoke_scale_factor, time_offset)
                normalized_noise = (noise_val + 1) / 2.0
                
                num_colors_bg = len(palette)
                color_index_float = normalized_noise * (num_colors_bg - 1)
                idx1 = int(color_index_float)
                idx2 = min(idx1 + 1, num_colors_bg - 1)
                blend_factor = color_index_float - idx1
                
                color1 = palette[idx1]
                color2 = palette[idx2]

                r = int(color1[0] * (1 - blend_factor) + color2[0] * blend_factor)
                g = int(color1[1] * (1 - blend_factor) + color2[1] * blend_factor)
                b = int(color1[2] * (1 - blend_factor) + color2[2] * blend_factor)
                low_res_bg_array[y_lr, x_lr] = [r, g, b]
        
        low_res_pil_img = Image.fromarray(low_res_bg_array)
        bg_img = low_res_pil_img.resize((width, height), Image.LANCZOS) 
        bg_img = bg_img.filter(ImageFilter.GaussianBlur(radius=style.get('bg_smoke_blur_radius', 2.0))) 

    elif style.get('background_type') == 'radial_gradient':
        bg_color_1 = palette[0]
        bg_color_2 = palette[1] if len(palette) > 1 else palette[0]
        for i in range(max(width, height) // 2, 0, -style.get('bg_gradient_step', 20)):
            ratio = i / (max(width, height) // 2)
            r = int(bg_color_1[0] * ratio + bg_color_2[0] * (1 - ratio))
            g = int(bg_color_1[1] * ratio + bg_color_2[1] * (1 - ratio))
            b = int(bg_color_1[2] * ratio + bg_color_2[2] * (1 - ratio))
            bg_draw.ellipse((width/2 - i, height/2 - i, width/2 + i, height/2 + i), fill=(r,g,b))
    elif style.get('background_type') == 'central_orb': 
        orb_color = palette[0]
        orb_radius = style.get('orb_base_radius', 100) + math.sin(t * style.get('orb_pulse_speed', 2.0)) * style.get('orb_pulse_amplitude', 20)
        orb_alpha = int(style.get('orb_alpha', 150) * (0.8 + 0.2 * math.sin(t * style.get('orb_pulse_speed', 2.0)))) 
        
        bg_draw.ellipse((width/2 - orb_radius, height/2 - orb_radius, 
                         width/2 + orb_radius, height/2 + orb_radius), 
                        fill=orb_color + (orb_alpha,))
        bg_img = bg_img.filter(ImageFilter.GaussianBlur(radius=style.get('orb_blur_radius', 10.0)))

    else: # Fundo sólido
        bg_img = Image.new('RGB', (width, height), color=style.get('solid_background_color', (0,0,0)))
    
    img = bg_img # Começa com o fundo

    # --- Padrões (Explosão Estelar Rotativa é o foco principal aqui) ---
    shapes_img = Image.new('RGBA', (width, height), (0,0,0,0))
    shapes_draw = ImageDraw.Draw(shapes_img)
    
    center_x, center_y = width / 2, height / 2

    if style['pattern_mode'] == 'star_explosion_rotational': # MODO Explosão Estelar Rotativa
        num_particles = style['num_elements']
        
        if not hasattr(create_dynamic_frame, 'star_particles_state') or t == 0:
            create_dynamic_frame.star_particles_state = []
            for i in range(num_particles):
                x = center_x 
                y = center_y
                
                angle = random.uniform(0, 2 * math.pi)
                initial_speed = random.uniform(style['particle_initial_speed_min'], style['particle_initial_speed_max'])
                vx = initial_speed * math.cos(angle)
                vy = initial_speed * math.sin(angle)
                
                color_idx = random.randint(0, len(palette) - 1)
                size = random.uniform(style['min_particle_size'], style['max_particle_size'])
                lifetime = random.uniform(style['min_particle_lifetime'], style['max_particle_lifetime'])
                
                create_dynamic_frame.star_particles_state.append({
                    'x': x, 'y': y, 'vx': vx, 'vy': vy, 'color_idx': color_idx, 
                    'size': size, 'lifetime': lifetime, 'age': 0, 'initial_angle': angle
                })
        
        new_star_particles_list = []
        for p in create_dynamic_frame.star_particles_state:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['age'] += 1
            
            dx = p['x'] - center_x
            dy = p['y'] - center_y
            dist = math.sqrt(dx*dx + dy*dy) + 1e-5 
            
            rotational_force_x = -dy / dist * style['rotational_strength']
            rotational_force_y = dx / dist * style['rotational_strength']
            
            p['vx'] += rotational_force_x
            p['vy'] += rotational_force_y
            
            p['vx'] *= style['particle_damping']
            p['vy'] *= style['particle_damping']
            
            current_size = p['size'] * (1 + math.sin(t * style['pulse_speed'] + p['initial_angle']) * style['pulse_amplitude'])
            current_size = max(1, current_size) 

            current_alpha = int(style['element_alpha'] * (1 - p['age'] / p['lifetime']))
            
            if current_alpha > 0 and p['age'] < p['lifetime']:
                particle_color = palette[p['color_idx']] + (current_alpha,)
                shapes_draw.ellipse((p['x'] - current_size/2, p['y'] - current_size/2,
                                     p['x'] + current_size/2, p['y'] + current_size/2),
                                    fill=particle_color)
                new_star_particles_list.append(p)
            
            if p['age'] >= p['lifetime']:
                new_x = center_x
                new_y = center_y
                new_angle = random.uniform(0, 2 * math.pi)
                new_initial_speed = random.uniform(style['particle_initial_speed_min'], style['particle_initial_speed_max'])
                new_vx = new_initial_speed * math.cos(new_angle)
                new_vy = new_initial_speed * math.sin(new_angle)
                
                new_color_idx = random.randint(0, len(palette) - 1)
                new_size = random.uniform(style['min_particle_size'], style['max_particle_size'])
                new_lifetime = random.uniform(style['min_particle_lifetime'], style['max_particle_lifetime'])
                
                new_star_particles_list.append({
                    'x': new_x, 'y': new_y, 'vx': new_vx, 'vy': new_vy, 'color_idx': new_color_idx, 
                    'size': new_size, 'lifetime': new_lifetime, 'age': 0, 'initial_angle': new_angle
                })
                
        create_dynamic_frame.star_particles_state = new_star_particles_list


    # --- Pós-processamento e Mesclagem de Camadas ---
    final_img = Image.alpha_composite(img.convert('RGBA'), shapes_img).convert('RGB')

    # Aplicar efeitos de brilho ou desfoque final
    if style['apply_bloom']:
        blurred_img = final_img.filter(ImageFilter.GaussianBlur(radius=style['bloom_radius']))
        final_img = ImageChops.add(final_img, blurred_img, scale=style['bloom_scale'], offset=0)
    
    if style['apply_motion_blur']:
        final_img = final_img.filter(ImageFilter.GaussianBlur(radius=style['motion_blur_radius']))

    # Ajuste de contraste e saturação final para impacto
    enhancer = Contrast(final_img) 
    final_img = enhancer.enhance(style['final_contrast'])
    enhancer = Color(final_img)    
    final_img = enhancer.enhance(style['final_saturation'])

    return np.array(final_img)

# --- Função de Geração de Vídeo ---
def generate_animated_video(output_filename, video_id, duration, fps): 
    width, height = 640, 480 # Qualidade 480p (640x480)
    
    random.seed(video_id) # Garante que os parâmetros sejam únicos por vídeo

    # --- Definição dos SUB-MODOS Visuais para Explosão Estelar Rotativa ---
    # Estes são os 4 sub-tipos que definem a aparência de cada vídeo "Explosão Estelar Rotativa"
    star_explosion_sub_modes = [
        { # Sub-modo 1: Explosão Clássica com Orbe Central Pulsante (o que você mais gostou)
            'id': 'orbe_pulsante',
            'name': 'Explosão Estelar Rotativa - Orbe Pulsante',
            'background_type': 'central_orb', 
            'orb_base_radius': random.uniform(40, 80), # Ajustado para 480p
            'orb_pulse_speed': random.uniform(1.0, 3.0),
            'orb_pulse_amplitude': random.uniform(5, 20), # Ajustado
            'orb_blur_radius': random.uniform(3.0, 8.0), # Ajustado
            'orb_alpha': random.randint(100, 200),
            'pattern_mode': 'star_explosion_rotational',
            'num_elements': random.randint(200, 500), # Ajustado para 480p
            'element_alpha': random.randint(180, 255), 
            'min_particle_size': random.uniform(0.5, 1.8), # Ajustado
            'max_particle_size': random.uniform(1.8, 4), # Ajustado
            'particle_initial_speed_min': random.uniform(0.6, 2.0), # Ajustado
            'particle_initial_speed_max': random.uniform(2.0, 4.0), # Ajustado
            'rotational_strength': random.uniform(0.01, 0.05), 
            'particle_damping': random.uniform(0.96, 0.99), 
            'min_particle_lifetime': random.randint(60, 180), 
            'max_particle_lifetime': random.randint(180, 350), 
            'pulse_speed': random.uniform(2.0, 5.0), 
            'pulse_amplitude': random.uniform(0.1, 0.4),
            'apply_bloom': True,
            'bloom_radius': random.uniform(1.5, 4), # Ajustado
            'bloom_scale': random.uniform(1.8, 2.8), 
            'apply_motion_blur': True,
            'motion_blur_radius': random.uniform(0.5, 1.5), # Ajustado
            'final_contrast': random.uniform(1.2, 1.8), 
            'final_saturation': random.uniform(1.5, 2.0) 
        },
        { # Sub-modo 2: Explosão com Fundo de Fumaça Perlin Sutil
            'id': 'fumaca_perlin',
            'name': 'Explosão Estelar Rotativa - Fumaça Perlin',
            'background_type': 'perlin_smoke',
            'bg_smoke_density_base': random.uniform(0.005, 0.010), # Ajustado para ser sempre positivo e com mais variação base
            'bg_smoke_density_amp': random.uniform(0.001, 0.003), # Ajustado
            'bg_smoke_speed_base': random.uniform(0.02, 0.1),
            'bg_smoke_density_speed': random.uniform(0.05, 0.2), 
            'bg_smoke_blur_radius': random.uniform(2.0, 5.0), # Ajustado
            'pattern_mode': 'star_explosion_rotational',
            'num_elements': random.randint(300, 800), # Ajustado
            'element_alpha': random.randint(150, 230), 
            'min_particle_size': random.uniform(0.5, 1.8),
            'max_particle_size': random.uniform(1.8, 5),
            'particle_initial_speed_min': random.uniform(1.0, 3.0), 
            'particle_initial_speed_max': random.uniform(3.0, 6.0),
            'rotational_strength': random.uniform(0.02, 0.06), 
            'particle_damping': random.uniform(0.95, 0.98), 
            'min_particle_lifetime': random.randint(80, 200), 
            'max_particle_lifetime': random.randint(200, 400),
            'pulse_speed': random.uniform(1.5, 4.0), 
            'pulse_amplitude': random.uniform(0.05, 0.2), 
            'apply_bloom': True,
            'bloom_radius': random.uniform(1.0, 4.0), 
            'bloom_scale': random.uniform(1.6, 2.6), 
            'apply_motion_blur': True,
            'motion_blur_radius': random.uniform(0.8, 2.5),
            'final_contrast': random.uniform(1.0, 1.5), 
            'final_saturation': random.uniform(1.3, 1.8) 
        },
        { # Sub-modo 3: Explosão com Gradiente Radial e Partículas Maiores
            'id': 'gradiente_radial',
            'name': 'Explosão Estelar Rotativa - Gradiente Radial',
            'background_type': 'radial_gradient',
            'bg_gradient_step': random.randint(10, 30), # Ajustado
            'pattern_mode': 'star_explosion_rotational',
            'num_elements': random.randint(200, 500), # Ajustado
            'element_alpha': random.randint(200, 255), 
            'min_particle_size': random.uniform(1.5, 4),
            'max_particle_size': random.uniform(4, 10),
            'particle_initial_speed_min': random.uniform(0.6, 2.0), 
            'particle_initial_speed_max': random.uniform(2.0, 4.0),
            'rotational_strength': random.uniform(0.005, 0.03), 
            'particle_damping': random.uniform(0.97, 0.995), 
            'min_particle_lifetime': random.randint(50, 150), 
            'max_particle_lifetime': random.randint(150, 300),
            'pulse_speed': random.uniform(2.5, 6.0), 
            'pulse_amplitude': random.uniform(0.2, 0.5), 
            'apply_bloom': True,
            'bloom_radius': random.uniform(2, 5), # Ajustado
            'bloom_scale': random.uniform(2.0, 3.0), 
            'apply_motion_blur': True,
            'motion_blur_radius': random.uniform(0.5, 1.5),
            'final_contrast': random.uniform(1.3, 1.9), 
            'final_saturation': random.uniform(1.6, 2.2) 
        },
        { # Sub-modo 4: Explosão Estelar - Fundo Preto Puro e Partículas Extremas
            'id': 'fundo_preto_puro',
            'name': 'Explosão Estelar Rotativa - Fundo Preto Puro',
            'background_type': 'solid',
            'solid_background_color': (0,0,0), 
            'pattern_mode': 'star_explosion_rotational',
            'num_elements': random.randint(400, 1000), # Ajustado
            'element_alpha': random.randint(220, 255), 
            'min_particle_size': random.uniform(0.4, 1.5), # Ajustado
            'max_particle_size': random.uniform(1.5, 4.0), # Ajustado
            'particle_initial_speed_min': random.uniform(1.5, 3.5), 
            'particle_initial_speed_max': random.uniform(3.5, 7.0),
            'rotational_strength': random.uniform(0.03, 0.08), 
            'particle_damping': random.uniform(0.90, 0.97), 
            'min_particle_lifetime': random.randint(100, 250), 
            'max_particle_lifetime': random.randint(250, 500),
            'pulse_speed': random.uniform(3.0, 7.0), 
            'pulse_amplitude': random.uniform(0.08, 0.25),
            'apply_bloom': True,
            'bloom_radius': random.uniform(0.8, 2.5), # Ajustado
            'bloom_scale': random.uniform(2.5, 4.0), 
            'apply_motion_blur': True,
            'motion_blur_radius': random.uniform(0.5, 1.5),
            'final_contrast': random.uniform(1.5, 2.5), 
            'final_saturation': random.uniform(1.8, 2.5) 
        }
    ]
    
    # Lógica de seleção aleatória dos sub-estilos (todos com a mesma chance)
    current_video_style = random.choice(star_explosion_sub_modes)
    
    video_params = {
        'seed': video_id, 
        'style': current_video_style,
        'palette': get_unique_palette(video_id), 
        'perlin_noise': PerlinNoise(seed=video_id) 
    }

    if video_params['style'].get('background_type') == 'solid':
        if video_params['style'].get('solid_background_color') is None: 
            video_params['style']['solid_background_color'] = random.choice(video_params['palette']) 

    print(f"Gerando vídeo com ID: {video_id}, Modo Visual: {video_params['style']['name']}")

    clip = VideoClip(lambda t: create_dynamic_frame(width, height, t, video_params), duration=duration)
    
    # Bitrate ajustado para a nova resolução e FPS, mantendo boa qualidade
    clip.write_videofile(output_filename, fps=fps, codec="libx264", bitrate="5000k", audio_codec="aac") 
    print(f"Vídeo '{output_filename}' gerado com sucesso!")

# --- Bloco Principal de Execução ---
if __name__ == "__main__":
    # --- Verificação de FFmpeg (CRUCIAL) ---
    print("Verificando instalação do FFmpeg (necessário para gerar vídeos)...")
    sys.stdout.flush() # Garante que a mensagem apareça imediatamente
    try:
        # Tenta executar 'ffmpeg -version' para ver se está no PATH
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True, text=True)
        print("FFmpeg encontrado e funcionando.")
    except FileNotFoundError:
        print("\nERRO: FFmpeg não encontrado no PATH do sistema!")
        print("MoviePy precisa do FFmpeg para criar vídeos. Por favor, baixe e instale-o:")
        print("1. Vá para https://ffmpeg.org/download.html")
        print("2. Baixe a 'build' estável para o seu sistema (Windows 'gpl' é comum).")
        print("3. Extraia o arquivo .zip para uma pasta fácil de acessar (ex: C:\\ffmpeg).")
        print("4. Adicione o caminho da pasta 'bin' (ex: C:\\ffmpeg\\bin) às variáveis de ambiente PATH do seu sistema.")
        print("   - Pesquise por 'variáveis de ambiente' no Windows, clique em 'Editar as variáveis de ambiente do sistema',")
        print("     clique em 'Variáveis de Ambiente...', selecione 'Path' na seção 'Variáveis do sistema', clique em 'Editar', e adicione o caminho.")
        print("5. **REINICIE O PROMPT DE COMANDO/TERMINAL** e tente executar o script novamente.")
        sys.stdout.flush() # Garante que a mensagem de erro apareça antes de sair
        input("\nPressione Enter para sair...")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"\nAVISO: FFmpeg parece estar instalado, mas houve um erro ao executá-lo: {e}")
        print("Isso pode indicar uma instalação corrompida. Tente reinstalá-lo.")
        sys.stdout.flush() # Garante que a mensagem de erro apareça antes de sair
        input("Pressione Enter para sair...")
        sys.exit(1)
    print("-" * 50)
    # --- Fim da Verificação de FFmpeg ---

    output_path = os.path.join(r"C:\Users\Administrador\Desktop\venv", "videos_gerados_unicos")
    
    print(f"Verificando/criando diretório de saída: {output_path}")
    sys.stdout.flush() 

    try:
        os.makedirs(output_path, exist_ok=True)
    except OSError as e:
        print(f"Erro ao criar o diretório '{output_path}': {e}")
        print("Pode ser um problema de permissões. Tente executar o Prompt de Comando como Administrador.")
        sys.stdout.flush()
        sys.exit(1)

    while True:
        try:
            print("Quantos vídeos você deseja gerar no total? ")
            sys.stdout.flush() 
            num_videos_to_generate = int(input())
            if num_videos_to_generate <= 0:
                print("Por favor, insira um número positivo.")
                sys.stdout.flush()
            else:
                break
        except ValueError:
            print("Entrada inválida. Por favor, insira um número inteiro.")
            sys.stdout.flush()

    while True:
        try:
            print("Qual FPS você prefere para os vídeos (padrão: 20, pressione Enter para usar o padrão)? ")
            sys.stdout.flush() 
            fps_input_str = input()
            if not fps_input_str: # Se o usuário pressionar Enter
                fps_input = 20
            else:
                fps_input = int(fps_input_str)
                if fps_input <= 0:
                    print("Por favor, insira um número positivo para FPS.")
                    sys.stdout.flush()
                    continue
            break
        except ValueError:
            print("Entrada inválida. Por favor, insira um número inteiro.")
            sys.stdout.flush()

    for i in range(num_videos_to_generate):
        video_filename = os.path.join(output_path, f"video_explosao_estelar_unico_{i+1}.mp4")
        generate_animated_video(video_filename, video_id=i+1, duration=20, fps=fps_input)

    print("\nGeração de vídeos concluída!")
    sys.stdout.flush()

    try:
        if platform.system() == "Windows":
            os.startfile(output_path)
            print(f"Abrindo a pasta: {output_path}")
            sys.stdout.flush()
        elif platform.system() == "Darwin": 
            subprocess.Popen(["open", output_path])
            print(f"Abrindo a pasta: {output_path}")
            sys.stdout.flush()
        else: 
            subprocess.Popen(["xdg-open", output_path])
            print(f"Abrindo a pasta: {output_path}")
            sys.stdout.flush()
    except Exception as e:
        print(f"Não foi possível abrir a pasta automaticamente: {e}")
        print(f"Você pode encontrá-la aqui: {output_path}")
        sys.stdout.flush()

    input("Pressione qualquer tecla para continuar. . .")
    sys.stdout.flush() # Garante que a última mensagem apareça antes do programa sair