"""Synthetic game regressions; no deployed game or external service is accessed."""
from copy import deepcopy
import unittest
from unittest.mock import patch

import main
from chess import Board, King, Pawn, Rook, WebInterface
from MoveHistory import MoveHistory


class HistoryTests(unittest.TestCase):
    def test_empty_history(self):
        history = MoveHistory(10)
        self.assertTrue(history.isempty())
        self.assertIsNone(history.pop())

    def test_pop_exhaustion_and_reuse(self):
        history = MoveHistory(3)
        history.push('first')
        self.assertEqual(history.pop(), 'first')
        self.assertTrue(history.isempty())
        self.assertIsNone(history.pop())
        history.push('new')
        self.assertEqual(history.pop(), 'new')
        self.assertTrue(history.isempty())

    def test_only_ten_latest_moves_survive_capacity(self):
        history = MoveHistory(10)
        for move in range(25):
            history.push(move)
        self.assertEqual([history.pop() for _ in range(10)], list(range(24, 14, -1)))
        self.assertTrue(history.isempty())
        self.assertIsNone(history.pop())

    def test_snapshot_owns_mutable_piece_state(self):
        board = Board()
        board.start()
        history = MoveHistory(10)
        history.push(board)
        board.move((0, 1), (0, 2))
        snapshot = history.pop()
        self.assertIsNotNone(snapshot.get_piece((0, 1)))
        self.assertTrue(snapshot.get_piece((0, 1)).notmoved)
        self.assertIsNone(snapshot.get_piece((0, 2)))

    def test_clear_starts_a_new_history(self):
        history = MoveHistory(2)
        history.push({'move': 1})
        history.clear()
        self.assertTrue(history.isempty())
        self.assertIsNone(history.pop())
        history.push({'move': 2})
        self.assertEqual(history.pop(), {'move': 2})

    def test_capacity_must_be_a_positive_integer(self):
        for value in [0, -1]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                MoveHistory(value)
        for value in [True, '10', 1.5]:
            with self.subTest(value=value), self.assertRaises(TypeError):
                MoveHistory(value)


class UndoRouteTests(unittest.TestCase):
    def setUp(self):
        # Rendering is covered separately below; isolate the state transition
        # assertions so missing templates cannot mask the original undo defects.
        self.render = patch('main.render_template', return_value='synthetic board')
        self.render.start()
        self.addCleanup(self.render.stop)
        main.app.config['TESTING'] = True
        main.game, main.ui, main.history = Board(), WebInterface(), MoveHistory(10)
        self.client = main.app.test_client()
        self.client.post('/newgame')

    def move(self, coordinates):
        return self.client.post('/play', data={'player_input': coordinates})

    def position(self, pieces):
        main.game._position = pieces
        for piece in pieces.values():
            piece.notmoved = True

    def test_undo_restores_piece_flags_and_turn(self):
        before = deepcopy(main.game._position)
        self.move('01 02')
        self.assertEqual(main.game.turn, 'Black')
        self.client.post('/undo')
        self.assertEqual(main.game.turn, 'White')
        self.assertEqual(set(main.game._position), set(before))
        self.assertTrue(main.game.get_piece((0, 1)).notmoved)
        self.assertTrue(main.history.isempty())

    def test_undo_of_empty_history_preserves_board_and_turn(self):
        before = repr(main.game._position)
        self.client.post('/undo')
        self.assertEqual(repr(main.game._position), before)
        self.assertEqual(main.game.turn, 'White')
        self.assertIn('empty', main.ui.errmsg)

    def test_new_game_clears_prior_undo_states(self):
        self.move('01 02')
        self.client.post('/newgame')
        self.assertTrue(main.history.isempty())
        self.client.post('/undo')
        self.assertEqual(main.game.turn, 'White')
        self.assertIsNotNone(main.game.get_piece((0, 1)))

    def test_undo_reopens_a_winning_game(self):
        self.position({(0, 0): Rook('White'), (4, 0): King('White'), (0, 1): King('Black')})
        self.move('00 01')
        self.assertEqual(main.game.winner, 'White')
        self.client.post('/undo')
        self.assertIsNone(main.game.winner)
        self.assertEqual(main.game.turn, 'White')
        self.assertEqual(main.game.get_piece((0, 1)).colour, 'Black')
        self.assertEqual(main.ui.direct, '/play')
        self.assertEqual(main.ui.btnlabel, 'MOVE')
        self.assertNotEqual(main.ui.endgame, 'disabled')

    def test_undo_pending_promotion_restores_the_pawn_and_turn(self):
        self.position({(0, 6): Pawn('White'), (4, 0): King('White'), (7, 7): King('Black')})
        self.assertEqual(self.move('06 07').location, '/promote')
        self.client.get('/promote')
        self.client.post('/undo')
        self.assertEqual(main.game.get_piece((0, 6)).name, 'pawn')
        self.assertFalse(main.game.promotion)
        self.assertEqual(main.game.turn, 'White')
        self.assertEqual(main.ui.direct, '/play')

    def test_undo_after_promotion_keeps_completed_promotion_state(self):
        self.position({(0, 6): Pawn('White'), (4, 0): King('White'), (7, 7): King('Black')})
        self.move('06 07')
        self.client.post('/promote', data={'player_input': 'q'})
        self.assertFalse(main.game.promotion)
        self.move('77 76')
        self.client.post('/undo')
        self.assertEqual(main.game.get_piece((0, 7)).name, 'queen')
        self.assertFalse(main.game.promotion)
        self.assertEqual(main.game.turn, 'Black')
        self.assertEqual(main.ui.direct, '/play')

    def test_new_game_resets_endgame_and_promotion_flags(self):
        main.game.promotion = True
        main.game.checkmate = 'White'
        main.game.winner = 'Black'
        main.ui.endgame = 'disabled'
        self.client.post('/newgame')
        self.assertFalse(main.game.promotion)
        self.assertIsNone(main.game.winner)
        self.assertIsNone(main.game.checkmate)
        self.assertNotEqual(main.ui.endgame, 'disabled')


class PageTests(unittest.TestCase):
    def setUp(self):
        main.app.config['TESTING'] = True
        main.game, main.ui, main.history = Board(), WebInterface(), MoveHistory(10)
        self.client = main.app.test_client()

    def test_home_and_existing_assets_render(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'SKITTLES CHESS GAME', response.data)
        for path in ['/static/style_a.css', '/static/horse.png']:
            with self.subTest(path=path):
                with self.client.get(path) as asset:
                    self.assertEqual(asset.status_code, 200)

    def test_normal_start_move_and_undo_render_real_templates(self):
        response = self.client.post('/newgame', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'White player:', response.data)
        response = self.client.post('/play', data={'player_input': '01 02'})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Black player:', response.data)
        response = self.client.post('/undo', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'White player:', response.data)


if __name__ == '__main__':
    unittest.main()
