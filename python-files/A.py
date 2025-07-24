#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pygame
import sys
import random
import math
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
import pymunk
import pymunk.pygame_util
from pygame import gfxdraw
import noise
from scipy.interpolate import interp1d
import moderngl
import cv2
from dataclasses import dataclass
from typing import List, Tuple, Dict, Optional
import json
import asyncio
import threading
from enum import Enum, auto
import logging
import time

# Oyun sabitleri
PENCERE_GENISLIK = 1280
PENCERE_YUKSEKLIK = 720
FPS = 60
YERÇEKIMI = 981.0
PARCACIK_SAYISI = 150

# Renkler
BEYAZ = (255, 255, 255)
SIYAH = (0, 0, 0)
KIRMIZI = (255, 0, 0)
YESIL = (0, 255, 0)
MAVI = (0, 0, 255)
TURUNCU = (255, 165, 0)
MOR = (128, 0, 128)

class OyunDurumu(Enum):
    MENU = auto()
    OYNANIYOR = auto()
    DURAKLAT = auto()
    OYUN_BITTI = auto()

@dataclass
class ParticleEfekt:
    x: float
    y: float
    hiz_x: float
    hiz_y: float
    yasam: float
    renk: Tuple[int, int, int]
    boyut: float

class UzayGemisi:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
        self.hiz_x = 0
        self.hiz_y = 0
        self.ivme = 0.5
        self.surtunme = 0.98
        self.yon = 0
        self.boyut = 40
        self.can = 100
        self.kalkan = 100
        self.ates_hizi = 250
        self.son_ates = 0
        self.parcaciklar: List[ParticleEfekt] = []
        
    def hareket(self, tuslar: Dict[int, bool]) -> None:
        # Hareket mantığı
        if tuslar.get(pygame.K_LEFT):
            self.hiz_x -= self.ivme
        if tuslar.get(pygame.K_RIGHT):
            self.hiz_x += self.ivme
        if tuslar.get(pygame.K_UP):
            self.hiz_y -= self.ivme
            self.parcacik_olustur()
        if tuslar.get(pygame.K_DOWN):
            self.hiz_y += self.ivme
            
        # Fizik hesaplamaları
        self.hiz_x *= self.surtunme
        self.hiz_y *= self.surtunme
        
        self.x = (self.x + self.hiz_x) % PENCERE_GENISLIK
        self.y = (self.y + self.hiz_y) % PENCERE_YUKSEKLIK
        
    def parcacik_olustur(self) -> None:
        for _ in range(3):
            aci = random.uniform(0, 2 * math.pi)
            hiz = random.uniform(2, 5)
            self.parcaciklar.append(ParticleEfekt(
                x=self.x,
                y=self.y,
                hiz_x=math.cos(aci) * hiz,
                hiz_y=math.sin(aci) * hiz,
                yasam=random.uniform(0.5, 1.5),
                renk=TURUNCU,
                boyut=random.uniform(2, 4)
            ))
            
    def parcaciklari_guncelle(self) -> None:
        yeni_parcaciklar = []
        for p in self.parcaciklar:
            p.x += p.hiz_x
            p.y += p.hiz_y
            p.yasam -= 0.016
            if p.yasam > 0:
                yeni_parcaciklar.append(p)
        self.parcaciklar = yeni_parcaciklar

    def ciz(self, ekran: pygame.Surface) -> None:
        # Parcacıkları çiz
        for p in self.parcaciklar:
            alpha = int(255 * (p.yasam / 1.5))
            surface = pygame.Surface((p.boyut * 2, p.boyut * 2), pygame.SRCALPHA)
            pygame.draw.circle(surface, (*p.renk, alpha), (p.boyut, p.boyut), p.boyut)
            ekran.blit(surface, (p.x - p.boyut, p.y - p.boyut))
            
        # Gemiyi çiz
        noktalar = [
            (self.x + math.cos(self.yon) * self.boyut, self.y + math.sin(self.yon) * self.boyut),
            (self.x + math.cos(self.yon + 2.6) * (self.boyut * 0.7), self.y + math.sin(self.yon + 2.6) * (self.boyut * 0.7)),
            (self.x + math.cos(self.yon - 2.6) * (self.boyut * 0.7), self.y + math.sin(self.yon - 2.6) * (self.boyut * 0.7))
        ]
        pygame.draw.polygon(ekran, BEYAZ, noktalar)

class Asteroid:
    def __init__(self):
        self.x = random.randrange(PENCERE_GENISLIK)
        self.y = random.randrange(PENCERE_YUKSEKLIK)
        self.hiz_x = random.uniform(-2, 2)
        self.hiz_y = random.uniform(-2, 2)
        self.boyut = random.randint(20, 50)
        self.noktalar = self._nokta_olustur()
        
    def _nokta_olustur(self) -> List[Tuple[float, float]]:
        noktalar = []
        for i in range(8):
            aci = i * (2 * math.pi / 8)
            uzaklik = random.uniform(self.boyut * 0.8, self.boyut * 1.2)
            x = math.cos(aci) * uzaklik
            y = math.sin(aci) * uzaklik
            noktalar.append((x, y))
        return noktalar
    
    def guncelle(self) -> None:
        self.x = (self.x + self.hiz_x) % PENCERE_GENISLIK
        self.y = (self.y + self.hiz_y) % PENCERE_YUKSEKLIK
        
    def ciz(self, ekran: pygame.Surface) -> None:
        cizim_noktalari = [(self.x + x, self.y + y) for x, y in self.noktalar]
        pygame.draw.polygon(ekran, BEYAZ, cizim_noktalari, 2)

class Oyun:
    def __init__(self):
        pygame.init()
        self.ekran = pygame.display.set_mode((PENCERE_GENISLIK, PENCERE_YUKSEKLIK))
        pygame.display.set_caption("Uzay Macerası")
        self.saat = pygame.time.Clock()
        
        self.gemi = UzayGemisi(PENCERE_GENISLIK // 2, PENCERE_YUKSEKLIK // 2)
        self.asteroidler = [Asteroid() for _ in range(5)]
        self.durum = OyunDurumu.OYNANIYOR
        self.tuslar = {}
        
        # Post-processing efektleri için
        self.post_process_shader = self._shader_yukle()
        
    def _shader_yukle(self) -> Optional[moderngl.Program]:
        try:
            ctx = moderngl.create_standalone_context()
            return ctx.program(
                vertex_shader='''
                    #version 330
                    in vec2 vert;
                    in vec2 texcoord;
                    out vec2 uv;
                    void main() {
                        gl_Position = vec4(vert, 0.0, 1.0);
                        uv = texcoord;
                    }
                ''',
                fragment_shader='''
                    #version 330
                    uniform sampler2D texture0;
                    in vec2 uv;
                    out vec4 fragColor;
                    void main() {
                        vec4 color = texture(texture0, uv);
                        float gray = dot(color.rgb, vec3(0.299, 0.587, 0.114));
                        fragColor = mix(color, vec4(gray), 0.2);
                    }
                '''
            )
        except Exception as e:
            logging.error(f"Shader yüklenemedi: {e}")
            return None
            
    def olaylari_isle(self) -> bool:
        for olay in pygame.event.get():
            if olay.type == pygame.QUIT:
                return False
            elif olay.type == pygame.KEYDOWN:
                self.tuslar[olay.key] = True
            elif olay.type == pygame.KEYUP:
                self.tuslar[olay.key] = False
        return True
        
    def guncelle(self) -> None:
        if self.durum == OyunDurumu.OYNANIYOR:
            self.gemi.hareket(self.tuslar)
            self.gemi.parcaciklari_guncelle()
            
            for asteroid in self.asteroidler:
                asteroid.guncelle()
                
            # Çarpışma kontrolü
            for asteroid in self.asteroidler:
                uzaklik = math.hypot(self.gemi.x - asteroid.x, self.gemi.y - asteroid.y)
                if uzaklik < (self.gemi.boyut + asteroid.boyut) * 0.7:
                    self.durum = OyunDurumu.OYUN_BITTI
                    
    def ciz(self) -> None:
        self.ekran.fill(SIYAH)
        
        self.gemi.ciz(self.ekran)
        for asteroid in self.asteroidler:
            asteroid.ciz(self.ekran)
            
        if self.durum == OyunDurumu.OYUN_BITTI:
            font = pygame.font.Font(None, 64)
            metin = font.render("OYUN BİTTİ!", True, KIRMIZI)
            self.ekran.blit(metin, (PENCERE_GENISLIK // 2 - metin.get_width() // 2,
                                   PENCERE_YUKSEKLIK // 2 - metin.get_height() // 2))
            
        pygame.display.flip()
        
    def calistir(self) -> None:
        while True:
            if not self.olaylari_isle():
                break
                
            self.guncelle()
            self.ciz()
            self.saat.tick(FPS)
            
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    oyun = Oyun()
    oyun.calistir()
