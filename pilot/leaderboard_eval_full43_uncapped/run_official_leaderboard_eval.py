"""Only CLI argument adaptation; original main and mathematical functions unchanged."""
import contextlib,copy,traceback
from types import SimpleNamespace
from common import *
def main():
    boundary();verify_frozen();out=RUN/'official';out.mkdir(exist_ok=True)
    with (out/'evaluation_log.txt').open('w',encoding='utf-8') as log,contextlib.redirect_stdout(log),contextlib.redirect_stderr(log):
        try:
            import leaderboard_eval as official
            args=SimpleNamespace(gold_leaderboards_file=str(GOLD),masked_leaderboards_file='',normalized_output_file=str(NORMALIZED),eval_results_file=str(out/'eval_results.json'),eval_values_file=str(out/'eval_values.json'))
            save(out/'invocation.json',vars(args));print('Invoking unchanged leaderboard_eval.main(args)');official.main(args)
            gold=read(GOLD);pred=official.construct_output_leaderboards(gold,read(NORMALIZED))
            save(out/'generated_leaderboards.json',pred);save(out/'gold_after_official_conversion.json',gold)
            assert official.evaluate(pred,gold)==read(out/'eval_values.json')['gold_results']
            print('Original main, construct_output_leaderboards, evaluate and save_results completed; no model initialized.')
        except Exception:
            traceback.print_exc();raise
    verify_frozen();save(out/'execution_status.json',{'status':'COMPLETE','original_main_executed':True,'cli_only_adaptation':True,'network_forbidden':True,'new_api_requests':0,'source_sha256':sha(REPO/'leaderboard_eval.py')});print(json.dumps(read(out/'eval_results.json')))
if __name__=='__main__':main()
