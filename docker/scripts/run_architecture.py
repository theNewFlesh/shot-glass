from pathlib import Path
import rolling_pin.repo_etl as rpo

root = '/home/ubuntu/shot-glass'
rpo.write_repo_architecture(
    Path(root, 'python'),
    Path(root, 'docs/architecture.svg'),
    exclude_regex='test|mock',
    orient='lr'
)
