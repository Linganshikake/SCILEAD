"""Subprocess entrypoint: install safety guards before importing any test/official code."""
import runpy
import sys
from pathlib import Path
from runtime_policy import OWNED, offline_guard

if __name__ == '__main__':
    suite = sys.argv[1]
    if suite not in ('test_prompt_variant', 'test_transport', 'test_original_partially',
                     'test_original_cold_start'):
        raise ValueError('Unknown offline suite')
    offline_guard()
    (OWNED / 'reproducibility').mkdir(exist_ok=True)
    sys.argv = [str(OWNED / (suite + '.py'))]
    runpy.run_path(sys.argv[0], run_name='__main__')
