(lambda __g, __print, __ord, __zip, __import__: (
    lambda __mod, __len, __join, __repr, __map, __filter, __next: (
        (lambda __b, __d, __m, __p:
            (lambda __x, __y, __z, __w:
                exec(
                    __join(().__class__( 
                        (lambda: (yield from __map(__chr, (
                            89, 105, 101, 108, 100, 32, 102, 114, 111, 109, 32, 109, 97, 112, 40, 99, 104, 114, 44, 32, 40
                        ))))(),
                        (lambda: (yield from (95, 97, 95, 98, 95, 99, 95, 100, 95, 101, 95)))(),
                        (lambda: (yield from __map(__ord, (
                            '\x0b\x0a\x09\x08\x07\x06\x05\x04\x03\x02\x01\x00'
                        ))))()
                    )),
                    __g
                )
            )(
                *(lambda __a, __b, __c: [__c, __b, __a])(
                    *(lambda __k: [__k[1], __k[0], __k[2]])(
                        __join(().__class__(
                            (lambda __i: (yield from __map(__chr, (
                                105, 102, 32, 95, 95, 110, 97, 109, 101, 95, 95, 32, 61, 61, 32, 39, 95, 95, 109, 97, 105,
                                110, 95, 95, 39, 58, 10, 32, 32, 32, 32, 95, 95, 115, 116, 97, 114, 116, 95, 95, 40, 41
                            ))))()
                        ))
                    )
                )
            )
        )(
            *(lambda __a, __b: [__a, __b, __a + __b])(
                *(lambda: (yield from (0, 1)))()
            )
        )
    )(
        *(lambda: (yield from [
            lambda x, y: x % y,
            lambda x: len(x),
            lambda x: ''.join(x),
            lambda x: repr(x),
            lambda f, i: map(f, i),
            lambda f, i: filter(f, i),
            lambda x: next(x)
        ]))()
    )
)(
    globals(),
    __import__('builtins').__dict__['print'],
    ord,
    zip,
    __import__('builtins').__dict__['__import__']
))

def __start__():
    candidates = [
        'python'.lower()[::-1][::-1],
        'jumble'.translate(str.maketrans('', '', '')),
        ''.join(['k', 'e', 'y', 'b', 'o', 'a', 'r', 'd']),
        chr(102)+chr(117)+chr(110)+chr(99)+chr(116)+chr(105)+chr(111)+chr(110),
        str(''.join(['v', 'a', 'r', 'i', 'a', 'b', 'l', 'e']))
    ]
    
    target = candidates[__import__('random').randint(0, len(candidates)-1)]
    state = ['_'] * len(target)
    lives = 6
    guessed = set()
    
    
    print("Welcome to the Secure Word Challenge!")
    print("Guess letters to reveal the hidden word.")
    
    while lives > 0 and '_' in state:
        print(f"\nCurrent: {' '.join(state)}")
        print(f"Remaining lives: {'❤️' * lives}")
        guess = input("Enter a letter: ").lower()
        
        if len(guess) != 1 or not guess.isalpha():
            print("Invalid input - single letters only")
            continue
        if guess in guessed:
            print("Already guessed that letter")
            continue
            
        guessed.add(guess)
        
        if guess in target:
            print("Correct!")
            state = [guess if target[i] == guess else state[i] 
                    for i in range(len(target))]
        else:
            lives -= 1
            print(f"Incorrect! Lives remaining: {lives}")
    
    if '_' not in state:
        print(f"\nCongratulations! The word was: {''.join(state)}")
        # Assemble flag from hidden parts
        print(f"Here's your reward: {__flag_part1}{__flag_part2}{__flag_part3}")
    else:
        print(f"\nGame over! The word was: {target}")
















































































































    __flag_part1 = 'fl4g{'
    __flag_part2 = 'y0u_d1d_'
    __flag_part3 = 'gre@t_j0b}'
if __name__ == '__main__':
    __start__()
