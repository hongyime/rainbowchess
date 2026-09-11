# Rainbow Chess

Project page: https://hongyime.github.io/rainbowchess/ (GitHub Pages serves static content; run Flask locally to play.)

![Project screenshot](./screenshot.png)


A web-based chess game with a colorful rainbow-cycling background.

## Description

Rainbow Chess (also known as Skittles Chess Game) is a local two-player chess experiment built with Python and Flask. It includes a board, basic move checks, pawn promotion, and undo for up to 10 moves, with a rainbow color-cycling background. The existing rules use king capture to end a game and do not implement complete standard chess legality.

## Features

- Interactive chess board with Unicode chess piece symbols
- Basic movement checks for King, Queen, Rook, Bishop, Knight and Pawn; rule gaps remain
- Pawn promotion to Queen, Rook, Bishop, or Knight
- Undo functionality with a circular stack that stores up to 10 moves
- Rainbow color-cycling background animation
- Responsive web interface

## Technologies Used

- Python 3.12 (tested)
- Flask (web framework)
- Jinja2 (templating engine)
- HTML/CSS/JavaScript
- Gunicorn (WSGI HTTP Server)

## Installation

```bash
# Clone the repository
git clone https://github.com/theprawnorganisation/rainbowchess.git

# Navigate to project directory
cd rainbowchess

# Install dependencies
pip install -r requirements.txt
```

## Usage

```bash
# Run the application
python main.py
```

The game will start on `http://localhost:5000`. Open your browser and navigate to this address to play.

The current server shares one in-memory board and undo history across all visitors. Use it for a single local game; browser/session isolation, complete rule validation and production Flask hosting remain maintenance tasks. No game data is persisted to Supabase or another database.

### Checks

```bash
python -W error::ResourceWarning -m unittest discover -s tests -v
```

The application workflow runs these checks for source, template, asset and dependency changes. They cover bounded undo history, independent piece snapshots, new-game resets, promotion/winner restoration and actual Flask page rendering.

### How to Play

1. Click "START" to begin a new game
2. Enter moves in the format `XY XY` (e.g., `01 03` to move a piece from column 0, row 1 to column 0, row 3)
3. Coordinates are 0-7 for both columns and rows
4. Use the "UNDO" button to revert moves if needed

## Demo

The game was originally hosted at: http://skittles-chessapp.herokuapp.com/

## Disclaimer

1. FOR EDUCATIONAL PURPOSES ONLY
2. USE AT YOUR OWN DISCRETION

## License

Apache-2.0. See [LICENSE](LICENSE) and [NOTICE](NOTICE).
