from flask import Flask
from flask import render_template, redirect
from chess import WebInterface, Board
from flask import request
from MoveHistory import MoveHistory
from flask import Flask, render_template


app = Flask(__name__)
ui = WebInterface() #create instance of webinterface
game = Board() #create instance of the board
history = MoveHistory(10) #creates linkedlist of size 10

@app.after_request
def add_header(r):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r

@app.after_request
def add_header(response):
    response.cache_control.max_age = 0
    return response

@app.route('/') #returns index.html which is our start page
def root():
    return render_template('index.html')

@app.route('/newgame', methods=['POST','GET']) #returns the chess.html which contains our chessboard and redirects to /play
def newgame():
    # Note that in Python, objects and variables
    # in the global space are available to
    # top-level functions
    game.start()
    history.clear()
    ui.board = game.board_html()
    ui.inputlabel = f'{game.turn} player: '
    ui.errmsg = ' '
    ui.btnlabel = 'MOVE'
    ui.endgame = ' '
    ui.direct = '/play'
    game.winner = None
    ui.winner = game.winner
    return redirect('/play')


@app.route('/play',methods=['POST', 'GET']) #returns correct thing according to gameplay, redirects to /promote if necessary
def play():
    # TODO: get player move from GET request object
    # TODO: if there is no player move, render the page template
	if request.method == "GET":
		pass
	elif request.method == "POST":
		Move = request.form['player_input']
		ui.errmsg = ' '
		if not game.validation(Move):

			history.push(game)

			start, end = game.prompt(Move)
			game.update(start,end)
			coord = game.promotepawns()
            # colour = game.get_piece(coord).colour
			if game.promotion == True:
				# ui.direct = "/promote"
				# ui.inputlabel = f'{game.turn} pawn promote to:'
				# ui.btnlabel = "PROMOTE"
				return redirect('/promote')
			elif game.winner != None:
				ui.endgame = "disabled"
				ui.direct = "/newgame"
				ui.errmsg = game.msg
				ui.btnlabel = "NEW GAME"
				ui.board = game.board_html()
				return render_template('chess.html', ui=ui, game=game)
			ui.board = game.board_html()
			game.next_turn()
			ui.inputlabel = f'{game.turn} player: '
			ui.errmsg = game.msg
			return render_template('chess.html', ui=ui, game=game)
		else:
			ui.errmsg = game.validation(Move)
			return render_template('chess.html', ui=ui, game=game)
	ui.board = game.board_html()

	return render_template('chess.html', ui=ui, game=game)
    # TODO: Validate move, redirect player back to /play again if move is invalid
    # If move is valid, check for pawns to promote
    # Redirect to /promote if there are pawns to promote, otherwise 

@app.route('/promote', methods=['POST', 'GET']) #prompts the user to choose which piece to promote to, only allow player to continue playing (/play) when he promotes correctly
def promote():
    ui.board = game.board_html()
    ui.inputlabel = f'{game.turn} pawn promote to (Please choose from r, k, b, or q):'
    ui.btnlabel = "PROMOTE"
    ui.direct = "/promote"
    if request.method == "POST":
        promote = request.form['player_input']
        ui.errmsg = ' '
        if game.promoteprompt(promote) == False:
            ui.errmsg = f'Invalid promotion. Please choose from r, k, b, or q'
            return redirect('/promote')
        else:
            game.promote(promote)
            ui.board = game.board_html()
            game.next_turn()
            ui.inputlabel = f'{game.turn} player: '
            ui.btnlabel = "MOVE"
            ui.direct = "/play"
            ui.errmsg = game.msg
            return redirect('/play')
    return render_template('chess.html', ui=ui, game=game)

@app.route('/undo',methods=['POST', 'GET']) #gets the previous version of the chessboard board from movehistory.py (stores versions of chess.html) and returns it, redirects to /play
def undo():
    global game
    snapshot = history.pop()
    if snapshot is None:
        ui.errmsg = "Invalid undo. MoveHistory is empty."
        return redirect('/play')
    game = snapshot
    ui.board = game.board_html()
    ui.winner = game.winner
    ui.endgame = ' '
    ui.btnlabel = 'MOVE'
    ui.direct = '/play'
    ui.inputlabel = f'{game.turn} player: '
    game.msg = ' '
    ui.errmsg = game.msg
    return redirect('/play')

if __name__ == '__main__':
    app.run("0.0.0.0",debug=False, use_reloader=True)
