# ahhh messy code 😱
# ts is what yall wanted ig


import keyboard,pygame,random,time,math
pygame.init()
pygame.mixer.init()
pygame.mixer.music.load("SONIC.EXE (Bass Boosted).mp3")
pygame.mixer.music.play(-1)
captioanarar=pygame.display.set_mode((0,0),pygame.FULLSCREEN|pygame.NOFRAME)
pygame.display.set_caption("scary virus funk 2025 mango mango mango")
pygame.mouse.set_visible(False)
original_image=pygame.image.load("fag.jpg").convert_alpha()
screen_size=captioanarar.get_size()
start=time.time()
duration=0.7;shake=12;pulse_freq=2.5;pulse_min=0.85;pulse_max=1.1
running=True;flash_alpha=0;last_flash=False
flash_surface=pygame.Surface(screen_size);flash_surface.fill((255,255,255))
def shift_surface(surf,x_shift,y_shift):
 w,h=surf.get_size()
 shifted=pygame.Surface((w,h),pygame.SRCALPHA)
 src_rect=pygame.Rect(max(-x_shift,0),max(-y_shift,0),w-abs(x_shift),h-abs(y_shift))
 dest_pos=(max(x_shift,0),max(y_shift,0))
 shifted.blit(surf,dest_pos,src_rect)
 return shifted
def block_all_except_esc(e):
 if e.name!="esc":
  return False
keyboard.hook(block_all_except_esc)
while running:
 for e in pygame.event.get():
  if e.type==pygame.KEYDOWN and e.key==pygame.K_ESCAPE:running=False
 elapsed=time.time()-start
 progress=min(elapsed/duration,1)
 captioanarar.fill((0,0,0))
 pos=pygame.mixer.music.get_pos()/1000.0
 vol_pulse=(random.uniform(0.7,1.0)*math.sin(2*math.pi*pulse_freq*pos)+1)/2
 pulse_scale=pulse_min+(pulse_max-pulse_min)*vol_pulse
 w=int(screen_size[0]*progress*pulse_scale)
 h=int(screen_size[1]*progress*pulse_scale)
 if w>0 and h>0:
  img=pygame.transform.scale(original_image,(w,h))
  r=img.copy()
  g=img.copy()
  b=img.copy()
  r.fill((255,0,0,100),special_flags=pygame.BLEND_RGBA_MULT)
  g.fill((0,255,0,100),special_flags=pygame.BLEND_RGBA_MULT)
  b.fill((0,0,255,100),special_flags=pygame.BLEND_RGBA_MULT)
  r=shift_surface(r,random.randint(-3,3),0)
  g=shift_surface(g,random.randint(-3,3),0)
  b=shift_surface(b,random.randint(-3,3),0)
  base_x=screen_size[0]//2-w//2;base_y=screen_size[1]//2-h//2
  captioanarar.blit(r,(base_x,base_y));captioanarar.blit(g,(base_x,base_y));captioanarar.blit(b,(base_x,base_y))
  shakex=random.randint(-shake,shake)*(1-progress)
  shakey=random.randint(-shake,shake)*(1-progress)
  captioanarar.blit(img,img.get_rect(center=(screen_size[0]//2+int(shakex),screen_size[1]//2+int(shakey))))
 flash_on=vol_pulse>0.85
 if flash_on and not last_flash:flash_alpha=150
 last_flash=flash_on
 if flash_alpha>0:
  flash_alpha=max(0,flash_alpha-20)
  flash_surface.set_alpha(flash_alpha)
  captioanarar.blit(flash_surface,(0,0))
 if random.random()<0.1:captioanarar.fill((random.randint(0,20),random.randint(0,20),random.randint(0,20)))
 pygame.display.flip()
keyboard.unhook_all()
