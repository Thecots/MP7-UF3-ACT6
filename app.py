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


# mira si hay un ganador


# iniciar sesión ✓
@app.route('/')
def index():
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

#palabra
@app.route('/word')
def join():
  if(request.args.get('username') == None):
    return render_template('signin.html')
  cur = mysql.connection.cursor()
  cur.execute('UPDATE partides set guest=%s WHERE id_partida=%s',(request.args.get('username'),request.args.get('id')))
  mysql.connection.commit()

  cur.close()
  return redirect(url_for('game', username = request.args.get('username'), id = request.args.get('id')))


# partida
@app.route('/game')
def game():
  if(request.args.get('username') == None):
    return render_template('signin.html')
  username = request.args.get('username')
  id = request.args.get('id')
  title = 'Tu turno'
  winner = False
  tablero = [
    [0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0],
  ]

  # turno 
  cur = mysql.connection.cursor()
  cur.execute('SELECT * FROM partides WHERE id_partida={0}'.format(request.args.get('id')))
  data = cur.fetchall()
  if (data[0][2] == request.args.get('username')):
    #host
    if(data[0][4] == 1):
      title = 'Tu turno'
    else:
      title = 'Esperando movimiento del rival'
  else:
    #guest
    if(data[0][4] != 1):
      title = 'Tu turno'
    else:
      title = 'Esperando movimiento del rival'
  cur.close()

# montar tablero
  cur = mysql.connection.cursor()
  cur.execute('SELECT * FROM moviments WHERE id_partida={0}'.format(request.args.get('id')))
  data2 = cur.fetchall()
  if(data2):
    for i in data2:
      q = 5
      while q >= 0:
        if(tablero[q][i[2]] == 0):
          tablero[q][i[2]] = i[1]
          q = -99
        q = q-1
  cur.close()

  # checkear ganador
  w = checkWinner(tablero)
  if(w):
    if data[0][2] == request.args.get('username'):
      #host
      if(w == 1):
        title = 'Has ganado!'
      else:
        title = 'Has perdido'
      winner = True
    else:
      #guest
      if(w != 1):
        title = 'Has ganado!'
      else:
        title = 'Has perdido'
      winner = True



  return render_template('game.html',
  username = username,
  id = id,
  title = title,
  tablero = tablero,
  winner = winner
  )


# mover
@app.route('/move')
def move():
  if(request.args.get('username') == None):
    return render_template('signin.html')

  # jugador
  cur = mysql.connection.cursor()
  cur.execute('SELECT * FROM partides WHERE id_partida={0}'.format(request.args.get('id')))
  data = cur.fetchall()
  
  player = ''
  if (data[0][2] == request.args.get('username')):
    #host
    player = 1
  else:
    #guest
    player = 2

  # cambiar turno
  cur = mysql.connection.cursor()
  cur.execute('UPDATE  partides SET torn = IF(torn=1,2,1)  WHERE id_partida={0}'.format(request.args.get('id')))
  mysql.connection.commit()
  cur.close()

  # insertar movimento
  cur = mysql.connection.cursor()
  cur.execute('INSERT INTO moviments (jugador, columna_moviment, id_partida) VALUES (%s,%s,%s)',(player,request.args.get('move'),request.args.get('id')))
  mysql.connection.commit()
  cur.close()
  return redirect(url_for('game', username = request.args.get('username'), id = request.args.get('id')))



# partida vs IA
@app.route('/local')
def local():
  if(request.args.get('username') == None):
    return render_template('signin.html')
  
  return render_template('local.html', username = request.args.get('username'))


if __name__ == '__main__':
  app.run(port = 5050)
