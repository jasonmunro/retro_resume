import pyxel


class TitleScreen:
    '''
    draw the title screen/intro with instructions
    on how to play
    '''

    def __init__(self):
        '''
        initialize some flags, a position counter,
        load the title font, and define the text to
        be printed
        '''

        self.pos = 1
        self.line1 = False
        self.line2 = False
        self.font = pyxel.Font("assets/deja.ttf", 14)
        self.lines = [
            "Jason Munro: The Game",
            "Play on to learn about Jason's skills!",
            "- Use the arrow keys to move",
            "- Use the spacebar to shoot",
            "- Shoot stuff to learn about Jason",
            "- Finish the game then hire that guy!"
        ]
    
    def print_by_char(self, x, y, color, orig_string, font=None):
        '''
        print a line one letter at a time every 3 frames of the
        event loop
        '''

        string = orig_string[0:self.pos]
        if pyxel.frame_count > 3 and pyxel.frame_count % 3 == 0:
            self.pos += 1
        pyxel.text(x, y, string, color, font)
        if len(string) == len(orig_string):
            self.pos = 1
            return True
        return False

    def instructions(self):
        '''
        after the first 2 lines are printed one letter at a time
        print the rest of the instructions with each line appearing
        every 30 frames
        '''

        pyxel.text(25, 20, self.lines[0], 16, self.font)
        pyxel.text(25, 50, self.lines[1], 10)
        if pyxel.frame_count > 180:
            pyxel.text(30, 75, self.lines[2], 3)
        if pyxel.frame_count > 210:
            pyxel.text(30, 85, self.lines[3], 3)
        if pyxel.frame_count > 240:
            pyxel.text(30, 95, self.lines[4], 3)
        if pyxel.frame_count > 270:
            pyxel.text(30, 105, self.lines[5], 4)
        if pyxel.frame_count > 300:
            color = 16
            if pyxel.frame_count % 50 in (0,1,2,3,4,5):
                color = 0 
            pyxel.text(45, 130, "Press the spacebar to start", color)
    
    def draw(self):
        '''
        entry point that does all the work, first prints line 1 and 2
        one letter at a time, then prints the instructions
        '''

        if not self.line1:
            self.line1 = self.print_by_char(25, 20, pyxel.frame_count % 16, self.lines[0], self.font)
        elif self.line1 and not self.line2:
            pyxel.text(25, 20, self.lines[0], 16, self.font)
            self.line2 = self.print_by_char(25, 50, pyxel.frame_count % 16, self.lines[1])
        else:
            self.instructions()


class Player:
    '''
    the player object. Handles moving the player
    around and stabbing/shooting stuff
    '''

    def __init__(self, x, y, stuff):
        '''
        variables to track the movement input, the current location,
        various states, the game level and the location of all the stuff
        that can be stabbed/shot
        '''

        self.last_dir = 'up'
        self.stuff = stuff
        self.in_sound = None
        self.dead_count = 0
        self.is_idle = 0
        self.is_dead = False
        self.cant_die = 0
        self.bullets = []
        self.level = 1
        self.x = x
        self.y = y
        self.w = 10
        self.h = 10

    def stab_start(self):
        '''
        play stab/shoot sound
        '''

        pyxel.play(1, 0)
        return pyxel.frame_count

    def stab_stop(self, start):
        '''
        stop stab/shoot sound
        '''

        if pyxel.frame_count > (start + 5):
            pyxel.stop(1)
            self.in_sound = None
        
    def update(self):
        '''
        check for key input and setup the new coordinates for the player
        location, if the space key is active perform a stab/shot
        '''

        if self.in_sound:
            self.stab_stop(self.in_sound)
        if pyxel.btn(pyxel.KEY_LEFT) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_LEFT):
            self.is_idle = 0
            self.x -= 2
            self.last_dir = 'left'
        elif pyxel.btn(pyxel.KEY_RIGHT) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT):
            self.is_idle = 0
            self.x += 2
            self.last_dir = 'right'
        elif pyxel.btn(pyxel.KEY_UP) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_UP):
            self.is_idle = 0
            self.y -= 2
            self.last_dir = 'up'
        elif pyxel.btn(pyxel.KEY_DOWN) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_DOWN):
            self.is_idle = 0
            self.y += 2
            self.last_dir = 'down'
        elif self.is_idle == 0:
            self.is_idle = pyxel.frame_count

        self.x = max(self.x, 0)
        self.x = min(self.x, pyxel.width - self.w)
        self.y = max(self.y, 0)
        self.y = min(self.y, pyxel.height - self.h)
        if pyxel.btnp(pyxel.KEY_SPACE) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_A):
            self.shoot()
            self.in_sound = self.stab_start()
            # switched to shooting but keeping stab around for now
            #self.stab()
            #self.in_sound = self.stab_start()
        self.bullet_hit()
        self.draw()

    def bullet_hit(self):
        '''
        see if a bullet hit stuff
        '''

        to_remove = None
        for index, bul in enumerate(self.bullets):
            for idx, vals in enumerate(self.stuff.stuff_map[self.level]):
                if idx in self.stuff.found:
                    continue
                if self.rect_instersect(bul, vals):
                    self.stuff.msg(vals['msg'], vals['t'])
                    self.stuff.found.append(idx)
                    to_remove = index
                    break
        if to_remove is not None:
            del(self.bullets[to_remove])

    def player_hit(self, rect):
        '''
        see if they player hit stuff
        '''

        for idx, vals in enumerate(self.stuff.stuff_map[self.level]):
            if idx in self.stuff.found:
                continue
            if self.rect_instersect(rect, vals):
                self.is_dead = True
                self.dead_count += 1
                break

    def stab_hit(self, rect):
        '''
        see if a stab hit stuff
        '''

        for idx, vals in enumerate(self.stuff.stuff_map[self.level]):
            if idx in self.stuff.found:
                continue
            if self.rect_instersect(rect, vals):
                self.stuff.msg(vals['msg'], vals['t'])
                self.stuff.found.append(idx)
                break
    
    def rect_instersect(self, rect1, rect2):
        '''
        using x, y, width, and height determine if 2
        rectangles overlap in the game screen
        '''

        # top left of rect1 contained in rect2
        if rect1['x'] >= rect2['x'] and \
            rect1['x'] <= (rect2['x'] + rect2['w']) and \
            rect1['y'] >= rect2['y'] and \
            rect1['y'] <= (rect2['y'] + rect2['h']):
            return True

        # bottom right of rect1 contained in rect2
        if (rect1['x'] + rect1['w']) >= rect2['x'] and \
            (rect1['x'] + rect1['w']) <= (rect2['x'] + rect2['w']) and \
            (rect1['y'] + rect1['h']) >= rect2['y'] and \
            (rect1['y'] + rect1['h']) <= (rect2['y'] + rect2['h']):
            return True

        # top right of rect1 contained in rect2
        if (rect1['x'] + rect1['w']) >= rect2['x'] and \
            (rect1['x'] + rect1['w']) <= (rect2['x'] + rect2['w']) and \
            rect1['y'] >= rect2['y'] and \
            rect1['y'] <= (rect2['y'] + rect2['h']):
            return True

        # bottom left of rect1 contained in rect2
        if rect1['x'] >= rect2['x'] and \
            rect1['x'] <= (rect2['x'] + rect2['w']) and \
            (rect1['y'] + rect1['h']) >= rect2['y'] and \
            (rect1['y'] + rect1['h']) <= (rect2['y'] + rect2['h']):
            return True
        return False

    def shoot(self):
        '''
        render a bullet shot
        '''

        rect = {'w': 1, 'h': 1}
        if self.last_dir == 'up':
            rect['x'] = self.x + 4
            rect['y'] = self.y - 1
            rect['dir'] = 'up'
        elif self.last_dir == 'down':
            rect['x'] = self.x + 4
            rect['y'] = self.y + self.w
            rect['dir'] = 'down'
        elif self.last_dir == 'left':
            rect['x'] = self.x - 1
            rect['y'] = self.y + 4
            rect['dir'] = 'left'
        elif self.last_dir == 'right':
            rect['x'] = self.x + self.w
            rect['y'] = self.y + 4
            rect['dir'] = 'right'
        pyxel.pset(rect['x'], rect['y'], 7)
        self.bullets.append(rect)
    
    def stab(self):
        '''
        render the stab action as a 6x2 rectangle, then check to
        see if it hit any stuff
        '''

        rect = {}
        if self.last_dir == 'up':
            rect['x'] = self.x + 4
            rect['y'] = self.y - 6
            rect['w'] = 2
            rect['h'] = 6
        elif self.last_dir == 'down':
            rect['x'] = self.x + 4
            rect['y'] = self.y + self.w
            rect['w'] = 2
            rect['h'] = 6
        elif self.last_dir == 'left':
            rect['x'] = self.x - 6
            rect['y'] = self.y + 4
            rect['w'] = 6
            rect['h'] = 2
        elif self.last_dir == 'right':
            rect['x'] = self.x + self.w
            rect['y'] = self.y + 4
            rect['w'] = 6
            rect['h'] = 2
        self.stab_hit(rect)
        pyxel.rect(rect['x'], rect['y'], rect['w'], rect['h'], 7)
        pyxel.rect(rect['x'], rect['y'], (rect['w'] - 1), (rect['h'] - 1), 13)

    def draw(self):
        '''
        draw the player at the current coordinates
        '''

        col = 3
        # blink while in invincable mode (2 seconds or so after
        # dying)
        if self.cant_die and pyxel.frame_count % 15 in (0,1,2):
                col = 11
        if self.is_dead:
            pyxel.rect(self.x, self.y, self.w, self.h, 8)
            pyxel.rect((self.x + 2), (self.y + 1), 2, 2, 0)
            pyxel.rect((self.x + 6), (self.y + 1), 2, 2, 0)
            pyxel.elli((self.x + 2), (self.y + 4), 6, 5, 0)
            self.stuff.msg('OUCH!', 'D')

        # draw player at possibly updated location
        elif self.last_dir == 'up':
            pyxel.rect(self.x, self.y, self.w, self.h, col)
            pyxel.rect((self.x + 2), (self.y + 1), 2, 2, 0)
            pyxel.rect((self.x + 6), (self.y + 1), 2, 2, 0)
            pyxel.rect((self.x + 2), (self.y + 6), 6, 1, 0)
        elif self.last_dir == 'down':
            pyxel.rect(self.x, self.y, self.w, self.h, col)
            pyxel.rect((self.x + 2), (self.y + 3), 2, 2, 0)
            pyxel.rect((self.x + 6), (self.y + 3), 2, 2, 0)
            pyxel.rect((self.x + 2), (self.y + 6), 6, 1, 0)
        elif self.last_dir == 'left':
            pyxel.rect(self.x, self.y, self.w, self.h, col)
            pyxel.rect((self.x + 1), (self.y + 1), 2, 2, 0)
            pyxel.rect((self.x + 5), (self.y + 1), 2, 2, 0)
            pyxel.rect((self.x + 2), (self.y + 6), 6, 1, 0)
        elif self.last_dir == 'right':
            pyxel.rect(self.x, self.y, self.w, self.h, col)
            pyxel.rect((self.x + 3), (self.y + 1), 2, 2, 0)
            pyxel.rect((self.x + 7), (self.y + 1), 2, 2, 0)
            pyxel.rect((self.x + 2), (self.y + 6), 6, 1, 0)

        # check invincable status
        if self.cant_die > 0 and (pyxel.frame_count - self.cant_die) < 50:
            self.move_bullets()
            return
        else:
            self.cant_die = 0

        # check for collision
        if not self.is_dead:
            self.player_hit({'x': self.x, 'y': self.y, 'w': self.w, 'h': self.h})

        # move bullets
        if len(self.bullets) > 0:
            self.move_bullets()

    def move_bullets(self):
        '''
        track fired bullets and move them along
        the path
        '''

        to_remove = []
        for idx, bul in enumerate(self.bullets):
            if bul['dir'] == 'up':
                bul['y'] -= 5
            elif bul['dir'] == 'down':
                bul['y'] += 5
            elif bul['dir'] == 'left':
                bul['x'] -= 5
            elif bul['dir'] == 'right':
                bul['x'] += 5
            if bul['x'] < 0 or bul['y'] < 0 or bul['x'] > pyxel.width or bul['y'] > pyxel.height:
                to_remove.append(idx)
            else:
                pyxel.pset(bul['x'], bul['y'], 7)
        for index in to_remove:
            if len(self.bullets) > index:
                del(self.bullets[index])


class Stuff:
    '''
    manage stuff that can be stabbed/shot
    '''

    def __init__(self):
        '''
        setup variables we need to track the state of stuff, and define what stuff
        shows up on what level
        '''

        self.stuff_exists = True
        self.current_mtype = None
        self.current_msg = None
        self.in_sound = False
        self.level = 1
        self.found = []
        self.stuff_map = {
            1: [
                {'d': 'y', 't': 'J', 'x': 100, 'y': 100, 'w': 10, 'h': 10, 'bg': 1, 'msg': 'Wrote code to run Stock Exchanges'},
                {'d': 'x', 't': 'J', 'x': 100, 'y': 100, 'w': 10, 'h': 10, 'bg': 1, 'msg': 'Ran my own software company'},
                {'d': 'x', 't': 'S', 'x': 30, 'y': 30, 'w': 10, 'h': 10, 'bg': 4, 'msg': 'Python expert 15+ years'},
                {'d': 'x', 't': 'S', 'x': 60, 'y': 120, 'w': 10, 'h': 10, 'bg': 4, 'msg': 'PHP expert 20+ years'},
                {'d': 'y', 't': 'F', 'x': 150, 'y': 10, 'w': 10, 'h': 10, 'bg': 2, 'msg': 'Big fan of retro gaming'},
                {'d': 'x', 't': 'F', 'x': 90, 'y': 40, 'w': 10, 'h': 10, 'bg': 2, 'msg': "I love dogs!"},
            ],
            2: [
                {'d': 'x', 't': 'J', 'x': 10, 'y': 60, 'w': 10, 'h': 10, 'bg': 1, 'msg': '6 years building algo trading systems'},
                {'d': 'x', 't': 'J', 'x': 50, 'y': 80, 'w': 10, 'h': 10, 'bg': 1, 'msg': 'Solved hard mapping problems in ag-tech'},
                {'d': 'y', 't': 'S', 'x': 190, 'y': 90, 'w': 10, 'h': 10, 'bg': 2, 'msg': 'Expert on E-mail protocols'},
                {'d': 'y', 't': 'S', 'x': 110, 'y': 50, 'w': 10, 'h': 10, 'bg': 2, 'msg': 'Full stack experience in multiple jobs'},
                {'d': 'y', 't': 'F', 'x': 90, 'y': 30, 'w': 10, 'h': 10, 'bg': 2, 'msg': 'I blog at unencumberedbyfacts.com'},
                {'d': 'y', 't': 'F', 'x': 20, 'y': 10, 'w': 10, 'h': 10, 'bg': 2, 'msg': 'I code everything in vim, including this'},
            ],
            3: [
                {'d': 'x', 't': 'J', 'x': 80, 'y': 0, 'w': 10, 'h': 10, 'bg': 4, 'msg': 'Coded billing systems for WordPress.com'},
                {'d': 'x', 't': 'J', 'x': 140, 'y': 50, 'w': 10, 'h': 10, 'bg': 4, 'msg': 'Experienced with cloud based envs'},
                {'d': 'y', 't': 'S', 'x': 65, 'y': 20, 'w': 10, 'h': 10, 'bg': 4, 'msg': 'Worked with all kinds of APIs'},
                {'d': 'y', 't': 'S', 'x': 5, 'y': 90, 'w': 10, 'h': 10, 'bg': 4, 'msg': 'Experienced leading a team'},
                {'d': 'x', 't': 'F', 'x': 160, 'y': 10, 'w': 10, 'h': 10, 'bg': 2, 'msg': 'Hitch-hiked the US in 1990 at age 19'},
                {'d': 'y', 't': 'F', 'x': 120, 'y': 60, 'w': 10, 'h': 10, 'bg': 2, 'msg': 'Built a custom Linux distro'},
            ],
            4: [
                {'d': 'x', 't': 'F', 'x': 10, 'y': 30, 'w': 60, 'h': 60, 'bg': 4, 'msg': 'BOSS'},
            ]
        }
    
    def msg(self, msg, mtype):
        '''
        after a successful stab/shot, show a message window with the
        info associated with that specific stuff. Also used for the
        "ouch" display
        '''

        if not self.in_sound:
            self.in_sound = True
            if mtype == 'D':
                pyxel.play(2, 2)
            else:
                pyxel.play(2, 1)
        self.current_mtype = mtype
        self.current_msg = msg

        # final multi-line message
        if msg == 'BOSS':
            pyxel.rectb(10, 10, 180, 120, 11)
            pyxel.rect(11, 11, 178, 118, 0)
            pyxel.text(15, 15, "FINAL Fact Unlocked!", 10)
            pyxel.text(15, 35, "Designing, building, and managing complex", 13)
            pyxel.text(15, 45, "software is what I am best at.", 13)
            pyxel.text(15, 60, "This game is the result of a fun weekend", 13)
            pyxel.text(15, 70, "project to learn pyxel. The code is", 13)
            pyxel.text(15, 80, "available at my github account", 13)
            pyxel.text(15, 95, "Thanks for playing!", 13)
            pyxel.text(60, 120, '"Enter" to continue', 1)

        # regular messages
        elif mtype in ('S', 'J', 'F'):
            pyxel.rectb(10, 10, 180, 60, 11)
            pyxel.rect(11, 11, 178, 58, 0)
            if mtype == 'S':
                pyxel.text(15, 15, "Skill Unlocked!", 10)
            elif mtype == 'J':
                pyxel.text(15, 15, "Job History Unlocked!", 10)
            elif mtype == 'F':
                pyxel.text(15, 15, "Fun Fact Unlocked!", 10)
            pyxel.text(15, 35, f'- {msg}', 13)
            pyxel.text(60, 60, '"Enter" to continue', 1)

        # Ouch!
        else:
            pyxel.rectb(20, 10, 160, 40, 4)
            pyxel.rect(21, 11, 158, 38, 0)
            pyxel.text(90, 20, msg, 8)
            pyxel.text(60, 40, '"Enter" to continue', 1)
    
    def update(self):
        '''
        update the location and render any remaining stuff. 
        The movement speed increases based on the level
        '''

        for idx, vals in enumerate(self.stuff_map[self.level]):
            if idx in self.found:
                continue
            if vals['d'] == 'x':
                if vals['x'] > pyxel.width:
                    vals['x'] = 0
                    vals['y'] = pyxel.rndi(0, 150)
                else:
                    vals['x'] += self.level
                    if pyxel.frame_count % 5 == 0:
                        vals['y'] += pyxel.rndi(-1, 1)
            else:
                if vals['y'] > pyxel.height:
                    vals['y'] = 0
                    vals['x'] = pyxel.rndi(0, 190)
                else:
                    vals['y'] += self.level
                    if pyxel.frame_count % 5 == 0:
                        vals['x'] += pyxel.rndi(-1, 1)
            pyxel.rect(vals['x'], vals['y'], vals['w'], vals['h'], vals['bg'])
            pyxel.rectb(vals['x'], vals['y'], vals['w'], vals['h'], 13)
            pyxel.text((vals['x'] + 3), (vals['y'] + 2), vals['t'], 16)


class Game:
    '''
    main entry point that uses all the classes above to
    run the game
    '''

    def __init__(self):
        '''
        init everything we need to track the state of the game
        '''

        self.in_title = True
        self.in_game = False
        self.in_trans = False
        self.bg_deg = 0
        self.in_end = False
        self.end_y = 0
        self.stuff = Stuff()
        self.player = Player(100, 80, self.stuff)
        self.level = 1
        self.title_screen = TitleScreen()
        self.border_col = 16
        self.trans_r = 0
        
        # start the game engine
        pyxel.init(200, 155, title="Jasons Munro: The Game")
        pyxel.playm(0, loop=True)
        pyxel.sounds[0].set("b3b3b3b3", "n", "7742", "s", 5)
        pyxel.sounds[1].set_notes('a1a2a4')
        pyxel.sounds[2].set_notes('d4d2d1')
        pyxel.run(self.update, self.draw)

    def transition(self):
        '''
        transition effect between the title screen and levels
        '''

        if self.level == 5:
            pyxel.circb(100, 80, self.trans_r, 4)
        else:
            pyxel.circ(100, 80, self.trans_r, (self.level + 4))
        if self.level == 4:
            pyxel.text(80, 75, f'LAST LEVEL', 0)
        elif self.level != 5:
            pyxel.text(85, 75, f'LEVEL: {self.level}', 0)
        self.trans_r += 5
        if self.trans_r > 140:
            self.player.cant_die = pyxel.frame_count
            self.in_trans = False
            self.in_title = False
            self.in_game = True
            if self.level == 5:
                self.in_end = True

    def update(self):
        '''
        state updates, called on each frame in the game loop
        '''

        # space to restart at the game over screen
        if self.in_end and pyxel.btnp(pyxel.KEY_SPACE):
            pyxel.reset()

        # q to quit
        if pyxel.btn(pyxel.KEY_Q):
            pyxel.quit()

        # enter to continue from message screen
        if self.stuff.current_msg and (pyxel.btn(pyxel.KEY_RETURN) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_B)):
            if self.stuff.current_mtype == 'D':
                self.player.cant_die = pyxel.frame_count
            self.player.is_dead = False
            self.stuff.current_mtype = None
            self.stuff.current_msg = None

        # space to leave title screen
        if (pyxel.btnp(pyxel.KEY_SPACE) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_A)) and self.in_title:
            self.transition()
            self.in_trans = True

    def end_screen(self):
        '''
        render game over screen
        '''

        pyxel.text(60, self.end_y, 'GAME OVER', 4, self.title_screen.font)
        pyxel.text(85, self.end_y + 30, 'You Won!', 4)
        if self.player.dead_count == 1:
            pyxel.text(55, self.end_y + 40, f'(but you died {self.player.dead_count} time)', 9)
        elif self.player.dead_count > 1:
            pyxel.text(55, self.end_y + 40, f'(but you died {self.player.dead_count} times)', 9)
        if self.end_y < 50:
            self.end_y += 1
        else:
            pyxel.text(45, 100, 'Press spacebar to play again', 1)
    
    def draw(self):
        '''
        draw updates, called on each frame of the game loop
        '''

        if not self.in_end:
            pyxel.cls(0)

        # game finished show end screen
        if self.in_end:
            pyxel.cls(0)
            self.end_screen()
            return

        # start new level
        if self.level in self.stuff.stuff_map and len(self.stuff.found) == len(self.stuff.stuff_map[self.level]):
            pyxel.cls(0)
            self.stuff.found = []
            self.trans_r = 0
            self.level += 1
            self.player.level += 1
            self.stuff.level += 1
            self.transition()
            self.in_trans = True

        # showing a message box
        if self.stuff.current_msg:
            #pyxel.bltm(0, 0, 0, 0, 0, 200, 155, rotate=self.bg_deg, scale=1.5)
            self.stuff.msg(self.stuff.current_msg, self.stuff.current_mtype)
            return

        # title screen
        if self.in_title:
            self.title_screen.draw()

        # transition screen
        if self.in_trans:
            self.player.bullets = []
            self.transition()

        # game screen
        if not self.in_trans and not self.in_end and self.in_game:
            #self.bg_deg += .01
            #if self.bg_deg == 360:
                #self.bg_deg = 0
            #pyxel.bltm(0, 0, 0, 0, 0, 200, 155, rotate=self.bg_deg, scale=1)
            self.player.update()
            self.stuff.update()
            self.stuff.in_sound = False


if __name__ == "__main__":
    Game()
