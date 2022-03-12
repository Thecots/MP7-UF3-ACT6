from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mysqldb import MySQL
from datetime import date

# mysql
app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'ahorcado'
mysql = MySQL(app)

# iniciar sesión ✓
@app.route('/')
def index():
  print('hola')
  return render_template('signin.html')

# crear partida ✓
@app.route('/create')
def create():
  username = request.args.get('username')
  today = date.today()
  cur = mysql.connection.cursor()
  cur.execute('INSERT INTO partides (data, host, torn) VALUES(%s,%s,%s)',(today,username,1))
  mysql.connection.commit()
  cur.close()
  return render_template('waiting.html', username = request.args.get('username'), id = cur.lastrowid)

# buscar partidas ✓
@app.route('/search')
def search():
  print('hola')
  if(request.args.get('username') == None):
    return render_template('signin.html')

  cur = mysql.connection.cursor()
  cur.execute('SELECT * FROM partides WHERE ISNULL(guest)')
  data = cur.fetchall()
  cur.close()
  return render_template('search.html', username = request.args.get('username'), data = data)

# borrar partida ✓
@app.route('/delete')
def delete():
  if(request.args.get('username') == None):
    return render_template('signin.html')
  cur = mysql.connection.cursor()
  cur.execute('DELETE FROM partides WHERE id_partida={0}'.format(request.args.get('id')))
  mysql.connection.commit()
  cur.close()
  return redirect(url_for('search', username=request.args.get('username')))

# esperando rival✓
@app.route('/waiting')
def waiting():
  if(request.args.get('username') == None):
    return render_template('signin.html')
  cur = mysql.connection.cursor()
  cur.execute('SELECT * FROM partides WHERE id_partida={0}'.format(request.args.get('id')))
  data = cur.fetchall()
  cur.close()
  if(data[0][3] == None):
    return render_template('waiting.html', username = request.args.get('username'), id = request.args.get('id'))
  return redirect(url_for('word', username = request.args.get('username'), id = request.args.get('id')))

# unirse a partida ✓
@app.route('/join')
def join():
  if(request.args.get('username') == None):
    return render_template('signin.html')
  cur = mysql.connection.cursor()
  cur.execute('UPDATE partides set guest=%s WHERE id_partida=%s',(request.args.get('username'),request.args.get('id')))
  mysql.connection.commit()
  cur.close()
  return redirect(url_for('word', username = request.args.get('username'), id = request.args.get('id')))

# escojer palabra ✓
@app.route('/word')
def word():
  if(request.args.get('username') == None):
    return render_template('signin.html')

  cur = mysql.connection.cursor()
  cur.execute('SELECT * FROM partides WHERE id_partida={0}'.format(request.args.get('id')))
  data = cur.fetchall()
  
  state = False
  i = 0

  if(data[0][2] == request.args.get('username')):
    #jugador 1
    if(data[0][4] == None):
        state = False
    else:
      i += 1
      state = True
  else:
    #jugador 2
    if(data[0][5] == None):
        state = False
    else:
      i += 1
      state = True
  cur.close()

  print(i)
  if(data[0][5] != None and data[0][4] != None):
    return redirect(url_for('partida', username = request.args.get('username'), id = request.args.get('id')))
  else:
    return render_template('word.html',
    username = request.args.get('username'),
    id = request.args.get('id'),
    state = state)
  
@app.route('/setWordSave')
def setWordSave():
  cur = mysql.connection.cursor()
  cur.execute('SELECT * FROM partides WHERE id_partida={0}'.format(request.args.get('id')))
  data = cur.fetchall()
  if(data[0][2] == request.args.get('username')):
    #jugador 1
    cur.execute('UPDATE partides set hostWord=%s WHERE id_partida=%s',(request.args.get('word').lower(),request.args.get('id')))
    mysql.connection.commit()
    cur.close()
  else:
    #jugador 2
    cur.execute('UPDATE partides set guestWord=%s WHERE id_partida=%s',(request.args.get('word').lower(),request.args.get('id')))
    mysql.connection.commit()
    cur.close()
  cur.close()
  return redirect(url_for('word', username = request.args.get('username'), id = request.args.get('id')))

def vidas(p,l):
  arr = []
  template = ''

  for i in range(len(p)):
    arr.append(p[i])

  v = 7

  if(l != None):
    for i in range(len(l)):
      if(l[i] in arr):
        v = v
      else:
        v -= 1
  return v

def palabras(p,l):
  arr = []
  template = ''
  if(l != None):
    for i in range(len(l)):
      arr.append(l[i])

  for i in range(len(p)):
    if(p[i] in arr):
      template += '<span>'+p[i]+'</span>'
    else:
      template += '<span class="bar"></span>'

  return template

def palabraswin(p,l):
  arr = []
  word = 0
  if(l != None):
    for i in range(len(l)):
      arr.append(l[i])

  for i in range(len(p)):
    if(p[i] in arr):
      word += 1
  

  if(word == len(p)):
    return True
  return False

def winner(p2,l1,p1,l2):

  if(vidas(p2,l1) == 0):
    return 2
  
  if(vidas(p1,l2) == 0):
    return 1

  if(palabraswin(p2,l1)):
    return 1

  if(palabraswin(p1,l2)):
    return 2  

  return 0

# partida ✓
@app.route('/partida')
def partida():
  if(request.args.get('username') == None):
    return render_template('signin.html')

  cur = mysql.connection.cursor()
  cur.execute('SELECT * FROM partides WHERE id_partida={0}'.format(request.args.get('id')))
  data = cur.fetchall()

  win = ''
  hp1 = 0
  hp2 = 0
  turno = 1

  if(data[0][2] == request.args.get('username')):
    #jugador 1
    if(data[0][8] == '1'):
      #turno host
      turno = 1
    else:
      #turno guest
      turno = 0

    arr = []
    pal = data[0][5]

    if(data[0][6] != None):
      for i in range(len(data[0][6])):
        arr.append(data[0][6][i])

    if(winner(data[0][5],data[0][6],data[0][4],data[0][7]) == 1):
      win = 'Has ganado!'
      turno = 3
    elif(winner(data[0][5],data[0][6],data[0][4],data[0][7]) == 2):
      win = 'Has perdido'
      turno = 3

    cur.close()
    return render_template('game.html',
    username = request.args.get('username'),
    id = request.args.get('id'),
    turno = turno,
    win = win,
    hp1 = vidas(data[0][5],data[0][6]),
    hp2 = vidas(data[0][4],data[0][7]),
    p1 = palabras(data[0][5],data[0][6]),
    p2 = palabras(data[0][4],data[0][7]),
    arr = arr,
    pal = pal
    )
    
  else:
    #jugador 2
    if(data[0][8] == '1'):
      #turno host
      turno = 0
    else:
      #turno guest
      turno = 1

    arr = []
    pal = data[0][4]
    
    if(winner(data[0][5],data[0][6],data[0][4],data[0][7]) == 1):
      win = 'Has perdido'
      turno = 3
    elif(winner(data[0][5],data[0][6],data[0][4],data[0][7]) == 2):
      win = 'Has ganado!'
      turno = 3

    if(data[0][7] != None):
      for i in range(len(data[0][7])):
        arr.append(data[0][7][i])

    cur.close()
    return render_template('game.html',
      username = request.args.get('username'),
      id = request.args.get('id'),
      turno = turno,
      win = win,
      hp1 = vidas(data[0][4],data[0][7]),
      hp2 = vidas(data[0][5],data[0][6]),
      p1 = palabras(data[0][4],data[0][7]),
      p2 = palabras(data[0][5],data[0][6]),
      arr = arr,
      pal = pal
    )

# añadir letra
@app.route('/move')
def move():
  if(request.args.get('username') == None):
    return render_template('signin.html')

  cur = mysql.connection.cursor()
  cur.execute('SELECT * FROM partides WHERE id_partida={0}'.format(request.args.get('id')))
  data = cur.fetchall()

  if(data[0][2] == request.args.get('username')):
    #jugador 1
    cur.execute('UPDATE partides set hostLetters=%s , torn=2  WHERE id_partida=%s',(('' if data[0][6] == None else data[0][6])+request.args.get('letter'),request.args.get('id')))
    mysql.connection.commit()
    cur.close()
  else:
    #jugador 2
    cur.execute('UPDATE partides set guestLetters=%s , torn=1 WHERE id_partida=%s',(('' if data[0][7] == None else data[0][7])+request.args.get('letter'),request.args.get('id')))
    mysql.connection.commit()
    cur.close()
  cur.close()


  return redirect(url_for('partida', username = request.args.get('username'), id = request.args.get('id')))


# partida vs IA
@app.route('/local')
def local():
  if(request.args.get('username') == None):
    return render_template('signin.html')
  return render_template('local.html', username = request.args.get('username'))


if __name__ == '__main__':
  app.run(port = 5050)