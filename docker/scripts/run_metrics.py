from pathlib import Path
import rolling_pin.repo_etl as rpo

root = '/home/ubuntu/shot-glass'
rpo.write_repo_plots_and_tables(
    Path(root, 'python'),
    Path(root, 'docs/plots.html'),
    Path(root, 'docs'),
)