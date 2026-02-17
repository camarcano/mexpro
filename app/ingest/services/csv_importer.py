"""Bulk import Trackman CSV data into the database."""

import hashlib
import logging
from datetime import datetime, timezone

from app.extensions import db
from app.models.pitch import Pitch
from app.models.game import Game
from app.models.player import Player
from app.models.upload_log import UploadLog
from app.ingest.services.csv_parser import parse_trackman_csv
from app.ingest.services.csv_validator import coerce_types

logger = logging.getLogger(__name__)

CHUNK_SIZE = 500


def compute_file_hash(filepath):
    """Compute SHA-256 hash of a file."""
    sha = hashlib.sha256()
    with open(filepath, 'rb') as f:
        for block in iter(lambda: f.read(8192), b''):
            sha.update(block)
    return sha.hexdigest()


def import_csv(filepath, filename, user_id=None):
    """Import a Trackman CSV into the database.

    Args:
        filepath: Full path to the CSV file.
        filename: Original filename for the upload log.
        user_id: ID of the user performing the upload (optional).

    Returns:
        UploadLog instance with import results.

    Yields:
        Progress dicts: {'step': str, 'current': int, 'total': int}
    """
    # Check for duplicate file
    file_hash = compute_file_hash(filepath)
    existing = UploadLog.query.filter_by(file_hash=file_hash, status='done').first()
    if existing:
        log = UploadLog(
            filename=filename,
            file_hash=file_hash,
            status='skipped',
            error_message=f'Duplicate file (matches upload #{existing.id})',
            uploaded_by_id=user_id,
        )
        db.session.add(log)
        db.session.commit()
        yield {'step': 'error', 'message': f'Duplicate file already imported as upload #{existing.id}'}
        return log

    # Create upload log
    log = UploadLog(
        filename=filename,
        file_hash=file_hash,
        status='processing',
        uploaded_by_id=user_id,
    )
    db.session.add(log)
    db.session.commit()

    try:
        yield {'step': 'parsing', 'message': 'Parsing CSV...'}
        df = parse_trackman_csv(filepath)

        yield {'step': 'validating', 'message': 'Validating and coercing types...'}
        df = coerce_types(df)

        total_rows = len(df)
        log.rows_total = total_rows
        imported = 0
        skipped = 0
        errors = 0

        # Extract game info from first row
        if total_rows > 0:
            first_row = df.iloc[0]
            game_id = first_row.get('game_id')
            if game_id:
                log.game_id = game_id
                _ensure_game(first_row)

        yield {'step': 'importing', 'message': f'Importing {total_rows} pitches...', 'total': total_rows}

        # Process in chunks
        for chunk_start in range(0, total_rows, CHUNK_SIZE):
            chunk = df.iloc[chunk_start:chunk_start + CHUNK_SIZE]
            batch = []

            for _, row in chunk.iterrows():
                pitch_uid = row.get('pitch_uid')
                if not pitch_uid:
                    errors += 1
                    continue

                # Skip if pitch already exists
                if Pitch.query.filter_by(pitch_uid=pitch_uid).first():
                    skipped += 1
                    continue

                # Auto-create players
                _ensure_player(row, 'pitcher_id', 'pitcher', 'pitcher_throws', 'pitcher_team')
                _ensure_player(row, 'batter_id', 'batter', None, 'batter_team')
                if row.get('catcher_id'):
                    _ensure_player(row, 'catcher_id', 'catcher', 'catcher_throws', 'catcher_team')

                # Build pitch record
                pitch_data = {col: row.get(col) for col in row.index if hasattr(Pitch, col)}
                pitch_data['upload_log_id'] = log.id
                batch.append(Pitch(**pitch_data))
                imported += 1

            if batch:
                db.session.bulk_save_objects(batch)
                db.session.commit()

            yield {
                'step': 'importing',
                'current': min(chunk_start + CHUNK_SIZE, total_rows),
                'total': total_rows,
                'imported': imported,
                'skipped': skipped,
            }

        # Update game pitch count
        if log.game_id:
            game = Game.query.filter_by(game_id=log.game_id).first()
            if game:
                game.total_pitches = Pitch.query.filter_by(game_id=log.game_id).count()
                # Mark as unverified if filename contains "unverified"
                game.is_verified = 'unverified' not in filename.lower()
                db.session.commit()

        log.rows_imported = imported
        log.rows_skipped = skipped
        log.rows_error = errors
        log.status = 'done'
        log.completed_at = datetime.now(timezone.utc)
        db.session.commit()

        yield {
            'step': 'done',
            'message': f'Import complete: {imported} imported, {skipped} skipped, {errors} errors',
            'imported': imported,
            'skipped': skipped,
            'errors': errors,
        }
        return log

    except Exception as e:
        logger.exception("CSV import failed")
        log.status = 'error'
        log.error_message = str(e)
        log.completed_at = datetime.now(timezone.utc)
        db.session.commit()
        yield {'step': 'error', 'message': str(e)}
        return log


def _ensure_game(row):
    """Create or update a Game record from a pitch row."""
    game_id = row.get('game_id')
    if not game_id:
        return

    game = Game.query.filter_by(game_id=game_id).first()
    if game is None:
        game = Game(
            game_id=game_id,
            game_uid=row.get('game_uid'),
            date=row.get('date'),
            home_team=row.get('home_team'),
            away_team=row.get('away_team'),
            stadium=row.get('stadium'),
            level=row.get('level'),
            league=row.get('league'),
        )
        db.session.add(game)
        db.session.commit()


def _ensure_player(row, id_field, name_field, throws_field, team_field):
    """Create or update a Player record."""
    trackman_id = row.get(id_field)
    if not trackman_id:
        return

    try:
        trackman_id = int(float(trackman_id))
    except (ValueError, TypeError):
        return

    player = Player.query.filter_by(trackman_id=trackman_id).first()
    name = row.get(name_field) if name_field else None

    if player is None:
        player = Player(
            trackman_id=trackman_id,
            name=name or f'Unknown ({trackman_id})',
            throws=row.get(throws_field) if throws_field else None,
            team=row.get(team_field) if team_field else None,
        )
        db.session.add(player)
        db.session.commit()
    else:
        # Update with latest info
        if name:
            player.name = name
        if throws_field and row.get(throws_field):
            player.throws = row.get(throws_field)
        if team_field and row.get(team_field):
            player.team = row.get(team_field)
        db.session.commit()
