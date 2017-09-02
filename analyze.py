import subprocess
import urllib2
import sys
import ssl
import re
import os
import platform
import gomoku_png

# Create directories for the results, if they don't exist already.
if not os.path.exists('sav'):
    os.makedirs('sav')
if not os.path.exists('results'):
    os.makedirs('results')

context = ssl._create_unverified_context()

if platform == 'Windows':
    args = "engine.exe"
else:
    args = ["/usr/local/bin/wine", "engine.exe"]

p = subprocess.Popen(args, stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr = subprocess.PIPE)

def send_command(p, s):
    #print(s)
    b = (s + '\r\n').encode('ascii')
    p.stdin.write(b)

def go(stones, turn):
    if not stones:
        return (107, 'h8')
    
    send_command(p, 'start 15 15')
    send_command(p, 'info rule 1')
    send_command(p, 'board');
    for stone in stones:
        send_command(p, '%d,%d,%d' % stone)
    send_command(p, 'done');                              
    p.stdin.flush()
    p.stdout.readline()
    p.stdout.readline()
    p.stdout.readline()

    lines = []
    lines.append(p.stdout.readline())
    lines.append(p.stdout.readline())
    lines.append(p.stdout.readline())

    evaluation = int(lines[0].decode('ascii').split('|')[-1].split()[0])
    if turn == 2:
        evaluation = -evaluation
        
    move = lines[2].decode('ascii').rstrip()
    x,y = move.split(',')
    move = chr(int(x) + ord('a')) + str(int(y) + 1) 

    return (evaluation, move)

def save_moves(table, moves):
    with open("sav/" + table + ".sav", "w") as f:
        f.write('15\r\n15\r\n%d\r\n' % len(moves))
        for move in moves:
            f.write('%d %d\r\n' % (15 - int(move[1:]), int(ord(move[0]) - ord('a'))))
        
def analyze(table):
    print("Analyzing table %s" % table)
    game = urllib2.urlopen('https://www.playok.com/en/game.phtml?gid=gm&pid=%s&txt' % (table), context=context).read().decode('ascii')

    stones = []
    moves = []

    turn = 1
    for stone in game.split('\r\n\r\n')[1].split():
        if (not stone[0].isdigit()):
            moves.append(stone)
            s = (ord(stone[0]) - ord('a'), int(stone[1:]) - 1, turn)
            stones.append(s)
            turn = 2 if turn == 1 else 1

    save_moves(table, moves)

    results = []
    for i in range(len(stones) - 1, -1, -1):
        evaluation, suggested_move = go(stones[:i], i % 2 + 1)
        if suggested_move == moves[i] and results:
            evaluation = results[0][0]
        result = (evaluation, suggested_move, moves[i])
        print(result)
        results.insert(0, result)

    analysis = []
    with open("results/" + table + ".txt", "w") as f:
        for i in range(len(results)):
            suggested_evaluation, suggested_move, move = results[i]
            if i + 1 < len(results):
                actual_evaluation = results[i + 1][0]
            else:
                actual_evaluation = results[i][0]
            analysis_line = (move, actual_evaluation, suggested_move, suggested_evaluation)
            analysis.append(analysis_line)
            f.write('%s,%s,%s,%s\n' % analysis_line)
    write_analysis(analysis)

def write_analysis(analysis):
    folder = 'analysis/' + str(table)
    os.makedirs(folder)
    stones = []
    move = 1
    for played, actual_evaluation, suggested_move, suggested_evaluation in analysis:
        loss = suggested_evaluation - actual_evaluation
        if move % 2 == 0:
            loss = -loss
        # If the loss is significant, output a png file showing the position.
        if loss > 100:
            gomoku_png.go(15, (played + '*r') + ' ' + (suggested_move + '*g') + ' ' + ' '.join(stones), folder + '/' + str(move) + '.png', None)
        move += 1
        stones.append(played)

if len(sys.argv) > 1:
    #table = sys.argv[1]
    #analyze(table)
    username = sys.argv[1]
    url = 'https://www.playok.com/en/stat.phtml?gid=gm&uid=%s&sk=2' % username
    games = urllib2.urlopen(url, context=context).read().decode('ascii')
    tables = re.findall(r'game.phtml\?gid=gm&amp;pid=(\d+)&amp;txt', games)
    for table in tables:
        if not os.path.isfile("results/" + table + ".txt"):    
            analyze(table)
else:
    print('Usage: python analyze.py username')
