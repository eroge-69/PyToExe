if 0 <= index < len(weapons):

                        selected_weapon = list(weapons.keys())[index]

                else:

                    if ammo[selected_weapon] > 0 and reload_timer <= 0:

                        closest = None

                        min_dist = 1000

                        for t in targets:

                            d = abs(t.rect.centery - my)

                            if d < min_dist:

                                closest = t

                                min_dist = d

                        if closest:

                            missiles.append(Missile(800, my, closest, selected_weapon))

                            ammo[selected_weapon] -= 1

                            reload_timer = weapons[selected_weapon]["reload"]



        for t in targets[:]:

            if not t.dead:

                t.move()

            t.draw()

            if t.dead:

                t.explosion_time += dt

                if t.explosion_time > 0.5:

                    targets.remove(t)

            elif t.rect.right < 0:

                targets.remove(t)



        for m in missiles[:]:

            m.move()

            m.draw()

            if m.target and m.rect.colliderect(m.target.rect):

                m.target.health -= weapons[m.weapon_name]["damage"]

                missiles.remove(m)

                if m.target.health <= 0:

                    m.target.dead = True

                    score += 1



        spawn_timer += 1

        if spawn_timer > (60 if difficulty == "easy" else 30) and len(targets) < max_targets:

            spawn_target()

            spawn_timer = 0



        if score >= max_targets:

            font = pygame.font.SysFont(None, 60)

            msg = font.render("ПОБЕДА!", True, GREEN)

            screen.blit(msg, (WIDTH//2 - 100, HEIGHT//2))

            pygame.display.flip()

            pygame.time.wait(3000)

            running = False



        if sum(ammo.values()) == 0 and not missiles:

            font = pygame.font.SysFont(None, 60)

            msg = font.render("ПОРАЖЕНИЕ", True, RED)

            screen.blit(msg, (WIDTH//2 - 120, HEIGHT//2))

            pygame.display.flip()

            pygame.time.wait(3000)

            running = False



        pygame.display.flip()



def main_menu():

    font = pygame.font.SysFont(None, 48)

    while True:

        screen.fill(DARK)

        title = font.render("СИМУЛЯТОР ТИРА", True, WHITE)

        screen.blit(title, (WIDTH//2 - 150, 100))

        easy_btn = pygame.Rect(WIDTH//2 - 100, 200, 200, 50)

        hard_btn = pygame.Rect(WIDTH//2 - 100, 300, 200, 50)

        pygame.draw.rect(screen, GREEN, easy_btn)

        pygame.draw.rect(screen, RED, hard_btn)

        screen.blit(font.render("Лёгкий", True, BLACK), (WIDTH//2 - 40, 210))

        screen.blit(font.render("Сложный", True, BLACK), (WIDTH//2 - 45, 310))

        pygame.display.flip()



        for event in pygame.event.get():

            if event.type == pygame.QUIT:

                pygame.quit(); sys.exit()

            elif event.type == pygame.MOUSEBUTTONDOWN:

                if easy_btn.collidepoint(event.pos):

                    game_loop("easy")

                elif hard_btn.collidepoint(event.pos):

                    game_loop("hard")



main_menu()