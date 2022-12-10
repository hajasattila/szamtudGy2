import ply.lex as lex       #lexer
import ply.yacc as yacc     #parser

# El van tárolva az összes token, amit használni fogunk
tokens = [
    'INT',
    'FLOAT',
    'NAME',
    'PLUS',
    'MINUS',
    'DIVIDE',
    'MULTIPLY',
    'EQUALS'
]

# Regurális kifejezésekkel kifejezzük melyik kifejezés mit jelent
t_PLUS = r'\+'
t_MINUS = r'\-'
t_MULTIPLY = r'\*'
t_DIVIDE = r'\/'
t_EQUALS = r'\='

# a ply-nak specialitása, hogy mmegadhatjuk a lexernek, milyen értékeket igrnoáljon. Itt a "space" lesz
t_ignore = r' '

#a bonyolultabb tokeneket, ahol több dolog is van, azt functionban tudjuk megadni

#float. 1 vagy több számot követ egy pont, és azután megint van egy, vagy több szám
#floatnak fontos, hogy elől legyen, különben mindig int-nek érzékelni. Nem lehetne "." a számok között.
def t_FLOAT(t):
    r'\d+\.\d+'  # regurális érték, ha pl 1.1 lenne
    try:
        t.value = float(t.value)
    except ValueError:          #Hibakezelés
        print("Valahogy a float nem jó %d", t.value)
        t.value = 0
        return t
    return t

#Egy, vagy annál hosszabb számok. Ha túlfut, vagy nem megfelelő az érték, akkor hibát ír
def t_INT(t):
    r'\d+'
    try:
        t.value = int(t.value)
    except ValueError:
        t.value = 0
        return print("Túl nagy az inted")
    return t

#A NAME az lesz majd a változók neve, amiben eltárolhatjuk a számokat
#a változó nevének megadjuk, hogy az eleje csak betű lehet a-zA-Z között, vagy _. Ezután bármilyen karakter állhat
def t_NAME(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = 'NAME'
    return t

#skippelek, ha baj van, és jelzem mi a probléma
def t_error(t):
    print("Nem megengedett karakter!")
    t.lexer.skip(1)
    
# lexer építése
lexer = lex.lex()

#megfelelő sorrendet értelmezi a parser
precedence = (
    ('left', 'PLUS', 'MINUS'),
    ('left', 'MULTIPLY', 'DIVIDE')
)

#definiáljuk a nyelvtanunkat. amit engedélyezünk: expressions (kifejezések), var_assigns(változó hozzárendelések), és empty mezők
def p_calc(p):
    '''
    calc : expression
         | var_assign
         | empty
    '''
    print(run(p[1]))

def p_var_assign(p):
    '''
    var_assign : NAME EQUALS expression
    '''
    p[0] = ('=', p[1], p[3])


# rekurzív
def p_expression(p):
    
    #kifejezések után, mik következhetnek. Szorzás, osztás, hozzáadás, kivonás
    '''
    expression : expression MULTIPLY expression
               | expression DIVIDE expression
               | expression PLUS expression
               | expression MINUS expression
    '''
    # Fát épít ki
    p[0] = (p[2], p[1], p[3])

def p_expression_int_float(p):
    '''
    expression : INT
               | FLOAT
    '''
    p[0] = p[1]

def p_expression_var(p):
    '''
    expression : NAME
    '''
    p[0] = ('var', p[1])

#visszajelzés, ha nem megfelelő az input a "nyelvtanuknak" megfelelően
# a p_error egy speciális ply fügvény
def p_error(p):
    return print("Szintakszis hiba!")
        
    
def p_empty(p):
    '''
    empty : expression
    '''
    p[0] = "Üresen hagytad a mezőt!"

# parser létrehozása
parser = yacc.yacc()

#változók tárolására való hely
env = {}

# a run function lesz a rekurzív függvényünk, ami bejárja a fát, amit a parser generált
def run(p):
    global env          #elakarjuk érni a kinti változónkat
    #Ha király a típus, akkor a megfelelő művelet alapján megcsináljuk a dolgunkat.
    if type(p) == tuple:
        if p[0] == '+':
            return run(p[1]) + run(p[2])
        elif p[0] == '-':
            return run(p[1]) - run(p[2])
        elif p[0] == '*':
            return run(p[1]) * run(p[2])
        elif p[0] == '/':
            return run(p[1]) / run(p[2])
        elif p[0] == '=':
            env[p[1]] = run(p[2])
            return ''
        elif p[0] == 'var':
            if p[1] not in env:         #ha nem szerepel a változó nevünk a dict-ben akkor
                return 'Nem deklarált változó nevet használtál!'
            else:
                return env[p[1]]
    else:
        return p


# Mindig adatot kérünk be, majd megfelelően végrehajtuk az utasítást
while True:
    try:
        s = input('>> ')
    except EOFError:        #ha nem olvasunk be valami megfelelő adatot, akkor break
        break
    parser.parse(s)
