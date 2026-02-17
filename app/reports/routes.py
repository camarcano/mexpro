from flask import render_template, request, send_file, abort
from flask_login import login_required
from app.reports import bp
from app.models.player import Player


@bp.route('/')
@login_required
def index():
    return render_template('reports/index.html')


@bp.route('/pitcher/<int:pitcher_id>/heatmap/<split>')
@login_required
def pitcher_heatmap(pitcher_id, split):
    """Serve a pitcher heatmap image as PNG."""
    from app.reports.services.heatmap_generator import HeatmapGenerator

    filters = {
        'game_id': request.args.get('game_id'),
        'start_date': request.args.get('start_date'),
        'end_date': request.args.get('end_date'),
    }
    filters = {k: v for k, v in filters.items() if v}

    gen = HeatmapGenerator(pitcher_id=pitcher_id, filters=filters)
    img_buf = gen.generate_heatmap(split=split)
    img_buf.seek(0)

    return send_file(img_buf, mimetype='image/png',
                     download_name=f'heatmap_{pitcher_id}_{split}.png')


@bp.route('/pitcher/by-name/<path:pitcher_name>/heatmap/<split>')
@login_required
def pitcher_heatmap_by_name(pitcher_name, split):
    """Serve a heatmap for a pitcher identified by name."""
    from app.reports.services.heatmap_generator import HeatmapGenerator

    filters = {
        'game_id': request.args.get('game_id'),
        'start_date': request.args.get('start_date'),
        'end_date': request.args.get('end_date'),
    }
    filters = {k: v for k, v in filters.items() if v}

    gen = HeatmapGenerator(pitcher_name=pitcher_name, filters=filters)
    img_buf = gen.generate_heatmap(split=split)
    img_buf.seek(0)

    return send_file(img_buf, mimetype='image/png',
                     download_name=f'heatmap_{pitcher_name}_{split}.png')


@bp.route('/pitcher/<int:pitcher_id>/pdf')
@login_required
def pitcher_pdf(pitcher_id):
    """Generate and serve a pitcher scouting report PDF."""
    from app.reports.services.pdf_generator import PitcherReportPDF

    player = Player.query.filter_by(trackman_id=pitcher_id).first_or_404()

    filters = {
        'game_id': request.args.get('game_id'),
        'start_date': request.args.get('start_date'),
        'end_date': request.args.get('end_date'),
    }
    filters = {k: v for k, v in filters.items() if v}

    pdf_gen = PitcherReportPDF(pitcher_id, player.name, filters)
    pdf_buf = pdf_gen.generate()
    pdf_buf.seek(0)

    filename = f"Pitcher_Report_{player.name.replace(' ', '_').replace(',', '')}.pdf"
    return send_file(pdf_buf, mimetype='application/pdf',
                     download_name=filename, as_attachment=True)
